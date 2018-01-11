# Infected discord bot script

import argparse
import requests, json
import time
import hashlib
import re

parser = argparse.ArgumentParser(description="Complains about errors to the discord server.")
parser.add_argument("errorFile", metavar="errorFile", type=str, help="The file to follow.")
parser.add_argument("webtokenUrl", metavar="token", type=str, help="The discord bot client token")

args = parser.parse_args()

errorFile = args.errorFile
webtoken = args.webtokenUrl

try:
    regressionDb = json.loads(open("regressiondb.json", "r").read())
    print("Loaded %s known errors" % len(regressionDb))
except Exception:
    print("Failed to load local db!")
    regressionDb = {}

def saveRegressionDb():
    with open("regressiondb.json", "w") as f:
        json.dump(regressionDb, f)

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def handleRegression(errorMsg, file):

    fileLineExtractRegex = "(.*) on line (.*)"

    fileRegexResult = re.match(fileLineExtractRegex, file)

    fileName = fileRegexResult.group(1)
    fileLine = fileRegexResult.group(2)

    seenFileBefore = True

    if not fileName in regressionDb:
        regressionDb[fileName] = {}
        seenFileBefore = False

    isNewMessage = False

    if not errorMsg in regressionDb[fileName]:
        regressionDb[fileName][errorMsg] = {}
        isNewMessage = True

    newFileLine = False

    if not fileLine in regressionDb[fileName][errorMsg]:
        newFileLine = True
        regressionDb[fileName][errorMsg][fileLine] = []

    hashed_value = md5(fileName)

    fileChangedSinceLastTime = False

    if not hashed_value in regressionDb[fileName][errorMsg][fileLine]:
        fileChangedSinceLastTime = True
        regressionDb[fileName][errorMsg][fileLine].append(hashed_value)

    saveRegressionDb()

    if not seenFileBefore:
        regressionString = "This is a new error in a new file"
    elif not fileChangedSinceLastTime:
        regressionString = "Seen before"
    elif not isNewMessage:
        if newFileLine:
            regressionString = "This error has been observed before, but on another line"
        else:
            regressionString = "This error has been observed before"
    elif isNewMessage:
        regressionString = "This error message is new"
    else:
        regressionString = "Unknown regression state(%s, %s, %s, %s)" % (seenFileBefore, isNewMessage, newFileLine, fileChangedSinceLastTime)

    return (isNewMessage, newFileLine, fileChangedSinceLastTime, regressionString)


