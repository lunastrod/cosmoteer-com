import discord
from discord import app_commands
import secret_token

#from dotenv import load_dotenv
#import os
#import center_of_mass

import base64
from io import BytesIO
import requests
import json

from datetime import datetime as dt

#load_dotenv()

API_URL = "https://cosmo-api-six.vercel.app/analyze"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

short_version_text="Made by LunastroD, Aug 2023 - Sep 2023"
version_text=short_version_text+", for the Excelsior discord server and the Cosmoteer community :3\n- Check out the source code at <https://github.com/lunastrod/cosmoteer-com>"
help_text=version_text+"""
/ping: responds with the bot's latency

/com: Calculates the center of mass of a cosmoteer ship.png
- parameters:
 - ship: the .ship.png file of the ship. Usually found in C:\\Users\\YOUR USERNAME\\Saved Games\\Cosmoteer\\YOUR STEAM ID\\Saved Ships
 - boost: turns boosters on or off. Default: on
 - flipvectors: flips the thrust vectors to avoid overlap. Default: off
 - strafecot: draws the center of thrust vectors on every direction instead of only fordwards. Default: on
 - partcom: draws the center of mass of each part. Default: off
 - draw: draws the output image. Default: on
/cost: Calculates cost analysis of a cosmoteer ship.png
- parameters:
 - ship: the .ship.png file of the ship. Usually found in C:\\Users\\YOUR USERNAME\\Saved Games\\Cosmoteer\\YOUR STEAM ID\\Saved Ships

- common questions:
 - does the bot consider the 5% lateral thrust of each thruster? yes
 - does the bot consider engine room buff? yes
 - is the cot exact? it should be
 - is the com exact? no, it's a decent approximation, it should be inside the green circle
 - is the max speed exact? no, it's an approximation, assume ±1%, and it assumes your ship is balanced

- If you notice any mistakes on things like the total mass or the speed, ping LunastroD"""

@client.event
async def on_ready():
    """
    Event handler that is called when the bot is ready to start receiving events.
    """
    # Set the bot's presence to the specified game
    await client.change_presence(activity=discord.Game(name="Cosmoteer (/help)"))
    
    # Print a message indicating that the slash commands are being synced
    print(dt.now(),"Syncing slash commands")
    
    # Sync the slash commands with the Discord API
    await tree.sync()
    
    # Print a list of guilds that the bot is connected to
    print("Guilds:")
    for guild in client.guilds:
        print("\t- " + guild.name, guild.id)
    
    # Print a message indicating that the bot is ready
    print(dt.now(),"Bot is ready")

