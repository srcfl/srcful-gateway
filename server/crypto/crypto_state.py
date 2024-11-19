from server.crypto import crypto


class CryptoState:

    @property
    def DEVICE(self):
        return CryptoState.device_key()
    
    @classmethod
    def device_key(cls) -> str:
        return "deviceName"
    
    @property   
    def SERIAL_NO(self):
        return CryptoState.serial_no_key()
    
    @classmethod
    def serial_no_key(cls) -> str:
        return "serialNumber"
    
    @property
    def PUBLIC_KEY(self):
        return CryptoState.public_key_key()
    
    @classmethod
    def public_key_key(cls) -> str:
        return "publicKey"
    
    @property
    def COMPACT_KEY(self):
        return CryptoState.compact_key_key()
    
    @classmethod
    def compact_key_key(cls) -> str:
        return "compactKey"
    
    @property
    def CHIP_DEATH_COUNT(self):
        return CryptoState.chip_death_count_key()
    
    @classmethod
    def chip_death_count_key(cls) -> str:
        return "chipDeathCount"

    def __init__(self):
        with crypto.Chip() as chip:
            self._device_name = chip.get_device_name()
            self._serial_number = chip.get_serial_number()
            self._public_key = chip.get_public_key()
            self._compact_key = crypto.public_key_to_compact(self._public_key)
    
    @property
    def device_name(self) -> str:
        return self._device_name
    
    @property
    def serial_number(self) -> bytes:
        return self._serial_number
    
    @property
    def public_key(self) -> bytes:
        return self._public_key
    
    @property
    def compact_key(self) -> bytes:
        return self._compact_key
        
    def to_dict(self, death_count: int) -> dict:
        ret = {}
        ret[self.DEVICE] = self.device_name
        ret[self.SERIAL_NO] = self.serial_number.hex()
        ret[self.PUBLIC_KEY] = self.public_key.hex()
        ret[self.COMPACT_KEY] = self.compact_key.decode("utf-8")
        ret[self.CHIP_DEATH_COUNT] = str(death_count)
        return ret

