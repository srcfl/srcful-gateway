from unittest.mock import Mock, patch
from server.web.handler.get.root import Handler
from server.web.handler.requestData import RequestData
from server.app.blackboard import BlackBoard
from server.crypto.crypto_state import CryptoState
import server.crypto.crypto as crypto


def test_doGet(blackboard):

    with patch("server.crypto.crypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.atcab_read_serial_number", return_value=crypto.ATCA_SUCCESS):

            # Create a RequestData object with the parameters you want to test
            mock_crypto_state = Mock(spec=CryptoState)
            mock_crypto_state.to_dict.return_value = {
                'deviceName': 'test_device',
                'serialNumber': '123456789',
                'publicKey': 'abcdef',
                'compactKey': 'compact',
                'chipDeathCount': '0'
            }
            bb = blackboard
            # The state property is computed from individual components
            bb._start_time = 0  # This affects uptime
            bb._devices.saved = []  # Set saved devices to empty list

            request_data = RequestData(bb, post_params={}, query_params={}, data={})

            # Create an instance of Handler
            handler = Handler()

            # Call the doGet method and capture the output
            status_code, response = handler.do_get(request_data)

    # Check that the status code is 200
    assert status_code == 200

    # Check that the response is the expected JSON
    assert len(response) > 100
