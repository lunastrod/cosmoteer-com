import discord
from discord import app_commands
import secret_token

import fight_db
import data_analysis

import base64
from io import BytesIO
import requests
import json
import random
import traceback

from datetime import datetime as dt


API_URL = "https://cosmo-api-six.vercel.app/"
API_NEW = "https://api.cosmoship.duckdns.org/"

BOT_PATH = "/home/astrod/Desktop/Bots/cosmoteer-com/"
db = fight_db.FightDB(db_name=BOT_PATH+"test.db")


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

short_version_text="Made by LunastroD, Aug 2023 - Sep 2023"
version_text=short_version_text+", for the Excelsior discord server and the Cosmoteer community :3\n- Check out the source code at <https://github.com/lunastrod/cosmoteer-com>\n- Thanks to Poney, CoconutTrebuchet, Plaus and jun(0) for their help"
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
the bot considers the lateral thrust of each thruster
the bot doesn't work with modded parts
"""

db_help_text = f""+version_text+"""

The Cosmoteer Design Tools bot has a database of every known multiplayer elimination archetype and their matchups that can be contributed to by anybody.
Below is a list of commands that are used to access and contribute to the database.

**/help:** Shows this message.

**/db_list_ships:** Lists every single ship type in the bot's archetype database. A handy reference for other db commands.

**/db_draw_archetype_tree:** Draws the family tree of archetypes.

**/db_add_ship:** Adds a new ship to the database. Also generates a backup before execution.

**/db_rename_ship:** Changes the existing name, parents name or description of a ship to a different specified one. Also generates a backup before execution. Only LunastroD or Plaus can use this command.

**/db_scoreboard:** Shows the win/loss/draw ratio for each ship in the database based on matchups. The optional "playername" parameter can be used to only show the scoreboard for a certain player.

**/db_get_matchups:** Lists each matchup (win, loss, draw) of a specified ship from the database. The optional "playername" parameter can be used to only show the matchups a certain player submitted. 

**/db_get_unknown_matchups:** Lists each matchup that has no votes from a specified ship from the database. The optional "playername" parameter can be used to only show the unknown matchups for a certain player.

**/db_add_fight:** Add a new matchup between 2 or more specified ships in the database. Using a ship category instead of a ship adds all fights of ships under that category. To add multiple fights for one ship/category use the second parameter and separate ships with a comma but no space.

**/db_remove_fight:** Removes a matchup between 2 specified ship in the database.

**/db_simulate_fight:** Simulates a fight between 2 specified ship, based on the listed matchup in the database.

**/db_export_csv:** Exports the entire database to a .csv file.

**/db_add_all_draws: Add all draws of the same ships facing each other to the database.**
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
        print(dt.now(),"requesting data")
        # try API_NEW and if it fails, try API_URL
        try:
            url = API_NEW + "analyze"
            response = requests.post(url, json=json_data)
            response.raise_for_status()
        except:
            url = API_URL + "analyze"
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
        if("data_returned" in locals()):#if the data was returned
            text = "Error: could not process ship :\n\t" + type(e).__name__ + ":" + str(e) + str(data_returned)
        else:
            text = "Error: could not process ship :\n\t" + type(e).__name__ + ":" + str(e) + "server did not respond"
        await interaction.followup.send(text, file=ship)
        return "Error: could not process ship"

@tree.command(name="compare", description="Compares two ships (id1 and id2)")
async def compare(interaction: discord.Interaction, ship1: int, ship2: int, scale: bool = False):
    print(dt.now(),"received command")
    await interaction.response.defer()
    print(dt.now(),"deferred")
    print(dt.now(),"requesting data")
    # try API_NEW and if it fails, try API_URL
    try:
        url = API_NEW + 'compare?ship1=' + str(ship1) + '&ship2=' + str(ship2) + '&scale=' + str(scale)
        response = requests.get(url)
        response.raise_for_status()
    except:
        url = API_URL + 'compare?ship1=' + str(ship1) + '&ship2=' + str(ship2) + '&scale=' + str(scale)
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
async def help(interaction: discord.Interaction, show_db_commands: bool = False):
    """
    Responds to a help command and sends a list of commands.

    Parameters:
        interaction (discord.Interaction): The interaction triggered by the user.

    Returns:
        None
    """
    if show_db_commands == False:
        print(dt.now(),"help command received")
        # Defer the initial response to prevent timeouts
        try:
            await interaction.response.defer()
            
            # Send the help text along with the legend image as a file
            await interaction.followup.send(help_text, file=discord.File(BOT_PATH+"legend.png"))
        except Exception as e:
            print(dt.now(),"Error:",e)
            await interaction.followup.send("Error:"+str(e))
    else:
        await interaction.response.defer()
        await send_long_message(interaction, db_help_text)

