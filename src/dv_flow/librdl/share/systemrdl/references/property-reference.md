# SystemRDL Built-In Property Reference

Quick reference for all built-in SystemRDL properties. **Dyn** = property can be assigned dynamically (after instantiation with `inst->prop = val`).

---

## Universal Properties (All Components)

| Property | Type | Default | Dyn | Components | Description |
|----------|------|---------|-----|------------|-------------|
| `name` | `string` | instance name | Yes | all | Human-readable display name |
| `desc` | `string` | `""` | Yes | all | Documentation description (supports RDLFormatCode tags) |
| `ispresent` | `boolean` | `true` | Yes | all | If false, instance is excluded from elaboration |
| `donttest` | `boolean` or `bit` | `false` | Yes | field, reg, regfile, addrmap | Exclude from structural testing. Bit mask for fields. |
| `dontcompare` | `boolean` or `bit` | `false` | Yes | field, reg, regfile, addrmap | Discard read data in comparisons. Bit mask for fields. |

---

## Field Properties

### Access Type

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `sw` | `accesstype` | `rw` | Yes | Software access: `rw`/`wr`, `r`, `w`, `na`, `rw1`, `w1` |
| `hw` | `accesstype` | `rw` | No | Hardware access: `rw`, `r`, `w`, `na` |

### Software Read Side-Effects

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `rclr` | `boolean` | `false` | Yes | Clear all bits on software read. Mutually exclusive with `rset`, `onread` |
| `rset` | `boolean` | `false` | Yes | Set all bits on software read. Mutually exclusive with `rclr`, `onread` |
| `onread` | `onreadtype` | — | Yes | Read side-effect: `rclr`, `rset`, `ruser`. Mutually exclusive with `rclr`, `rset`. `ruser` requires external field |

### Software Write Functions

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `woset` | `boolean` | `false` | Yes | Write-one-to-set (`field \| data`). Mutually exclusive with `woclr`, `onwrite` |
| `woclr` | `boolean` | `false` | Yes | Write-one-to-clear (`field & ~data`). Mutually exclusive with `woset`, `onwrite` |
| `onwrite` | `onwritetype` | — | Yes | Write function: `woset`, `woclr`, `wot`, `wzs`, `wzc`, `wzt`, `wclr`, `wset`, `wuser`. `wuser` requires external |

### Software Control

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `swwe` | `boolean` or `reference` | `false` | Yes | SW write-enable active-high. False = SW cannot write. Mutually exclusive with `swwel` |
| `swwel` | `boolean` or `reference` | `false` | Yes | SW write-enable active-low. False = SW can write. Mutually exclusive with `swwe` |
| `swmod` | `boolean` | `false` | Yes | Assert output signal when field modified by SW |
| `swacc` | `boolean` | `false` | Yes | Assert output signal when field accessed by SW |
| `singlepulse` | `boolean` | `false` | No | 1-bit field; auto-clears after one cycle when SW writes 1. Reset must be 0 |

### Hardware Signal and Access

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `activehigh` | `boolean` | `true` | No | Reset/enable signal polarity is active-high |
| `activelow` | `boolean` | `false` | No | Reset/enable signal polarity is active-low. Mutually exclusive with `activehigh` |
| `reset` | `bit` | X (unknown) | No | Static reset value (alternative to `= value` at instantiation) |
| `resetsignal` | `reference` | — | No | Signal instance that drives this field's reset |
| `we` | `boolean` or `reference` | `false` | No | Write-enable active-high for HW writes. False = not write-enabled (continuous drive). Mutually exclusive with `wel` |
| `wel` | `boolean` or `reference` | `false` | No | Write-enable active-low for HW writes. Mutually exclusive with `we` |
| `hwenable` | `reference` | — | No | Reference to HW enable signal (alternative to `we`) |
| `hwmask` | `reference` | — | No | Reference to HW mask signal; masked bits not updated by HW |
| `hwclr` | `boolean` | `false` | No | HW can clear the field (zero all bits) by asserting a dedicated input pin |
| `hwset` | `boolean` | `false` | No | HW can set the field (set all bits) by asserting a dedicated input pin |
| `anded` | `boolean` | `false` | No | Generate AND-reduction of field bits as output signal |
| `ored` | `boolean` | `false` | No | Generate OR-reduction of field bits as output signal |
| `xored` | `boolean` | `false` | No | Generate XOR-reduction of field bits as output signal |

