# SystemRDL Field Properties

Fields are the lowest-level structural component. All field behavior is determined by the combination of properties set on the field.

## Software and Hardware Access

### `sw` — Software Access Type

Controls how software (the CPU/bus) can access the field.

| Value | Meaning |
|-------|---------|
| `rw` or `wr` | Read and write (default) |
| `r` | Read-only |
| `w` | Write-only |
| `na` | No access |
| `rw1` | Read-write, but software can only write once after reset |
| `w1` | Write-only, but software can only write once after reset |

Dynamic: **Yes**

### `hw` — Hardware Access Type

Controls how hardware (RTL logic) can access the field.

| Value | Meaning |
|-------|---------|
| `rw` | Hardware reads and writes (default) |
| `r` | Hardware reads only |
| `w` | Hardware writes (provides input value) |
| `na` | No hardware access |

Dynamic: **No**

### sw + hw Combinations

| `sw` | `hw` | Implementation |
|------|------|----------------|
| `rw` | `rw` | Storage element |
| `rw` | `r`  | Storage element |
| `rw` | `w`  | Storage element |
| `rw` | `na` | Storage element |
| `r`  | `rw` | Storage element |
| `r`  | `r`  | Wire/Bus — constant value |
| `r`  | `w`  | Wire/Bus — hardware assigns value |
| `r`  | `na` | Wire/Bus — constant value |
| `w`  | `rw` | Storage element |
| `w`  | `r`  | Storage element |
| `w`  | `w`  | **Error** — meaningless |
| `w`  | `na` | **Error** — meaningless |
| `na` | `rw` | Undefined |
| `na` | `r`  | Undefined |
| `na` | `w`  | **Error** — unloaded net |
| `na` | `na` | **Error** — nonexistent net |

> Any hardware-writable field is inherently volatile.

All hardware-writable fields are continuously driven (combinationally) unless a write-enable (`we`/`wel`) is specified.

---

## Reset Value

The reset value is specified at instantiation time after `=`:

```systemrdl
field {} data[8] = 8'hAB;    // reset value 0xAB
field {} flags[4] = 0;        // reset value 0
```

By default (if not specified), the reset value is unknown (`x` in simulation). A signal-driven reset can be specified with `resetsignal`.

---

## Hardware Signal Properties

These properties connect a field to hardware signals for reset, write-enable, and output generation.

| Property | Type | Dynamic | Description |
|----------|------|---------|-------------|
| `activehigh` | `boolean` | No | Reset/enable signal is active-high (default) |
| `activelow` | `boolean` | No | Reset/enable signal is active-low |
| `resetsignal` | `reference` | No | Signal instance that drives this field's reset |
| `reset` | `bit` | No | Static or signal-driven reset value (alternative to `= value` syntax) |
| `we` | `boolean` or `reference` | No | Write-enable active-high; if reference, connects to that signal/field |
| `wel` | `boolean` or `reference` | No | Write-enable active-low |
| `hwenable` | `reference` | No | Hardware enable signal (alternative to `we` for HW writes) |
| `hwmask` | `reference` | No | Hardware mask signal; masked bits not written by HW |
| `hwclr` | `boolean` | No | Hardware can clear (zero) the field by asserting a pin |
| `hwset` | `boolean` | No | Hardware can set (all-ones) the field by asserting a pin |
| `anded` | `boolean` | No | Generate AND-reduction output signal |
| `ored` | `boolean` | No | Generate OR-reduction output signal |
| `xored` | `boolean` | No | Generate XOR-reduction output signal |

```systemrdl
// Field with a dedicated reset signal
signal rst_n { activelow; };
rst_n hw_rst;

field { resetsignal = hw_rst; } my_field[8] = 0;

// Field with write-enable
signal wr_en { activehigh; };
wr_en we_sig;
field { hw = rw; we = we_sig; } guarded_field[8] = 0;
```

---

## Software Read Side-Effect Properties

These properties describe what happens to the field's value when software reads it.

| Property | Type | Dynamic | Behavior |
|----------|------|---------|----------|
| `rclr` | `boolean` | Yes | Clear (zero) field on software read |
| `rset` | `boolean` | Yes | Set (all-ones) field on software read |
| `onread` | `onreadtype` | Yes | Parameterized read side-effect (see table below) |

