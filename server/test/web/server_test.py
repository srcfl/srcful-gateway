from ...web.server import Server
from http.server import HTTPServer


def timeFunc():
    return 0
def getChipInfoFunc():
    return "testymctestface"

def test_open_close():
    s = Server(('localhost', 8081), {}, timeFunc, getChipInfoFunc)
    assert isinstance(s._webServer, HTTPServer)
    s.close()
    assert s._webServer is None
