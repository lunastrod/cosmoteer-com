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
import random

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

/com: Calculates both the center of mass and the cost analysis of a cosmoteer ship.png
parameters:
- ship: the .ship.png file of the ship. Usually found in C:\\Users\\YOUR USERNAME\\Saved Games\\Cosmoteer\\YOUR STEAM ID\\Saved Ships
- flipvectors: flips the thrust vectors to avoid overlap. Default: off
- draw_all_cot: draws the center of thrust vectors on every direction instead of only fordwards. Default: on
- draw_all_com: draws the center of mass of each part. Default: off

/compare: Compare two ships submitted to "cosmoteer ship library" <https://cosmo-lilac.vercel.app/>
parameters:
- ship1: contains the first ship id. Ship ids are usually found in the website url when selected
- ship2: contains the second ship id.

common questions:
does the bot consider the lateral thrust of each thruster? yes
the bot doesn't work with modded parts, rocket thrusters, medium/big hyperdrives or any newer parts
"""

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
async def com(interaction: discord.Interaction, ship: discord.Attachment, boost: bool = True, flip_vectors: bool = False, draw_all_cot: bool = True, draw_all_com: bool = False):
    command = tree.get_command('full')
    await command.callback(interaction, ship, boost, flip_vectors, draw_all_cot, draw_all_com)


@tree.command(name="cost", description="Calculates the cost analysis of a cosmoteer ship.png")
async def cost(interaction: discord.Interaction, ship: discord.Attachment, boost: bool = True, flip_vectors: bool = False, draw_all_cot: bool = True, draw_all_com: bool = False):
    command = tree.get_command('full')
    await command.callback(interaction, ship, boost, flip_vectors, draw_all_cot, draw_all_com)


@tree.command(name="full", description="Calculates the center of mass and cost analysis of a cosmoteer ship.png")
async def full(interaction: discord.Interaction, ship: discord.Attachment, boost: bool = True, flip_vectors: bool = False, draw_all_cot: bool = True, draw_all_com: bool = False):
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
            "flip_vectors": flip_vectors,
            "analyze" : True
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
        # Get the URL of the center of mass image
        url_com = data_returned['url_com']
        # prepare the data
        center_of_mass_x = round(data_returned['center_of_mass_x'], 2)
        center_of_mass_y = round(data_returned['center_of_mass_y'], 2)
        total_mass = round(data_returned['total_mass'], 2)
        top_speed = round(data_returned['top_speed'], 2)
        crew = data_returned['crew']
        price = data_returned['price']
        made_by = data_returned['author']
        # convert the data
        data_converted = {
            "Center of mass": f"{center_of_mass_x}, {center_of_mass_y}",
            "Total mass": total_mass,
            "Max speed": f"{top_speed} m/s",
            "Total crew": crew,
            "Aprox cost": price,
            "Made by": made_by,
        }
        
        text = "use the /help command for more info\n"

        categoriescom = ["Center of mass", "Total mass", "Max speed", "Total crew", "Aprox cost"]
        if(data_returned['author']!=""):
            categoriescom += ["Made by"]
        embedcom = discord.Embed(
            title="Center of mass analysis",
            color=discord.Color.green()
        )
        # Create a formatted table header with consistent column widths
        table_headercom =  "Category        | Data         \n"
        table_headercom += "----------------|--------------\n"
        # Create a formatted table body with each category's data
        table_bodycom = ""
        for category in categoriescom:
            data = data_converted[category]
            # Format each column with padding to ensure consistent width
            category_formatted = f"{category:<15}"
            data_formatted = f"{data:>15}"
            table_bodycom += f"{category_formatted} | {data_formatted}\n"
        # Combine the header and body to form the table
        tablecom = f"```\n{table_headercom}{table_bodycom}```"
        # Add the table to the Discord embed
        embedcom.add_field(name="\u200b", value=tablecom, inline=False)  # "\u200b" is a zero-width space for better formatting
        
        url_stats = data_returned["analysis"]["url_analysis"]
        analysis = data_returned["analysis"]
        categories = ["total_price", "price_crew", "price_armor", "price_weapons", "price_mouvement", 
                        "price_shield", "price_storage", "price_utility", "price_power"]
        text_categories={"total_price":"total", "price_crew":"crew", "price_armor":"armor",
                         "price_weapons":"weapons", "price_mouvement":"thrust", "price_shield":"shield",
                         "price_storage":"storage", "price_utility":"misc", "price_power":"power"}
        embed = discord.Embed(
            title="Price analysis",
            color=discord.Color.green()
        )
        # Create a formatted table header with consistent column widths
        table_header =  "Category  | Percent | Price\n"
        table_header += "----------|---------|----------\n"
        # Create a formatted table body with each category's data
        table_body = ""
        for category in categories:
            percent = f"{analysis[category]['percent']*100:.2f}%"
            price = analysis[category]["price"]
            # Format each column with padding to ensure consistent width
            category_formatted = f"{text_categories[category]:<9}"
            percent_formatted = f"{percent:>7}"
            price_formatted = f"{price:>8}"
            table_body += f"{category_formatted} | {percent_formatted} | {price_formatted}\n"
        # Combine the header and body to form the table
        table = f"```\n{table_header}{table_body}```"
        # Add the table to the Discord embed
        embed.add_field(name="\u200b", value=table, inline=False)  # "\u200b" is a zero-width space for better formatting
        print(dt.now(), "sending to Discord")
        # Create an Embed for the Center of Mass image
        embedcom.set_image(url=url_com)
        # Create an Embed for the Stats image
        embed.set_image(url=url_stats)
        embeds = [embedcom, embed]
        await interaction.followup.send(text, embeds=embeds, files=[ship])
        print(dt.now(), "sent to Discord")
    except Exception as e:
        print(dt.now(),"error",e)
        text = "Error: could not process ship :\n\t" + type(e).__name__ + ":" + str(e)
        await interaction.followup.send(text, file=ship)
        return "Error: could not process ship"

@tree.command(name="compare", description="Compares two ships (id1 and id2)")
async def compare(interaction: discord.Interaction, ship1: int, ship2: int, scale: bool = False):
    print(dt.now(),"received command")
    await interaction.response.defer()
    print(dt.now(),"deferred")
    url = 'https://cosmo-api-six.vercel.app/compare?ship1=' + str(ship1) + '&ship2=' + str(ship2) + '&scale=' + str(scale)
    print(dt.now(),"requesting data")
    response = requests.get(url)
    response.raise_for_status()
    print(dt.now(),"server responded")
    # Get the response
    data_returned = response.json()

    # ship 1 url and name
    urlship1 = data_returned["urlship1"]
    shipname1 = data_returned["shipname1"]
    embed1 = discord.Embed(
        title="Ship1 : " + str(shipname1),
        url="https://cosmo-lilac.vercel.app/ship/"+str(ship1),
        color=discord.Color.green()
    )
    embed1.set_image(url=urlship1)
    # ship 2 url and name
    urlship2 = data_returned["urlship2"]
    shipname2 = data_returned["shipname2"]
    embed2 = discord.Embed(
        title="Ship2 : " + str(shipname2),
        url="https://cosmo-lilac.vercel.app/ship/"+str(ship2),
        color=discord.Color.green()
    )
    embed2.set_image(url=urlship2)
 
    # Get the URL of the chart
    url_stats = data_returned["url_analysis"]
    analysis = data_returned
    embed = discord.Embed(
        title="Price analysis for ships " + str(ship1) + " and " + str(ship2),
        color=discord.Color.green()
    )
    # Create a formatted table header with consistent column widths
    table_header =  "Category | Ship1(%)| Ship2(%)\n"
    table_header += "---------|---------|----------\n"
    # Create a formatted table body with each category's data
    table_body = ""
    total1 = f"{analysis['total_price1']['percent']*100:.2f}%"
    total2 = f"{analysis['total_price2']['percent']*100:.2f}%"
    table_body += f"total    | {total1:>7} | {total2:>7}\n"
    price_crew1 = f"{analysis['price_crew1']['percent']*100:.2f}%"
    price_crew2 = f"{analysis['price_crew2']['percent']*100:.2f}%"
    table_body += f"crew     | {price_crew1:>7} | {price_crew2}\n"
    price_armor1 = f"{analysis['price_armor1']['percent']*100:.2f}%"
    price_armor2 = f"{analysis['price_armor2']['percent']*100:.2f}%"
    table_body += f"armor    | {price_armor1:>7} | {price_armor2:>7}\n"
    price_weapons1 = f"{analysis['price_weapons1']['percent']*100:.2f}%"
    price_weapons2 = f"{analysis['price_weapons2']['percent']*100:.2f}%"
    table_body += f"weapons  | {price_weapons1:>7} | {price_weapons2:>7}\n"
    price_mouvement1 = f"{analysis['price_mouvement1']['percent']*100:.2f}%"
    price_mouvement2 = f"{analysis['price_mouvement2']['percent']*100:.2f}%"
    table_body += f"thrust   | {price_mouvement1:>7} | {price_mouvement2:>7}\n"
    price_shield1 = f"{analysis['price_shield1']['percent']*100:.2f}%"
    price_shield2 = f"{analysis['price_shield2']['percent']*100:.2f}%"
    table_body += f"shield   | {price_shield1:>7} | {price_shield2:>7}\n"
    price_storage1 = f"{analysis['price_storage1']['percent']*100:.2f}%"
    price_storage2 = f"{analysis['price_storage2']['percent']*100:.2f}%"
    table_body += f"storage  | {price_storage1:>7} | {price_storage2:>7}\n"
    price_utility1 = f"{analysis['price_utility1']['percent']*100:.2f}%"
    price_utility2 = f"{analysis['price_utility2']['percent']*100:.2f}%"
    table_body += f"misc     | {price_utility1:>7} | {price_utility2:>7}\n"
    price_power1 = f"{analysis['price_power1']['percent']*100:.2f}%"
    price_power2 = f"{analysis['price_power2']['percent']*100:.2f}%"
    table_body += f"power    | {price_power1:>7} | {price_power2:>7}\n"
    
    # Combine the header and body to form the table
    table = f"```\n{table_header}{table_body}```"
    # Add the table to the Discord embed
    embed.add_field(name="\u200b", value=table, inline=False)  # "\u200b" is a zero-width space for better formatting
    print(dt.now(), "sending to Discord")
    # Create an Embed for the Stats image
    embed.set_image(url=url_stats)
    embeds = [embed1, embed2, embed]
    await interaction.followup.send(embeds=embeds)
    print(dt.now(), "sent to Discord")

@tree.command(name="ping", description="responds with the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('Pong! {0}ms'.format(round(client.latency*1000)))

@tree.command(name="hmmm", description="responds with hmmm")
async def ping(interaction: discord.Interaction):
    if(random.random()<0.05):
        await interaction.response.send_message("oh no, not again, please no, not the hmmm, anything but the hmmm, please")
    else:
        await interaction.response.send_message("hmmm")

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
