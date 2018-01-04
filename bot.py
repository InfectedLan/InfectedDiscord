# Infected discord bot script

import argparse
import re
import discord
import sys
import time

parser = argparse.ArgumentParser(description="Complains about errors to the discord server.")
parser.add_argument("errorFile", metavar="errorFile", type=str, help="The file to follow.")
parser.add_argument("discordClientToken", metavar="token", type=str, help="The discord bot client token")

args = parser.parse_args()

errorFile = args.errorFile
clientToken = args.discordClientToken

# Fire up discord bot
client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    talk_channel = 0
    for channel in client.get_all_channels():
    	print("Name: %s, id: %s" % (channel.name, channel.id))
    	if channel.name == "errors":
    		talk_channel = channel
    		break
    await client.send_message(talk_channel, 'Discord bot is ON')
    # Follow the file
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
                    await client.send_message(talk_channel, 'New error message: \n```\n%s\n```' % line)
                    #print(line)

client.run(clientToken)