@tree.command(name="elim_rps", description='play rock-paper-scissors, but with elimination archtypes!')
async def rps(interaction: discord.Interaction, player_pick: str):
    ships={"cannon wall":{"wins":["avoider"]},
           "avoider"    :{"wins":["dc spinner"]},
           "dc spinner" :{"wins":["cannon wall"]}
    }

    player_pick=player_pick.lower().strip()
    computer_pick = random.choice(list(ships.keys()))

    if(player_pick not in ships):
        await interaction.response.send_message(f"Error:{player_pick} You need to pick between "+', '.join(list(ships.keys())))
        return
    player_win=False
    computer_win=False
    if(computer_pick in ships[player_pick]["wins"]):
        player_win=True
    elif(player_pick in ships[computer_pick]["wins"]):
        computer_win=True


    if player_win == True: # Display results to user
        await interaction.response.send_message(f"{interaction.user.display_name} picked `{player_pick}` and Cosmoteer Design Tools picked `{computer_pick}`; {interaction.user.display_name} wins!")
    elif computer_win:
        await interaction.response.send_message(f"{interaction.user.display_name} picked `{player_pick}` and Cosmoteer Design Tools picked `{computer_pick}`; Cosmoteer Design Tools wins!")
    else:
        await interaction.response.send_message(f"{interaction.user.display_name} and Cosmoteer Design Tools picked `{player_pick}`; it is a draw!")

# Function to split and send long messages at newline characters
async def send_long_message(interaction: discord.Interaction, text: str, chunk_size: int = 1800, use_code_blocks: bool = False):
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunk = text[start:]
        else:
            # Find the last newline character within the chunk
            newline_index = text.rfind('\n', start, end)
            if newline_index == -1:
                newline_index = end
            chunk = text[start:newline_index]
            start = newline_index + 1
        
        if use_code_blocks:
            chunk = f"```\n{chunk}\n```"

        if start == 0:
            await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(chunk)

        if end >= len(text):
            break

@tree.command(name="db_add_fight", description='adds a new fight to the database')
async def db_add_fight(interaction: discord.Interaction, shipname1: str, shipname2: str, result: str):
    shipname1=shipname1.lower().strip()
    shipname2 = shipname2.lower().strip()
    result = result.lower().strip()
    switched_ship_names = False
    not_a_draw = True

    if result=="draw" or result=="d":
        result=fight_db.FIGHT_RESULT.DRAW
        not_a_draw = False
    elif result=="win" or result=="w":
        result=fight_db.FIGHT_RESULT.WIN
    elif result=="lose" or result=="l":
        result=fight_db.FIGHT_RESULT.WIN
        temp=shipname1
        shipname1=shipname2
        shipname2=temp
        switched_ship_names = True
    else:
        await interaction.response.send_message(f"Error: result must be 'win', 'lose' or 'draw'")
        return

    author = str(interaction.user.id)
    author_name = interaction.user.display_name

    try:
        if not switched_ship_names:
            for ship_name in shipname2.split(","):
                if not_a_draw and ship_name == shipname1:
                    await interaction.response.send_message(f"Can not add a non draw result for 2 ships of the same type.")
                    return
                else:
                    db.insert_fight(shipname1, ship_name, author, author_name, result)
        else:
            for ship_name in shipname1.split(","):
                if not_a_draw and ship_name == shipname2:
                    await interaction.response.send_message(f"Can not add a non draw result for 2 ships of the same type.")
                    return
                else:
                    db.insert_fight(ship_name, shipname2, author, author_name, result)

        winner_text=""
        if result==fight_db.FIGHT_RESULT.WIN:
            winner_text="the winner is "+shipname1
        elif result==fight_db.FIGHT_RESULT.DRAW:
            winner_text="it is a draw"
        await interaction.response.send_message(f"In a fight between {shipname1} and {shipname2}, {winner_text}, according to {author_name}")
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return

