---
name: rdl-peakrdl
description: >
  Generate register-model outputs from SystemRDL source files using PeakRDL.
  Use when working with .rdl files and needing HTML documentation (rdl.Html),
  a synthesisable SystemVerilog CSR block (rdl.Regblock), a UVM register model
  (rdl.Uvm), a C header with address/mask definitions (rdl.CHeader), an IP-XACT
  XML component (rdl.IpXact), or a normalised SystemRDL export (rdl.SystemRdl).
license: Apache-2.0
metadata:
  author: dv-flow-librdl
  version: "1.0"
compatibility: Requires dv-flow-mgr and PeakRDL (peakrdl CLI) in the Python environment.
---

# PeakRDL Integration (`rdl`)

The `rdl` package wraps [PeakRDL](https://peakrdl.readthedocs.io) to transform
SystemRDL register-description files into a variety of output formats as part of
a dv-flow build graph.  Each task consumes one or more upstream `systemRDLSource`
filesets, invokes the appropriate `peakrdl` sub-command, and emits a typed output
fileset that can be wired to downstream tasks.

> **When creating or modifying SystemRDL content**, consult `systemrdl/SKILL.md`
> for language guidance before wiring any `rdl.*` task.

---

## Task reference

| Task            | Consumes                              | Produces               | Purpose                                      |
|-----------------|---------------------------------------|------------------------|----------------------------------------------|
| `rdl.Html`      | `systemRDLSource`, `systemRDLIncDir`  | `rdlHtmlDoc`           | Interactive HTML register-map documentation  |
| `rdl.Regblock`  | `systemRDLSource`, `systemRDLIncDir`  | `systemVerilogSource`  | Synthesisable SV CSR block + package         |
| `rdl.Uvm`       | `systemRDLSource`, `systemRDLIncDir`  | `systemVerilogSource`  | UVM `uvm_reg_block` register model           |
| `rdl.CHeader`   | `systemRDLSource`, `systemRDLIncDir`  | `rdlCHeader`           | C header with base-address and field masks   |
| `rdl.IpXact`    | `systemRDLSource`, `systemRDLIncDir`  | `rdlIpXact`            | IP-XACT component XML                        |
| `rdl.SystemRdl` | `systemRDLSource`, `systemRDLIncDir`  | `systemRDLSource`      | Normalised / flattened SystemRDL re-export   |

---

## Parameters

Parameters shared by **all** tasks:

| Parameter | Type | Default | Description                                                                                              |
|-----------|------|---------|----------------------------------------------------------------------------------------------------------|
| `top`     | str  | `""`    | Top-level addrmap name to elaborate (`peakrdl -t`). Required when the file contains more than one addrmap or when the addrmap name differs from the file stem. |
| `incdirs` | list | `[]`    | Additional include directories for `` `include `` directives.                                            |
| `defines` | list | `[]`    | Preprocessor macro definitions (`MACRO` or `MACRO=VALUE`).                                               |
| `args`    | list | `[]`    | Extra arguments passed verbatim to `peakrdl`.                                                            |

### `rdl.Html` — additional parameters

| Parameter        | Type | Default | Description                                             |
|------------------|------|---------|---------------------------------------------------------|
| `title`          | str  | `""`    | Override the HTML page title.                           |
| `show_signals`   | bool | `false` | Include signal components in the documentation.         |
| `reverse_fields` | bool | `false` | Display register fields in LSB-to-MSB order.            |

### `rdl.Regblock` — additional parameters

| Parameter      | Type | Default  | Description                                                                                                                          |
|----------------|------|----------|--------------------------------------------------------------------------------------------------------------------------------------|
| `cpuif`        | str  | `"apb3"` | CPU interface protocol. Options: `passthrough`, `apb3`, `apb3-flat`, `apb4`, `apb4-flat`, `axi4-lite`, `axi4-lite-flat`, `avalon-mm`, `avalon-mm-flat`, `obi`, `obi-flat`. |
| `module_name`  | str  | `""`     | Override the generated SV module name.                                                                                               |
| `package_name` | str  | `""`     | Override the generated SV package name.                                                                                              |

### `rdl.Uvm` — additional parameters

| Parameter     | Type | Default | Description                                             |
|---------------|------|---------|---------------------------------------------------------|
| `use_factory` | bool | `false` | Instantiate register classes via the UVM factory.       |

### `rdl.CHeader` — additional parameters

| Parameter    | Type | Default     | Description                                                                       |
|--------------|------|-------------|-----------------------------------------------------------------------------------|
| `std`        | str  | `"gnu99"`   | C standard to target: `gnu23`, `gnu17`, `gnu11`, `gnu99`, `gnu90`, `gnu89`, `latest`. |
| `type_style` | str  | `"lexical"` | Type-name style: `lexical` reuses equivalent definitions; `hier` uses hierarchy.  |

### `rdl.IpXact` — additional parameters

| Parameter  | Type | Default  | Description                                             |
|------------|------|----------|---------------------------------------------------------|
| `vendor`   | str  | `""`     | IP-XACT component vendor field.                         |
| `library`  | str  | `""`     | IP-XACT component library field.                        |
| `version`  | str  | `""`     | IP-XACT component version field.                        |
| `standard` | str  | `"2014"` | IP-XACT revision: `"2009"` or `"2014"`.                 |

*(`rdl.SystemRdl` has no additional parameters beyond the shared set.)*

---

## File types

| Filetype              | Direction | Description                                          |
|-----------------------|-----------|------------------------------------------------------|
| `systemRDLSource`     | input     | SystemRDL `.rdl` source files.                       |
| `systemRDLIncDir`     | input     | Directories containing `` `include ``-able `.rdl` files. |
| `rdlHtmlDoc`          | output    | Directory tree of generated HTML documentation.      |
| `systemVerilogSource` | output    | Generated `.sv` files (CSR block or UVM model).      |
| `rdlCHeader`          | output    | Generated `.h` C header file.                        |
| `rdlIpXact`           | output    | Generated IP-XACT `.xml` file.                       |

---

## How to wire tasks

1. **Provide SystemRDL sources.**  Declare a `std.FileSet` task of type `systemRDLSource`
   pointing at your `.rdl` files.

   > When creating or modifying SystemRDL content, consult `systemrdl/SKILL.md`.

2. **Add the desired `rdl.*` task** and list the source task in its `needs:` field.

3. **Set `top:`** whenever the top-level addrmap name cannot be inferred automatically
   (multiple addrmaps in one file, or the addrmap name differs from the file name).

4. **Select `cpuif:`** for `rdl.Regblock` — the default is `apb3`; change to e.g.
   `axi4-lite` if your design requires a different bus protocol.

5. **Connect outputs** to downstream tasks via their `needs:` field.
   `systemVerilogSource` outputs from `rdl.Regblock` / `rdl.Uvm` can feed directly
   into HDL simulation or synthesis tasks.

---

## Examples

### HTML documentation

```yaml
- name: rdl_src
  uses: std.FileSet
  with:
    type: systemRDLSource
    include: "regs/**/*.rdl"

- name: html_docs
  uses: rdl.Html
  needs: [rdl_src]
  with:
    top: my_chip_regs
    title: "My Chip Register Map"
```

### SystemVerilog CSR block (AXI4-Lite)

```yaml
- name: regblock
  uses: rdl.Regblock
  needs: [rdl_src]
  with:
    top: my_chip_regs
    cpuif: axi4-lite

- name: sim
  uses: hdlsim.vlt.SimImage
  needs: [regblock, tb_src]
  with:
    top: [tb_top]
```

### UVM register model

```yaml
- name: uvm_model
  uses: rdl.Uvm
  needs: [rdl_src]
  with:
    top: my_chip_regs
    use_factory: true
```

### C header

```yaml
- name: cheader
  uses: rdl.CHeader
  needs: [rdl_src]
  with:
    top: my_chip_regs
```

### IP-XACT export

```yaml
- name: ipxact_export
  uses: rdl.IpXact
  needs: [rdl_src]
  with:
    top: my_chip_regs
    vendor: mycompany.com
    library: chip
    version: "1.0"
    standard: "2014"
```

### Normalised SystemRDL re-export

```yaml
- name: rdl_export
  uses: rdl.SystemRdl
  needs: [rdl_src]
  with:
    top: my_chip_regs
```

---

## Common pitfalls

- **Missing `top:`** — if the `.rdl` file defines more than one addrmap, or the addrmap
  name differs from the file stem, PeakRDL will fail with an elaboration error.  Always
  set `top:` explicitly in those cases.

- **Wrong `cpuif` for `rdl.Regblock`** — the default (`apb3`) may not match your SoC
  bus fabric.  Check your integration requirements and set `cpuif:` accordingly.

- **No input files received** — each task emits an error marker and exits non-zero if
  no `systemRDLSource` fileset reaches it.  Verify `needs:` lists the correct source task.

- **Include paths** — if your `.rdl` files use `` `include `` directives, pass the
  containing directories via `incdirs:` or supply a separate `systemRDLIncDir` fileset.
