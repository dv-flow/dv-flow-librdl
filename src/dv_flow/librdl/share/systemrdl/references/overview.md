# SystemRDL Lexical Conventions and Overview

## File Extension and Encoding

SystemRDL source files use the `.rdl` extension. Files are encoded in UTF-8. UCS code points beyond ASCII are only permitted inside comments and string literals. SystemRDL is **case-sensitive**.

## Comments

```systemrdl
// Single-line comment — extends to end of line

/* Block comment —
   may span multiple lines.
   Single-line comments (//) inside a block comment are ignored. */
```

Block comments cannot be nested.

## Identifiers

Identifiers name user-defined types and instances. Two forms:

- **Simple**: starts with a letter or underscore `_`, followed by letters, digits `0-9`, and underscores.
- **Escaped**: begins with `\` followed by a simple identifier. Escaped form allows using keywords as identifiers (e.g., `\field`).

```systemrdl
my_identifier     // valid simple identifier
_y0123            // valid — starts with underscore
My_IdEnTiFiEr     // valid — case-sensitive
\reg              // escaped identifier: "reg" used as a name
```

## Keywords

The following identifiers are reserved as keywords and cannot be used as unescaped identifiers:

```
abstract      accesstype    addressingtype  addrmap       alias
all           bit           boolean         bothedge      compact
component     componentwidth constraint     default       encode
enum          errextbus     external        false         field
fullalign     hw            inside          internal      level
longint       mem           na              negedge       nonsticky
number        onreadtype    onwritetype     posedge       property
r             rclr          ref             reg           regalign
regfile       reset         rset            rw            rw1
signal        string        struct          sw            sync
this          true          type            unsigned      w
w1            wclr          woclr           woset         wr
wot           wset          wuser           wzc           wzs
wzt
```

**Reserved words** (reserved for future use, also cannot be used as identifiers):
```
alternate  byte  int  precedencetype  real  shortint  shortreal  signed  with  within
```

## Number Formats

All numbers in SystemRDL are unsigned. Underscores `_` may appear anywhere in the numeric portion (except the first digit or the width prefix) as visual separators.

| Format | Syntax | Example |
|--------|--------|---------|
| Simple decimal | digits | `40`, `255` |
| Simple hexadecimal | `0x` + hex digits | `0x45`, `0xFF` |
| Verilog decimal | `width'dvalue` | `4'd1`, `8'd255` |
| Verilog hexadecimal | `width'hvalue` | `8'hFF`, `32'hDEAD_BEEF` |
| Verilog binary | `width'bvalue` | `3'b101`, `8'b0000_1111` |

> **Important**: Ambiguous-width Verilog numbers like `'hFF` (no width prefix) are **not** supported. Always specify the width.

```systemrdl
40            // simple decimal
0x45          // simple hexadecimal
4'd1          // 4-bit decimal value 1
3'b101        // 3-bit binary
32'hDE_AD_BE_EF  // 32-bit hex with visual separators
7'h7f         // 7-bit hex
```

It is an error if a Verilog-style number's value does not fit within the specified bit-width.

## Strings

A string is a sequence of characters enclosed in double quotes. Use `\"` to embed a double quote.

```systemrdl
"This is a string"
"Spans
 multiple lines"
"Contains a \"quoted\" word"
```

For documentation generation, consecutive whitespace within a string is collapsed to a single space.

### RDLFormatCode Tags (for `name` and `desc` strings)

Strings in `name` and `desc` properties may use phpBB-style formatting tags:

| Tag | Effect |
|-----|--------|
| `[b]text[/b]` | Bold |
| `[i]text[/i]` | Italic |
| `[u]text[/u]` | Underline |
| `[color=red]text[/color]` | Colored text |
| `[url]http://...[/url]` | Hyperlink |
| `[url=http://...]label[/url]` | Labeled hyperlink |
| `[size=N]text[/size]` | Font size |

```systemrdl
desc = "This field controls [b]power state[/b]. See [url=http://example.com]datasheet[/url].";
```

## White Space

Space, horizontal tab, line feed, and carriage return are all white space. White space is insignificant except:
- It separates tokens that would otherwise merge
- A newline terminates a single-line comment (`//`)
- Inside strings, consecutive white space is collapsed to a single space (for doc generation)

## Top-Level File Structure

A `.rdl` file contains a sequence of declarations at the root scope:

```systemrdl
// Optional: type definitions (enum, struct, property)
// One or more component definitions
// Exactly one root addrmap definition (or instantiation) drives generation

addrmap my_chip {
    // register definitions and instances
};
```

Multiple `.rdl` files may be compiled together; the root `addrmap` is identified by the compiler as the top of the hierarchy.
