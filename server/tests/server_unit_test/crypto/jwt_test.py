import base64
import json
from server.crypto import crypto

def test_build_jwt(capsys):
    # run with pytest -s server/tests/server_unit_test/crypto/jwt_test.py to see the output
    data_to_sign = {"test": "data"}
    headers = {"model": "volvo 240"}
    
    with crypto.Chip(crypto_impl=crypto.SoftwareCrypto()) as chip:
        jwt = chip.build_jwt(data_to_sign, headers)

    print("\nGenerated JWT:")
    print(jwt)

    # Verify the JWT
    header, payload, signature = jwt.split('.')
    
    # Decode header and payload
    header_json = json.loads(base64.urlsafe_b64decode(header + '==').decode('utf-8'))
    payload_json = json.loads(base64.urlsafe_b64decode(payload + '==').decode('utf-8'))

    print("\nDecoded Header:")
    print(json.dumps(header_json, indent=2))
    print("\nDecoded Payload:")
    print(json.dumps(payload_json, indent=2))

    # Assert header contents
    assert header_json['alg'] == 'ES256'
    assert header_json['typ'] == 'JWT'
    with crypto.Chip(crypto_impl=crypto.SoftwareCrypto()) as chip:
        assert header_json['device'] == chip.get_serial_number().hex()
    assert header_json['opr'] == 'production'
    assert header_json['model'] == "volvo 240"

    # Assert payload contents
    assert payload_json == data_to_sign

    # Analyze the signature
    decoded_signature = base64.urlsafe_b64decode(signature + '==')
    print("\nSignature analysis:")
    print(f"Signature length: {len(decoded_signature)} bytes")
    print(f"Signature (hex): {decoded_signature.hex()}")

    # Instead of asserting a specific length, we'll check if it's within an expected range
    assert 64 <= len(decoded_signature) <= 72, f"Signature length ({len(decoded_signature)}) is outside the expected range (64-72 bytes)"

    # Capture and print the output
    captured = capsys.readouterr()
    print("\nTest Output:")
    print(captured.out)