"""
@tree.command(name="db_add_all_draws", description='adds a new ship to the database')
async def db_add_all_draws(interaction: discord.Interaction):
    author = str(interaction.user.id)
    author_name = interaction.user.display_name
    try:
        for ship in db.get_ships():
            db.insert_fight(ship, ship, author, author_name, 0)
        await interaction.response.send_message(f"All draws of the same ships fighting each other added to the database")
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return"""


@tree.command(name="db_add_all_draws", description='adds a new ship to the database')
async def db_add_all_draws(interaction: discord.Interaction):
    author = str(interaction.user.id)
    author_name = interaction.user.display_name
    try:
        await interaction.response.defer()  # Acknowledge the interaction to avoid timeout
        for ship in db.get_ships():
            db.insert_fight(ship, ship, author, author_name, 0)
        await interaction.followup.send("All draws of the same ships fighting each other added to the database")
    except Exception as e:
        await interaction.followup.send(f"Error: {e}")

@tree.command(name="db_add_ship", description='adds a new ship to the database')
async def db_add_ship(interaction: discord.Interaction, shipname: str, parentname: str=None, description: str=None):
    shipname=shipname.lower().strip()
    if parentname!=None:
        parentname = parentname.lower().strip()
    try:
        if parentname == shipname:
            await interaction.response.send_message(f"Ship cant be its own parent")
        if (not db.archetype_exists(parentname)) and parentname is not None:
            await interaction.response.send_message(f"That parent does not exist")

        backup = backup_file()
        await interaction.response.send_message(f"Ship {shipname} added to the database", file=backup)
        db.add_ship(shipname, parentname, description)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return
    
@tree.command(name="db_remove_fight", description='removes a fight from the database')
async def db_remove_fight(interaction: discord.Interaction, shipname1: str, shipname2: str):
    shipname1=shipname1.lower().strip()
    shipname2=shipname2.lower().strip()
    author=str(interaction.user.id)
    try:
        db.remove_fight(shipname1, shipname2, author)
        await interaction.response.send_message(f"Fight between {shipname1} and {shipname2} removed from the database")
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return
    
@tree.command(name="db_get_matchups", description='gets the matchups of a ship from the database')
async def db_get_matchups(interaction: discord.Interaction, shipname: str, playername: str=None):
    shipname=shipname.lower().strip()
    try:
        await interaction.response.defer()
        wins, draws, losses=db.get_matchups(shipname, playername)
        text_wins="Wins:\n"
        for ship in wins:
            text_wins+=f"- **{ship}** : {', '.join(wins[ship])}\n"
        text_draws="Draws:\n"
        for ship in draws:
            text_draws+=f"- **{ship}** : {', '.join(draws[ship])}\n"
        text_losses="Losses:\n"
        for ship in losses:
            text_losses+=f"- **{ship}** : {', '.join(losses[ship])}\n"
        text=f"Matchups for **{shipname}**\n"+text_wins+"\n"+text_draws+"\n"+text_losses
        await send_long_message(interaction, text)
    except Exception as e:
        await interaction.response.send_message(f"Error:{str(traceback.format_exception_only(type(e), e)[0])}")
        return

    
@tree.command(name="db_simulate_fight", description='simulates a fight between two ships')
async def db_simulate_fight(interaction: discord.Interaction, shipname1: str, shipname2: str):
    shipname1=shipname1.lower().strip()
    shipname2=shipname2.lower().strip()
    try:
        result=db.simulate_fight(shipname1, shipname2)
        people_win=result.get(fight_db.FIGHT_RESULT.WIN)
        if people_win==None:
            people_win=[]
        people_draw=result.get(fight_db.FIGHT_RESULT.DRAW)
        if people_draw==None:
            people_draw=[]
        people_lose=result.get(fight_db.FIGHT_RESULT.LOSE)
        if people_lose==None:
            people_lose=[]
        text=f"In a fight between {shipname1} and {shipname2}, the results are:\n {len(people_win)} people think {shipname1} would win\n {len(people_draw)} people think it would be a draw\n {len(people_lose)} people think {shipname2} would win"
        await interaction.response.send_message(text)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return

