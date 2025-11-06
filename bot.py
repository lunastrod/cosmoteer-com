"""Discord Bot for ship analysis"""

import base64
import json
import os
import random
import traceback
from datetime import datetime as dt
from io import BytesIO
import logging
import hashlib

import discord
import requests
from discord import app_commands
from dotenv import load_dotenv

import data_analysis
import fight_db
import text_content

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord")

API_URL = "https://api.cosmoship.duckdns.org/"
API_NEW = "https://cosmo-api-six.vercel.app/"

try:
    db = fight_db.FightDB(db_name="/home/astrod/Desktop/Bots/cosmoteer-com/test.db")
    logger.info("Successfully initialized db")
except Exception as e:
    logger.error("Error initializing the db:")
    logger.error(traceback.format_exc())

intents = discord.Intents.default()
# client = discord.Client(intents=intents)
client = discord.AutoShardedClient(shard_count=3, intents=intents)

tree = app_commands.CommandTree(client)

VERSION_TEXT = text_content.VERSION_TEXT
HELP_TEXT = text_content.HELP_TEXT
DB_HELP_TEXT = text_content.DB_HELP_TEXT

@client.event
async def on_ready():
    """
    Event handler that is called when the bot is ready to start receiving events.
    """
    # Set the bot's presence to the specified game
    await client.change_presence(activity=discord.Game(name="Cosmoteer (/help)"))

    # Print a message indicating that the slash commands are being synced
    print(dt.now(), "Syncing slash commands")

    # Sync the slash commands with the Discord API
    await tree.sync()

    # Print a list of guilds that the bot is connected to
    print("Guilds:")
    for guild in client.guilds:
        print("\t- " + guild.name, guild.id)

    # Print a message indicating that the bot is ready
    print(dt.now(), "Bot is ready")


@tree.command(name="com", description="Calculates the center of mass of a cosmoteer ship.png")
async def com(
    interaction: discord.Interaction,
    ship: discord.Attachment,
    boost: bool = True,
    flip_vectors: bool = False,
    draw_all_cot: bool = True,
    draw_all_com: bool = False,
    cosmoship_api: bool = False,
):
    """
    Calculates the center of mass of a cosmoteer ship.png.

    Args:
    interaction (discord.Interaction): The interaction object representing the command invocation.
    ship (discord.Attachment): The attachment object representing the ship.png file.
    boost (bool, optional): Flag indicating whether to enable boosters. Defaults to True.
    flip_vectors (bool, optional): Flag indicating whether to flip the thrust vectors.
        Defaults to False.
    draw_all_cot (bool, optional): Flag indicating whether to draw the center of thrust vectors
        on every direction. Defaults to True.
    draw_all_com (bool, optional): Flag indicating whether to draw the center of mass of each part.
        Defaults to False.

    Returns:
        None
    """
    command = tree.get_command("full")
    await command.callback(
        interaction, ship, boost, flip_vectors, draw_all_cot, draw_all_com, cosmoship_api
    )


@tree.command(name="cost", description="Calculates the cost analysis of a cosmoteer ship.png")
async def cost(
    interaction: discord.Interaction,
    ship: discord.Attachment,
    boost: bool = True,
    flip_vectors: bool = False,
    draw_all_cot: bool = True,
    draw_all_com: bool = False,
):
    """
    Calculates the cost analysis of a cosmoteer ship.png.

    Args:
        interaction (discord.Interaction): The interaction object representing
            the command invocation.
        ship (discord.Attachment): The attachment object representing the ship.png file.
        boost (bool, optional): Flag indicating whether to enable boosters. Defaults to True.
        flip_vectors (bool, optional): Flag indicating whether to flip the thrust vectors.
            Defaults to False.
        draw_all_cot (bool, optional): Flag indicating whether to draw the center of thrust
            vectors on every direction. Defaults to True.
        draw_all_com (bool, optional): Flag indicating whether to draw the center of mass of
            each part. Defaults to False.

    Returns:
        None
    """
    command = tree.get_command("full")
    await command.callback(interaction, ship, boost, flip_vectors, draw_all_cot, draw_all_com)