@tree.command(name="com", description="Calculates the center of mass of a cosmoteer ship.png")
async def com(interaction: discord.Interaction, ship: discord.Attachment, boost: bool = True, flip_vectors: bool = False, draw_all_cot: bool = True, draw_all_com: bool = False, draw: bool = True):
    """
    Calculates the center of mass of a cosmoteer ship.png.

    Parameters:
    - interaction: The Discord interaction object.
    - ship: The attached image of the ship.
    - boost: Whether to apply boost.
    - draw_all_cot: Whether to draw all center of thrust lines.
    - draw_all_com: Whether to draw all center of mass lines.
    - draw_cot: Whether to draw center of thrust lines.
    - draw_com: Whether to draw center of mass lines.
    - draw: Whether to draw the output images.
    """
    
    print(dt.now(),"received command")
    await interaction.response.defer()
    print(dt.now(),"deferred")

    # Read the image bytes and encode them to base64
    image_bytes = await ship.read()
    base64_string = base64.b64encode(image_bytes).decode('utf-8')

    # Create a file object for the original image
    ship = discord.File(BytesIO(image_bytes), filename="input_file.png")

    try:
        # Prepare the request data
        args = {
            "boost": boost,
            "draw_all_cot": draw_all_cot,
            "draw_all_com": draw_all_com,
            "draw_cot": True,
            "draw_com": True,
            "draw": True,
            "flip_vectors": flip_vectors
        }
        json_data = json.dumps({'image': base64_string, 'args': args})

        # Send the request to the server
        url = API_URL
        print(dt.now(),"requesting data")
        response = requests.post(url, json=json_data)
        response.raise_for_status()
        print(dt.now(),"server responded")
        

        # Get the response
        data_returned = response.json()
        # if draw is false do not retrieve the center of mass image
        if draw == True:
            # Get the URL of the center of mass image
            
            url_com = data_returned['url_com']
            # Fetch the center of mass image
            print(dt.now(),"requesting image")
            response_url_com = requests.get(url_com)
            response_url_com.raise_for_status()
            content_response = response_url_com.content
            print(dt.now(),"server responded")

            # Create a file object for the center of mass image
            picture = discord.File(BytesIO(content_response), filename="output_file.png")
            
            # Prepare the list of files to send
            files_to_send = [ship, picture]
        else:
            # Prepare the list of files to send
            files_to_send = [ship]


        # Prepare the text response
        text = "use the /help command for more info\n"
        if(data_returned['author']!=""):
            text += f"Made by: {data_returned['author']}\n"
        text += f"Center of mass: {round(data_returned['center_of_mass_x'], 2)}, {round(data_returned['center_of_mass_y'], 2)}\n"
        text += f"Total mass: {round(data_returned['total_mass'], 2)}t\n"
        text += f"Predicted max speed: {round(data_returned['top_speed'], 2)}m/s\n"
        text += f"Total crew: {data_returned['crew']}\n"
        text += f"Aprox cost: {data_returned['price']:,}\n"

        # Send the text response and files
        print(dt.now(),"sending to discord")
        await interaction.followup.send(text, files=files_to_send)
        print(dt.now(),"sent to discord")

    except Exception as e:
        print(dt.now(),"error",e)
        text = "Error: could not process ship :\n\t"+str(e)
        await interaction.followup.send(text, file=ship)
        return "Error: could not process ship"

