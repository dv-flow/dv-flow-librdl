#****************************************************************************
#* peakrdl_systemrdl.py
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


async def SystemRdl(runner, input) -> TaskDataResult:
    """
    Export a SystemRDL register model back to normalised SystemRDL via peakrdl systemrdl.

    Produces a systemRDLSource FileSet containing the exported .rdl file.
    Useful for stripping includes, expanding parameters, or converting from
    IP-XACT to a single self-contained SystemRDL file.
    """
    files, incdirs = collect_rdl_inputs(input)

    if not files:
        return TaskDataResult(
            status=1,
            markers=[TaskMarker(
                severity=SeverityE.Error,
                msg="rdl.SystemRdl: no systemRDLSource files received"
            )]
        )

    out_dir = input.rundir
    out_file = os.path.join(out_dir, "regs.rdl")

    p = input.params
    cmd = [peakrdl_exe(), "systemrdl"]
    cmd += build_common_args(
        files, incdirs,
        defines=[], top=p.top,
        extra_incdirs=list(p.incdirs),
        extra_defines=list(p.defines),
        args=list(p.args),
    )
    cmd += ["-o", out_file]

    markers = []
    status = await runner.exec(
        cmd,
        logfile="systemrdl.log",
        logfilter=PeakRdlLogParser(notify=lambda m: markers.append(m)).line,
    )

    output = []
    if status == 0:
        rdl_files = [os.path.basename(f)
                     for f in glob.glob(os.path.join(out_dir, "*.rdl"))]
        output.append(FileSet(
            src=input.name,
            filetype="systemRDLSource",
            basedir=out_dir,
            files=rdl_files,
        ))

    return TaskDataResult(status=status, changed=True, output=output, markers=markers)
