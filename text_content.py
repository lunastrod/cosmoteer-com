"""Text for the bot"""

SHORT_VERSION_TEXT = "Made by LunastroD, Aug 2023 - Sep 2023"
VERSION_TEXT = (
    SHORT_VERSION_TEXT
    + ", for the Excelsior discord server and the Cosmoteer community :3\n"
    + "- Check out the source code at <https://github.com/lunastrod/cosmoteer-com>\n"
    + "- Thanks to Poney, CoconutTrebuchet, Plaus and jun(0) for their help"
)
HELP_TEXT = (
    VERSION_TEXT
    + """
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
)

DB_HELP_TEXT = (
    ""
    + VERSION_TEXT
    + """

The Cosmoteer Design Tools bot has a database of every known multiplayer elimination archetype and their matchups that can be contributed to by anybody.
Below is a list of commands that are used to access and contribute to the database.

**/help:** Shows this message.

**/db_list_ships:** Lists every single ship type in the bot's archetype database. A handy reference for other db commands.

**/db_draw_archetype_tree:** Draws the family tree of archetypes.

**/db_add_ship:** Adds a new ship to the database. Also generates a backup before execution.

**/db_rename_ship:** Changes the existing name, parents name or description of a ship to a different specified one. Also generates a backup before execution. Only LunastroD or Plaus can use this command.

**/db_ship_meta_analysis:** Shows ship specific values and stats. 

**/db_scoreboard:** Shows the win/loss/draw ratio for each ship in the database based on matchups. The optional "playername" parameter can be used to only show the scoreboard for a certain player.

**/db_get_matchups:** Lists each matchup (win, loss, draw) of a specified ship from the database. The optional "playername" parameter can be used to only show the matchups a certain player submitted. 

**/db_get_unknown_matchups:** Lists each matchup that has no votes from a specified ship from the database. The optional "playername" parameter can be used to only show the unknown matchups for a certain player.

**/db_add_fight:** Add a new matchup between 2 or more specified ships in the database. Using a ship category instead of a ship adds all fights of ships under that category. To add multiple fights for one ship/category use the second parameter and separate ships with a comma but no space.

**/db_remove_fight:** Removes a matchup between 2 specified ship in the database.

**/db_simulate_fight:** Simulates a fight between 2 specified ship, based on the listed matchup in the database.

**/db_export_csv:** Exports the entire database to a .csv file.

**/db_add_all_draws: Add all draws of the same ships facing each other to the database.**
"""
)
