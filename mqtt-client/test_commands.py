#!/usr/bin/env python3
"""
Test script to send commands to the MQTT client
This can be used to test the /control topic functionality
"""

import json
import ssl
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv


def create_test_client():
    """Create a test MQTT client for sending commands"""
    # Load environment variables from mqtt.env file
    load_dotenv('mqtt.env')

    client = mqtt.Client()

    # Configure TLS (same as main client)
    ca_cert_content = os.getenv('MQTT_ROOT_CA')
    if ca_cert_content:
        ca_cert_path = '/tmp/test-ca-cert.pem'
        with open(ca_cert_path, 'w') as f:
            f.write(ca_cert_content)

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(ca_cert_path)
        context.check_hostname = False
        client.tls_set_context(context)

    # Set credentials
    username = os.getenv('MQTT_USERNAME')
    password = os.getenv('MQTT_PASSWORD')
    if username and password:
        client.username_pw_set(username, password)

    return client


def send_modbus_command(command_data):
    """Send a modbus command to the modbus request topic"""
    client = create_test_client()

    broker_host = os.getenv('MQTT_BROKER_HOST', 'localhost')
    broker_port = int(os.getenv('MQTT_BROKER_PORT', '8883'))

    try:
        client.connect(broker_host, broker_port, 60)

        payload = json.dumps(command_data)

        client.publish('iamcat/modbus/request', payload, qos=1)
        print(f"Sent modbus command: {payload}")

        client.disconnect()

    except Exception as e:
        print(f"Error sending modbus command: {e}")


if __name__ == "__main__":
    print("MQTT Modbus Test Commands")
    print("1. modbus_read (function code 3)")
    print("2. modbus_read (function code 4)")
    print("3. modbus_write (function code 16)")

    choice = input("Enter command number (1-3): ")

    modbus_examples = {
        '1': {
            "function_code": 3,
            "device_id": "A2332407312",
            "address": 10056,
            "size": 1,
            "type": "U16",
            "endianess": "big",
            "scale_factor": 1
        },
        '2': {
            "function_code": 4,
            "device_id": "A2332407312",
            "address": 10056,
            "size": 1,
            "type": "U16",
            "endianess": "big",
            "scale_factor": 1
        },
        '3': {
            "function_code": 16,
            "device_id": "A2332407312",
            "address": 33207,
            "values": 170,
            "type": "U16"
        }
    }

    if choice in modbus_examples:
        send_modbus_command(modbus_examples[choice])
    else:
        print("Invalid choice")
