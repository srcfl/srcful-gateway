from unittest.mock import patch

from server.web.handler.get.root import Handler
from server.web.handler.requestData import RequestData
from server.blackboard import BlackBoard

import server.crypto.crypto as crypto




def test_doGet():

    with patch("server.crypto.crypto.atcab_init", return_value=crypto.ATCA_SUCCESS):
        with patch("server.crypto.crypto.atcab_read_serial_number", return_value=crypto.ATCA_SUCCESS):

            # Create a RequestData object with the parameters you want to test
            request_data = RequestData(BlackBoard(), post_params={}, query_params={}, data={})

            # Create an instance of Handler
            handler = Handler()

            # Call the doGet method and capture the output
            status_code, response = handler.do_get(request_data)

    # Check that the status code is 200
    assert status_code == 200

    # Check that the response is the expected JSON
    assert len(response) > 100