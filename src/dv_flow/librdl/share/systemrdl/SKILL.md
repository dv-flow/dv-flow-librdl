---
name: systemrdl
description: Write, review, and edit SystemRDL 2.0 register description files (.rdl). Use when the task involves creating or modifying SystemRDL input files that describe hardware registers, register files, and address maps for chip design flows.
metadata:
  author: dv-flow-librdl
  version: "1.0"
---

# SystemRDL 2.0

SystemRDL is a language for describing hardware registers in chip designs. A SystemRDL description is used by tools to generate RTL logic, UVM register models, documentation, and test programs — all from a single source of truth.

## Component Hierarchy

SystemRDL descriptions are built from nested components:

```
addrmap        ← top-level address map (one per .rdl file typically)
  regfile      ← optional grouping of registers (no RTL module boundary)
    reg        ← a register: set of fields at one address
      field    ← one or more bits with defined HW/SW behavior
```

Supporting components used within the hierarchy:
- `signal` — hardware signal (used for reset lines, write-enables)
- `enum` — enumeration type for field value encoding
- `mem` — memory region within an address map
- `constraint` — verification constraint

## Quick-Start Example

A complete, minimal example covering the most common patterns:

```systemrdl
// Simple peripheral with a control register and status register

// Define a reusable interrupt-status field type
field intr_field_t {
    hw   = w;        // hardware writes (sets) this field
    sw   = rw;       // software reads and clears
    woclr;           // write-one-to-clear
    intr;            // marks as interrupt source
};

addrmap my_peripheral {
    default hw       = r;    // most fields: hardware reads, software writes
    default sw       = rw;
    addressing       = regalign;  // default: each reg aligned to its size
    bigendian        = false;

    // --- Control Register at address 0x00 ---
    reg ctrl_r {
        name = "Control Register";
        desc = "Controls peripheral operation.";

        // bits[0]: enable bit
        field {} enable[1] = 0;    // 1 bit, reset=0, inherits default sw=rw/hw=r

        // bits[4:1]: mode select (4-bit enumeration)
        enum mode_e {
            IDLE    = 4'h0 { desc = "Peripheral is idle."; };
            RUN     = 4'h1 { desc = "Peripheral is running."; };
            PAUSE   = 4'h2 { desc = "Peripheral is paused."; };
        };
        field { encode = mode_e; } mode[4] = 4'h0;

        // bits[15:8]: threshold (8-bit, hardware also reads)
        field { hw = rw; } threshold[8] = 8'hFF;
    };

    // --- Status Register at address 0x04 ---
    reg status_r {
        name = "Status Register";
        regwidth = 32;

        // bits[7:0]: 8-bit read-only hardware-written counter value
        field { sw = r; hw = w; } count[8] = 0;

        // bits[8]: overflow interrupt (write-1-to-clear)
        intr_field_t overflow_intr[1] = 0;

        // bits[9]: done flag (read-only, hardware sets, software reads)
        field { sw = r; hw = w; } done[1] = 0;
    };

    // Instantiate registers
    ctrl_r   ctrl   @ 0x00;
    status_r status @ 0x04;
};
```

## Key Syntax Patterns

### Defining and instantiating a component

```systemrdl
// Definitive (named type, reusable):
reg my_reg { field {} data[32] = 0; };
my_reg reg_a;          // instance "reg_a"
my_reg reg_b @ 0x08;   // instance "reg_b" at address 0x08

// Anonymous (type defined inline, used once):
reg { field {} data[32] = 0; } reg_c;
```

### Property assignment

```systemrdl
field my_field {
    sw    = rw;           // named value
    hw    = r;
    rclr;                 // shorthand for rclr = true
    reset = 8'h00;        // explicit reset value
    name  = "My Field";
    desc  = "This field does X.";
};
```

### Default properties (apply to all subsequent instances in scope)

```systemrdl
addrmap foo {
    default sw = rw;   // all fields in this map default to sw=rw
    default hw = r;    // all fields default to hw=r
    // ...
};
```

### Dynamic property assignment (after instantiation)

```systemrdl
reg my_reg {
    field {} f[8];
};
my_reg inst;
inst.f->reset = 8'hAB;   // set reset value on specific instance
```

### Address assignment

```systemrdl
my_reg a @ 0x000;      // absolute address
my_reg b @ 0x004;
my_reg arr[16] @ 0x100 += 4;   // 16-element array, stride 4 bytes
my_reg c %= 0x10;              // align next instance to 0x10
```

### Arrays

```systemrdl
reg chan_r { field {} data[32]; };
chan_r channels[8] @ 0x100;   // 8 registers at 0x100..0x11C (stride 4)
```

### Parameters

```systemrdl
reg #(longint unsigned WIDTH = 32) generic_r {
    field {} data[WIDTH] = 0;
};
generic_r #(.WIDTH(16)) narrow_r;   // 16-bit instantiation
```

## Common Field Patterns

```systemrdl
// Read-write storage (most common)
field { sw = rw; hw = rw; } rw_field[8] = 0;

// Read-only status (hardware writes, software reads)
field { sw = r;  hw = w;  } ro_field[8] = 0;

// Write-only (software writes, hardware reads)
field { sw = w;  hw = r;  } wo_field[8] = 0;

// Clear-on-read
field { sw = r;  hw = w;  rclr; } clr_on_rd[8] = 0;

// Write-one-to-clear (interrupt status)
field { sw = rw; hw = w;  woclr; } w1c_field[1] = 0;

// Write-one-to-set
field { sw = rw; hw = r;  woset; } w1s_field[8] = 0;

// Single-pulse (write 1, auto-clears next cycle)
field { sw = rw; hw = r;  singlepulse; } pulse[1] = 0;

// Counter (incremented by hardware)
field { counter; hw = r; sw = rw; } cnt[16] = 0;
```

## Reference Files

Load the appropriate reference file when you need details:

| Reference | When to use |
|-----------|-------------|
| [overview.md](references/overview.md) | Lexical rules, identifiers, number formats, keywords, string formatting |
| [component-hierarchy.md](references/component-hierarchy.md) | Defining/instantiating components, parameters, scoping, property assignment mechanics, nesting rules |
| [field-properties.md](references/field-properties.md) | Any field property: sw/hw access, onread/onwrite, reset, counter, interrupt, HW signal properties |
| [register-component.md](references/register-component.md) | Register-level rules, field bit positioning, alias registers, internal/external, register properties |
| [addressing.md](references/addressing.md) | Address computation, addressing modes (compact/regalign/fullalign), regfile and addrmap properties, mem |
| [data-types.md](references/data-types.md) | Enumerations, structs, arrays, type casting, expressions and operators |
| [user-defined-properties.md](references/user-defined-properties.md) | Defining and using custom (user-defined) properties |
| [advanced-topics.md](references/advanced-topics.md) | Reset signals, hierarchical interrupts, byte/bit ordering, preprocessor directives (`define/`ifdef/`include, Perl) |
| [property-reference.md](references/property-reference.md) | Quick lookup of any built-in property: type, default, applicable components, dynamic flag |
