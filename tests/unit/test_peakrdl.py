"""
Smoke tests for the rdl.* PeakRDL tasks.

Each test:
1. Creates a std.FileSet node pointing at tests/unit/data/smoke.rdl
2. Creates the task node under test
3. Runs via TaskSetRunner and asserts status == 0 with expected output
"""
import asyncio
import os
import pytest

from dv_flow.mgr import TaskListenerLog, TaskSetRunner, PackageLoader
from dv_flow.mgr.task_graph_builder import TaskGraphBuilder


def _make_runner_and_builder(tmpdir):
    runner = TaskSetRunner(os.path.join(str(tmpdir), "rundir"))
    loader = PackageLoader()
    rgy = loader.load_rgy(["std", "rdl"])
    builder = TaskGraphBuilder(rgy, os.path.join(str(tmpdir), "rundir"))
    return runner, builder


def _rdl_src_node(builder, data_dir):
    return builder.mkTaskNode(
        "std.FileSet",
        name="rdl_src",
        type="systemRDLSource",
        base=data_dir,
        include="smoke.rdl",
    )


# ---------------------------------------------------------------------------
# rdl.Html
# ---------------------------------------------------------------------------
def test_html(tmpdir, data_dir):
    runner, builder = _make_runner_and_builder(tmpdir)

    rdl_src = _rdl_src_node(builder, data_dir)
    task = builder.mkTaskNode(
        "rdl.Html",
        name="html",
        needs=[rdl_src],
        top="my_regs",
    )

    runner.add_listener(TaskListenerLog().event)
    out = asyncio.run(runner.run(task))

    assert runner.status == 0

    html_fs = next(
        (fs for fs in out.output
         if fs.type == "std.FileSet" and fs.filetype == "rdlHtmlDoc"),
        None,
    )
    assert html_fs is not None, "expected rdlHtmlDoc fileset in output"
    assert os.path.isdir(html_fs.basedir)


# ---------------------------------------------------------------------------
# rdl.Regblock
# ---------------------------------------------------------------------------
def test_regblock(tmpdir, data_dir):
    runner, builder = _make_runner_and_builder(tmpdir)

    rdl_src = _rdl_src_node(builder, data_dir)
    task = builder.mkTaskNode(
        "rdl.Regblock",
        name="regblock",
        needs=[rdl_src],
        top="my_regs",
        cpuif="apb3",
    )

    runner.add_listener(TaskListenerLog().event)
    out = asyncio.run(runner.run(task))

    assert runner.status == 0

    sv_fs = next(
        (fs for fs in out.output
         if fs.type == "std.FileSet" and fs.filetype == "systemVerilogSource"),
        None,
    )
    assert sv_fs is not None, "expected systemVerilogSource fileset in output"
    assert len(sv_fs.files) > 0, "expected at least one generated .sv file"


# ---------------------------------------------------------------------------
# rdl.Uvm
# ---------------------------------------------------------------------------
def test_uvm(tmpdir, data_dir):
    runner, builder = _make_runner_and_builder(tmpdir)

    rdl_src = _rdl_src_node(builder, data_dir)
    task = builder.mkTaskNode(
        "rdl.Uvm",
        name="uvm",
        needs=[rdl_src],
        top="my_regs",
    )

    runner.add_listener(TaskListenerLog().event)
    out = asyncio.run(runner.run(task))

    assert runner.status == 0

    sv_fs = next(
        (fs for fs in out.output
         if fs.type == "std.FileSet" and fs.filetype == "systemVerilogSource"),
        None,
    )
    assert sv_fs is not None, "expected systemVerilogSource fileset in output"
    assert len(sv_fs.files) > 0, "expected at least one generated .sv file"


# ---------------------------------------------------------------------------
# rdl.CHeader
# ---------------------------------------------------------------------------
def test_cheader(tmpdir, data_dir):
    runner, builder = _make_runner_and_builder(tmpdir)

    rdl_src = _rdl_src_node(builder, data_dir)
    task = builder.mkTaskNode(
        "rdl.CHeader",
        name="cheader",
        needs=[rdl_src],
        top="my_regs",
    )

    runner.add_listener(TaskListenerLog().event)
    out = asyncio.run(runner.run(task))

    assert runner.status == 0

    h_fs = next(
        (fs for fs in out.output
         if fs.type == "std.FileSet" and fs.filetype == "rdlCHeader"),
        None,
    )
    assert h_fs is not None, "expected rdlCHeader fileset in output"
    assert len(h_fs.files) > 0, "expected at least one generated .h file"


# ---------------------------------------------------------------------------
# rdl.IpXact
# ---------------------------------------------------------------------------
def test_ipxact(tmpdir, data_dir):
    runner, builder = _make_runner_and_builder(tmpdir)

    rdl_src = _rdl_src_node(builder, data_dir)
    task = builder.mkTaskNode(
        "rdl.IpXact",
        name="ipxact",
        needs=[rdl_src],
        top="my_regs",
    )

    runner.add_listener(TaskListenerLog().event)
    out = asyncio.run(runner.run(task))

    assert runner.status == 0

    xml_fs = next(
        (fs for fs in out.output
         if fs.type == "std.FileSet" and fs.filetype == "rdlIpXact"),
        None,
    )
    assert xml_fs is not None, "expected rdlIpXact fileset in output"
    assert len(xml_fs.files) > 0, "expected at least one generated .xml file"


# ---------------------------------------------------------------------------
# rdl.SystemRdl
# ---------------------------------------------------------------------------
def test_systemrdl(tmpdir, data_dir):
    runner, builder = _make_runner_and_builder(tmpdir)

    rdl_src = _rdl_src_node(builder, data_dir)
    task = builder.mkTaskNode(
        "rdl.SystemRdl",
        name="systemrdl",
        needs=[rdl_src],
        top="my_regs",
    )

    runner.add_listener(TaskListenerLog().event)
    out = asyncio.run(runner.run(task))

    assert runner.status == 0

    rdl_fs = next(
        (fs for fs in out.output
         if fs.type == "std.FileSet" and fs.filetype == "systemRDLSource"),
        None,
    )
    assert rdl_fs is not None, "expected systemRDLSource fileset in output"
    assert len(rdl_fs.files) > 0, "expected at least one generated .rdl file"
