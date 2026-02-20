# SystemRDL Component Hierarchy and General Rules

## Component Types

| Keyword | Component | Role |
|---------|-----------|------|
| `field` | Field | Bit-field within a register; lowest-level structural component |
| `reg` | Register | Set of fields atomically accessible at one address |
| `regfile` | Register File | Hierarchical grouping of registers; no RTL module boundary |
| `addrmap` | Address Map | Hierarchical grouping with address space and optional RTL module boundary |
| `signal` | Signal | Hardware signal used for resets and write-enables |
| `enum` | Enumeration | Named enumeration type for encoding field values |
| `mem` | Memory | Memory region within an address map |
| `constraint` | Constraint | Verification constraint applied to field values |

## Nesting Rules (What Can Contain What)

| Component | May instantiate |
|-----------|----------------|
| `addrmap` | `reg`, `regfile`, `mem`, `addrmap`, `signal` |
| `regfile` | `reg`, `regfile`, `signal` |
| `reg` | `field` instances; `signal`, `enum`, `constraint` definitions only |
| `field` | `signal`, `enum`, `constraint` definitions only (no sub-instances) |
| `mem` | Register overlay definitions (optional) |

## Defining Components

### Definitive Definition (named type, reusable)

```systemrdl
component_keyword type_name [#(parameters)] {
    // body
} [instances];
```

The type is named and can be instantiated multiple times. The body may contain:
- Default property assignments
- Property assignments
- Component instantiations
- Nested component definitions
- Constraint and struct definitions

### Anonymous Definition (inline, used once)

```systemrdl
component_keyword { body } instance_element [, instance_element]*;
```

The first instance name also becomes the implicit type name for the anonymous component.

### Examples

```systemrdl
// Definitive field definition (reusable type "status_f")
field status_f {
    sw = r;
    hw = w;
};

// Definitive register using the above type
reg status_reg {
    status_f busy[1] = 0;
    status_f done[1] = 0;
    status_f error[1] = 0;
};

// Anonymous field inside a register
reg ctrl_reg {
    field { sw = rw; hw = r; } enable[1] = 0;
    field { sw = rw; hw = r; } mode[4]   = 0;
};

// Anonymous register inside an address map
addrmap my_map {
    reg { field {} data[32] = 0; } scratch @ 0x00;
};
```

## Component Parameters

All component types except `enum` and `constraint` support Verilog-style parameters.

### Defining Parameters

```systemrdl
reg #(
    longint unsigned WIDTH = 32,    // parameter with default
    longint unsigned RESET = 0
) generic_reg {
    field {} data[WIDTH] = RESET;
};
```

Parameter types: any primary data type (`longint unsigned`, `bit`, `boolean`, `string`) or a specific bit width.

### Instantiating with Parameters

```systemrdl
generic_reg #(.WIDTH(16), .RESET(16'hFFFF)) narrow_inst;
generic_reg #(.WIDTH(8))  byte_inst;    // RESET uses default 0
generic_reg               wide_inst;    // both use defaults
```

### Generated Type Names

When a parameterized type is instantiated with different parameter values, the compiler auto-generates a unique type name incorporating the parameter values. These generated names are visible in tool output but not normally written by the user.

### Inserting into Type Namespace

A parameterized instantiation can be given an explicit type alias:

```systemrdl
// Instantiating a parameterized type creates a new named type implicitly
```

## Instantiating Components

### Full Instantiation Syntax

```systemrdl
type_name [#(param_overrides)] instance_name
    [{array_size}]* [addr_alloc] [= reset_value]
    [, more_instance_names ...] ;
```

Where:
- `{array_size}` — creates an array of instances (one or more dimensions); last index increments fastest
- `addr_alloc` — `@N`, `+= N`, or `%= N` (see `addressing.md`)
- `= reset_value` — reset value for field instances only

### Single instance
```systemrdl
my_reg_type my_inst @ 0x100;
```

### Array of instances
```systemrdl
my_reg_type channels[8] @ 0x000;         // 8 instances, auto-stride
my_reg_type buf[4] @ 0x080 += 8;         // 4 instances, stride 8 bytes
```

### Multidimensional array
```systemrdl
my_reg_type matrix[4][8];   // 4 rows × 8 cols; last index ([8]) increments fastest
```

### Multiple instances in one statement
```systemrdl
my_reg_type a, b, c;   // three instances, auto-addressed
```

## Property Assignment

### Inside a Component Body

```systemrdl
field my_field {
    sw    = rw;        // named value assignment
    hw    = r;
    rclr;              // shorthand for boolean property: rclr = true
    reset = 8'h00;     // numeric assignment
    name  = "Data";    // string assignment
};
```

### Default Property Assignment

`default` sets the value for all subsequent instances in the same scope:

```systemrdl
addrmap my_map {
    default sw = rw;     // applies to all fields in this addrmap
    default hw = r;

    reg { field {} a[8]; field {} b[8]; } r1;  // a and b both get sw=rw, hw=r
};
```

Defaults propagate inward (to nested components) but cannot override explicit assignments.

### Dynamic Assignment (Post-Instantiation)

After a component is instantiated, properties can be overridden using the `->` operator:

```systemrdl
reg my_reg {
    field {} f[8];
    field {} g[8];
};
my_reg inst;
inst.f->reset = 8'hAB;     // override reset on instance inst.f
inst.g->sw    = r;          // make inst.g read-only
```

Dynamic assignment works on instances in the enclosing scope. The path uses `.` for hierarchy and `->` for property access.

### Property Assignment Precedence (highest to lowest)

1. Dynamic assignment in enclosing scope (e.g., `inst.f->prop = val`)
2. Explicit assignment inside the instance's definition body
3. `default` assignment in the same component body where instance is defined
4. `default` in an outer (enclosing) component body
5. Built-in default value for the property

## Scoping and Namespaces

- Each component body introduces a new scope.
- Types defined inside a body are local to that body.
- Types at root scope are globally visible.
- `this` keyword refers to the current component instance.
- Accessing a nested instance property: `parent.child->property`
- Accessing a sibling or same-scope instance from inside a component body requires the instance name.

### Type Visibility Example

```systemrdl
// Root scope: globally visible
enum chip_mode_e { OFF = 0; ON = 1; };

addrmap top {
    // "chip_mode_e" is visible here
    reg ctrl {
        field { encode = chip_mode_e; } mode[1] = 0;
    };
    ctrl ctrl_inst;
};
```

## The `ispresent` Property

Setting `ispresent = false` on an instance causes the compiler to exclude it from the elaborated design. Useful for parameterized designs where some components are optional:

```systemrdl
reg optional_reg { field {} data[32] = 0; };
optional_reg opt_inst;
opt_inst->ispresent = false;   // excluded from final design
```

## Universal Properties (Available on All Components)

| Property | Type | Dynamic | Description |
|----------|------|---------|-------------|
| `name` | `string` | Yes | Human-readable name; defaults to instance name if unset |
| `desc` | `string` | Yes | Documentation description |
| `ispresent` | `boolean` | Yes | If false, component is excluded from elaboration |
| `donttest` | `boolean` or `bit` | Yes | Exclude from structural testing |
| `dontcompare` | `boolean` or `bit` | Yes | Exclude read-data from comparison in testing |

`donttest` and `dontcompare` are mutually exclusive (their bit masks must not overlap).
