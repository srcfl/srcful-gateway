import os
from pyfakefs.fake_filesystem_unittest import Patcher
import server.bootstrap as bootstrap
from server.inverters.modbus import Modbus
from unittest.mock import MagicMock
import logging

log = logging.getLogger(__name__)

def test_bootstrap_constructor():
    b = bootstrap.Bootstrap("test.txt")
    assert b is not None
    assert b.filename == "test.txt"


def test_bootstrap_process_lines():
    b = bootstrap.Bootstrap("test.txt")
    exp = ("TCP", "localhost", 502, "SOLAREDGE", 4)
    # exp = ("RTU", "/dev/ttyS0", 9600, 8, 'N', 1, "lqt40s", 1)
    assert b._process_lines([], 10, []) == []
    assert b._process_lines([""], 10, []) == []
    assert b._process_lines(["#"], 10, []) == []
    assert b._process_lines([" #"], 10, []) == []
    assert b._process_lines(["   # comment"], 10, []) == []
    assert b._process_lines(["   # comment", ""], 10, []) == []

    if exp[0] == "TCP":
        tasks = b._process_lines(
            [f"OpenInverter {exp[0]} {exp[1]} {exp[2]} {exp[3]} {exp[4]}\n"], 10, []
        )
    elif exp[0] == "RTU":
        tasks = b._process_lines(
            [
                f"OpenInverter {exp[0]} {exp[1]} {exp[2]} {exp[3]} {exp[4]} {exp[5]} {exp[6]} {exp[7]}\n"
            ],
            10,
            [],
        )

    assert len(tasks) == 1
    assert tasks[0].inverter.get_config() == exp


def test_booststrap_get_tasks_nofile():
    with Patcher() as patcher:
        file_name = "/var/srcfulgw/bootstrap_test.txt"
        assert not patcher.fs.exists(file_name)
        b = bootstrap.Bootstrap(file_name)
        assert b.get_tasks(10, []) == []


def test_booststrap_remove_inverter():
    inverter = MagicMock()
    exp = ("TCP", "localhost", 502, "SOLAREDGE", 4)
    assert "get_config" in dir(Modbus)
    inverter.get_config.return_value = exp

    b = bootstrap.Bootstrap('')
    b.remove_inverter(inverter)

    assert inverter.get_config.called


def test_bootstrap_add_inverter():
    with Patcher() as patcher:
        # this one actually creates a file
        file_name = "/var/srcfulgw/bootstrap_test.txt"
        assert not patcher.fs.exists(file_name)
        b = bootstrap.Bootstrap(file_name)
        exp = ("TCP", "localhost", 502, "SOLAREDGE", 4)
        # exp = ("RTU", "/dev/ttyS0", 9600, 8, 'N', 1, "lqt40s", 1)
        inverter = MagicMock()

        assert "get_config" in dir(Modbus)
        inverter.get_config.return_value = exp

        b.add_inverter(inverter)

        with open(file_name, "r") as f:
            lines = f.readlines()
            log.info("######", lines)

        assert os.path.exists(file_name)
        assert patcher.fs.exists(file_name)

        assert b.get_tasks(10, [])[0].inverter.get_config() == exp


def test_bootstrap_append_inverter():
    with Patcher() as patcher:
        # this one actually creates a file
        file_name = "/var/srcfulgw/bootstrap_test.txt"
        assert not patcher.fs.exists(file_name)
        b = bootstrap.Bootstrap(file_name)
        exp = ("TCP", "localhost", 502, "SOLAREDGE", 4)
        # exp = ("RTU", "/dev/ttyS0", 9600, 8, 'N', 1, "lqt40s", 1)

        b.append_inverter(exp)

        with open(file_name, "r") as f:
            lines = f.readlines()
            log.info("######", lines)

        assert os.path.exists(file_name)
        assert patcher.fs.exists(file_name)

        assert b.get_tasks(10, [])[0].inverter.get_config() == exp
