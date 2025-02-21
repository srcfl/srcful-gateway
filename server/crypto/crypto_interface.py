from abc import ABC, abstractmethod


class CryptoInterface(ABC):
    @abstractmethod
    def atcab_init(self, cfg):
        pass

    @abstractmethod
    def atcab_release(self):
        pass

    @abstractmethod
    def atcab_info(self, revision):
        pass

    @abstractmethod
    def atcab_read_serial_number(self):
        pass

    @abstractmethod
    def atcab_get_pubkey(self, key_id):
        pass

    @abstractmethod
    def atcab_sign(self, key_id, message):
        pass

    @abstractmethod
    def atcab_random(self):
        pass

    @abstractmethod
    def atcab_verify(self, signature, data, public_key=None) -> tuple[int, bool]:
        pass
