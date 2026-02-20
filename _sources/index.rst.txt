.. DV Flow LibRDL documentation master file

###############
DV Flow LibRDL
###############

LibRDL is a DV-Flow library that provides tasks for performing common
SystemRDL operations via `PeakRDL <https://peakrdl.readthedocs.io>`_.
It wraps the PeakRDL tool suite so that register model generation can
be integrated into a DV-Flow pipeline alongside compilation, simulation,
and other tasks.

.. contents::
    :depth: 2


Task: Html
==========
Generate HTML documentation for a SystemRDL register model.

Runs ``peakrdl html`` to produce interactive HTML documentation pages
for the register model.  The output directory can be served directly
as a static website.

Consumes upstream ``systemRDLSource`` filesets.  Produces a ``rdlHtmlDoc``
fileset whose ``basedir`` points to the generated HTML directory.

Example
-------

.. code-block:: yaml

    package:
      name: my_chip

      tasks:
        - name: rdl_src
          uses: std.FileSet
          with:
            type: systemRDLSource
            include: "*.rdl"

        - name: html_docs
          uses: rdl.Html
          needs: [rdl_src]
          with:
            top: my_regs
            title: "My Chip Register Map"

Consumes
--------

* systemRDLSource
* systemRDLIncDir

Produces
--------

* rdlHtmlDoc

Parameters
----------

* **top** - [Optional] Top-level addrmap to elaborate (``peakrdl -t``)
* **incdirs** - [Optional] Additional include directories
* **defines** - [Optional] Preprocessor macro definitions (``MACRO`` or ``MACRO=VALUE``)
* **args** - [Optional] Extra arguments passed verbatim to peakrdl
* **title** - [Optional] Override the HTML page title
* **show_signals** - [Optional] Include signal components in the generated documentation (default: false)
* **reverse_fields** - [Optional] Display register fields in LSB-to-MSB order (default: false)


Task: Regblock
==============
Generate a synthesisable SystemVerilog CSR block from a SystemRDL register model.

Runs ``peakrdl regblock`` to produce a SystemVerilog module and package
that implement a control/status register (CSR) block with a configurable
CPU interface.

Consumes upstream ``systemRDLSource`` filesets.  Produces a
``systemVerilogSource`` fileset so the output can be fed directly into
HDL simulation or synthesis tasks.

Example
-------

.. code-block:: yaml

    package:
      name: my_chip

      tasks:
        - name: rdl_src
          uses: std.FileSet
          with:
            type: systemRDLSource
            include: "*.rdl"

        - name: regblock
          uses: rdl.Regblock
          needs: [rdl_src]
          with:
            top: my_regs
            cpuif: axi4-lite

        - name: sim
          uses: hdlsim.vlt.SimImage
          needs: [regblock, tb_src]
          with:
            top: [tb_top]

Consumes
--------

* systemRDLSource
* systemRDLIncDir

Produces
--------

* systemVerilogSource

Parameters
----------

* **top** - [Optional] Top-level addrmap to elaborate
* **incdirs** - [Optional] Additional include directories
* **defines** - [Optional] Preprocessor macro definitions
* **args** - [Optional] Extra arguments passed verbatim to peakrdl
* **cpuif** - [Optional] CPU interface protocol (default: ``apb3``).
  One of: ``passthrough``, ``apb3``, ``apb3-flat``, ``apb4``, ``apb4-flat``,
  ``axi4-lite``, ``axi4-lite-flat``, ``avalon-mm``, ``avalon-mm-flat``,
  ``obi``, ``obi-flat``
* **module_name** - [Optional] Override the generated SystemVerilog module name
* **package_name** - [Optional] Override the generated SystemVerilog package name


Task: Uvm
=========
Generate a UVM register model (``uvm_reg_block``) from a SystemRDL register model.

Runs ``peakrdl uvm`` to produce a SystemVerilog UVM register model that
can be used in UVM-based testbenches.

Consumes upstream ``systemRDLSource`` filesets.  Produces a
``systemVerilogSource`` fileset.

Example
-------

