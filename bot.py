import discord
from discord import app_commands
import secret_token
import center_of_mass

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

version_text="Made by LunastroD, Aug 2023, for the Excelsior discord server and the awesome Cosmoteer community :3\nCheck out the source code at https://github.com/lunastrod/cosmoteer-com"
short_version_text="Made by LunastroD, Aug 2023"

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Cosmoteer (!!help)"))
    print("Syncing slash commands")
    await tree.sync()
    print("Guilds:")
    for guild in tree.guilds:
        print("\t" + guild.name, guild.id)
    print("Bot is ready")

@tree.command(name="com", description="Calculates the center of mass of a cosmoteer ship.png")
async def com(interaction: discord.Interaction, ship: discord.Attachment):
    await ship.save('discord_bot\ship.ship.png')
    try:
        data=center_of_mass.com("discord_bot\ship.ship.png", "discord_bot\out.png")#calculate the center of mass
    except:
        await interaction.response.send_message("Error: could not process ship")
        return
    with open('discord_bot\out.png', 'rb') as f:#send the output image
        picture = discord.File(f)
        text="Center of mass: " + str(round(data[0],2)) + ", " + str(round(data[1],2)) + "\nTotal mass: " + str(round(data[2],2)) + "t"
        await interaction.response.send_message(text,file=picture)

@tree.command(name="version", description=short_version_text)
async def version(interaction: discord.Interaction):
    await interaction.response.send_message(version_text)

client.run(secret_token.token)