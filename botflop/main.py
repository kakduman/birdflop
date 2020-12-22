import os
import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
bot = commands.Bot(command_prefix = ".", intents=discord.Intents.all())

load_dotenv()
token = os.getenv('token')
crabwings_role_id = int(os.getenv('crabwings_role'))
duckfeet_role_id = int(os.getenv('duckfeet_role'))
client_role_id = int(os.getenv('client_role'))
subuser_role_id = int(os.getenv('subuser_role'))
guild_id = int(os.getenv('guild_id'))

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
                    print("Success message sent to " + str(message.author.id) + ". User linked to API key " + message.content + " and client_id " + str(json_response['attributes']['id']))     
                else:
                    await channel.send('Sorry, this Panel account is already linked to a Discord account.')
                    print("Duplicate message sent to " + str(message.author.id) + " for using API key " + message.content + " linked to client_id " + str(json_response['attributes']['id']))

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
                print('invalid sent to ' + str(message.author.id))
        else:
            #Says this if API key is incorrect # of characters
            await channel.send('Sorry, that doesn\'t appear to be an API token. An API token should be a long string resembling this: ```yQSB12ik6YRcmE4d8tIEj5gkQqDs6jQuZwVOo4ZjSGl28d46```')
            print("obvious incorrect sent to " + str(message.author.id))
    await bot.process_commands(message)

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
    
bot.run(token)