@tree.command(
    name="full",
    description="Calculates the center of mass and cost analysis of a cosmoteer ship.png",
)
async def full(
    interaction: discord.Interaction,
    ship: discord.Attachment,
    boost: bool = True,
    flip_vectors: bool = False,
    draw_all_cot: bool = True,
    draw_all_com: bool = False,
    cosmoship_api: bool = False,
):
    """
    Calculates the center of mass and cost analysis of a cosmoteer ship.png.

    Args:
        interaction (discord.Interaction): The interaction object representing
            the command invocation.
        ship (discord.Attachment): The attachment object representing the ship.png file.
        boost (bool, optional): Flag indicating whether to enable boosters. Defaults to True.
        flip_vectors (bool, optional): Flag indicating whether to flip the thrust vectors.
            Defaults to False.
        draw_all_cot (bool, optional): Flag indicating whether to draw the center of thrust
            vectors on every direction. Defaults to True.
        draw_all_com (bool, optional): Flag indicating whether to draw the center of mass of
            each part. Defaults to False.
    """
    # switch between API_NEW and API_URL
    if cosmoship_api:
        primary_api = API_URL
        secondary_api = API_NEW
    else:
        primary_api = API_NEW
        secondary_api = API_URL
    print(dt.now(), "received command")
    await interaction.response.defer()
    print(dt.now(), "deferred")
    # Read the image bytes and encode them to base64
    image_bytes = await ship.read()
    #calculates hmmm%
    hmmm_perc= hashlib.blake2s(image_bytes).digest()
    hmmm_perc= int.from_bytes(hmmm_perc, 'big')
    hmmm_perc= hmmm_perc / ((1 << 256) - 1)
    hmmm_perc= round(hmmm_perc*100,6)

    base64_string = base64.b64encode(image_bytes).decode("utf-8")
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
            "analyze": True,
        }
        json_data = json.dumps({"image": base64_string, "args": args})
        # Send the request to the server
        print(dt.now(), "requesting data")
        # try API_NEW and if it fails, try API_URL
        try:
            url = primary_api + "analyze"
            response = requests.post(url, json=json_data, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"error fetching data, switching to old API {dt.now()} Exception: {e}")
            url = secondary_api + "analyze"
            response = requests.post(url, json=json_data, timeout=30)
            response.raise_for_status()
        print(dt.now(), "server responded")
        # Get the response
        data_returned = response.json()

        # Get the URL of the center of mass image
        url_com = data_returned["url_com"]
        # prepare the data
        center_of_mass_x = round(data_returned["center_of_mass_x"], 2)
        center_of_mass_y = round(data_returned["center_of_mass_y"], 2)
        total_mass = round(data_returned["total_mass"], 2)
        top_speed = round(data_returned["top_speed"], 2)
        crew = data_returned["crew"]
        price = data_returned["price"]
        made_by = data_returned["author"]
        # convert the data
        data_converted = {
            "Center of mass": f"{center_of_mass_x}, {center_of_mass_y}",
            "Total mass": total_mass,
            "Max speed": f"{top_speed} m/s",
            "Total crew": crew,
            "Aprox cost": price,
            "Made by": made_by,
            "hmmm%": f"{hmmm_perc}%",
        }

        text = "use the /help command for more info\n"

        categoriescom = ["Center of mass", "Total mass", "Max speed", "Total crew", "Aprox cost"]
        if data_returned["author"] != "":
            categoriescom += ["Made by"]
        categoriescom += ["hmmm%"]
        embedcom = discord.Embed(title="Center of mass analysis", color=discord.Color.green())
        # Create a formatted table header with consistent column widths
        table_headercom = "Category        | Data         \n"
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
        embedcom.add_field(
            name="\u200b", value=tablecom, inline=False
        )  # "\u200b" is a zero-width space for better formatting

        url_stats = data_returned["analysis"]["url_analysis"]
        analysis = data_returned["analysis"]
        categories = [
            "total_price",
            "price_crew",
            "price_armor",
            "price_weapons",
            "price_mouvement",
            "price_shield",
            "price_storage",
            "price_utility",
            "price_power",
        ]
        text_categories = {
            "total_price": "total",
            "price_crew": "crew",
            "price_armor": "armor",
            "price_weapons": "weapons",
            "price_mouvement": "thrust",
            "price_shield": "shield",
            "price_storage": "storage",
            "price_utility": "misc",
            "price_power": "power",
        }
        embed = discord.Embed(title="Price analysis", color=discord.Color.green())
        # Create a formatted table header with consistent column widths
        table_header = "Category  | Percent | Price\n"
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
        embed.add_field(
            name="\u200b", value=table, inline=False
        )  # "\u200b" is a zero-width space for better formatting
        print(dt.now(), "sending to Discord")
        # Create an Embed for the Center of Mass image
        embedcom.set_image(url=url_com)
        # Create an Embed for the Stats image
        embed.set_image(url=url_stats)
        embeds = [embedcom, embed]
        await interaction.followup.send(text, embeds=embeds, files=[ship])
        print(dt.now(), "sent to Discord")
    except Exception as e:
        print(dt.now(), "error", e)
        if "data_returned" in locals():  # if the data was returned
            text = (
                "Error: could not process ship :\n\t"
                + type(e).__name__
                + ":"
                + str(e)
                + str(data_returned)
            )
        else:
            text = (
                "Error: could not process ship :\n\t"
                + type(e).__name__
                + ":"
                + str(e)
                + "server did not respond"
            )
        await interaction.followup.send(text, file=ship)
        return "Error: could not process ship"


