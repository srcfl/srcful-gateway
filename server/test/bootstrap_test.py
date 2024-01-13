import os
from pyfakefs.fake_filesystem_unittest import Patcher
from .. import bootstrap
from ..tasks.openInverterTask import OpenInverterTask
from ..inverters.inverter_types import INVERTERS, OPERATION, SCAN_RANGE, SCAN_START
from unittest.mock import MagicMock

def test_bootstrap_constructor():
  b = bootstrap.Bootstrap("test.txt")
  assert b != None
  assert b.filename == "test.txt"

def test_bootstrap_processLines():
  b = bootstrap.Bootstrap("test.txt")
  exp = ("TCP", "localhost", 502, "solaredge", 4)
  # exp = ("RTU", "/dev/ttyS0", 9600, 8, 'N', 1, "lqt40s", 1)
  assert b._processLines([], 10, []) == []
  assert b._processLines([""], 10, []) == []
  assert b._processLines(["#"], 10, []) == []
  assert b._processLines([" #"], 10, []) == []
  assert b._processLines(["   # comment"], 10, []) == []
  assert b._processLines(["   # comment", ""], 10, []) == []

  if exp[0] == "TCP":
    tasks =  b._processLines([f"OpenInverter {exp[0]} {exp[1]} {exp[2]} {exp[3]} {exp[4]}\n"], 10, [])
  elif exp[0] == "RTU":
    tasks =  b._processLines([f"OpenInverter {exp[0]} {exp[1]} {exp[2]} {exp[3]} {exp[4]} {exp[5]} {exp[6]} {exp[7]}\n"], 10, [])

  assert len(tasks) == 1
  assert tasks[0].inverter.getConfig() == exp

def test_booststrap_getTasks_nofile():
  with Patcher() as patcher:
    fileName = "/var/srcfulgw/bootstrap_test.txt"
    assert not patcher.fs.exists(fileName)
    b = bootstrap.Bootstrap(fileName)
    assert b.getTasks(10, []) == []

def test_bootstrap_addInverter():
  with Patcher() as patcher:
    # this one actually creates a file
    fileName = "/var/srcfulgw/bootstrap_test.txt"
    assert not patcher.fs.exists(fileName)
    b = bootstrap.Bootstrap(fileName)
    exp = ("TCP", "localhost", 502, "solaredge", 4)
    # exp = ("RTU", "/dev/ttyS0", 9600, 8, 'N', 1, "lqt40s", 1)
    inverter = MagicMock()
    inverter.getConfig.return_value = exp

    b.addInverter(inverter)

    with open(fileName, "r") as f:
      lines = f.readlines()
      print("######", lines)

    assert os.path.exists(fileName)
    assert patcher.fs.exists(fileName)

    assert b.getTasks(10, [])[0].inverter.getConfig() == exp

def test_bootstrap_appendInverter():
  with Patcher() as patcher:
    # this one actually creates a file
    fileName = "/var/srcfulgw/bootstrap_test.txt"
    assert not patcher.fs.exists(fileName)
    b = bootstrap.Bootstrap(fileName)
    exp = ("TCP", "localhost", 502, "solaredge", 4)
    # exp = ("RTU", "/dev/ttyS0", 9600, 8, 'N', 1, "lqt40s", 1)

    b.appendInverter(exp)

    with open(fileName, "r") as f:
      lines = f.readlines()
      print("######", lines)

    assert os.path.exists(fileName)
    assert patcher.fs.exists(fileName)

    assert b.getTasks(10, [])[0].inverter.getConfig() == exp