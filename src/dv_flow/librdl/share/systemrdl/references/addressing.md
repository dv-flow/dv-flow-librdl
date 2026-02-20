# SystemRDL Addressing, Register Files, and Address Maps

## Address Allocation Operators

When instantiating `reg`, `regfile`, `mem`, or `addrmap` components, three operators control address placement:

| Operator | Syntax | Description |
|----------|--------|-------------|
| Absolute address | `inst @ 0x100` | Place instance at exactly this byte address |
| Stride | `inst[N] += S` | For arrays: spacing between consecutive elements (in bytes) |
| Alignment | `inst %= A` | Align instance's start address to the next multiple of A |

```systemrdl
// Explicit addresses
reg_a   ctrl    @ 0x000;
reg_a   status  @ 0x004;

// Array with explicit stride
reg_b   channels[8] @ 0x100 += 8;   // at 0x100, 0x108, 0x110, ... 0x138

// Alignment — next instance starts at next multiple of 0x40
reg_c   big_reg %= 0x40;
```

Addresses not explicitly assigned are computed automatically based on the addressing mode of the containing addrmap.

---

## Addressing Modes

Set with the `addressing` property on an `addrmap`. Applies to all components directly or indirectly contained within.

### `regalign` (default)

Each component's start address is a multiple of its size in bytes. Array elements are aligned to individual element size (no gaps between elements).

```systemrdl
addrmap example {
    addressing = regalign;   // or omit — this is the default

    reg { field {} a; } r32;         // 32-bit reg, 4 bytes → address 0x0
    reg { regwidth=64; field {} a; } r64;  // 64-bit reg, 8 bytes → address 0x8
    reg { field {} a; } arr[4];      // array of 4×32-bit regs → 0x10, 0x14, 0x18, 0x1C
};
```

### `compact`

Components are packed as tightly as possible while still being aligned to `accesswidth` bytes.

```systemrdl
addrmap example {
    default accesswidth = 32;
    addressing = compact;

    reg { field {} a; }             r32;     // 4 bytes → address 0x0
    reg { regwidth=64; field {} a; } r64;    // 8 bytes → address 0x4 (no gap needed)
    reg { field {} a; }             arr[4];  // → 0xC, 0x10, 0x14, 0x18
};
```

### `fullalign`

Like `regalign` for single instances, but array **first element** is aligned to the total array size (rounded up to nearest power of two). Subsequent elements are packed with no gaps.

```systemrdl
addrmap example {
    addressing = fullalign;

    reg { field {} a; } r32;         // → 0x0
    reg { regwidth=64; field {} a; } r64;  // → 0x8
    reg { field {} a; } arr[20];     // 20 × 4 bytes = 80 bytes → next pow2 = 128
                                     // → element 0 at 0x80, element 1 at 0x84, ...
};
```

---

## Address Map (`addrmap`) Component

An `addrmap` defines an address space. The top-level `addrmap` is the root of the design hierarchy. Nested `addrmap` instances create sub-maps.

```systemrdl
addrmap my_chip {
    default hw = r;
    default sw = rw;

    // Direct register
    reg { field {} data[32] = 0; } scratch @ 0x000;

    // Nested sub-map
    addrmap uart_0 {
        reg { field {} ctrl[32]; } ctrl  @ 0x0;
        reg { field {} stat[32]; } stat  @ 0x4;
    };
    uart_0 uart0 @ 0x1000;
    uart_0 uart1 @ 0x2000;
};
```

### Address Map Properties

| Property | Type | Default | Dynamic | Description |
|----------|------|---------|---------|-------------|
| `addressing` | `addressingtype` | `regalign` | No | Address allocation mode: `compact`, `regalign`, `fullalign` |
| `alignment` | `longint unsigned` | — | No | Override alignment for all instances in map |
| `bigendian` | `boolean` | false | Yes | Use big-endian byte ordering |
| `littleendian` | `boolean` | false | Yes | Use little-endian byte ordering |
| `msb0` | `boolean` | false | No | Bit 0 is MSB (reversed bit indexing for all fields in map) |
| `lsb0` | `boolean` | true | No | Bit 0 is LSB (default) |
| `rsvdset` | `boolean` | false | No | Unspecified field bits read as 1 |
| `rsvdsetX` | `boolean` | false | No | Unspecified field bits read as unknown (X) |
| `sharedextbus` | `boolean` | false | No | All external components in this map share one bus interface |
| `errextbus` | `boolean` | false | No | Map has an error input from external components |
| `accesswidth` | `longint unsigned` | 32 | No | Default software access width (bits) for all registers |
| `default_hw_access` | `accesstype` | `rw` | No | Default `hw` property for all fields |
| `default_sw_access` | `accesstype` | `rw` | No | Default `sw` property for all fields |