@tree.command(name="ping", description="responds with the bot's latency")
async def ping(interaction: discord.Interaction):
    """
    Responds to a ping command and sends the bot's latency in milliseconds.

    Parameters:
        interaction (discord.Interaction): The interaction triggered by the user.

    Returns:
        None
    """
    await interaction.response.send_message(f"Pong! {round(client.latency * 1000)}ms")


@tree.command(name="hmmm", description="responds with hmmm")
async def hmmm(interaction: discord.Interaction):
    """a little fun"""
    if random.random() < 0.05:
        await interaction.response.send_message(
            "oh no, not again, please no, not the hmmm, anything but the hmmm, please"
        )
    else:
        await interaction.response.send_message("hmmm")


@tree.command(name="help", description="shows the list of commands")
async def show_help(interaction: discord.Interaction, show_db_commands: bool = False):
    """
    Responds to a help command and sends a list of commands.

    Parameters:
        interaction (discord.Interaction): The interaction triggered by the user.

    Returns:
        None
    """
    if not show_db_commands:
        print(dt.now(), "help command received")
        # Defer the initial response to prevent timeouts
        try:
            await interaction.response.defer()

            # Send the help text along with the legend image as a file
            await interaction.followup.send(HELP_TEXT, file=discord.File("legend.png"))
        except Exception as e:
            print(dt.now(), "Error:", e)
            await interaction.followup.send("Error:" + str(e))
    else:
        await interaction.response.defer()
        await send_long_message(interaction, DB_HELP_TEXT)


@tree.command(
    name="elim_rps", description="play rock-paper-scissors, but with elimination archtypes!"
)
async def rps(interaction: discord.Interaction, player_pick: str):
    """rock-paper-scissors"""
    ships = {
        "cannon wall": {"wins": ["avoider"]},
        "avoider": {"wins": ["dc spinner"]},
        "dc spinner": {"wins": ["cannon wall"]},
    }

    player_pick = player_pick.lower().strip()
    computer_pick = random.choice(list(ships.keys()))

    if player_pick not in ships:
        await interaction.response.send_message(
            f"Error:{player_pick} You need to pick between " + ", ".join(list(ships.keys()))
        )
        return
    player_win = False
    computer_win = False
    if computer_pick in ships[player_pick]["wins"]:
        player_win = True
    elif player_pick in ships[computer_pick]["wins"]:
        computer_win = True

    if player_win:  # Display results to user
        message = (
            f"{interaction.user.display_name} picked `{player_pick}` and "
            f"Cosmoteer Design Tools picked `{computer_pick}`; "
            f"{interaction.user.display_name} wins!"
        )
        await interaction.response.send_message(message)
    elif computer_win:
        message = (
            f"{interaction.user.display_name} picked `{player_pick}` and "
            f"Cosmoteer Design Tools picked `{computer_pick}`; "
            f"Cosmoteer Design Tools wins!"
        )
        await interaction.response.send_message(message)
    else:
        message = (
            f"{interaction.user.display_name} and Cosmoteer Design Tools picked `{player_pick}`; "
            f"it is a draw!"
        )
        await interaction.response.send_message(message)


# Function to split and send long messages at newline characters
async def send_long_message(
    interaction: discord.Interaction,
    text: str,
    chunk_size: int = 1800,
    use_code_blocks: bool = False,
):
    """help to send long messages"""
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunk = text[start:]
        else:
            # Find the last newline character within the chunk
            newline_index = text.rfind("\n", start, end)
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