@tree.command(name="db_list_ships", description='lists all ships in the database')
async def db_list_ships(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        ships=db.get_ships()
        #sort the ships
        ships.sort()
        text="Ships in the database:\n"
        for ship in ships:
            text+=f"- {ship}\n"
        await send_long_message(interaction, text)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return

@tree.command(name="db_draw_archetype_tree", description='Draws a the archetype tree')
async def db_draw_archetype_tree(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        text = data_analysis.visualize_tree()
        await send_long_message(interaction, text)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return
    
@tree.command(name="db_get_unknown_matchups", description='gets the unknown matchups of a ship from the database')
async def db_get_unknown_matchups(interaction: discord.Interaction, shipname: str, player_name: str=None):
    shipname=shipname.lower().strip()
    try:
        await interaction.response.defer()
        ships=db.get_unknown_matchups(shipname, player_name)
        text="Unknown matchups for "+shipname+":\n"
        for ship in ships:
            text+=f"- {ship}\n"
        await send_long_message(interaction, text)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return

@tree.command(name="db_export_csv", description='exports the database to a csv file')
async def db_export_csv(interaction: discord.Interaction):
    try:
        # Create a file object for the CSV file
        csv_file = backup_file(is_csv=True)
        # Send the CSV file to the user
        await interaction.response.send_message("Database exported to CSV file", file=csv_file)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return
    
@tree.command(name="db_export_db", description='exports the database to a db file')
async def db_export_db(interaction: discord.Interaction):
    try:
        #db.export_db("fight_database.db")
        # Create a file object for the DB file
        db_file = backup_file()
        # Send the DB file to the user
        await interaction.response.send_message("Database exported to DB file", file=db_file)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return
    
@tree.command(name="db_rename_ship", description='renames a ship in the database')
async def db_rename_ship(interaction: discord.Interaction, old_name: str, new_name: str=None, new_parent_name: str=None, new_description: str=None):
    old_name=old_name.lower().strip()
    if new_name!=None:
        new_name=new_name.lower().strip()
    try:
        backup = backup_file()
        author=str(interaction.user.id)

        if author!="457210821773361152" and author != "450347288301273108":
            raise ValueError("Only LunastroD or Plaus can rename ships!")

        await interaction.response.send_message("Backup file created.", file=backup)
        message = db.rename_ship(old_name, new_name, new_parent_name, new_description)
        await interaction.followup.send(message)
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Error: {e}")
        else:
            await interaction.followup.send(f"Error: {e}")


@tree.command(name="db_scoreboard", description='shows the scoreboard of the database')
async def db_scoreboard(interaction: discord.Interaction, player_name: str=None):
    try:
        await interaction.response.defer()
        ships=db.get_ships()
        scoreboard={}
        for s in ships:
            scoreboard[s]=[0,0,0,0]
            for s2 in ships:
                wins,draws,losses=db.get_matchups(s,player_name)
                players_win=len(wins.get(s2,[]))
                players_draw=len(draws.get(s2,[]))
                players_lose=len(losses.get(s2,[]))
                players_matches=players_win+players_draw+players_lose
                if players_matches==0:
                    continue
                scoreboard[s][0]+=players_win/players_matches
                scoreboard[s][1]+=players_draw/players_matches
                scoreboard[s][2]+=players_lose/players_matches
                scoreboard[s][3]+=1

        #sort the ships by number of wins
        ships.sort(key=lambda x: scoreboard[x][0], reverse=True)
        table = "Scoreboard             |Win |Draw|Lost|Total\n"
        for ship in ships:
            table += f"{ship.ljust(23)}|{str(round(scoreboard[ship][0],1)).rjust(4)}|{str(round(scoreboard[ship][1],1)).rjust(4)}|{str(round(scoreboard[ship][2],1)).rjust(4)}|{str(scoreboard[ship][3])}\n"
        await send_long_message(interaction, table, use_code_blocks=True)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return

def backup_file(is_csv=False):
    if not is_csv:
        db.export_db("fight_database.db")
        # Create a file object for the DB file
        db_file = discord.File(BOT_PATH + "test.db", filename="fight_database.db")
        return db_file
    db.export_csv("fight_database.csv")
    # Create a file object for the CSV file
    return discord.File("fight_database.csv", filename="fight_database.csv")

# #client.run(os.getenv("DISCORDBOTAPI"))
client.run(secret_token.token)
