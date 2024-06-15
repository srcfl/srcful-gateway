from server.crypto import crypto

from server.tasks.getNameTask import GetNameTask
from unittest.mock import patch
import requests

# these tests currently rely on the api being up and running

def test_make_the_call_with_task_json():
    with patch('server.crypto.crypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.atcab_read_serial_number', return_value=crypto.ATCA_SUCCESS):
            t = GetNameTask(0, {})
            reply = requests.post(t.post_url, json=t._json())
    assert reply.status_code == 200


def test_make_the_call_with_execute():
    with patch('server.crypto.crypto.atcab_init', return_value=crypto.ATCA_SUCCESS):
        with patch('server.crypto.crypto.atcab_read_serial_number', return_value=crypto.ATCA_SUCCESS):
            t = GetNameTask(0, {})
            t.execute(0)
    assert t.name is not None