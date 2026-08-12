#****************************************************************************
#* peakrdl_export.py
#*
#* Copyright 2023-2025 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may
#* not use this file except in compliance with the License.
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software
#* distributed under the License is distributed on an "AS IS" BASIS,
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#* See the License for the specific language governing permissions and
#* limitations under the License.
#*
#****************************************************************************
import os
import glob
from dv_flow.mgr import TaskDataResult, FileSet
from dv_flow.mgr.task_data import TaskMarker, SeverityE
from .peakrdl_base import collect_rdl_inputs, build_common_args, PeakRdlLogParser, peakrdl_exe


# Per-format defaults: (output filetype, output file extension, output is a
# directory). A format that is not listed still works -- it just needs
# `filetype` and `filename` set explicitly.
_FORMAT_DEFAULTS = {
    "fw-hdl":    ("systemVerilogSource", ".sv",   False),
    "regblock":  ("systemVerilogSource", "",      True),
    "uvm":       ("systemVerilogSource", ".sv",   False),
    "pss":       ("pssSource",           ".pss",  False),
    "html":      ("rdlHtmlDoc",          "",      True),
    "c-header":  ("rdlCHeader",          ".h",    False),
    "ip-xact":   ("rdlIpXact",           ".xml",  False),
    "systemrdl": ("systemRDLSource",     ".rdl",  False),
}


def _render_options(options) -> list:
    """
    Render the `options` map into exporter flags.

    A key is a long-form flag without the leading dashes; `_` and `-` are
    interchangeable, so `type_style` and `type-style` both reach
    `--type-style`. A boolean true emits the bare flag, false omits it, and any
    other value emits `--flag <value>`. A list emits the flag once per element.
    """
    args = []
    for key, value in options.items():
        flag = "--" + str(key).replace("_", "-").lstrip("-")
        if isinstance(value, bool):
            if value:
                args.append(flag)
        elif isinstance(value, (list, tuple)):
            for v in value:
                args.extend([flag, str(v)])
        elif value is None or value == "":
            continue
        else:
            args.extend([flag, str(value)])
    return args


async def Export(runner, input) -> TaskDataResult:
    """
    Run a PeakRDL exporter over the incoming SystemRDL sources.

    One task for every exporter: `format` selects the peakrdl subcommand, and
    `options` carries whatever flags that exporter defines. Third-party exporter
    plug-ins (fw-hdl, pss, ...) work the same way as the built-in ones, with no
    change here.
    """
    files, incdirs = collect_rdl_inputs(input)

    p = input.params

    if p.format == "":
        return TaskDataResult(
            status=1,
            markers=[TaskMarker(
                severity=SeverityE.Error,
                msg="rdl.Export: no exporter 'format' specified"
            )]
        )

    if not files:
        return TaskDataResult(
            status=1,
            markers=[TaskMarker(
                severity=SeverityE.Error,
                msg="rdl.Export(%s): no systemRDLSource files received" % p.format
            )]
        )

    def_filetype, def_ext, def_isdir = _FORMAT_DEFAULTS.get(
        p.format, ("systemVerilogSource", ".sv", False))

    filetype = p.filetype if p.filetype != "" else def_filetype
    is_dir = def_isdir

    out_dir = input.rundir
    if is_dir:
        # The exporter writes a tree; hand it a subdirectory so the log and the
        # exec data do not land inside the published fileset.
        out_path = os.path.join(out_dir, p.filename if p.filename != "" else "out")
        pub_dir = out_path
        pattern = "**/*"
    else:
        filename = p.filename
        if filename == "":
            stem = p.top if p.top != "" else "regs"
            filename = stem + def_ext
        out_path = os.path.join(out_dir, filename)
        pub_dir = out_dir
        pattern = "*" + (os.path.splitext(filename)[1] or def_ext)

    cmd = [peakrdl_exe(), p.format]
    cmd += build_common_args(
        files, incdirs,
        defines=[], top=p.top,
        extra_incdirs=list(p.incdirs),
        extra_defines=list(p.defines),
        args=[],
    )
    cmd += ["-o", out_path]
    cmd += _render_options(dict(p.options))
    # `args` goes last so a hand-written flag can override anything above.
    cmd += list(p.args)

    markers = []
    status = await runner.exec(
        cmd,
        logfile="peakrdl_%s.log" % p.format.replace("-", "_"),
        logfilter=PeakRdlLogParser(notify=lambda m: markers.append(m)).line,
    )

    output = []
    if status == 0:
        generated = sorted(
            os.path.relpath(f, pub_dir)
            for f in glob.glob(os.path.join(pub_dir, pattern), recursive=True)
            if os.path.isfile(f))
        output.append(FileSet(
            src=input.name,
            filetype=filetype,
            basedir=pub_dir,
            files=generated,
            incdirs=[pub_dir] if p.incdir else [],
        ))

    return TaskDataResult(status=status, changed=True, output=output, markers=markers)
