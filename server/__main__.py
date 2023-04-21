import argparse
import server.app as app

import logging
import os
import sys

log = logging.getLogger(__name__)

if __name__ == "__main__":

  class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)
 
    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result
 
  #handler = logging.StreamHandler(sys.stdout)
  handler = logging.StreamHandler()
  formatter = OneLineExceptionFormatter(logging.BASIC_FORMAT)
  handler.setFormatter(formatter)
  logging.root.addHandler(handler)

  logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

  # parse arguments from command line
  parser = argparse.ArgumentParser(description='Srcful Energy Gateway')

  # port and host for the web server
  parser.add_argument('-wh', '--web_host', type=str,
                      default='0.0.0.0', help='host for the web server.')
  parser.add_argument('-wp', '--web_port', type=int,
                      default=5000, help='port for the web server.')

  # port, host and type for the inverter
  parser.add_argument('-ih', '--inverter_host', type=str,
                      default='localhost', help='host for the inverter.')
  parser.add_argument('-ip', '--inverter_port', type=int,
                      default=502, help='port for the inverter (default=502).')
  parser.add_argument('-it', '--inverter_type', type=str, default='unknown',
                      help='type of inverter, e.g. huawei (default=unknown).')
  parser.add_argument('-ia', '--inverter_address', type=int,
                      default=1, help='modbus address of the inverter (default=1).')

  args = parser.parse_args()

  log.info("Running with the following configuration: %s", args)

  app.main((args.web_host, args.web_port), (args.inverter_host,
           args.inverter_port, args.inverter_type, args.inverter_address))