@tree.command(name="db_add_fight", description="adds a new fight to the database")
async def db_add_fight(
    interaction: discord.Interaction, shipname1: str, shipname2: str, result: str
):
    """
    Adds a new fight to the database.

    Args:
        interaction (discord.Interaction): The interaction object.
        shipname1 (str): The name of the first ship.
        shipname2 (str): The name of the second ship.
        result (str): The result of the fight.

    Returns:
        None
    """
    shipname1 = shipname1.lower().strip().replace("_", " ")
    shipname2 = shipname2.lower().strip().replace("_", " ")
    result = result.lower().strip().replace("_", " ")
    switched_ship_names = False
    not_a_draw = True

    if result in {"draw", "d"}:
        result = fight_db.FIGHT_RESULT.DRAW
        not_a_draw = False
    elif result in {"win", "w"}:
        result = fight_db.FIGHT_RESULT.WIN
    elif result in {"lose", "l"}:
        result = fight_db.FIGHT_RESULT.WIN
        shipname1, shipname2 = shipname2, shipname1  # switch ship names
        switched_ship_names = True
    else:
        await interaction.response.send_message("Error: result must be 'win', 'lose' or 'draw'")
        return

    author = str(interaction.user.id)
    author_name = interaction.user.display_name

    try:
        if not switched_ship_names:
            for ship_name in shipname2.split(","):
                if not_a_draw and ship_name == shipname1:
                    await interaction.response.send_message(
                        "Can not add a non draw result for 2 ships of the same type."
                    )
                    return
                # else: no need for an else since there is a return
                db.insert_fight(shipname1, ship_name, author, author_name, result)
        else:
            for ship_name in shipname1.split(","):
                if not_a_draw and ship_name == shipname2:
                    await interaction.response.send_message(
                        "Can not add a non draw result for 2 ships of the same type."
                    )
                    return
                # else: no need for an else since there is a return
                db.insert_fight(ship_name, shipname2, author, author_name, result)

        winner_text = ""
        if result == fight_db.FIGHT_RESULT.WIN:
            winner_text = "the winner is " + shipname1
        elif result == fight_db.FIGHT_RESULT.DRAW:
            winner_text = "it is a draw"
        await interaction.response.send_message(
            f"In a fight between {shipname1} and {shipname2}, "
            f"{winner_text}, according to {author_name}"
        )
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return


@tree.command(name="db_add_all_draws", description="sets all ships to draw in the database")
async def db_add_all_draws(interaction: discord.Interaction):
    """sets all ships to draw in the database"""
    author = str(interaction.user.id)
    author_name = interaction.user.display_name
    try:
        await interaction.response.defer()  # Acknowledge the interaction to avoid timeout
        for ship in db.get_ships():
            db.insert_fight(ship, ship, author, author_name, 0)
        await interaction.followup.send(
            "All draws of the same ships fighting each other added to the database"
        )
    except Exception as e:
        await interaction.followup.send(f"Error: {e}")


@tree.command(name="db_add_ship", description="adds a new ship to the database")
async def db_add_ship(
    interaction: discord.Interaction, shipname: str, parentname: str = None, description: str = None
):
    """adds a new ship to the database"""
    shipname = shipname.lower().strip()
    if parentname is not None:
        parentname = parentname.lower().strip()
    try:
        if parentname == shipname:
            await interaction.response.send_message("Ship cant be its own parent")
        if (not db.archetype_exists(parentname)) and parentname is not None:
            await interaction.response.send_message("That parent does not exist")

        backup = backup_file()
        await interaction.response.send_message(
            f"Ship {shipname} added to the database", file=backup
        )
        db.add_ship(shipname, parentname, description)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return


@tree.command(name="db_remove_fight", description="removes a fight from the database")
async def db_remove_fight(interaction: discord.Interaction, shipname1: str, shipname2: str):
    """removes a fight from the database"""
    shipname1 = shipname1.lower().replace("_", " ").strip()
    shipname2 = shipname2.lower().replace("_", " ").strip()
    author = str(interaction.user.id)
    try:
        db.remove_fight(shipname1, shipname2, author)
        await interaction.response.send_message(
            f"Fight between {shipname1} and {shipname2} removed from the database"
        )
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return


@tree.command(name="db_get_matchups", description="gets the matchups of a ship from the database")
async def db_get_matchups(interaction: discord.Interaction, shipname: str, playername: str = None):
    """gets the matchups of a ship from the database"""
    shipname = shipname.lower().replace("_", " ").strip()
    try:
        await interaction.response.defer()
        wins, draws, losses = db.get_matchups(shipname, playername)
        text_wins = "Wins:\n"
        for ship, matches in wins.items():
            text_wins += f"- **{ship}** : {', '.join(matches)}\n"
        text_draws = "Draws:\n"
        for ship, matches in draws.items():
            text_draws += f"- **{ship}** : {', '.join(matches)}\n"
        text_losses = "Losses:\n"
        for ship, matches in losses.items():
            text_losses += f"- **{ship}** : {', '.join(matches)}\n"
        text = f"Matchups for **{shipname}**\n" + text_wins + "\n" + text_draws + "\n" + text_losses
        await send_long_message(interaction, text)
    except Exception as e:
        await interaction.followup.send(
            f"Error:{str(traceback.format_exception_only(type(e), e)[0])}"
        )
        return


