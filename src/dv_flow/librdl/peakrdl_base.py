#****************************************************************************
#* peakrdl_base.py
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
import re
import sys
from typing import List, Tuple
from dv_flow.mgr.task_data import TaskMarker, SeverityE


def collect_rdl_inputs(input) -> Tuple[List[str], List[str]]:
    """
    Gather SystemRDL source files and include directories from upstream filesets.

    Returns (files, incdirs) where both are lists of absolute paths.
    Files come from 'systemRDLSource' filesets; incdirs come from
    'systemRDLIncDir' filesets and from the incdirs field of source filesets.
    """
    files = []
    incdirs = []

    for item in input.inputs:
        if item.type == "std.FileSet":
            if item.filetype == "systemRDLSource":
                for f in item.files:
                    files.append(os.path.join(item.basedir, f))
                if hasattr(item, "incdirs"):
                    incdirs.extend(item.incdirs)
            elif item.filetype == "systemRDLIncDir":
                for d in item.files:
                    incdirs.append(os.path.join(item.basedir, d))

    return files, incdirs


def build_common_args(
    files: List[str],
    incdirs: List[str],
    defines: List[str],
    top: str,
    extra_incdirs: List[str],
    extra_defines: List[str],
    args: List[str],
) -> List[str]:
    """
    Build the common part of a peakrdl command line.

    Produces:  [<files...>] [-I <dir>...] [-D <def>...] [-t <top>] [<args...>]
    """
    cmd = list(files)

    all_incdirs = list(incdirs) + list(extra_incdirs)
    for d in all_incdirs:
        cmd.extend(["-I", d])

    all_defines = list(extra_defines)
    for d in all_defines:
        cmd.extend(["-D", d])

    if top:
        cmd.extend(["-t", top])

    cmd.extend(args)
    return cmd


class PeakRdlLogParser:
    """
    Parse peakrdl stderr/stdout output and emit TaskMarkers for errors and warnings.
    """

    _re_error   = re.compile(r'^\s*(error|SystemRDL error)', re.IGNORECASE)
    _re_warning = re.compile(r'^\s*(warning)', re.IGNORECASE)
    _re_loc     = re.compile(r'(\S+):(\d+):(\d+):', re.IGNORECASE)

    def __init__(self, notify=None):
        self.notify = notify

    def line(self, text: str):
        """Process one output line and call notify(TaskMarker) when appropriate."""
        if self._re_error.search(text):
            severity = SeverityE.Error
        elif self._re_warning.search(text):
            severity = SeverityE.Warning
        else:
            return

        if self.notify:
            m = self._re_loc.search(text)
            if m:
                self.notify(TaskMarker(
                    severity=severity,
                    msg=text.strip(),
                    file=m.group(1),
                    line=int(m.group(2)),
                ))
            else:
                self.notify(TaskMarker(severity=severity, msg=text.strip()))


def peakrdl_exe() -> str:
    """Return the path to the peakrdl executable (same Python env as this package)."""
    bin_dir = os.path.dirname(sys.executable)
    exe = os.path.join(bin_dir, "peakrdl")
    if os.path.isfile(exe):
        return exe
    return "peakrdl"