`onread` values:

| Value | Behavior |
|-------|----------|
| `rclr` | All bits cleared on read (field = 0) |
| `rset` | All bits set on read (field = all 1s) |
| `ruser` | Read modifies field in a custom way; field must be `external` |

> `rclr`, `rset`, and `onread` are **mutually exclusive** — only one may be set per field.
> A field with `onread = ruser` must be declared `external`.
> A field with any `onread` property must have software read access (`sw = r` or `sw = rw`).
> When `rclr` is active, the reset clears to 0, not to the field's default reset value.

---

## Software Write Function Properties

These properties describe how software write data is applied to the field.

| Property | Type | Dynamic | Behavior |
|----------|------|---------|----------|
| `woset` | `boolean` | Yes | Write-one-to-set: `field = field \| write_data` |
| `woclr` | `boolean` | Yes | Write-one-to-clear: `field = field & ~write_data` |
| `onwrite` | `onwritetype` | Yes | Parameterized write function (see table below) |

`onwrite` values:

| Value | Behavior |
|-------|----------|
| `woset` | Bitwise write-one-to-set: `field \| write_data` |
| `woclr` | Bitwise write-one-to-clear: `field & ~write_data` |
| `wot` | Bitwise write-one-to-toggle: `field ^ write_data` |
| `wzs` | Bitwise write-zero-to-set: `field \| ~write_data` |
| `wzc` | Bitwise write-zero-to-clear: `field & write_data` |
| `wzt` | Bitwise write-zero-to-toggle: `field ~^ write_data` |
| `wclr` | All bits cleared on any write: `field = 0` |
| `wset` | All bits set on any write: `field = all 1s` |
| `wuser` | Custom write behavior; field must be `external` |

> `onwrite`, `woclr`, and `woset` are **mutually exclusive** — only one may be set per field.
> A field with `onwrite = wuser` must be declared `external`.
> A field with any `onwrite` property must have software write access.

```systemrdl
// Interrupt status field: set by hardware, cleared by software writing 1
field { sw = rw; hw = w; woclr; intr; } irq_status[1] = 0;

// Bitmask enable: software sets bits, hardware reads
field { sw = rw; hw = r; woset; } irq_enable[8] = 0;

// Status register with clear-on-read
field { sw = r; hw = w; rclr; } event_count[8] = 0;
```

---

## Software Control Properties

| Property | Type | Dynamic | Description |
|----------|------|---------|-------------|
| `swwe` | `boolean` or `reference` | Yes | SW write-enable active-high; if false, field is effectively read-only to SW |
| `swwel` | `boolean` or `reference` | Yes | SW write-enable active-low; mutually exclusive with `swwe` |
| `swmod` | `boolean` | Yes | Generate output signal when field is modified by SW (write, or read with side-effect) |
| `swacc` | `boolean` | Yes | Generate output signal whenever field is accessed by SW |
| `singlepulse` | `boolean` | No | Field is 1-bit; asserts for one cycle when SW writes 1, then auto-clears to 0; reset must be 0 |

```systemrdl
// Locked register: only writable when lock signal is inactive
signal lock_sig {};
field { sw = rw; swwel = lock_sig; } locked_field[8] = 0;

// Trigger register: single-pulse
field { sw = rw; hw = r; singlepulse; } trigger[1] = 0;
```

---

## Counter Properties

Counter fields track hardware event counts. The counter type (up/down/up-down) is inferred from which increment/decrement properties are present.

