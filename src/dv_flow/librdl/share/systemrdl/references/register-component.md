# SystemRDL Register Component

A register (`reg`) is the fundamental addressable unit in SystemRDL — a set of fields that are atomically accessed at a single address.

## Definition and Instantiation

```systemrdl
// Definitive definition
reg my_reg {
    // field and other component definitions/instantiations
    field {} data[32] = 0;
};
my_reg reg_a @ 0x00;
my_reg reg_b @ 0x04;

// Anonymous definition (inline)
reg { field {} data[32] = 0; } scratch @ 0x00;
```

### Constraints on Register Contents

- At least one field must be instantiated.
- Only `field` instances are permitted inside a register (not reg, regfile, addrmap, mem).
- `signal`, `enum`, and `constraint` can be **defined** (not instantiated as children) inside a register.
- Fields must not overlap in bit position unless one is read-only and the other is write-only.
- No field may occupy a bit position beyond the register's MSB.

## Register Width

The `regwidth` property sets the total register width in bits:

```systemrdl
reg wide_reg {
    regwidth = 64;        // 64-bit register; default is 32
    field {} lo[32] = 0;
    field {} hi[32] = 0;
};
```

Rules:
- Default `regwidth` is **32**.
- Must be a power of 2 and ≥ 8 (e.g., 8, 16, 32, 64, 128…).

## Field Bit Positioning

Fields are placed within the register's bit width either explicitly (with indices) or implicitly (by the compiler).

### Explicit placement

```systemrdl
reg my_reg {
    field {} status[3:0];    // bits 3 down to 0 (4-bit field at LSB)
    field {} mode[7:4];      // bits 7 down to 4 (4-bit field)
    field {} data[31:8];     // bits 31 down to 8 (24-bit field)
};
```

Range notation `[msb:lsb]` — `msb` must be ≥ `lsb` in `lsb0` mode.

```systemrdl
field {} f[width];           // width-bit field, position auto-assigned
field {} f[msb:lsb];         // explicit bit range
```

### Implicit (auto-assigned) placement

In `lsb0` mode (default): fields are placed sequentially starting from bit 0, each immediately following the previous field.

```systemrdl
reg example {
    field {} a[4];     // bits 3:0
    field {} b[8];     // bits 11:4
    field {} c[4];     // bits 15:12
    // bits 31:16 are reserved/unspecified
};
```

In `msb0` mode: fields are placed sequentially starting from bit `regwidth-1` downward. `msb0`/`lsb0` is a property set on an `addrmap`, affecting all registers within it.

### Overlapping fields (read-write split)

```systemrdl
reg split_reg {
    field { sw = r; hw = w; } read_view[32];       // read view
    field { sw = w; hw = r; } write_view[32];      // write view — overlaps only if sw types differ
};
```

This is valid only when one field is read-only and the other is write-only at the same bit positions.

## Register Properties

| Property | Type | Default | Dynamic | Description |
|----------|------|---------|---------|-------------|
| `regwidth` | `longint unsigned` | 32 | No | Register width in bits |
| `accesswidth` | `longint unsigned` | = `regwidth` | No | Width of one software access in bits |
| `errextbus` | `boolean` | false | No | External register includes an error input |
| `alignment` | `longint unsigned` | — | No | Override address alignment for this register |
| `sharedextbus` | `boolean` | false | No | All external registers in scope share a common bus interface |

### `accesswidth` Usage

When a register is wider than one bus access (e.g., 64-bit register on a 32-bit bus), `accesswidth` specifies the individual access width:

```systemrdl
reg double_wide {
    regwidth    = 64;
    accesswidth = 32;    // accessed as two 32-bit reads/writes
    field {} lo[32] = 0;
    field {} hi[32] = 0;
};
```

## Internal vs. External Registers

### Internal (default)

The SystemRDL compiler generates all register logic (flip-flops, mux, etc.).

```systemrdl
reg ctrl { field {} enable[1] = 0; };
ctrl ctrl_inst;          // internal (default)
```

### External

The designer provides the RTL implementation. The compiler generates only the interface (port declarations). The `external` keyword appears before the instance (not in the definition):

```systemrdl
reg fifo_status { field { sw = r; hw = w; } count[8] = 0; };
external fifo_status fifo_st;   // external — tool generates port, not logic
```

Or in a definition-and-instantiation context:

```systemrdl
reg { field { sw = r; hw = w; } data[32] = 0; } external ext_reg;
```

## Alias Registers

An alias register provides an alternate software view of an existing (primary) register. Both the alias and primary share the same physical storage, but can have different software access properties (e.g., read-only alias for a read-write register).

```systemrdl
reg base_reg {
    field { sw = rw; hw = rw; } data[32] = 0;
};

reg alias_type {
    field { sw = r; hw = rw; } data[32];   // read-only view of same storage
};

base_reg  primary_inst @ 0x00;
alias alias_type primary_inst : alias_inst @ 0x10;
//    ^^^^^^^^^^^ alias type   ^^^^^^^^^^^^^  primary instance
```

Syntax: `alias alias_type primary_instance_ref : alias_instance_name;`

Rules:
- Alias must be the same type (internal/external) as its primary.
- The alias register type should have the same fields as the primary (same widths and positions).
- Multiple aliases to the same primary are allowed.

## Register Arrays

```systemrdl
my_reg channels[8];            // 8 registers, auto-addressed
my_reg buf[4] @ 0x100 += 8;   // 4 registers at 0x100, 0x108, 0x110, 0x118
```

Each array element occupies one regwidth/8 bytes (unless `accesswidth` differs or explicit stride is given).

## Interrupt Registers

A register containing one or more fields with the `intr` property automatically generates an interrupt output signal — the OR-reduction of all active, enabled interrupt fields. This output is accessible from the containing addrmap to wire to a parent interrupt controller.

```systemrdl
reg irq_reg {
    field { sw = rw; hw = w; woclr; intr; sticky; } rx_full[1]  = 0;
    field { sw = rw; hw = w; woclr; intr; sticky; } tx_empty[1] = 0;
    field { sw = rw; hw = w; woclr; intr; sticky; } error[1]    = 0;
};
```

The register-level interrupt output can then be connected to an interrupt field in a parent addrmap's interrupt aggregation register.

## Understanding Field Ordering

When fields are placed implicitly:
- In `lsb0` mode: first-listed field starts at bit 0, fields are packed upward with no gaps.
- If reserved bits are needed, insert a reserved field:

```systemrdl
reg padded_reg {
    field {}                     active[4];   // bits 3:0
    field { sw = na; hw = na; }  rsvd[4];     // bits 7:4 — reserved
    field {}                     config[8];   // bits 15:8
};
```
