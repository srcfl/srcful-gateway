from ...crypto import crypto


def test_initChip_release():
  assert crypto.initChip()
  assert crypto.release()


def test_getHeaderFormat():
  crypto.initChip()
  header = crypto.buildHeader()
  crypto.release()
  assert 'alg' in header
  assert 'typ' in header
  assert 'opr' in header
  assert 'device' in header


def test_getHeaderContents():
  crypto.initChip()
  header = crypto.buildHeader()
  crypto.release()
  assert header['alg'] == 'ES256'
  assert header['typ'] == 'JWT'
  assert header['opr'] == 'production'
