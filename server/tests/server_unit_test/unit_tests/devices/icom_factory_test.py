from server.devices.ICom import ICom
from server.devices.IComFactory import IComFactory
from server.tests import config_defaults as cfg

def test_get_config_schemas():
    for device_class in IComFactory.supported_devices:
        schema = device_class.get_config_schema()
        assert schema is not None
        assert schema.get(ICom.CONNECTION_KEY) is not None


def test_create_icom():
    for device_class in IComFactory.supported_devices:

        config = cfg.class_config_map[device_class]

        icom = IComFactory.create_com(config)
        assert icom is not None

        icom = IComFactory.create_com(icom.get_config())
        assert icom is not None
        assert isinstance(icom, device_class)

def test_clone():
    for device_class in IComFactory.supported_devices:
        icom = IComFactory.create_com(cfg.class_config_map[device_class])
        assert icom is not None

        clone = icom.clone()
        assert clone is not None
        assert isinstance(clone, device_class)