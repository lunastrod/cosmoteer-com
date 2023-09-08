import discord
from discord import app_commands
# import secret_token
from dotenv import load_dotenv
import os
import center_of_mass
import base64
from io import BytesIO

load_dotenv()

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
async def com(interaction: discord.Interaction, ship: discord.Attachment, boost: bool = True, strafecot: bool = True, partcom: bool = False):
    # Defer the initial response to let the user know the command is being processed
    await interaction.response.defer()

    # Read the image bytes from the attachment
    image_bytes = await ship.read()

    # Encode the image bytes in base64 format
    base64_string = base64.b64encode(image_bytes).decode('utf-8')

    try:
        # Prepare the arguments for the center_of_mass calculation
        args = {"boost": boost, "draw_all_cot": strafecot, "draw_all_com": partcom, "draw_cot": True, "draw_com": True}

        # Call the center_of_mass function with the base64 string and the arguments
        data_com, data_cot, speed, error_msg, base64_output = center_of_mass.com(base64_string, "", args)
    except Exception as e:
        # Print the error message and return if an exception occurs
        print(e)
        print("Error: could not process ship")
        return "Error: could not process ship"

    # Decode the base64 output into bytes
    decoded_bytes = base64.b64decode(base64_output)

    # Create a BytesIO stream for the output file
    file_stream = BytesIO(decoded_bytes)

    # Create a BytesIO stream for the input file
    file_stream_in = BytesIO(image_bytes)

    # Create discord.File objects for the output and input files
    picture = discord.File(file_stream, filename="output_file.png")
    ship = discord.File(file_stream_in, filename="input_file.png")
    
    # Prepare the list of files to send in the response
    files_to_send = [ship, picture]
    
    # Prepare the text response
    text = ""
    text += error_msg
    text += "use the /help command for more info\n"
    text += "Center of mass: " + str(round(data_com[0], 2)) + ", " + str(round(data_com[1], 2)) + "\n"
    text += "Total mass: " + str(round(data_com[2], 2)) + "t\n"
    text += "Predicted max speed: " + str(round(speed, 2)) + "m/s\n"

    # Send the response with the text and files
    await interaction.followup.send(text, files=files_to_send)
        


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
    center_of_mass.draw_legend("legend.png")
    
    # Send the help text along with the legend image as a file
    await interaction.followup.send(help_text, file=discord.File("legend.png"))

client.run(os.getenv("DISCORDBOTAPI"))