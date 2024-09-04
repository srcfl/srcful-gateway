import os
from pyfakefs.fake_filesystem_unittest import Patcher
import server.bootstrap as bootstrap
from server.inverters.modbus import Modbus
from unittest.mock import MagicMock
import logging
import server.tests.config_defaults as cfg

log = logging.getLogger(__name__)

def test_bootstrap_constructor():
    b = bootstrap.Bootstrap("test.txt")
    assert b is not None
    assert b.filename == "test.txt"
    

def test_bootstrap_process_lines():
    b = bootstrap.Bootstrap("test.txt")
        
    configs = [cfg.TCP_CONFIG, cfg.RTU_CONFIG, cfg.SOLARMAN_CONFIG, cfg.SUNSPEC_CONFIG]
    lines = []
    
    for config in configs:
        line = "OpenInverter " + " ".join(str(v) for v in config.values()) + "\n"
        lines.append(line)
    
    # exp = ("RTU", "/dev/ttyS0", 9600, 8, 'N', 1, "lqt40s", 1)
    assert b._process_lines([], 10, []) == []
    assert b._process_lines([""], 10, []) == []
    assert b._process_lines(["#"], 10, []) == []
    assert b._process_lines([" #"], 10, []) == []
    assert b._process_lines(["   # comment"], 10, []) == []
    assert b._process_lines(["   # comment", ""], 10, []) == []

    tasks = b._process_lines(lines, 10, [])

    assert len(tasks) == len(configs)
    
    for task in tasks:
        assert task.der.get_config() in configs


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
    b.remove_device(inverter)

    assert inverter.get_config.called


def test_bootstrap_add_inverter():
    with Patcher() as patcher:
        # this one actually creates a file
        file_name = "/var/srcfulgw/bootstrap_test.txt"
        assert not patcher.fs.exists(file_name)
        b = bootstrap.Bootstrap(file_name)
        
        solaredge_conf = cfg.TCP_CONFIG

        der = MagicMock()

        assert "get_config" in dir(Modbus)
        der.get_config.return_value = solaredge_conf

        b.add_device(der)

        with open(file_name, "r") as f:
            lines = f.readlines()
            log.info("######", lines)

        assert os.path.exists(file_name)
        assert patcher.fs.exists(file_name)

        assert b.get_tasks(10, [])[0].der.get_config() == solaredge_conf


def test_bootstrap_append_inverter():
    with Patcher() as patcher:
        # this one actually creates a file
        file_name = "/var/srcfulgw/bootstrap_test.txt"
        assert not patcher.fs.exists(file_name)
        b = bootstrap.Bootstrap(file_name)
        solaredge_conf = cfg.TCP_CONFIG

        b.append_inverter(solaredge_conf)

        with open(file_name, "r") as f:
            lines = f.readlines()
            log.info("######", lines)

        assert os.path.exists(file_name)
        assert patcher.fs.exists(file_name)

        assert b.get_tasks(10, [])[0].der.get_config() == solaredge_conf
