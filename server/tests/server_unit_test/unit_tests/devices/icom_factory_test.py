from server.devices.ICom import ICom
from server.devices.IComFactory import IComFactory

def test_get_config_schemas():
    for device_class in IComFactory.supported_devices:
        schema = device_class.get_config_schema()
        assert schema is not None
        assert schema.get(ICom.CONNECTION_KEY) is not None



