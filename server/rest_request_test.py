import requests
import json
 
url = "https://api.srcful.dev/"

request = {'gatewayConfiguration': {'gatewayName': {'id': 1}}}

body = json.dumps(request)

print(body)

def gatewayNameQuery(id):
  return """
  {
    gatewayConfiguration {
      gatewayName(id:"%s") {
        name
      }
    }
  }
  """ % id

 
response = requests.post(url=url, json={"query": gatewayNameQuery("wabi")})
print("response status code: ", response.status_code)
if response.status_code == 200:
    print("response : ", response.content)

