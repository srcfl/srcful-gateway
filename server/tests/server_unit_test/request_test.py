import server.request as request


def test_request():
    assert request.add(1, 2) == 3