@tree.command(name="cost", description="Calculates cost analysis of a cosmoteer ship.png")
async def com(interaction: discord.Interaction, ship: discord.Attachment):

    
    print(dt.now(),"received command")
    await interaction.response.defer()
    print(dt.now(),"deferred")

    # Read the image bytes and encode them to base64
    image_bytes = await ship.read()
    base64_string = base64.b64encode(image_bytes).decode('utf-8')

    # Create a file object for the original image
    ship = discord.File(BytesIO(image_bytes), filename="input_file.png")

    try:
        # Prepare the request data
        args = {
            "boost": False,
            "draw_all_cot": False,
            "draw_all_com": False,
            "draw_cot": False,
            "draw_com": False,
            "draw": False,
            "flip_vectors": False,
            "analysis" : True
        }
        json_data = json.dumps({'image': base64_string, 'args': args})

        # Send the request to the server
        url = API_URL
        print(dt.now(),"requesting data")
        response = requests.post(url, json=json_data)
        response.raise_for_status()
        print(dt.now(),"server responded")
        

        # Get the response
        data_returned = response.json()
        # if draw is false do not retrieve the center of mass image
        # Get the URL of the center of mass image
        print(data_returned)
        url_stats = data_returned["analysis"]["url_analysis"]
        # Fetch the center of mass image
        print(dt.now(),"requesting image")
        response_url_stats = requests.get(url_stats)
        response_url_stats.raise_for_status()
        content_response = response_url_stats.content
        print(dt.now(),"server responded")

        # Create a file object for the center of mass image
        picture = discord.File(BytesIO(content_response), filename="output_file.png")
        
        # Prepare the list of files to send
        files_to_send = [ship, picture]

        """
        {"url_com": false, "center_of_mass_x": -0.481210071401729, "center_of_mass_y": 5.3820744081172505, "total_mass": 266.09999999999997, "top_speed": 0.0, "crew": 62, "price": 287760, "tags": ["chaingun", "small_reactor"], "author": "kine", "all_direction_speeds": {"NW": 0.0, "N": 0.0, "NE": 0.0, "E": 0.0, "SE": 0.0, "S": 0.0, "SW": 0.0, "W": 0.0}, "analysis": {"url_analysis": "https://i.ibb.co/P1YCgm7/c63c50987278.png", "total_price": {"price": 287760, "percent": 1}, "price_crew": {"price": 43600, "percent": 0.15151515151515152}, "price_weapons": {"price": 175800, "percent": 0.6109257714762302}, "price_armor": {"price": 0, "percent": 0.0}, "price_mouvement": {"price": 0, "percent": 0.0}, "price_power": {"price": 25000, "percent": 0.08687795385043091}, "price_shield": {"price": 0, "percent": 0.0}, "price_storage": {"price": 27360, "percent": 0.0950792326939116}}}
        """

        # prepare data
        total_price = data_returned["analysis"]["total_price"]["price"]
        price_crew = data_returned["analysis"]["price_crew"]["price"]
        price_armor = data_returned["analysis"]["price_armor"]["price"]
        price_weapons = data_returned["analysis"]["price_weapons"]["price"]
        price_mouvement = data_returned["analysis"]["price_mouvement"]["price"]
        price_shield = data_returned["analysis"]["price_shield"]["price"]
        price_storage = data_returned["analysis"]["price_storage"]["price"]
        price_utility = data_returned["analysis"]["price_utility"]["price"]
        price_power = data_returned["analysis"]["price_power"]["price"]
        percent_crew = data_returned["analysis"]["price_crew"]["percent"]
        percent_armor = data_returned["analysis"]["price_armor"]["percent"]
        percent_weapons = data_returned["analysis"]["price_weapons"]["percent"]
        percent_mouvement = data_returned["analysis"]["price_mouvement"]["percent"]
        percent_shield = data_returned["analysis"]["price_shield"]["percent"]
        percent_storage = data_returned["analysis"]["price_storage"]["percent"]
        percent_utility = data_returned["analysis"]["price_utility"]["percent"]
        percent_power = data_returned["analysis"]["price_power"]["percent"]
        
        # Prepare the text response
        text = "use the /help command for more info\n"
        text += f"Total price: {total_price}\n"
        text += f"Crew price: {price_crew} | {percent_crew}%\n"
        text += f"Armor price: {price_armor} | {percent_armor}%\n"
        text += f"Weapons price: {price_weapons} | {percent_weapons}%\n"
        text += f"Movement price: {price_mouvement} | {percent_mouvement}%\n"
        text += f"Shield price: {price_shield} | {percent_shield}%\n"
        text += f"Storage price: {price_storage} | {percent_storage}%\n"
        text += f"Utility price: {price_utility} | {percent_utility}%\n"
        text += f"Power price: {price_power} | {percent_power}%\n"

        # Send the text response and files
        print(dt.now(),"sending to discord")
        await interaction.followup.send(text, files=files_to_send)
        print(dt.now(),"sent to discord")

    except Exception as e:
        print(dt.now(),"error",e)
        text = "Error: could not process ship :\n\t"+str(e)
        await interaction.followup.send(text, file=ship)
        return "Error: could not process ship"

@tree.command(name="ping", description="responds with the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('Pong! {0}ms'.format(round(client.latency*1000)))

@tree.command(name="help", description="shows the list of commands")
async def help(interaction: discord.Interaction):
    """
    Responds to a help command and sends a list of commands.

    Parameters:
        interaction (discord.Interaction): The interaction triggered by the user.

    Returns:
        None
    """
    print(dt.now(),"help command received")
    # Defer the initial response to prevent timeouts
    await interaction.response.defer()
    
    # Generate the legend image for the command
    #center_of_mass.draw_legend("legend.png")
    
    # Send the help text along with the legend image as a file
    await interaction.followup.send(help_text, file=discord.File("legend.png"))
    print(dt.now(),"help command sent")

#client.run(os.getenv("DISCORDBOTAPI"))
client.run(secret_token.token)
