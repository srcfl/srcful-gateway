import os


def get():
    if os.name == 'Linux':
        try:
            return open('/sys/class/net/eth0/address').readline().strip().upper()
        except FileNotFoundError:
            return "FF:FF:FF:FF:FF:FF"
    else:
        import uuid
        return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
