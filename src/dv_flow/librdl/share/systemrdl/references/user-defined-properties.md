# SystemRDL User-Defined Properties

User-defined properties (UDPs) let you attach custom metadata to any component type. They are commonly used to carry information for downstream tools (documentation generators, UVM model generators, IP management tools) that is not captured by built-in SystemRDL properties.

## Defining a User-Defined Property

```systemrdl
property property_name {
    component = component_type [| component_type]*;   // required
    type      = value_type;                           // required
    [default  = default_value;]                       // optional
    [constraint = componentwidth;]                    // optional, only for bit type
};
```

UDP definitions must be placed at **root scope** (not inside a component body).

### `component` Attribute

Specifies which component types can use this property. Use `|` to allow multiple types:

| Value | Component |
|-------|-----------|
| `field` | Field |
| `reg` | Register |
| `regfile` | Register file |
| `addrmap` | Address map |
| `mem` | Memory |
| `signal` | Signal |
| `constraint` | Constraint |
| `all` | All component types |

```systemrdl
property owner_info { component = reg | regfile | addrmap; type = string; };
property hdl_label  { component = field;                   type = string; };
property is_secure  { component = all;                     type = boolean; default = false; };
```

### `type` Attribute

| Type | Description | Example value |
|------|-------------|---------------|
| `number` | N-bit unsigned (backward compat, same as `bit`) | `8'hFF` |
| `bit` | N-bit unsigned | `4'b1010` |
| `longint unsigned` | 64-bit unsigned integer | `1024` |
| `boolean` | True/false | `true` |
| `string` | Character string | `"module_a"` |
| `ref` | Reference to a component instance | `mymap.myreg` |
| enumerator | A user-defined enum type | `my_enum::VAL_A` |
| struct literal | A user-defined struct type | `'my_struct{ ... }` |
| `type[]` | Array of any of the above | `'{ "a", "b" }` |
| `addrmap`, `regfile`, `reg`, `mem`, `field` | Specialized reference to that component type | `submap` |

### `default` Attribute

Sets a default value that applies to all instances of the specified component types where the property is not explicitly assigned:

```systemrdl
property voltage_domain { component = reg | regfile; type = string; default = "VDD_CORE"; };
```

> Properties of type `ref` or any component type (`reg`, `field`, etc.) cannot have a default value that references a parameterized type instance.

### `constraint` Attribute

Only applicable when `type = bit`. Forces the bit width to match the field/register width:

```systemrdl
property bit_mask { component = field; type = bit; constraint = componentwidth; };
```

---

## Binding (Assigning) a User-Defined Property

UDPs are **not automatically bound** to instances — they must be explicitly assigned.

### Inside a Component Body

```systemrdl
property block_id { component = reg | regfile; type = longint unsigned; };

reg my_reg {
    block_id = 42;
    field {} data[32] = 0;
};
```

### Via Dynamic Assignment

```systemrdl
my_reg inst;
inst->block_id = 99;
```

### Cascaded Assignment with `default`

Inside a body, `default` assigns a UDP to all child instances:

```systemrdl
addrmap secure_map {
    default is_secure = true;    // all registers in this map get is_secure=true

    reg { field {} key[32]; } key_reg;     // is_secure = true (from default)
    reg { field {} data[32]; } data_reg;   // is_secure = true (from default)
};
```

---

## Reading a User-Defined Property

Access the value using the `->` operator (same as built-in properties):

```systemrdl
some_instance->property_name
```

A UDP value can appear on the right-hand side of another property assignment or in an expression:

```systemrdl
// Use a UDP value as input to another property assignment
other_inst->some_property = my_inst->block_id;
```

---

## Complete Example

```systemrdl
// --- Root scope: UDP definitions ---

property hw_module  { component = reg | regfile | addrmap; type = string; };
property sw_label   { component = field | reg;             type = string; };
property reset_by   { component = reg | field;             type = string; default = "sys_rst_n"; };
property test_mask  { component = field; type = bit; constraint = componentwidth; };

// --- Enumeration for field encoding ---
enum access_key_e { LOCKED = 0; UNLOCKED = 1; };

// --- Component definitions ---
regfile uart_rf {
    hw_module = "uart_core";    // bind hw_module UDP to this regfile

    reg ctrl_r {
        sw_label = "UART_CTRL";

        field { sw = rw; hw = r; encode = access_key_e; } lock[1] = 0;
        field { sw = rw; hw = r; } baud_div[16] = 16'd434;  // ~115200 at 50MHz
        field { sw = rw; hw = r; } enable[1]    = 0;

        // Override reset_by for this register
        reset_by = "uart_rst_n";
    };

    reg stat_r {
        sw_label = "UART_STAT";

        field { sw = r;  hw = w; } rx_full[1]  = 0;
        field { sw = r;  hw = w; } tx_empty[1] = 0;
        field { sw = rw; hw = w; woclr; intr; } rx_err[1] = 0;

        // test_mask: mark the reserved bits as don't-test
        field { sw = na; hw = na; } rsvd[29];
    };

    ctrl_r ctrl   @ 0x0;
    stat_r status @ 0x4;
};

addrmap my_soc {
    uart_rf uart0 @ 0x4000_0000;
    uart_rf uart1 @ 0x4000_1000;
};
```

---

## Notes

- UDP names do not conflict with built-in property names (they live in a separate namespace).
- Use UDPs liberally to attach tool-specific metadata without impacting standard SystemRDL semantics.
- Common use cases: RTL module names, software register names/labels, ownership information, security attributes, custom test attributes.
