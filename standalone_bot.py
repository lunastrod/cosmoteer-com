import discord
from discord import app_commands
import secret_token
import center_of_mass
import asyncio

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

short_version_text="Made by LunastroD, Aug 2023 - Sep 2023"
version_text=short_version_text+", for the Excelsior discord server and the Cosmoteer community :3\n    -Check out the source code at <https://github.com/lunastrod/cosmoteer-com>"
help_text="""/version: """+version_text+"""

/help: Shows this message

/com: Calculates the center of mass of a cosmoteer ship.png
- parameters:
 - ship: the .ship.png file of the ship. Usually found in C:\\Users\\UR USERNAME\\Saved Games\\Cosmoteer\\UR STEAM ID\\Saved Ships
 - boost: turns boosters on or off. Default: on
 - flipvectors: flips the thrust vectors to avoid overlap. Default: off
 - strafecot: draws the center of thrust vectors on every direction instead of only fordwards. Default: on
 - partcom: draws the center of mass of each part. Default: off

- common questions:
 - does the bot consider the 5% lateral thrust of each thruster? yes
 - does the bot consider engine room buff? yes
 - is the cot exact? it should be
 - is the com exact? no, it's a decent approximation, it should be inside the green circle
 - is the max speed exact? no, it's an approximation, assume ±1%, and it assumes your ship is balanced

- If you notice any mistakes on things like the total mass or the speed, ping LunastroD"""

db_help_text = f"""/version: """+version_text+"""

The Cosmoteer Design Tools bot has a database of every known multiplayer elimination archetype and their matchups that can be contributed to by anybody.
Below is a list of commands that are used to access and contribute to the database.

/help: Shows this message

/db_list_ships: Lists every single ship type in the bot's archetype database. A handy reference for other db commands.

/db_add_ships: Adds a new ship to the database.

/db_rename_ship: Changes the existing name of a ship to a different specified one.

/db_scoreboard: Shows the win/loss/draw ratio for each ship in the database based on matchups.

/db_get_matchups: Lists each matchup (win, loss, draw) of a specified ship from the database.

/db_get_unknown_matchups: Lists each matchup that has no votes from a specified ship from the database.

/db_add_fight: Add a new matchup between 2 specified ship in the database.

/db_remove_fight: Removes a matchup between 2 specified ship in the database.

/db_simulate_fight: Simulates a fight between 2 specified ship, based on the listed matchup in the database.

/db_export_csv: Exports the entire database to a .csv file.
"""

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Cosmoteer (/help)"))
    print("Syncing slash commands")
    await tree.sync()
    print("Guilds:")
    for guild in client.guilds:
        print("\t- " + guild.name, guild.id)
    print("Bot is ready")

@tree.command(name="com", description="Calculates the center of mass of a cosmoteer ship.png")
async def com(interaction: discord.Interaction, ship: discord.Attachment, boost: bool = True, flipvectors: bool = False, strafecot: bool = True, partcom: bool = False):
    print("defer")
    await interaction.response.defer()
    print("deferred, saving")
    await ship.save('discord_bot/ship.ship.png')
    #copy legend.png to out.png
    with open('legend.png', 'rb') as f, open("discord_bot/out.png", "wb") as s:
        s.write(f.read())
    print("saved, calculating")
    try:
        args={"boost":boost,"draw_all_cot":strafecot,"draw_all_com":partcom,"draw_cot":True,"draw_com":True,"flip_vectors":flipvectors}
        data_com, data_cot, speed, error_msg=center_of_mass.com("discord_bot/ship.ship.png", "discord_bot/out.png",args)#calculate the center of mass
    except:
        await interaction.followup.send("Error: could not process ship",file=discord.File("discord_bot/ship.ship.png"))
        return
    print("calculated, sending")
    with open('discord_bot/out.png', 'rb') as f, open("discord_bot/ship.ship.png", "rb") as s:#send the output image
        picture = discord.File(f)
        ship = discord.File(s)
        files_to_send: list[discord.File] = [ship,picture]
        text=""
        text+=error_msg
        text+="use the /help command for more info\n"
        text+="Center of mass: " + str(round(data_com[0],2)) + ", " + str(round(data_com[1],2)) + "\n"
        text+="Total mass: " + str(round(data_com[2],2)) + "t\n"
        text+="Predicted max speed: " + str(round(speed,2)) + "m/s\n"

        
        await asyncio.sleep(3)
        await interaction.followup.send(text,files=files_to_send)
        print(text)
        print("sent")
        


@tree.command(name="version", description=short_version_text)
async def version(interaction: discord.Interaction):
    await interaction.response.send_message(version_text)

@tree.command(name="help", description="shows the list of commands")
async def help(interaction: discord.Interaction, list_database_commands: bool = False):
    if not list_database_commands == True:
        await interaction.response.defer()
        center_of_mass.draw_legend("legend.png")
        await interaction.followup.send(help_text,file=discord.File("legend.png"))
    else:
        await interaction.response.send_message(db_help_text)

client.run(secret_token.token)