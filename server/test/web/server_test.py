from io import BytesIO
from server.web.server import Server, requestHandlerFactory

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

def test_handler_postBytest2Dict():
  h = requestHandlerFactory(None, None, None, None)
  d = h.post2Dict('')
  assert  d == {}
  assert h.post2Dict('foo') == {}
  assert h.post2Dict('foo=') == {'foo': ''}
  assert h.post2Dict('foo=bar') == {'foo': 'bar'}
  assert h.post2Dict('foo=bar&baz=qux') == {'foo': 'bar', 'baz': 'qux'}
  assert h.post2Dict('name=John%20Doe&age=30&location=New%20York') == {'name': 'John Doe', 'age': '30', 'location': 'New York'}

def test_handler_getPostdata():
  h = requestHandlerFactory(None, None, None, None)
  assert h.getData({'Content-Length': '0'}, BytesIO(b'')) == {}
  
  data = b'name=John%20Doe&age=30&location=New%20York'
  assert h.getData({'Content-Length': len(data)}, BytesIO(data)) == {'name': 'John Doe', 'age': '30', 'location': 'New York'}

  data = b'{"name": "John Doe", "age": 30, "location": "New York"}'
  assert h.getData({'Content-Length': len(data)}, BytesIO(data)) == {'name': 'John Doe', 'age': 30, 'location': 'New York'}

  data = b'{"name": "John&Doe", "age": 30, "location": "New York = Kalmar"}'
  assert h.getData({'Content-Length': len(data)}, BytesIO(data)) == {'name': 'John&Doe', 'age': 30, 'location': 'New York = Kalmar'}
  