`bigendian` and `littleendian` are mutually exclusive.
`msb0` and `lsb0` are mutually exclusive.

### Bridges / Multiple-View Maps

An addrmap can be defined with the `bridge` property to support multiple overlapping bus views of the same address space. Each bridge addrmap describes one bus master's perspective:

```systemrdl
addrmap bridge_map {
    bridge;
    // registers visible from multiple interfaces at different offsets
};
```

---

## Register File (`regfile`) Component

A `regfile` groups registers into a reusable hierarchy **without** creating an RTL module boundary (unlike `addrmap`). Use `regfile` to organize large register banks into logical groups.

```systemrdl
regfile channel_rf {
    reg { field {} ctrl[32]; } ctrl   @ 0x0;
    reg { field {} stat[32]; } status @ 0x4;
    reg { field {} data[32]; } data   @ 0x8;
};

addrmap multi_channel {
    channel_rf ch[8] @ 0x000;   // 8 channels at 0x000..0x05C (each 0x0C bytes)
};
```

### Register File Properties

| Property | Type | Default | Dynamic | Description |
|----------|------|---------|---------|-------------|
| `alignment` | `longint unsigned` | — | No | Override address alignment for content |
| `sharedextbus` | `boolean` | false | No | Share external bus for all external regs in this file |
| `errextbus` | `boolean` | false | No | External registers have an error input |
| `default_hw_access` | `accesstype` | — | No | Default `hw` for all fields |
| `default_sw_access` | `accesstype` | — | No | Default `sw` for all fields |
| `name` | `string` | — | Yes | Descriptive name |
| `desc` | `string` | — | Yes | Documentation description |

### Nesting Register Files

```systemrdl
regfile bank_rf {
    channel_rf channels[4];
    reg { field {} bank_ctrl[32]; } ctrl @ 0x100;
};

addrmap top {
    bank_rf bank_a @ 0x0000;
    bank_rf bank_b @ 0x1000;
};
```

---

## Memory (`mem`) Component

A `mem` represents a memory region (e.g., a FIFO buffer, SRAM) within an address map. It does not contain individual field definitions by default, but can include register overlays.

```systemrdl
mem fifo_buf {
    memwidth  = 32;       // word width in bits
    mementries = 256;     // number of entries → total size = 256 × 4 = 1024 bytes
    sw = rw;
    hw = rw;
};

addrmap with_mem {
    fifo_buf fifo @ 0x1000;
};
```

### Memory Properties

| Property | Type | Default | Dynamic | Description |
|----------|------|---------|---------|-------------|
| `memwidth` | `longint unsigned` | 8 | No | Width of each memory word in bits |
| `mementries` | `longint unsigned` | 1 | No | Number of addressable entries |
| `sw` | `accesstype` | `rw` | No | Software access type |
| `hw` | `accesstype` | `rw` | No | Hardware access type |
| `errextbus` | `boolean` | false | No | Memory has an error input |

---

## Address Computation Examples

```systemrdl
addrmap peripheral {
    // Default: regalign. Registers 32-bit (4 bytes each).

    reg { field {} f[32]; } r0;          // → 0x00 (first, starts at 0)
    reg { field {} f[32]; } r1;          // → 0x04 (auto: +4)
    reg { field {} f[32]; } r2 @ 0x10;  // → 0x10 (explicit)
    reg { field {} f[32]; } r3;          // → 0x14 (auto: +4 after 0x10)

    // 64-bit register needs 8-byte alignment in regalign mode
    reg { regwidth=64; field {} f[64]; } wide @ 0x20;  // → 0x20
    // next auto-address would be 0x28

    // Array: 4 × 32-bit regs
    reg { field {} f[32]; } arr[4] @ 0x40;
    // arr[0] @ 0x40, arr[1] @ 0x44, arr[2] @ 0x48, arr[3] @ 0x4C

    // Array with custom stride (sparse mapping)
    reg { field {} f[32]; } sparse[4] @ 0x100 += 0x10;
    // sparse[0] @ 0x100, sparse[1] @ 0x110, sparse[2] @ 0x120, sparse[3] @ 0x130
};
```
