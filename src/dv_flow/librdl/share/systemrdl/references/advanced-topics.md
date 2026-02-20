# SystemRDL Advanced Topics

## Signals

Signals model hardware wires used for resets, write-enables, and hardware enables within a SystemRDL description. A signal is not a register — it represents a pin or wire driven externally.

### Signal Definition

```systemrdl
signal signal_type_name {
    // signal properties
    activehigh;     // or activelow
    // sync or async
};
signal_type_name instance_name;
```

Or anonymously:
```systemrdl
signal { activelow; } rst_n;
```

### Signal Properties

| Property | Type | Description |
|----------|------|-------------|
| `activehigh` | `boolean` | Signal asserts at logic 1 (default) |
| `activelow` | `boolean` | Signal asserts at logic 0 |
| `sync` | `boolean` | Synchronous signal |
| `async` | `boolean` | Asynchronous signal |

`activehigh` and `activelow` are mutually exclusive.

### Using Signals for Reset

```systemrdl
// Define a reset signal
signal { activelow; async; } rst_n;

// Reference it in a field
field my_f {
    resetsignal = rst_n;    // this field resets when rst_n asserts
    hw = rw; sw = rw;
};
reg my_reg {
    signal { activelow; } local_rst;
    my_f data[8] = 0;
};
```

The reset polarity is determined by `activehigh`/`activelow` on the signal itself. The reset value (what the field resets to) comes from the `= value` at instantiation.

### Signal Scope

A signal instance is accessible within the component where it is defined and all nested components. Signals are typically defined at the `addrmap` or `reg` level where they're used.

---

## Reset Application

There are three ways to specify a field's reset value:

1. **Inline at instantiation** (most common):
   ```systemrdl
   field {} data[8] = 8'hAB;    // resets to 0xAB
   ```

2. **Via signal** (`resetsignal`):
   ```systemrdl
   signal { activelow; } rstn;
   field { resetsignal = rstn; } data[8] = 8'h00;
   // When rstn asserts (goes low), data resets to 0x00
   ```

3. **Unknown reset** (default when `=` is omitted):
   ```systemrdl
   field {} data[8];    // reset value is X (unknown)
   ```

Multiple reset signals at different levels can be used within the same register or addrmap.

---

## Hierarchical Interrupts

SystemRDL supports a hierarchy of interrupt sources that propagate up through nested addrmaps.

### Interrupt Field Model

A field with `intr` marks a hardware interrupt source. Fields can be:
- **Sticky** (`intr; sticky;` or just `intr`): The field holds its asserted state until software clears it (e.g., by writing 1 with `woclr`).
- **Non-sticky** (`intr; nonsticky;`): The field reflects the real-time state of the source; clears automatically when the source deasserts.
- **Sticky-bit** (`intr; stickybit;`): Each bit is individually sticky.

### Enable and Mask

```systemrdl
reg irq_status_r {
    field { sw = rw; hw = w; woclr; intr; sticky; } src_a[1] = 0;
    field { sw = rw; hw = w; woclr; intr; sticky; } src_b[1] = 0;
};

reg irq_enable_r {
    field { sw = rw; hw = r; } en_a[1] = 1;
    field { sw = rw; hw = r; } en_b[1] = 1;
};

addrmap irq_block {
    irq_status_r status @ 0x0;
    irq_enable_r enable @ 0x4;

    // Connect enable fields to interrupt status fields
    status.src_a->enable = enable.en_a;
    status.src_b->enable = enable.en_b;
};
```

### Interrupt Hierarchy

A register's interrupt output (OR of all enabled, active `intr` fields) can feed a field in a parent addrmap's interrupt register:

```systemrdl
// Leaf level: a peripheral with its own interrupt register
addrmap uart_0 {
    reg { field { sw=rw; hw=w; woclr; intr; sticky; } rx_err[1]=0; } irq @ 0x0;
    // ... other regs
};

// Top level: aggregates interrupts from sub-modules
addrmap top_chip {
    reg top_irq_r {
        field { sw=rw; hw=w; woclr; intr; sticky; } uart0_irq[1] = 0;
        field { sw=rw; hw=w; woclr; intr; sticky; } uart1_irq[1] = 0;
    };

    uart_0 uart0 @ 0x1000;
    uart_0 uart1 @ 0x2000;

    top_irq_r top_irq @ 0x0;

    // Wire leaf interrupt outputs to top-level interrupt fields
    top_irq.uart0_irq->next = uart0.irq.rx_err;
    top_irq.uart1_irq->next = uart1.irq.rx_err;
};
```

### Halt Enable and Halt Mask