| Property | Type | Dynamic | Description |
|----------|------|---------|-------------|
| `counter` | `boolean` | No | Marks field as a counter |
| `incrvalue` | `longint unsigned` or `reference` | No | Increment amount (default: 1) or reference to controlling field/signal |
| `decrvalue` | `longint unsigned` or `reference` | No | Decrement amount (default: 1) or reference to controlling field/signal |
| `incrwidth` | `longint unsigned` | No | Bit width of external increment-value bus (alternative to `incrvalue`) |
| `decrwidth` | `longint unsigned` | No | Bit width of external decrement-value bus (alternative to `decrvalue`) |
| `incr` | `reference` | No | Signal or field that triggers the increment event |
| `decr` | `reference` | No | Signal or field that triggers the decrement event |
| `overflow` | — | — | Read-only reference target: asserts when counter overflows |
| `underflow` | — | — | Read-only reference target: asserts when counter underflows |
| `incrsaturate` | `boolean` or `longint unsigned` | No | If true: saturate at max. If value N: saturate at N |
| `decrsaturate` | `boolean` or `longint unsigned` | No | If true: saturate at 0. If value N: saturate at N |
| `incrthreshold` | `boolean` or `longint unsigned` | No | Generate threshold output when field ≥ N (or max if true) |
| `decrthreshold` | `boolean` or `longint unsigned` | No | Generate threshold output when field ≤ N (or 0 if true) |

Counter type is inferred:
- Only `incrvalue`/`incrwidth`/`incr` → **up counter**
- Only `decrvalue`/`decrwidth`/`decr` → **down counter**
- Both incr and decr properties → **up/down counter**

```systemrdl
// Simple 8-bit up counter, incremented by hardware
field { counter; hw = r; sw = rw; } event_cnt[8] = 0;

// 16-bit saturating up counter, value incremented by 2
field {
    counter;
    hw = r; sw = rw;
    incrvalue = 2;
    incrsaturate;          // saturates at max value (0xFFFF)
} packet_cnt[16] = 0;

// Up/down counter with overflow output connected to another field
field {
    counter;
    hw = r; sw = rw;
    incrvalue = 1;
    decrvalue = 1;
} updown_cnt[8] = 0;

reg my_reg {
    field { counter; hw = r; sw = rw; } cnt[16] = 0;
    field { sw = r;  hw = w; } ovf[1]  = 0;
};
// Connect overflow to the status bit
my_reg r1;
r1.ovf->next = r1.cnt->overflow;
```

---

## Interrupt Properties

Interrupt fields capture hardware events that need software attention.

| Property | Type | Dynamic | Description |
|----------|------|---------|-------------|
| `intr` | `boolean` | No | Marks this field as an interrupt status bit |
| `nonsticky` | `boolean` | No | Interrupt auto-clears when source deasserts (must use with `intr`) |
| `sticky` | `boolean` | No | Interrupt holds until software clears (default behavior with `intr`) |
| `stickybit` | `boolean` | No | Individual sticky bit: each bit is independent |
| `enable` | `reference` | No | Reference to field/signal that enables this interrupt |
| `mask` | `reference` | No | Reference to field/signal that masks this interrupt |
| `haltenable` | `reference` | No | Reference to halt-enable field/signal |
| `haltmask` | `reference` | No | Reference to halt-mask field/signal |

A register containing any `intr` field automatically generates an interrupt output — the OR (or AND) of all enabled, unmasked interrupt bits. This output can be connected to a parent addrmap's interrupt input.

```systemrdl
reg irq_status_r {
    // Interrupt enable register in same peripheral
    // (defined elsewhere as irq_enable_r)

    field { sw = rw; hw = w; woclr; intr; sticky; } uart_rx[1]   = 0;
    field { sw = rw; hw = w; woclr; intr; sticky; } uart_tx[1]   = 0;
    field { sw = rw; hw = w; woclr; intr; nonsticky; } dma_done[1] = 0;
};
```

---

## Miscellaneous Field Properties

| Property | Type | Dynamic | Description |
|----------|------|---------|-------------|
| `encode` | `reference` (enum type) | No | Assigns an enum type to this field for value encoding/documentation |
| `fieldwidth` | `longint unsigned` | No | Default bit width for definitively-defined fields instantiated without explicit size |

```systemrdl
enum priority_e {
    LOW    = 2'd0;
    MEDIUM = 2'd1;
    HIGH   = 2'd2;
    URGENT = 2'd3;
};

field priority_f {
    sw = rw;
    hw = r;
    encode = priority_e;
    fieldwidth = 2;           // default width when instantiated as: priority_f my_inst;
};

reg task_reg {
    priority_f task_priority;  // 2 bits wide (from fieldwidth)
    priority_f irq_priority;
};
```
