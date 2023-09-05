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
    await client.change_presence(activity=discord.Game(name="Cosmoteer (/help)"))
    print("Syncing slash commands")
    await tree.sync()
    print("Guilds:")
    for guild in client.guilds:
        print("\t- " + guild.name, guild.id)
    print("Bot is ready")

@tree.command(name="com", description="Calculates the center of mass of a cosmoteer ship.png")
async def com(interaction: discord.Interaction, ship: discord.Attachment):
    print("defer")
    await interaction.response.defer()
    print("deferred, saving")
    await ship.save('discord_bot\ship.ship.png')
    print("saved, calculating")
    try:
        data_com, data_cot, speed=center_of_mass.com("discord_bot\ship.ship.png", "discord_bot\out.png")#calculate the center of mass
    except:
        await interaction.followup.send("Error: could not process ship",file=discord.File("discord_bot\ship.ship.png"))
        return
    print("calculated, sending")
    with open('discord_bot\out.png', 'rb') as f, open("discord_bot\ship.ship.png", "rb") as s:#send the output image
        picture = discord.File(f)
        ship = discord.File(s)
        files_to_send: list[discord.File] = [ship,picture]
        text="use the /help command for more info\n"
        text+="Center of mass: " + str(round(data_com[0],2)) + ", " + str(round(data_com[1],2)) + "\n"
        text+="Total mass: " + str(round(data_com[2],2)) + "t\n"
        text+="Predicted max speed: " + str(round(speed,2)) + "m/s\n"
        
        await asyncio.sleep(3)
        await interaction.followup.send(text,files=files_to_send)
        


@tree.command(name="version", description=short_version_text)
async def version(interaction: discord.Interaction):
    await interaction.response.send_message(version_text)

@tree.command(name="help", description="shows the list of commands")
async def help(interaction: discord.Interaction):
    await interaction.response.defer()
    center_of_mass.draw_legend("legend.png")
    await interaction.followup.send(help_text,file=discord.File("legend.png"))

client.run(secret_token.token)