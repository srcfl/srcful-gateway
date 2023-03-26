from typing import Callable

class Handler:

  def doGet(stats: dict, timeMSFunc:Callable, chipInfoFunc:Callable):
    freqReads = stats['freqReads']
    energyHarvested = stats['harvests']
    energyTransported = 0
    if 'harvestTransports' in stats:
      energyTransported = stats['harvestTransports']
    startTime = stats['startTime']

 
    ret = "<html><head><title>Srcful Energy Gateway</title></head>"
    ret += "<body>"
    ret += "<h1>Srcful Energy Gateway</h1>"
    ret += f"<h2>{stats['name']}</h2>"

    ret += f"<p>chipInfo: {chipInfoFunc()}</p>"

    elapsedTime = timeMSFunc() - startTime

    # convert elapsedTime to days, hours, minutes, seconds in a tuple
    days, remainder = divmod(elapsedTime // 1000, 60*60*24)
    hours, remainder = divmod(remainder, 60*60)
    minutes, seconds = divmod(remainder, 60)

    # output the gateway current uptime in days, hours, minutes, seconds
    ret += f"<p>Uptime (days, hours, minutes, seconds): {(days, hours, minutes, seconds)}</p>"

    ret += f"<p>freqReads: {freqReads} in {elapsedTime} ms<br/>"
    ret += f"average freqReads: {freqReads / elapsedTime * 1000} per second</p>"

    ret += f"last freq: {stats['lastFreq']} Hz</p>"

    ret += f"<p>energyHarvested: {energyHarvested} in {elapsedTime} ms</br>"
    ret += f"average energyHarvested: {energyHarvested / elapsedTime * 1000} per second</p>"

    ret += f"<p>energyTransported: {energyTransported} in {elapsedTime} ms</br>"
    ret += f"average energyTransported: {energyTransported / elapsedTime * 1000} per second</p>"
    
    ret += f"ALL: {stats}</p>", "utf-8"

    ret += "</body></html>", "utf-8"
