#import requests
#import json
 
#url = "https://api.srcful.dev/"

#request = {'gatewayConfiguration': {'gatewayName': {'id': 1}}}

#body = json.dumps(request)


#def gatewayNameQuery(id):
#  return """
#  {
#    gatewayConfiguration {
#      gatewayName(id:"%s") {
#        name
#      }
#    }
#  }
#  """ % id

 
#response = requests.post(url=url, json={"query": gatewayNameQuery("wabi")})
#if response.status_code == 200:
    # pass

