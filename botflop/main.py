import os
import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
from datetime import datetime
import threading

bot = commands.Bot(command_prefix = ".", intents=discord.Intents.all())

load_dotenv()
token = os.getenv('token')
crabwings_role_id = int(os.getenv('crabwings_role'))
duckfeet_role_id = int(os.getenv('duckfeet_role'))
client_role_id = int(os.getenv('client_role'))
subuser_role_id = int(os.getenv('subuser_role'))
guild_id = int(os.getenv('guild_id'))
verification_channel = int(os.getenv('verification_channel'))
verification_message = int(os.getenv('verification_message'))

@bot.event
async def on_ready():
    # Marks bot as running
    print('I have started.')
    
@bot.event
async def on_message(message):
    channel = message.channel
    if message.author != bot.user and message.guild == None:

        # Potential API key, so tries it out
        if len(message.content) == 48:
            url = "https://panel.birdflop.com/api/client/account"

            cookies = {
                'pterodactyl_session': 'eyJpdiI6InhIVXp5ZE43WlMxUU1NQ1pyNWRFa1E9PSIsInZhbHVlIjoiQTNpcE9JV3FlcmZ6Ym9vS0dBTmxXMGtST2xyTFJvVEM5NWVWbVFJSnV6S1dwcTVGWHBhZzdjMHpkN0RNdDVkQiIsIm1hYyI6IjAxYTI5NDY1OWMzNDJlZWU2OTc3ZDYxYzIyMzlhZTFiYWY1ZjgwMjAwZjY3MDU4ZDYwMzhjOTRmYjMzNDliN2YifQ%3D%3D',
            }

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + message.content,
            }

            print("Querying " + url)
            response = requests.get(url, headers=headers, cookies=cookies)

            # If API token is verified to be correct:
            if str(response) == "<Response [200]>":

                # Formats response of account in JSON format
                json_response = response.json()

                
                # Loads contents of users.json
                file = open('users.json', 'r')
                data = json.load(file)
                file.close()

                # Checks if user exists. If so, skips adding them to users.json
                already_exists = False
                for user in data['users']:
                    if user['client_id'] == json_response['attributes']['id']:
                        already_exists = True
                        print("User already exists")
                if already_exists == False:       
                    data['users'].append({
                        'discord_id': message.author.id,
                        'client_id': json_response['attributes']['id'],
                        'client_api_key': message.content
                    })
                    json_dumps = json.dumps(data, indent = 2)
                    # Adds user to users.json
                    file = open('users.json', 'w')
                    file.write(json_dumps)
                    file.close()
                    
                    guild = bot.get_guild(guild_id)
                    member = guild.get_member(message.author.id)
                    if member:

                        url = "https://panel.birdflop.com/api/client"

                        cookies = {
                            'pterodactyl_session': 'eyJpdiI6InhIVXp5ZE43WlMxUU1NQ1pyNWRFa1E9PSIsInZhbHVlIjoiQTNpcE9JV3FlcmZ6Ym9vS0dBTmxXMGtST2xyTFJvVEM5NWVWbVFJSnV6S1dwcTVGWHBhZzdjMHpkN0RNdDVkQiIsIm1hYyI6IjAxYTI5NDY1OWMzNDJlZWU2OTc3ZDYxYzIyMzlhZTFiYWY1ZjgwMjAwZjY3MDU4ZDYwMzhjOTRmYjMzNDliN2YifQ%3D%3D',
                        }

                        headers = {
                            'Accept': 'application/json',
                            'Authorization': 'Bearer ' + message.content,
                        }

                        print("Querying " + url)
                        response = requests.get(url, headers=headers, cookies=cookies)

                        # If API token is verified to be correct, continues
                        if str(response) == "<Response [200]>":

                            # Formats response for servers in JSON format
                            servers_json_response = response.json()

                            user_client = False
                            user_subuser = False
                            user_crabwings = False
                            user_duckfeet = False
                            for server in servers_json_response['data']:
                                server_owner = server['attributes']['server_owner']
                                if server_owner == True:
                                    user_client = True
                                elif server_owner == False:
                                    user_subuser = True
                                server_node = server['attributes']['node']
                                if server_node == "Crabwings - NYC":
                                    user_crabwings = True
                                elif server_node == "Duckfeet - EU":
                                    user_duckfeet = True
                            if user_client == True:
                                role = discord.utils.get(guild.roles, id=client_role_id)
                                await member.add_roles(role)
                            if user_subuser == True:
                                role = discord.utils.get(guild.roles, id=subuser_role_id)
                                await member.add_roles(role)
                            if user_crabwings == True:
                                role = discord.utils.get(guild.roles, id=crabwings_role_id)
                                await member.add_roles(role)
                            if user_duckfeet == True:
                                role = discord.utils.get(guild.roles, id=duckfeet_role_id)
                                await member.add_roles(role)
                    
                    await channel.send ('Your Discord account has been linked to your panel account! Do not delete your API key.')
                    print("Success message sent to " + message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")" + ". User linked to API key " + message.content + " and client_id " + str(json_response['attributes']['id']))     
                else:
                    await channel.send('Sorry, this Panel account is already linked to a Discord account.')
                    print("Duplicate message sent to " + message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")" + " for using API key " + message.content + " linked to client_id " + str(json_response['attributes']['id']))

            # Makes json pretty with indentations and stuff, then writes to file
