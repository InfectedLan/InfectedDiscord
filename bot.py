# Infected discord bot script

import argparse
import requests, json
import time
import re

parser = argparse.ArgumentParser(description="Complains about errors to the discord server.")
parser.add_argument("errorFile", metavar="errorFile", type=str, help="The file to follow.")
parser.add_argument("webtokenUrl", metavar="token", type=str, help="The discord bot client token")

args = parser.parse_args()

errorFile = args.errorFile
webtoken = args.webtokenUrl

def sendNotification(errMsg):

    print("Got message %s" % errMsg)

    regex = "\[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[client ([a-zA-Z0-9: .]*)\] ([a-zA-Z ]*): *([^\/]*)in ([\/a-zA-Z._:0-9]*)\\\\nStack trace:\\\\n([a-zA-Z0-9#\/ ._():\\'{}]*\\\\n)* *thrown in ([a-zA-Z0-9\/._ ]*), referer: (?P<referer>.*)"

    result = re.match(regex, errMsg)

    if result:
        payload = {
            "username": "Loggine",
            # "avatar_url": "",
            "tts": False,
            "embeds": [{
                "title": "New log event",
                #"url": entry["url"],
                # "timestamp": "",
                # "color": "",
                #"footer": {},
                #"image": {
                #    "url": entry["imageUrl"],
                #},
                #"thumbnail": {
                #    "url": entry["imageUrl"],
                #},
                #"author": {
                #    "name": data["sellerName"],
                #    # Maybe use gravatar when default avatar?
                #    "icon_url": "https://s.yimg.jp/images/serp/as/ic_prof_default.png",
                #    # "proxy_icon_url": "",
                #},
                "fields": [
                    {
                        "name": "Date",
                        "value": result.group(1),
                        "inline": True
                    },
                    {
                        "name": "Client",
                        "value": result.group(4),
                        "inline": True
                    },
                    {
                        "name": "Type",
                        "value": result.group(5),
                        "inline": True
                    },
                    {
                        "name": "Exception",
                        "value": result.group(6),
                        "inline": True
                    },
                    {
                        "name": "File",
                        "value": result.group(7),
                        "inline": True
                    },
                    {
                        "name": "URL",
                        "value": result.group("referer"),
                        "inline": True
                    }
                ]#,
                #description": "```%s```" % errMsg
            }]
        }
    else:
        payload = {
            "username": "Loggine",
            # "avatar_url": "",
            "tts": False,
            "embeds": [{
                "title": "New log event",
                #"url": entry["url"],
                # "timestamp": "",
                # "color": "",
                #"footer": {},
                #"image": {
                #    "url": entry["imageUrl"],
                #},
                #"thumbnail": {
                #    "url": entry["imageUrl"],
                #},
                #"author": {
                #    "name": data["sellerName"],
                #    # Maybe use gravatar when default avatar?
                #    "icon_url": "https://s.yimg.jp/images/serp/as/ic_prof_default.png",
                #    # "proxy_icon_url": "",
                #},
                #"fields": [
                #    {
                #        "name": "Time Remaining",
                #        "value": data["daysLeft"],
                #        "inline": True
                #    },
                #    {
                #        "name": "Closing Time",
                #        "value": data["endTime"],
                #        "inline": True
                #    },
                #    {
                #        "name": "Early Finish",
                #        "value": data["earlyTermination"],
                #        "inline": True
                #    },
                #    {
                #        "name": "Automatic Extension",
                #        "value": data["autoExtend"],
                #        "inline": True
                #    },
                #    {
                #        "name": "Current Bid",
                #        "value": data["bidStr"],
                #        "inline": True
                #    },
                #    {
                #        "name": "Buy-out Price",
                #        "value": data["buyoutStr"],
                #        "inline": True
                #    },
                #    {
                #        "name": "Search term",
                #        "value": ", ".join(entry["keywordList"])
                #    }
                #],
                "description": "```%s```" % errMsg
            }]
        }
    #print(json.dumps(payload))

    print("Sending to %s" % webtoken)

    r = requests.post(webtoken, data=json.dumps(payload), headers={"Content-Type": "application/json"})
    time.sleep(0.5)

print("Error log watcher hello world")

with open(errorFile) as file_:
    # Go to the end of file
    file_.seek(0,2)
    while True:
        curr_position = file_.tell()
        line = file_.readline()
        if not line:
            file_.seek(curr_position)
            time.sleep(0.1)
        else:
            sendNotification(line)
            #print(line)
