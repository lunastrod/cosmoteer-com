"""
# This is new in the discord.py 2.0 update, example code for slash commands

# imports
import discord
import discord.ext

# setting up the bot
intents = discord.Intents.all() 
# if you don't want all intents you can do discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# sync the slash command to your server
@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=Your guild ID here))
    # print "ready" in the console when the bot is ready to work
    print("ready")

# make the slash command
@tree.command(name="name", description="description")
async def slash_command(interaction: discord.Interaction):    
    await interaction.response.send_message("command")

# run the bot
client.run("token")
"""
#convert this code to slash commands
"""
import discord
from discord.ext import commands
import secret_token
import center_of_mass

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!!', intents=intents)

version_text="Made by LunastroD, Aug 2023, for the Excelsior discord server and the awesome Cosmoteer community :3\nCheck out the source code at https://github.com/lunastrod/cosmoteer-com"
short_version_text="Made by LunastroD, Aug 2023"

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Cosmoteer (!!help)"))
    #print guilds
    print("Guilds:")
    for guild in bot.guilds:
        print("\t" + guild.name, guild.id)
    print("Bot is ready")

@bot.command(brief='Calculates the center of mass of cosmoteer ships', description='Calculates the center of mass of cosmoteer ships.\nInstructions:\n\t-send a ship.png\n\t-the center of mass of your ship will be drawn as a green circle\n\t-you can send multiple ships on the same message\n\t-this tool is only a good aproximation of the com, total mass might be a bit off too') #calculate center of mass
async def com(ctx):
    if len(ctx.message.attachments) == 0:
        await ctx.send("No ships detected")
    if len(ctx.message.attachments) > 10:
        await ctx.send("Too many ships at once")
    for attachment in ctx.message.attachments:
        await attachment.save('discord_bot\ship.ship.png')
        try:
            data=center_of_mass.com("discord_bot\ship.ship.png", "discord_bot\out.png")
        except:
            await ctx.send("Error: could not process ship")
            continue
        with open('discord_bot\out.png', 'rb') as f:
            picture = discord.File(f)
            text="Center of mass: " + str(round(data[0],2)) + ", " + str(round(data[1],2)) + "\nTotal mass: " + str(round(data[2],2)) + "t"
            await ctx.send(text,file=picture)

@bot.command(brief=short_version_text, description=version_text)
async def version(ctx):
    await ctx.send(version_text)

bot.run(secret_token.token)
"""

#SLASH COMMANDS:

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
    #sync slash commands
    print("Guilds:")
    await tree.sync()
    #print guilds
    #for guild in tree.guilds:
        #print("\t" + guild.name, guild.id)
    print("Bot is ready")

@tree.command(name="com", description="Calculates the center of mass of a cosmoteer ship.png")
async def com(interaction: discord.Interaction):
    if len(interaction.message.attachments) == 0:
        await interaction.response.send_message("No ships detected")
    if len(interaction.message.attachments) > 10:
        await interaction.response.send_message("Too many ships at once")
    for attachment in interaction.message.attachments:
        await attachment.save('discord_bot\ship.ship.png')
        try:
            data=center_of_mass.com("discord_bot\ship.ship.png", "discord_bot\out.png")
        except:
            await interaction.response.send_message("Error: could not process ship")
            continue
        with open('discord_bot\out.png', 'rb') as f:
            picture = discord.File(f)
            text="Center of mass: " + str(round(data[0],2)) + ", " + str(round(data[1],2)) + "\nTotal mass: " + str(round(data[2],2)) + "t"
            await interaction.response.send_message(text,file=picture)

@tree.command(name="version", description=short_version_text)
async def version(interaction: discord.Interaction):
    await interaction.response.send_message(version_text)

client.run(secret_token.token)