#                json_dumps = json.dumps(json_response, indent = 2)
#                file = open("data.json", "w")
#                file.write(json_dumps)
#                file.close()

#               linked_servers = {}
#               linked_servers['server'] = []
#               for server in json_response['data']:
#                   server_owner = server['attributes']['server_owner']
#                   server_uuid = server['attributes']['uuid']
#                   server_name = server['attributes']['name']
#                   server_node = server['attributes']['node']
#                   message_sender = message.author.id
#                   info = str(server_owner) + server_uuid + server_name + server_node + str(message_sender)
#                   print(info)
#                   file = open('/home/container/data/' + str(message.author.id) + '.json', "a")
#                   file.write(info + '\n')
#                   file.close()
            else: 
                #Says if API key is the corect # of characters but invalid
                await channel.send("Sorry, that appears to be an invalid API key.")
                print('invalid sent to ' + message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")")
        else:
            #Says this if API key is incorrect # of characters
            await channel.send('Sorry, that doesn\'t appear to be an API token. An API token should be a long string resembling this: ```yQSB12ik6YRcmE4d8tIEj5gkQqDs6jQuZwVOo4ZjSGl28d46```')
            print("obvious incorrect sent to " + message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")")
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    global verification_message
    global verification_channel
    if payload.message_id != verification_message:
        return
    if payload.user_id == bot.user.id:
        return
    # Remove the reaction
    guild = discord.utils.get(bot.guilds, id=guild_id)
    verification_channel_obj = await bot.fetch_channel(verification_channel)
    verification_message_obj = await verification_channel_obj.fetch_message(verification_message)
    user = bot.get_user(payload.user_id)
    await verification_message_obj.remove_reaction(payload.emoji, user)
    if str(payload.emoji) == "✅":
        await user.send("Hey there! It looks like you'd like to verify your account. I'm here to help you with that!\n\nIf you're confused at any point, see https://birdflop.com/verification for a tutorial including images.\n\nWith that said, let's get started! You'll want to start by grabbing some API credentials for your account by signing into https://panel.birdflop.com. Head over to the **Account** section in the top right, then click on the **API Credentials tab**. You'll want to create an API key with description `Verification` and `172.18.0.2` in the **Allowed IPs section**.\n\nWhen you finish entering the necessary information, hit the blue **Create **button.\n\nNext, you'll want to copy your API credentials. After clicking **Create**, you'll receive a long string. Copy it with `ctrl+c` (`cmnd+c` on Mac) or by right-clicking it and selecting **Copy**.\n\nIf you click on the **Close **button before copying the API key, no worries! Delete your API key and create a new one with the same information.\n\nFinally, direct message your API key to Botflop: that's me!\n\nTo verify that you are messaging the key to the correct user, please ensure that the my ID is `Botflop#2403` and that my username is marked with a blue **BOT** badge. Additionally, the only server under the **Mutual Servers** tab should be Birdflop Hosting.\n\nAfter messaging me your API key, you should receive a success message. If you do not receive a success message, please create a ticket in the Birdflop Discord's support channel (https://ptb.discord.com/channels/746125698644705524/764280387253305354/764281363759104000)")
        print("sent verification challenge to " + user.name + "#" + str(user.discriminator) + " (" + str(user.id) + ")")
    else:
        file = open('users.json', 'r')
        data = json.load(file)
        file.close()
        i = 0
        j = -1
        for client in data['users']:
            j += 1
            if client['discord_id'] == user.id:
                data['users'].pop(j)
                i = 1
        if i == 1:
            json_dumps = json.dumps(data, indent = 2)
            file = open('users.json', 'w')
            file.write(json_dumps)
            file.close()
            print('successfully unlinked ' + user.name + "#" + str(user.discriminator) + " (" + str(user.id) + ")")

@bot.command()
async def ping(ctx):
	await ctx.send(f'Your ping is {round(bot.latency * 1000)}ms')

@bot.command(name="react", pass_context=True)
@has_permissions(administrator=True)
async def react(ctx, url, reaction):
    channel = await bot.fetch_channel(int(url.split("/")[5]))
    message = await channel.fetch_message(int(url.split("/")[6]))
    await message.add_reaction(reaction)
    print('reacted to ' + url + ' with ' + reaction)

'''def checkTime():
    # This function runs periodically every 1 second
    threading.Timer(1, checkTime).start()

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    if(current_time == '02:11:00'):  # check if matches with the desired time
        print('sending message')


checkTime()'''

bot.run(token)

# full name: message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")"