### Counter Properties (field only)

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `counter` | `boolean` | `false` | No | Mark field as a counter |
| `incrvalue` | `longint unsigned` or `reference` | 1 | No | Increment amount or reference to controlling field/signal |
| `decrvalue` | `longint unsigned` or `reference` | 1 | No | Decrement amount or reference to controlling field/signal |
| `incrwidth` | `longint unsigned` | — | No | Bus width for external increment value input (alternative to `incrvalue`) |
| `decrwidth` | `longint unsigned` | — | No | Bus width for external decrement value input (alternative to `decrvalue`) |
| `incr` | `reference` | — | No | Signal/field that triggers an increment event |
| `decr` | `reference` | — | No | Signal/field that triggers a decrement event |
| `overflow` | — | — | — | Reference target: output asserts on counter overflow (use as RHS of assignment) |
| `underflow` | — | — | — | Reference target: output asserts on counter underflow (use as RHS of assignment) |
| `incrsaturate` | `boolean` or `longint unsigned` | `false` | No | Saturate at max value (true) or at specified value N |
| `decrsaturate` | `boolean` or `longint unsigned` | `false` | No | Saturate at min value/0 (true) or at specified value N |
| `incrthreshold` | `boolean` or `longint unsigned` | `false` | No | Generate threshold output when field value ≥ N (or ≥ max if true) |
| `decrthreshold` | `boolean` or `longint unsigned` | `false` | No | Generate threshold output when field value ≤ N (or ≤ 0 if true) |

### Interrupt Properties (field only)

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `intr` | `boolean` | `false` | No | Mark field as an interrupt status bit |
| `sticky` | `boolean` | `false` | No | Interrupt holds until software clears. Default behavior when `intr` is set without `nonsticky` |
| `nonsticky` | `boolean` | `false` | No | Interrupt auto-clears when source deasserts. Must be used with `intr` |
| `stickybit` | `boolean` | `false` | No | Each bit is individually sticky |
| `enable` | `reference` | — | No | Reference to field/signal that enables this interrupt source |
| `mask` | `reference` | — | No | Reference to field/signal that masks this interrupt source |
| `haltenable` | `reference` | — | No | Reference to halt-enable field/signal |
| `haltmask` | `reference` | — | No | Reference to halt-mask field/signal |

### Miscellaneous Field Properties

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `encode` | `reference` (enum type) | — | No | Assign an enum type to this field for value encoding |
| `fieldwidth` | `longint unsigned` | 1 | No | Default bit width for definitive field instantiated without explicit `[N]` |
| `next` | `reference` | — | Yes | Next value of this field (used to connect signals/fields: `f->next = other->overflow`) |

---

## Register Properties

| Property | Type | Default | Dyn | Components | Description |
|----------|------|---------|-----|------------|-------------|
| `regwidth` | `longint unsigned` | 32 | No | reg | Register width in bits. Must be power of 2 ≥ 8 |
| `accesswidth` | `longint unsigned` | = regwidth | No | reg | Software access width in bits |
| `errextbus` | `boolean` | `false` | No | reg | External register interface includes an error input |
| `alignment` | `longint unsigned` | — | No | reg | Address alignment override for this register |
| `sharedextbus` | `boolean` | `false` | No | reg | Share external bus interface with other external registers in scope |

---

## Register File Properties

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `alignment` | `longint unsigned` | — | No | Address alignment override for contents of this regfile |
| `sharedextbus` | `boolean` | `false` | No | Share external bus for all external regs in this regfile |
| `errextbus` | `boolean` | `false` | No | External registers in this regfile include an error input |
| `default_hw_access` | `accesstype` | — | No | Default `hw` property for all fields |
| `default_sw_access` | `accesstype` | — | No | Default `sw` property for all fields |

---