.. code-block:: yaml

    - name: uvm_model
      uses: rdl.Uvm
      needs: [rdl_src]
      with:
        top: my_regs
        use_factory: true

Consumes
--------

* systemRDLSource
* systemRDLIncDir

Produces
--------

* systemVerilogSource

Parameters
----------

* **top** - [Optional] Top-level addrmap to elaborate
* **incdirs** - [Optional] Additional include directories
* **defines** - [Optional] Preprocessor macro definitions
* **args** - [Optional] Extra arguments passed verbatim to peakrdl
* **use_factory** - [Optional] Instantiate register model classes via the UVM factory (default: false)


Task: CHeader
=============
Generate a C header with address and field bit-mask definitions from a SystemRDL register model.

Runs ``peakrdl c-header`` to produce a C header file containing base
address constants and bit-field mask/shift definitions for every
register in the model.

Consumes upstream ``systemRDLSource`` filesets.  Produces a ``rdlCHeader``
fileset.

Example
-------

.. code-block:: yaml

    - name: cheader
      uses: rdl.CHeader
      needs: [rdl_src]
      with:
        top: my_regs

Consumes
--------

* systemRDLSource
* systemRDLIncDir

Produces
--------

* rdlCHeader

Parameters
----------

* **top** - [Optional] Top-level addrmap to elaborate
* **incdirs** - [Optional] Additional include directories
* **defines** - [Optional] Preprocessor macro definitions
* **args** - [Optional] Extra arguments passed verbatim to peakrdl
* **std** - [Optional] C standard to target (default: ``gnu99``).
  One of: ``gnu23``, ``gnu17``, ``gnu11``, ``gnu99``, ``gnu90``, ``gnu89``, ``latest``
* **type_style** - [Optional] Type name style — ``lexical`` reuses equivalent definitions; ``hier`` uses hierarchy (default: ``lexical``)


Task: IpXact
============
Export a SystemRDL register model to IP-XACT XML.

Runs ``peakrdl ip-xact`` to export the register model as an IP-XACT
component XML file, suitable for import into IP-XACT-aware EDA tools.

Consumes upstream ``systemRDLSource`` filesets.  Produces a ``rdlIpXact``
fileset.

Example
-------

.. code-block:: yaml

    - name: ipxact_export
      uses: rdl.IpXact
      needs: [rdl_src]
      with:
        top: my_regs
        vendor: mycompany.com
        library: chip
        version: "1.0"
        standard: "2014"

Consumes
--------

* systemRDLSource
* systemRDLIncDir

Produces
--------

* rdlIpXact

Parameters
----------

* **top** - [Optional] Top-level addrmap to elaborate
* **incdirs** - [Optional] Additional include directories
* **defines** - [Optional] Preprocessor macro definitions
* **args** - [Optional] Extra arguments passed verbatim to peakrdl
* **vendor** - [Optional] IP-XACT component vendor field
* **library** - [Optional] IP-XACT component library field
* **version** - [Optional] IP-XACT component version field
* **standard** - [Optional] IP-XACT standard revision — ``2009`` or ``2014`` (default: ``2014``)


Task: SystemRdl
===============
Export a SystemRDL register model back to normalised SystemRDL.

Runs ``peakrdl systemrdl`` to re-export the elaborated register model
as a normalised SystemRDL source file.  Useful for stripping includes,
expanding parameters, or converting from IP-XACT to SystemRDL.

Consumes upstream ``systemRDLSource`` filesets.  Produces a
``systemRDLSource`` fileset containing the exported ``.rdl`` file.

Example
-------

.. code-block:: yaml

    - name: rdl_export
      uses: rdl.SystemRdl
      needs: [rdl_src]
      with:
        top: my_regs

Consumes
--------

* systemRDLSource
* systemRDLIncDir

Produces
--------

* systemRDLSource

Parameters
----------

* **top** - [Optional] Top-level addrmap to elaborate
* **incdirs** - [Optional] Additional include directories
* **defines** - [Optional] Preprocessor macro definitions
* **args** - [Optional] Extra arguments passed verbatim to peakrdl


.. note::
    All trademarks are the property of their respective owners.
