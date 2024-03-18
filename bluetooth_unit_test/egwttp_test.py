import random
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


def test_reconstruct_long_message_with_offsets_and_buffer():
    location = "/test"
    method = "GET"
    data = "ABC" * 503  # Long message
    buffer = [""]
    offset = 0  # we start at offset 0 as the first message so we dont need to wait for 0 to be needed in randomization
    while True:
        
        response = construct_response(location, method, data, offset)
        assert len(response) <= 512
        header, received_data = response.decode().split("\r\n\r\n", 1)
        header_lines = header.split("\r\n")[1:]  # Skip the status line
        headers = dict(h.split(": ", 1) for h in header_lines)

        content_length = int(headers["Content-Length"])  # Get the Content-Length header
        if len(buffer) < content_length:
            buffer = [""] * content_length

        buffer[offset:offset+len(received_data)] = received_data  # Place the received data in the buffer at the correct offset
        offset = random.randint(0, len(data) - 1)  # Simulate receiving data at a random offset
        if "" not in buffer:  # If the buffer is full, we've received all the data
            break

    reconstructed_data = "".join(buffer)  # Join the buffer into a single string
    assert len(reconstructed_data) == len(data)  # Check that we got all the data
    assert reconstructed_data == data  # Check that the reconstructed data matches the original data


def test_reconstruct_long_message_network():
    location = "/api/network"
    method = "GET"
    data = '{"connections": [{"connection": {"id": "eather", "permissions": [], "timestamp": 1709572162, "type": "802-11-wireless", "uuid": "8b5d9847-373a-40dd-813c-f9eeed6d91e7"}, "802-11-wireless": {"hidden": 1, "mac-address-blacklist": [], "mode": "infrastructure", "security": "802-11-wireless-security", "seen-bssids": ["14:DD:A9:CB:62:D0"], "ssid": [101, 97, 116, 104, 101, 114]}, "802-11-wireless-security": {"auth-alg": "open", "key-mgmt": "wpa-psk"}, "ipv4": {"address-data": [], "addresses": [], "dns-search": [], "method": "auto", "route-data": [], "routes": []}, "ipv6": {"address-data": [], "addresses": [], "dns-search": [], "method": "auto", "route-data": [], "routes": []}, "proxy": {}}, {"connection": {"autoconnect-priority": -999, "id": "Wired connection 1", "interface-name": "eth0", "permissions": [], "timestamp": 1709571611, "type": "802-3-ethernet", "uuid": "79d5b1a1-c8b1-3b84-b77e-fd02875635b3"}, "802-3-ethernet": {"auto-negotiate": 0, "mac-address-blacklist": [], "s390-options": {}}, "ipv4": {"address-data": [], "addresses": [], "dns-search": [], "method": "auto", "route-data": [], "routes": []}, "ipv6": {"address-data": [], "addresses": [], "dns-search": [], "method": "auto", "route-data": [], "routes": []}, "proxy": {}}, {"connection": {"autoconnect": 0, "id": "supervisor0", "interface-name": "supervisor0", "permissions": [], "timestamp": 1709571610, "type": "bridge", "uuid": "1035567f-1cfa-4148-ad43-db1a2cdae75b"}, "802-3-ethernet": {"auto-negotiate": 0, "mac-address-blacklist": [], "s390-options": {}}, "bridge": {"interface-name": "supervisor0", "multicast-startup-query-interval": 3124, "stp": 0, "vlans": []}, "ipv4": {"address-data": [{"address": "10.114.104.1", "prefix": 25}], "addresses": [[23622154, 25, 0]], "dns-search": [], "method": "manual", "route-data": [], "routes": []}, "ipv6": {"address-data": [], "addresses": [], "dns-search": [], "method": "link-local", "route-data": [], "routes": []}, "proxy": {}}]}'
    original_data = data
    reconstructed_data = bytearray(len(bytes(data, 'utf-8')))  # preallocate bytearray of the correct size
    offset = 0

    while True:
        response = construct_response(location, method, data, offset)
        assert len(response) <= 512
        header, received_data = response.split(b"\r\n\r\n", 1)
        header_lines = header.decode().split("\r\n")[1:]  # We still need to perform string operations on the header
        headers = dict(h.split(": ", 1) for h in header_lines)

        content_length = int(headers["Content-Length"])
        assert len(reconstructed_data) == content_length  # buffer size should match content_length

        if "Offset" in headers:
            offset = int(headers["Offset"])
        else:
            offset = 0

        # This step overwrites the empty space in buffer with newly received data
        reconstructed_data[offset: offset + len(received_data)] = received_data

        # Check if all data received are not None or zero byte
        if all(byte != 0 for byte in reconstructed_data):
            break

        # set the offset to the next zero byte
        offset = reconstructed_data.index(0)

    reconstructed_data = reconstructed_data.decode()  # Decode the bytearray back into a string

    assert len(reconstructed_data) == len(original_data)
    assert reconstructed_data == original_data
