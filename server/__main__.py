import argparse
import server.app.app as app
import logging
import os
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


if __name__ == "__main__":

    # Formatter does not follow pep8
    class OneLineExceptionFormatter(logging.Formatter):
        def formatException(self, exc_info):
            result = super().formatException(exc_info)
            return repr(result)

        def format(self, record):
            result = super().format(record)
            if record.exc_text:
                result = result.replace("\n", "")
            return result

    # handler = logging.StreamHandler(sys.stdout)
    handler = logging.StreamHandler()
    formatter = OneLineExceptionFormatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    logging.root.setLevel(os.environ.get("LOGLEVEL", "DEBUG"))
    # logging.root.setLevel("DEBUG")
    logging.root.handlers = []
    logging.root.addHandler(handler)

    log = logging.getLogger(__name__)

    # parse arguments from command line
    parser = argparse.ArgumentParser(description="Srcful Energy Gateway")

    # port and host for the web server
    parser.add_argument(
        "-wh",
        "--web_host",
        type=str,
        default="0.0.0.0",
        help="host address for the rest web server.",
    )
    parser.add_argument(
        "-wp", "--web_port", type=int, default=5000, help="host port for the rest web server."
    )

    # address and port of the host environment i.e how you actually reach the rest api
    # this is more complex because docker.
    parser.add_argument(
        "-hip",
        "--host_ip",
        type=str,
        default="",
        help="host environment address to access the rest web server. Typically set if running in container.",
    )
    parser.add_argument(
        "-hp", "--host_port", type=int, default=-1, help="host enviroment port for the rest web server. Typically set if running in container."
    )

    # port, host and type for the inverter
    default_inverter_type = "unknown"
    parser.add_argument(
        "-ih",
        "--inverter_host",
        type=str,
        default="localhost",
        help="host for the inverter.",
    )
    parser.add_argument(
        "-ip",
        "--inverter_port",
        type=int,
        default=502,
        help="port for the inverter (default=502).",
    )
    parser.add_argument(
        "-it",
        "--inverter_type",
        type=str,
        default=default_inverter_type,
        help="type of inverter, e.g. huawei (default=unknown).",
    )
    parser.add_argument(
        "-ia",
        "--inverter_address",
        type=int,
        default=1,
        help="modbus address of the inverter (default=1).",
    )

    args = parser.parse_args()

    # if the host ip is not set, use the web host
    if args.host_ip == "":
        args.host_ip = args.web_host
    if args.host_ip == "0.0.0.0":
        args.host_ip = get_ip()
    if args.host_port == -1:
        args.host_port = args.web_port
    

    log.info("Running server service with the following configuration: %s", args)

    inverter = None
    # check if the invertertype is the default value
    if args.inverter_type is not default_inverter_type:
        inverter = (
            args.inverter_host,
            args.inverter_port,
            args.inverter_type,
            args.inverter_address,
        )
    app.main((args.host_ip, args.host_port), (args.web_host, args.web_port), inverter)
