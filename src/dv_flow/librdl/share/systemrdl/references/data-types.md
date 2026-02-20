# SystemRDL Data Types, Enumerations, Structs, and Expressions

## Primary Scalar Types

| Type | Description | Example values |
|------|-------------|----------------|
| `bit [N]` | N-bit unsigned value | `4'hF`, `8'b1010_0101` |
| `longint unsigned` | 64-bit unsigned integer | `0`, `256`, `0xFFFF_FFFF` |
| `boolean` | Two-state true/false | `true`, `false` |
| `string` | Character string | `"hello world"` |
| `number` | Backward-compat alias for `bit` (avoid in new code) | `8'hFF` |

## Built-in Enumeration Types

These types are built into the language and appear as property values (not defined by the user).

**Access type** (`accesstype`): `rw`, `wr`, `r`, `w`, `na`, `rw1`, `w1`

**On-read type** (`onreadtype`): `rclr`, `rset`, `ruser`

**On-write type** (`onwritetype`): `woset`, `woclr`, `wot`, `wzs`, `wzc`, `wzt`, `wclr`, `wset`, `wuser`

**Addressing type** (`addressingtype`): `compact`, `regalign`, `fullalign`

---

## User-Defined Enumerations

Enumerations define a set of named values for encoding field values.

### Defining an Enumeration

```systemrdl
enum state_e {
    IDLE    = 2'd0;                         // explicit value
    ACTIVE  = 2'd1 { desc = "Running."; };  // with optional desc
    PAUSE   = 2'd2;
    ERROR   = 2'd3 { name = "Error State"; desc = "Fault detected."; };
};
```

Each enumerator entry can have optional `name` and `desc` properties in `{ }`.

### Auto-Incrementing Values

Entries without an explicit value are assigned the previous entry's value + 1, starting at 0:

```systemrdl
enum priority_e {
    LOW;      // = 0
    MEDIUM;   // = 1
    HIGH;     // = 2
    CRITICAL; // = 3
};
```

### Using an Enumeration in a Field

Assign the enum type to a field with the `encode` property:

```systemrdl
field { sw = rw; hw = r; encode = state_e; } state[2] = 0;
```

The field's bit width must be sufficient to represent all enum values.

### Type Consistency

All enumerator values must be unique within an enumeration. The type is resolved at elaboration time — if two different enum types are used in expressions together, they must be compatible (same value space).

---

## Structs

Structs are aggregate types used for user-defined property values.

### Defining a Struct

```systemrdl
struct range_s {
    longint unsigned low;
    longint unsigned high;
};
```

### Deriving a Struct (Inheritance)

```systemrdl
struct extended_range_s : range_s {
    string label;    // adds a label field to the base struct
};
```

The derived struct inherits all members of the parent and adds new ones.

### Struct Literals

Create a struct value with the literal syntax `'type_name { member: value, ... }`:

```systemrdl
property addr_range { type = range_s; component = addrmap; };

addrmap my_map {
    addr_range = 'range_s { low: 0, high: 0xFFF };
};
```

---

## Arrays

Arrays are used as the type for user-defined properties (not for component instantiation, which uses `[N]` notation).

### Array Types

Append `[]` to any scalar or struct type name:

```systemrdl
property tag_list { type = string[]; component = reg; };
```

### Array Literals

```systemrdl
'{ value0, value1, value2 }         // general array literal
'{ 8'h10, 8'h20, 8'h30 }           // array of bit values
'{ "alpha", "beta", "gamma" }       // array of strings
```

### Element Access

```systemrdl
reg_inst->tag_list[0]   // access element 0 of an array property
```

---

## Identifier References (`ref` type)

A `ref` value is a reference to a component instance, used in user-defined properties and in certain built-in properties like `enable`, `mask`, `we`, `hwenable`.

```systemrdl
// Referencing an instance by path
chip.block.my_reg.my_field

// "this" refers to the current component
this->sw

// Accessing a property value via ->
inst_name->property_name
```

---

## Expressions and Operators

Expressions appear in property values, parameters, reset values, and array sizes.

### Arithmetic Operators

| Operator | Meaning |
|----------|---------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulo |
| `**` | Exponentiation (power) |

### Bitwise Operators

| Operator | Meaning |
|----------|---------|
| `&` | Bitwise AND |
| `\|` | Bitwise OR |
| `^` | Bitwise XOR |
| `~` | Bitwise NOT |
| `~^` or `^~` | XNOR |
| `>>` | Right shift |
| `<<` | Left shift |

### Logical Operators

| Operator | Meaning |
|----------|---------|
| `&&` | Logical AND |
| `\|\|` | Logical OR |
| `!` | Logical NOT |

### Comparison Operators

| Operator | Meaning |
|----------|---------|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |

### Other Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `? :` | Ternary conditional | `en ? 8'hFF : 8'h00` |
| `{ , }` | Concatenation | `{hi_bits, lo_bits}` |
| `{N{ }}` | Replication | `{4{2'b10}}` → `8'b10101010` |
| `inside` | Set membership | `x inside {0, 1, [4:7]}` |

### Casting

Type casts convert between compatible types:

```systemrdl
boolean'(1)          // cast integer 1 to boolean true
8'(some_value)       // truncate or zero-extend to 8 bits
longint unsigned'(x) // cast to 64-bit unsigned
```

### Expression Type Rules

- Expressions involving two operands use the wider type for the result.
- Assignment truncates or zero-extends to fit the left-hand side type.
- The left-hand side of a property assignment does not influence expression type evaluation (right-hand side type stands on its own).

---

## Type Compatibility

- Values of `number` and `bit` types are compatible and interchangeable.
- `boolean` can be assigned from integer expressions where 0 = false, non-zero = true.
- Enum types are compatible only if they share the same definition (same set of enumerators).
- Struct types are compatible only if they have the same (or derived) definition.
- Array types are compatible if element types are compatible.

---

## Practical Examples

```systemrdl
// Parameterized field with expression for reset
reg #(longint unsigned W = 8, longint unsigned RST = 0) gen_r {
    field {} data[W] = RST;
};

// Using expression in address
addrmap ex {
    reg { field {} d[32]; } r[16] @ 0x100 += 4;  // 16 regs at 0x100..0x13C
};

// Enum with auto-increment
enum irq_src_e {
    NONE  = 0;
    DMA;        // 1
    UART;       // 2
    SPI;        // 3
    GPIO;       // 4
};

field { encode = irq_src_e; } irq_src[3] = 0;  // 3 bits wide, can hold 0..7
```
