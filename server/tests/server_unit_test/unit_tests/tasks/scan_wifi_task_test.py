from server.tasks.scanWiFiTask import ScanWiFiTask


def test_create():
    t = ScanWiFiTask(0, {})
    assert t is not None

def test_execute():
    t = ScanWiFiTask(0, {})
    t.execute(0)
    assert t is not None