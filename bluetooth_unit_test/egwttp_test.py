import pytest
from bluetooth.egwttp import construct_response, is_request, is_response, parse_request

def test_construct_response():
    location = "/test"
    method = "GET"
    data = "{\"key\": \"value\"}"
    offset = 0
    response = construct_response(location, method, data, offset)
    assert response.startswith(b"EGWTP/1.1 200 OK\r\nLocation: /test\r\nMethod: GET\r\nContent-Type: text/json\r\nContent-Length: 16")
    assert response.endswith(b"{\"key\": \"value\"}")

def test_is_request():
    valid_request = "GET /test EGWTTP/1.1"
    invalid_request = "Invalid request"
    assert is_request(valid_request) == True
    assert is_request(invalid_request) == False

def test_is_response():
    valid_response = "EGWTP/1.1 200 OK"
    invalid_response = "Invalid response"
    assert is_response(valid_response) == True
    assert is_response(invalid_response) == False

def test_parse_request():
    request = "GET /test EGWTTP/1.1\r\nContent-Type: text/json\r\nContent-Length: 16\r\n\r\n{\"key\": \"value\"}"
    expected_header = {
        "Content-Type": "text/json",
        "Content-Length": "16",
        "Offset": 0,
        "method": "GET",
        "path": "/test",
        "version": "EGWTTP/1.1"
    }
    expected_content = "{\"key\": \"value\"}"
    header, content = parse_request(request)
    assert header == expected_header
    assert content == expected_content

def test_construct_response_with_offset():
    location = "/test"
    method = "GET"
    data = "{\"key\": \"value\"}"
    offset = 10
    response = construct_response(location, method, data, offset)
    assert len(response) <= 512
    assert response.startswith(b"EGWTP/1.1 200 OK\r\n")
    assert b"Method: GET\r\n" in response
    assert b"Content-Type: text/json\r\n" in response
    assert f"Content-Length: {len(data)}\r\n".encode("utf-8") in response
    assert b"Offset: 10" in response
    assert b"\r\n\r\n" in response
    assert response.endswith(b"{\"key\": \"value\"}"[offset:])

def test_reconstruct_long_message():
    location = "/test"
    method = "GET"
    data = "A" * 1000  # Long message
    reconstructed_data = ""
    offset = 0
    while True:
        response = construct_response(location, method, data, offset)
        assert len(response) <= 512
        header, received_data = response.decode().split("\r\n\r\n", 1)
        header_lines = header.split("\r\n")[1:]  # Skip the status line
        headers = dict(h.split(": ", 1) for h in header_lines)
        content_length = int(headers["Content-Length"])  # Get the Content-Length header
        offset += len(received_data)  # Update the offset based on what we got
        reconstructed_data += received_data
        if len(reconstructed_data) >= content_length:  # if we got all the data, break
            break
    assert len(reconstructed_data) == len(data)  # Check that we got all the data
    assert reconstructed_data == data  # Check that the reconstructed data matches the original data


def test_reconstruct_long_message_pattern():
    location = "/test"
    method = "GET"
    data = "ABC" * 503  # Long message
    reconstructed_data = ""
    offset = 0
    while True:
        response = construct_response(location, method, data, offset)
        assert len(response) <= 512
        header, received_data = response.decode().split("\r\n\r\n", 1)
        header_lines = header.split("\r\n")[1:]  # Skip the status line
        headers = dict(h.split(": ", 1) for h in header_lines)
        content_length = int(headers["Content-Length"])  # Get the Content-Length header
        offset += len(received_data)  # Update the offset based on what we got
        reconstructed_data += received_data
        if len(reconstructed_data) >= content_length:  # if we got all the data, break
            break
    assert len(reconstructed_data) == len(data)  # Check that we got all the data
    assert reconstructed_data == data  # Check that the reconstructed data matches the original data