For designs that distinguish between maskable and non-maskable interrupts, `haltenable` and `haltmask` provide a parallel interrupt path that cannot be masked by software:

```systemrdl
status.src_a->haltenable = halt_enable.en_a;
status.src_a->haltmask   = halt_mask.msk_a;
```

---

## Bit Ordering

### `lsb0` (default)

Bit 0 is the least significant bit. Field ranges are written as `[MSB:LSB]` where MSB > LSB:

```systemrdl
field {} f[7:0];    // 8-bit field occupying bits 7 down to 0
field {} g[15:8];   // 8-bit field occupying bits 15 down to 8
```

Fields placed implicitly start from bit 0 and pack upward.

### `msb0`

Bit 0 is the most significant bit (reversed convention). Set on the containing `addrmap`:

```systemrdl
addrmap msb_map {
    msb0;

    reg my_reg {
        field {} f[0:7];    // 8-bit field, bit 0 is MSB
        field {} g[8:15];   // 8-bit field, bits 8..15
    };
};
```

`msb0` and `lsb0` are mutually exclusive and apply to all registers within the addrmap.

---

## Byte Ordering

`bigendian` and `littleendian` are set on `addrmap` and describe how multi-byte registers are accessed across the bus:

```systemrdl
addrmap big_endian_map {
    bigendian;
    // ...
};

addrmap little_endian_map {
    littleendian;    // common for ARM-based systems
    // ...
};
```

These are mutually exclusive. They affect how software byte-lane accesses map to register field bits.

---

## Preprocessor Directives

SystemRDL supports two preprocessor mechanisms: Verilog-style macros and embedded Perl.

### Verilog-Style Preprocessor

Preprocessor directives begin with a backtick (`` ` ``).

#### Macro Define and Use

```systemrdl
`define NUM_CHANNELS 8
`define BASE_ADDR    32'h4000_0000

addrmap chip {
    reg { field {} data[32]; } ch[`NUM_CHANNELS] @ `BASE_ADDR;
};
```

#### Conditional Compilation

```systemrdl
`define INCLUDE_DEBUG 1

`ifdef INCLUDE_DEBUG
    reg { field {} dbg_data[32]; } debug_reg @ 0xFF0;
`elsif INCLUDE_TRACE
    reg { field {} trace[32]; } trace_reg @ 0xFF0;
`else
    // no debug register
`endif
```

Directives: `` `ifdef ``, `` `ifndef ``, `` `elsif ``, `` `else ``, `` `endif ``, `` `undef ``, `` `resetall ``

#### File Inclusion

```systemrdl
`include "common_fields.rdl"
`include "peripheral_defs.rdl"
```

- Included files are processed as if their content were inserted at the point of the `` `include ``.
- Circular includes are not permitted.
- Nesting depth of includes may be limited by the compiler.

### Embedded Perl Preprocessing

Perl code can be embedded for generating repetitive structures. Perl blocks are delimited by `<%` `%>`. Inline expressions use `<%= expr %>`.

```systemrdl
<% my $num_ch = 4; %>

addrmap generated_map {
<% for my $i (0 .. $num_ch - 1) { %>
    reg { field {} data[32]; } ch_<%= $i %> @ <%= $i * 4 %>;
<% } %>
};
```

The Perl preprocessor runs before the SystemRDL compiler, so its output must be valid SystemRDL.

---

## Content Deprecation (`ispresent`)

The `ispresent` property (universal, boolean, dynamic) can be used to conditionally remove components from the compiled design:

```systemrdl
reg optional_feature_r { field {} ctrl[32] = 0; };

addrmap configurable {
    optional_feature_r opt @ 0x100;

    `ifdef NO_OPT_FEATURE
    opt->ispresent = false;   // removed from final design
    `endif
};
```

Setting `ispresent = false` removes the instance and all its children from elaboration. The address space it would have occupied is freed.

---

## Alias Registers — Advanced Use

Alias registers are typically used for:
- **Byte-lane access**: provide 8-bit write aliases for a 32-bit register
- **Read vs. write semantics**: read alias has `rclr`, write alias has `woclr`
- **Shadow registers**: write-only alias at a different address clears the primary

```systemrdl
reg primary_r {
    field { sw = rw; hw = rw; } data[32] = 0;
};

reg clear_alias_t {
    field { sw = w; hw = r; woclr; } data[32];   // write-one-to-clear view
};

primary_r      main_reg    @ 0x00;
alias clear_alias_t main_reg : clear_reg @ 0x04;
```

Both `main_reg` and `clear_reg` share the same physical storage. Writing to `clear_reg` clears individual bits; reading/writing `main_reg` has normal read-write semantics.