@tree.command(name="db_ship_meta_analysis", description="Analyses a ships place in the meta.")
async def db_ship_meta_analysis(interaction: discord.Interaction, shipname: str):
    """Analyses a ships place in the meta."""
    shipname = shipname.lower().replace("_", " ").strip()
    try:
        await interaction.response.defer()
        text = "Name: " + shipname + "\n"
        text += "Description: " + db.get_ship_description(shipname) + "\n"
        text += "Page rank: " + str(data_analysis.page_rank_ship(shipname)) + "\n"
        await send_long_message(interaction, text)
    except Exception as e:
        await interaction.followup.send(
            f"Error:{str(traceback.format_exception_only(type(e), e)[0])}"
        )
        return


@tree.command(name="db_simulate_fight", description="simulates a fight between two ships")
async def db_simulate_fight(interaction: discord.Interaction, shipname1: str, shipname2: str):
    """simulates a fight between two ships"""
    shipname1 = shipname1.lower().replace("_", " ").strip()
    shipname2 = shipname2.lower().replace("_", " ").strip()
    try:
        result = db.simulate_fight(shipname1, shipname2)
        people_win = result.get(fight_db.FIGHT_RESULT.WIN)
        if people_win is None:
            people_win = []
        people_draw = result.get(fight_db.FIGHT_RESULT.DRAW)
        if people_draw is None:
            people_draw = []
        people_lose = result.get(fight_db.FIGHT_RESULT.LOSE)
        if people_lose is None:
            people_lose = []
        text = (
            f"In a fight between {shipname1} and {shipname2}, "
            f"the results are:\n {len(people_win)} people think {shipname1} would win\n "
            f"{len(people_draw)} people think it would be a draw\n "
            f"{len(people_lose)} people think {shipname2} would win"
        )
        await interaction.response.send_message(text)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return


@tree.command(name="db_list_ships", description='lists all ships in the database',)
async def db_list_ships(interaction: discord.Interaction, filter_keyword: str=None):
    if filter_keyword:
        filter_keyword.lower().replace('_', ' ').strip()
    try:
        await interaction.response.defer()
        ships = db.get_ships()
        # sort the ships
        ships.sort()

        text="Ships in the database:\n"
        for ship in ships:
            if filter_keyword:
                if filter_keyword in ship:
                    text+=f"- {ship}\n"
            else:
                text+=f"- {ship}\n"
        await send_long_message(interaction, text)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return


@tree.command(name="db_draw_archetype_tree", description="Draws a the archetype tree")
async def db_draw_archetype_tree(interaction: discord.Interaction):
    """Draws a the archetype tree"""
    try:
        await interaction.response.defer()
        text = data_analysis.visualize_tree()
        await send_long_message(interaction, text)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return


@tree.command(
    name="db_get_unknown_matchups",
    description="gets the unknown matchups of a ship from the database",
)
async def db_get_unknown_matchups(
    interaction: discord.Interaction, shipname: str, player_name: str = None
):
    """gets the unknown matchups of a ship from the database"""
    shipname = shipname.lower().replace("_", " ").strip()
    try:
        await interaction.response.defer()
        ships = db.get_unknown_matchups(shipname, player_name)
        text = "Unknown matchups for " + shipname + ":\n"
        for ship in ships:
            text += f"- {ship}\n"
        await send_long_message(interaction, text)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return


@tree.command(name="db_export_csv", description="exports the database to a csv file")
async def db_export_csv(interaction: discord.Interaction):
    """exports the database to a csv file"""
    try:
        # Create a file object for the CSV file
        csv_file = backup_file(is_csv=True)
        # Send the CSV file to the user
        await interaction.response.send_message("Database exported to CSV file", file=csv_file)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return


@tree.command(name="db_export_db", description="exports the database to a db file")
async def db_export_db(interaction: discord.Interaction):
    """exports the database to a db file"""
    try:
        # db.export_db("fight_database.db")
        # Create a file object for the DB file
        db_file = backup_file()
        # Send the DB file to the user
        await interaction.response.send_message("Database exported to DB file", file=db_file)
    except Exception as e:
        await interaction.response.send_message(f"Error:{e}")
        return


