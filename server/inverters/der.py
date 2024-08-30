from .ICom import ICom


class DER:
    """
    DER class
    """

    def __init__(self, com: ICom):
        """
        Constructor
        """
        self.com = com

    def connect(self) -> bool:
        return self.com.connect()

    def disconnect(self) -> None:
        return self.com.disconnect()

    def reconnect(self) -> bool:
        return self.com.reconnect()
    
    def is_open(self) -> bool:
        return self.com.is_open()

    def read_harvest_data(self, force_verbose=False) -> dict:
        return self.com.read_harvest_data(force_verbose)

    def get_harvest_data_type(self) -> str:
        return self.com.get_harvest_data_type()
    
    def get_config(self) -> dict:
        return self.com.get_config()
    
    def get_profile(self) -> dict:
        return self.com.get_profile()