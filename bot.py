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

#load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

short_version_text="Made by LunastroD, Aug 2023 - Sep 2023"
version_text=short_version_text+", for the Excelsior discord server and the Cosmoteer community :3\n    -Check out the source code at <https://github.com/lunastrod/cosmoteer-com>"
help_text="""
/com: Calculates the center of mass of a cosmoteer ship.png

/version: """+version_text+"""

/help: Shows this message

common questions:
- does the bot consider the 5% lateral thrust? yes
- does the bot consider engine room buff? yes
- is the cot exact? it should be
- is the com exact? no, it's a decent approximation, it should be inside the green circle
- is the max speed exact? no, it's an approximation, assume ±1%, and it assumes your ship is balanced
- are boosters on or off for the calculation of the cot? they are on

- If you notice any mistakes on things like the total mass or the speed, ping me
"""

@client.event
async def on_ready():
    """
    Event handler that is called when the bot is ready to start receiving events.
    """
    # Set the bot's presence to the specified game
    await client.change_presence(activity=discord.Game(name="Cosmoteer (/help)"))
    
    # Print a message indicating that the slash commands are being synced
    print("Syncing slash commands")
    
    # Sync the slash commands with the Discord API
    await tree.sync()
    
    # Print a list of guilds that the bot is connected to
    print("Guilds:")
    for guild in client.guilds:
        print("\t- " + guild.name, guild.id)
    
    # Print a message indicating that the bot is ready
    print("Bot is ready")

@tree.command(name="com", description="Calculates the center of mass of a cosmoteer ship.png")
async def com(interaction: discord.Interaction, ship: discord.Attachment, boost: bool = True, draw_all_cot: bool = True, draw_all_com: bool = False, draw_cot: bool = True, draw_com: bool = True, draw: bool = True):
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
    
    await interaction.response.defer()

    # Read the image bytes and encode them to base64
    image_bytes = await ship.read()
    base64_string = base64.b64encode(image_bytes).decode('utf-8')

    try:
        # Prepare the request data
        args = {
            "boost": boost,
            "draw_all_cot": draw_all_cot,
            "draw_all_com": draw_all_com,
            "draw_cot": draw_cot,
            "draw_com": draw_com,
            "draw": draw
        }
        json_data = json.dumps({'image': base64_string, 'args': args})

        # Send the request to the server
        url = 'https://cosmo-api-six.vercel.app/analyze'
        response = requests.post(url, json=json_data)
        response.raise_for_status()
        
        # Create a file object for the original image
        ship = discord.File(BytesIO(image_bytes), filename="input_file.png")

        # Get the response
        data_returned = response.json()
        # if draw is false do not retrieve the center of mass image
        if draw == True:
            # Get the URL of the center of mass image
            
            url_com = data_returned['url_com']

            # Fetch the center of mass image
            response_url_com = requests.get(url_com)
            response_url_com.raise_for_status()
            content_response = response_url_com.content

            # Create a file object for the center of mass image
            picture = discord.File(BytesIO(content_response), filename="output_file.png")
            
            # Prepare the list of files to send
            files_to_send = [ship, picture]
        else:
            # Prepare the list of files to send
            files_to_send = [ship]


        # Prepare the text response
        text = "use the /help command for more info\n"
        text += f"Center of mass: {round(data_returned['center_of_mass_x'], 2)}, {round(data_returned['center_of_mass_y'], 2)}\n"
        text += f"Total mass: {round(data_returned['total_mass'], 2)}t\n"
        text += f"Predicted max speed: {round(data_returned['top_speed'], 2)}m/s\n"

        # Send the text response and files
        await interaction.followup.send(text, files=files_to_send)

    except requests.exceptions.RequestException as e:
        print(e)
        text = "Error: could not process ship :"+str(e)
        await interaction.followup.send(text, files=files_to_send)
        return "Error: could not process ship"
        


@tree.command(name="version", description=short_version_text)
async def version(interaction: discord.Interaction):
    """
    Command to display the version of the tree.

    Parameters:
        interaction (discord.Interaction): The interaction object representing the user's command.

    Returns:
        None
    """
    await interaction.response.send_message(version_text)

@tree.command(name="help", description="shows the list of commands")
async def help(interaction: discord.Interaction):
    """
    Responds to a help command and sends a list of commands.

    Parameters:
        interaction (discord.Interaction): The interaction triggered by the user.

    Returns:
        None
    """
    # Defer the initial response to prevent timeouts
    await interaction.response.defer()
    
    # Generate the legend image for the command
    #center_of_mass.draw_legend("legend.png")
    
    # Send the help text along with the legend image as a file
    await interaction.followup.send(help_text, file=discord.File("legend.png"))

#client.run(os.getenv("DISCORDBOTAPI"))
client.run(secret_token.token)