## Address Map Properties

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `addressing` | `addressingtype` | `regalign` | No | Address mode: `compact`, `regalign`, `fullalign` |
| `alignment` | `longint unsigned` | — | No | Address alignment override for all instances in map |
| `bigendian` | `boolean` | `false` | Yes | Use big-endian byte ordering. Mutually exclusive with `littleendian` |
| `littleendian` | `boolean` | `false` | Yes | Use little-endian byte ordering. Mutually exclusive with `bigendian` |
| `msb0` | `boolean` | `false` | No | Bit 0 = MSB for all registers in map. Mutually exclusive with `lsb0` |
| `lsb0` | `boolean` | `true` | No | Bit 0 = LSB for all registers in map (default). Mutually exclusive with `msb0` |
| `rsvdset` | `boolean` | `false` | No | Unspecified field bits read as 1 |
| `rsvdsetX` | `boolean` | `false` | No | Unspecified field bits read as unknown (X) |
| `sharedextbus` | `boolean` | `false` | No | All external components in map share one bus interface |
| `errextbus` | `boolean` | `false` | No | Map includes an error input from external components |
| `accesswidth` | `longint unsigned` | 32 | No | Default software access width (bits) for all registers |
| `default_hw_access` | `accesstype` | `rw` | No | Default `hw` value for all fields in map |
| `default_sw_access` | `accesstype` | `rw` | No | Default `sw` value for all fields in map |
| `bridge` | `boolean` | `false` | No | Map is a bridge supporting multiple-view access |

---

## Memory Properties

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `memwidth` | `longint unsigned` | 8 | No | Width of each memory word in bits |
| `mementries` | `longint unsigned` | 1 | No | Number of addressable entries in the memory |
| `sw` | `accesstype` | `rw` | No | Software access type for the memory |
| `hw` | `accesstype` | `rw` | No | Hardware access type for the memory |
| `errextbus` | `boolean` | `false` | No | Memory has an error input |

---

## Signal Properties

| Property | Type | Default | Dyn | Description |
|----------|------|---------|-----|-------------|
| `activehigh` | `boolean` | `true` | No | Signal asserts at logic 1 (default). Mutually exclusive with `activelow` |
| `activelow` | `boolean` | `false` | No | Signal asserts at logic 0. Mutually exclusive with `activehigh` |
| `sync` | `boolean` | `false` | No | Synchronous signal |
| `async` | `boolean` | `false` | No | Asynchronous signal |

---

## Verification / HDL Path Properties

Used to specify the HDL path for formal or simulation-based verification. These properties are typically assigned after instantiation via dynamic assignment.

| Property | Type | Dyn | Description |
|----------|------|-----|-------------|
| `hdl_path` | `string` | Yes | Full HDL path to the field's storage element |
| `hdl_path_gate` | `string` | Yes | HDL path for gate-level simulation |
| `hdl_path_slice` | `string[]` | Yes | Array of HDL path slices for multi-part fields |
| `hdl_path_gate_slice` | `string[]` | Yes | Array of gate-level HDL path slices |

```systemrdl
my_reg inst @ 0x00;
inst.data->hdl_path = "u_ctrl.data_reg.Q";
inst.data->hdl_path_slice = '{"u_ctrl.data_hi.Q[7:0]", "u_ctrl.data_lo.Q[7:0]"};
```

---

## `onreadtype` Values Summary

| Value | Applied with | Behavior |
|-------|-------------|----------|
| `rclr` | `rclr;` or `onread=rclr` | Field cleared to 0 on software read |
| `rset` | `rset;` or `onread=rset` | Field set to all-1s on software read |
| `ruser` | `onread=ruser` | Custom behavior; field must be external |

## `onwritetype` Values Summary

| Value | Applied with | Behavior |
|-------|-------------|----------|
| `woset` | `woset;` or `onwrite=woset` | `field \| write_data` |
| `woclr` | `woclr;` or `onwrite=woclr` | `field & ~write_data` |
| `wot` | `onwrite=wot` | `field ^ write_data` (toggle on 1) |
| `wzs` | `onwrite=wzs` | `field \| ~write_data` (set on 0) |
| `wzc` | `onwrite=wzc` | `field & write_data` (clear on 0) |
| `wzt` | `onwrite=wzt` | `field ~^ write_data` (toggle on 0) |
| `wclr` | `onwrite=wclr` | Field cleared to 0 on any write |
| `wset` | `onwrite=wset` | Field set to all-1s on any write |
| `wuser` | `onwrite=wuser` | Custom behavior; field must be external |