def sendNotification(errMsg):

    print("Got message %s" % errMsg)

    # Full regex
    # \[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[client ([a-zA-Z0-9: .]*)\] ([a-zA-Z ]*): *([^\/]*)in ([\/a-zA-Z._:0-9]*)\\nStack trace:\\n([a-zA-Z0-9#\/ ._():\'{}]*\\n)* *thrown in ([a-zA-Z0-9\/._ ]*), referer: (.*)

    # Apache-finding regex
    # \[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[client ([a-zA-Z0-9: .]*)\] (.*)

    # Error regex
    # ([a-zA-Z ]*): *([^\/]*)in ([\/a-zA-Z._:0-9]*)\\nStack trace:\\n([a-zA-Z0-9#!\/ .,_\-():\'{}<>\\]*\\n)*([a-zA-Z0-9\/._ ]*), referer: (?P<referer>.*)
    apache_regex = "\[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[client ([a-zA-Z0-9: .]*)\] (.*)"
    #regex = "\[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[([a-zA-Z0-9: .]*)\] \[client ([a-zA-Z0-9: .]*)\] ([a-zA-Z ]*): *([^\/]*)in ([\/a-zA-Z._:0-9]*)\\\\nStack trace:\\\\n([a-zA-Z0-9#\/ ._():\\'{}]*\\\\n)* *thrown in ([a-zA-Z0-9\/._ ]*), referer: (?P<referer>.*)"


    apache = re.match(apache_regex, errMsg)

    if apache:
        time = apache.group(1)
        entry_type = apache.group(2)
        client = apache.group(4)
        body = apache.group(5)
        try:
            if entry_type == "php7:error":
                error_regex = "([a-zA-Z ]*): *([^\/]*)in ([\/a-zA-Z._:0-9]*)\\\\nStack trace:\\\\n([a-zA-Z0-9#!\/ .,_\-():\\'{}<>\\\\]*\\\\n)*([a-zA-Z0-9\/._ ]*), referer: (?P<referer>.*)"

                error_result = re.match(error_regex, body)

                regressionData = handleRegression(error_result.group(2), error_result.group(3))

                payload = {
                    "username": "Loggine",
                    "icon_emoji": ":warning:",
                    # "avatar_url": "",
                    "tts": False,
                    "embeds": [{
                        "title": ":rotating_light:New log event:rotating_light:",
                        "fields": [
                            {
                                "name": "Date",
                                "value": time,
                                "inline": True
                            },
                            {
                                "name": "Client",
                                "value": client,
                                "inline": True
                            },
                            {
                                "name": "Type",
                                "value": error_result.group(1),
                                "inline": True
                            },
                            {
                                "name": "Exception",
                                "value": error_result.group(2),
                                "inline": True
                            },
                            {
                                "name": "File",
                                "value": error_result.group(3),
                                "inline": True
                            },
                            {
                                "name": "URL",
                                "value": error_result.group("referer"),
                                "inline": True
                            },
                            {
                                "name": "Seen before?",
                                "value": regressionData[3],
                                "inline": True
                            }
                        ]
                    }]
                }
            elif entry_type=="php7:warn":
                warn_regex = "([a-zA-Z ]*): *(.*)in ([\/a-zA-Z._:0-9 ]*)"

                warn_result = re.match(warn_regex, body)

                regressionData = handleRegression(warn_result.group(2), warn_result.group(3))

                payload = {
                    "username": "Loggine",
                    # "avatar_url": "",
                    "tts": False,
                    "embeds": [{
                        "title": ":warning:New log event:warning:",
                        "fields": [
                            {
                                "name": "Date",
                                "value": time,
                                "inline": True
                            },
                            {
                                "name": "Client",
                                "value": client,
                                "inline": True
                            },
                            {
                                "name": "Type",
                                "value": warn_result.group(1),
                                "inline": True
                            },
                            {
                                "name": "Exception",
                                "value": warn_result.group(2),
                                "inline": True
                            },
                            {
                                "name": "File",
                                "value": warn_result.group(3),
                                "inline": True
                            },
                            {
                                "name": "Seen before?",
                                "value": regressionData[3],
                                "inline": True
                            }
                        ]
                    }]
                }
            elif entry_type=="php7:notice":
                return
                notice_regex = "([a-zA-Z ]*): *([^\/]*)in ([\/a-zA-Z._:0-9 ]*)"

                notice_result = re.match(notice_regex, body)

                regressionData = handleRegression(notice_result.group(2), notice_result.group(3))

                payload = {
                    "username": "Loggine",
                    # "avatar_url": "",
                    "tts": False,
                    "embeds": [{
                        "title": ":loudspeaker:New log event:loudspeaker:",
                        "fields": [
                            {
                                "name": "Date",
                                "value": time,
                                "inline": True
                            },
                            {
                                "name": "Client",
                                "value": client,
                                "inline": True
                            },
                            {
                                "name": "Type",
                                "value": notice_result.group(1),
                                "inline": True
                            },
                            {
                                "name": "Exception",
                                "value": notice_result.group(2),
                                "inline": True
                            },
                            {
                                "name": "File",
                                "value": notice_result.group(3),
                                "inline": True
                            },
                            {
                                "name": "Seen before?",
                                "value": regressionData[3],
                                "inline": True
                            }
                        ]
                    }]
                }
            else:
                payload = {
                    "username": "Loggine",
                    "tts": False,
                    "embeds": [{
                        "title": "New log event",
                        "description": "```%s```" % errMsg
                    }]
                }
            
        except:
            payload = {
                "username": "Loggine",
                "tts": False,
                "embeds": [{
                    "title": "An error occurred handling the following error",
                    "fields": [
                            {
                                "name": "Date",
                                "value": time,
                                "inline": True
                            },
                            {
                                "name": "Client",
                                "value": client,
                                "inline": True
                            },
                            {
                                "name": "Type",
                                "value": entry_type,
                                "inline": True
                            }
                        ]
                    "description": "```%s```" % body,
                }]
            }
    # Fallback
    else:
        payload = {
            "username": "Loggine",
            "tts": False,
            "embeds": [{
                "title": "New log event",
                "description": "```%s```" % errMsg
            }]
        }
    #print(json.dumps(payload))

    print("Sending to %s" % webtoken)

    r = requests.post(webtoken, data=json.dumps(payload), headers={"Content-Type": "application/json"})

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
