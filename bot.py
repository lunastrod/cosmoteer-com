import discord
import secret_token
from discord.ext import commands
import center_of_mass

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!!', intents=intents)

version_text="Made by LunastroD, Aug 2023, for the Excelsior discord server and the awesome Cosmoteer community :3\nCheck out the source code at https://github.com/lunastrod/cosmoteer-com"
short_version_text="Made by LunastroD, Aug 2023"

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Cosmoteer (!!help)"))

@bot.command(brief='Calculates the center of mass of cosmoteer ships', description='Calculates the center of mass of cosmoteer ships.\nInstructions:\n\t-send a ship.png\n\t-the center of mass of your ship will be drawn as a green circle\n\t-you can send multiple ships on the same message\n\t-this tool is only a good aproximation of the com, total mass might be a bit off too') #calculate center of mass
async def com(ctx):
    if len(ctx.message.attachments) == 0:
        await ctx.send("No ships detected")
    if len(ctx.message.attachments) > 10:
        await ctx.send("Too many ships at once")
    for attachment in ctx.message.attachments:
        await attachment.save('discord_bot\ship.ship.png')
        data=center_of_mass.com("discord_bot\ship.ship.png", "discord_bot\out.png")
        with open('discord_bot\out.png', 'rb') as f:
            picture = discord.File(f)
            text="Center of mass: " + str(round(data[0],2)) + ", " + str(round(data[1],2)) + "\nTotal mass: " + str(round(data[2],2)) + "t"
            await ctx.send(text,file=picture)

@bot.command(brief=short_version_text, description=version_text)
async def version(ctx):
    await ctx.send(version_text)

bot.run(secret_token.token)