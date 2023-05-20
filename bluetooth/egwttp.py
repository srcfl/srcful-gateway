from typing import Tuple

def construct_response(location: str, data:str) -> bytes:
  # we construct a response similar to http
  # eg. EGWTP/1.1 200 OK
  #     Content-Type: text/json
  #     Content-Length: 123

  header = "EGWTP/1.1 200 OK\r\n"
  header += "Location: {}\r\n".format(location)
  header += "Content-Type: text/json\r\n"
  header += "Content-Length: {}\r\n\r\n".format(len(data.encode('utf-8')))
  content = header + data

  return content.encode('utf-8')


def is_request(data: str):
  first_line = data.split("\r\n")[0].strip()
  print(f'line:"{first_line}"')
  return first_line.endswith(" EGWTTP/1.1")


def is_response(data: str):
  return data.startswith("EGWTP/1.1 ")


def parse_request(data: str) -> Tuple[dict, str]:
  # we parse a request similar to http
  # eg. GET /api/endpoint EGWTP/1.1
  #     Content-Type: text/json
  #     Content-Length: 123

  header, content = data.split("\r\n\r\n")
  header_lines = header.split("\r\n")

  header_line = header_lines[0]
  header_line_parts = header_line.split(" ")

  header_lines = header_lines[1:]
  header_lines = [line.split(": ") for line in header_lines]
  header_dict = {line[0]: line[1] for line in header_lines}
  header_dict['method'] = header_line_parts[0]
  header_dict['path'] = header_line_parts[1]
  header_dict['version'] = header_line_parts[2]

  return header_dict, content