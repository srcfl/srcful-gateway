import json
from ..handler import GetHandler
from ..requestData import RequestData
from ....devices.IComFactory import IComFactory


class Handler(GetHandler):
    def schema(self):
        return self.create_schema("returns the supported inverters",
                                  returns={"devices": {
                                      "protocol_type": [{
                                          "id": "string",
                                          "maker": "string",
                                          "display_name": "string",
                                          "protocol": "string (optional)"
                                      }]
                                  }})

    def get_supported_inverters(self):
        supported_inverters = IComFactory.get_supported_devices()

        return {'devices': supported_inverters}

    def do_get(self, data: RequestData):
        return 200, json.dumps(self.get_supported_inverters())


class SupportedConfigurations(GetHandler):
    def schema(self):
        return self.create_schema("returns the supported configurations",
                                  returns={
                                      "protocol_type": {
                                          "description": "Configuration parameters for each protocol type",
                                          "properties": {
                                              "property_name": "string - description of the property"
                                          }
                                      }
                                  })

    def get_supported_configurations(self):
        return IComFactory.get_connection_configs()

    def do_get(self, data: RequestData):
        return 200, json.dumps(self.get_supported_configurations())
