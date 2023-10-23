import os
from pyfakefs.fake_filesystem_unittest import Patcher
from .. import bootstrap
from ..tasks.openInverterTask import OpenInverterTask
from ..inverters.InverterTCP import InverterTCP

def test_bootstrap_constructor():
  b = bootstrap.Bootstrap("test.txt")
  assert b != None
  assert b.filename == "test.txt"

def test_bootstrap_processLines():
  b = bootstrap.Bootstrap("test.txt")
  exp = ("localhost", 502, "solaredge", 1)

  assert b._processLines([], 10, []) == []
  assert b._processLines([""], 10, []) == []
  assert b._processLines(["#"], 10, []) == []
  assert b._processLines([" #"], 10, []) == []
  assert b._processLines(["   # comment"], 10, []) == []
  assert b._processLines(["   # comment", ""], 10, []) == []

  tasks =  b._processLines([f"OpenInverter {exp[0]} {exp[1]} {exp[2]} {exp[3]}"], 10, [])
  assert len(tasks) == 1
  assert tasks[0].inverter.getConfig() == exp

def test_booststrap_getTasks_nofile():
  with Patcher() as patcher:
    fileName = "/var/srcfulgw/bootstrap_test.txt"
    assert not patcher.fs.exists(fileName)
    b = bootstrap.Bootstrap(fileName)
    assert b.getTasks(10, []) == []


def test_bootstrap_appendInverter():
  with Patcher() as patcher:
    # this one actually creates a file
    fileName = "/var/srcfulgw/bootstrap_test.txt"
    assert not patcher.fs.exists(fileName)
    b = bootstrap.Bootstrap(fileName)
    exp = ("localhost", 502, "solaredge", 1)

    b.appendInverter(exp)
    assert os.path.exists(fileName)
    assert patcher.fs.exists(fileName)

    assert b.getTasks(10, [])[0].inverter.getConfig() == exp
