
from ..handler import GetHandler

from ..requestData import RequestData


class Handler(GetHandler):
    def do_get(self, data: RequestData):
        ret = "<html><head><title>Srcful Energy Gateway</title></head>"
        ret += "<body>"
        ret += f"<h1>Srcful Energy Gateway {data.bb.get_version()}</h1>"

        ret += f"<p>chipInfo: {data.bb.get_chip_info()} (This should not be all zeros)</p>"

        elapsed_time = data.bb.elapsed_time

        # convert elapsedTime to days, hours, minutes, seconds in a tuple
        days, remainder = divmod(elapsed_time // 1000, 60 * 60 * 24)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        # output the gateway current uptime in days, hours, minutes, seconds
        ret += f"<p>Uptime (days, hours, minutes, seconds): {(days, hours, minutes, seconds)}</p>"

        ret += '<p> To configure your gateway, please visit <a href="https://app.srcful.io">app.srcful.io</a></p>'

        ret += "</body></html>"

        return 200, ret
