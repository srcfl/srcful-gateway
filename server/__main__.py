import argparse
import server.app as app

if __name__ == "__main__":
  # parse arguments from command line
  parser = argparse.ArgumentParser(description='Srcful Energy Gateway')
  
  # port and host for the web server
  parser.add_argument('-wh', '--web_host', type=str, default='0.0.0.0', help='host for the web server.')
  parser.add_argument('-wp', '--web_port', type=int, default=5000, help='port for the web server.')

  # port, host and type for the inverter
  parser.add_argument('-ih', '--inverter_host', type=str, default='localhost', help='host for the inverter.')
  parser.add_argument('-ip', '--inverter_port', type=int, default=502, help='port for the inverter (default=502).')
  parser.add_argument('-it', '--inverter_type', type=str, default='unknown', help='type of inverter, e.g. huawei (default=unknown).')

  args = parser.parse_args()

  print("Running with the following configuration:", args)

  app.main((args.web_host, args.web_port), (args.inverter_host, args.inverter_port, args.inverter_type))