@tree.command(name="db_rename_ship", description="renames a ship in the database")
async def db_rename_ship(
    interaction: discord.Interaction,
    old_name: str,
    new_name: str = None,
    new_parent_name: str = None,
    new_description: str = None,
):
    """renames a ship in the database"""
    old_name = old_name.lower().replace("_", " ").strip()
    if new_name is not None:
        new_name = new_name.lower().replace("_", " ").strip()
    try:
        backup = backup_file()
        author = str(interaction.user.id)

        if author not in {"457210821773361152", "450347288301273108"}:
            raise ValueError("Only LunastroD or Plaus can rename ships!")

        await interaction.response.send_message("Backup file created.", file=backup)
        message = db.rename_ship(old_name, new_name, new_parent_name, new_description)
        await interaction.followup.send(message)
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Error: {e}")
        else:
            await interaction.followup.send(f"Error: {e}")


# refactored scoreboard, slpit into functions
@tree.command(name="db_scoreboard", description="shows the scoreboard of the database")
async def db_scoreboard(
    interaction: discord.Interaction, player_name: str = None, sort_by: str = "win"
):
    """Shows the scoreboard of the database."""
    try:
        await interaction.response.defer()

        ships = db.get_ships()
        page_rank_dic = data_analysis.page_rank(data_analysis.get_fights_graph())
        sort_list = ["win", "draw", "loss", "matches", "page rank"]

        if sort_by not in sort_list:
            raise ValueError("Can only sort by: " + str(sort_list))

        scoreboard = calculate_scoreboard(ships, page_rank_dic, player_name)
        sorted_ships = sort_ships(ships, scoreboard, sort_by, sort_list)

        leading_message = f"Scoreboard ({sort_by.capitalize()})"
        table = format_scoreboard(sorted_ships, scoreboard, leading_message)

        await send_long_message(interaction, table, use_code_blocks=True)
    except Exception as e:
        await interaction.followup.send(f"Error: {e}")
        return


def calculate_scoreboard(ships, page_rank_dic, player_name):
    """Calculates the scoreboard for each ship."""
    scoreboard = {s: [0, 0, 0, 0, round(page_rank_dic[s], 4)] for s in ships}
    for s in ships:
        for s2 in ships:
            wins, draws, losses = db.get_matchups(s, player_name)
            players_win = len(wins.get(s2, []))
            players_draw = len(draws.get(s2, []))
            players_lose = len(losses.get(s2, []))
            players_matches = players_win + players_draw + players_lose
            if players_matches == 0:
                continue
            scoreboard[s][0] += players_win / players_matches
            scoreboard[s][1] += players_draw / players_matches
            scoreboard[s][2] += players_lose / players_matches
            scoreboard[s][3] += 1
    return scoreboard


def sort_ships(ships, scoreboard, sort_by, sort_list):
    """Sorts the ships based on the specified criterion."""
    return sorted(ships, key=lambda x: scoreboard[x][sort_list.index(sort_by)], reverse=True)


def format_scoreboard(sorted_ships, scoreboard, leading_message):
    """Formats the scoreboard into a string table."""
    return f"{leading_message.ljust(22)} |Win|Draw|Lost|Total|Page Rank\n" + "\n".join(
        [
            f"{ship.ljust(23)}|{str(round(scoreboard[ship][0], 1)).rjust(4)}|"
            f"{str(round(scoreboard[ship][1], 1)).rjust(4)}|"
            f"{str(round(scoreboard[ship][2], 1)).rjust(4)}|"
            f"{str(scoreboard[ship][3]).rjust(3)}|"
            f"{str(scoreboard[ship][4])}\n"
            for ship in sorted_ships
        ]
    )


def backup_file(is_csv=False):
    """
    Backup the database to a file.

    Args:
        is_csv (bool, optional): Whether to export the database as a CSV file. Defaults to False.

    Returns:
        discord.File: A file object representing the backup file.
        If `is_csv` is False, the file is a DB file.
        Otherwise, the file is a CSV file.
    """
    if not is_csv:
        db.export_db("fight_database.db")
        # Create a file object for the DB file
        db_file = discord.File("test.db", filename="fight_database.db")
        return db_file
    db.export_csv("fight_database.csv")
    # Create a file object for the CSV file
    return discord.File("fight_database.csv", filename="fight_database.csv")


client.run(os.getenv("TOKEN"))
