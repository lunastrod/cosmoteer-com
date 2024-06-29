import fight_db
import secret_token

BOT_PATH = "/home/astrod/Desktop/Bots/cosmoteer-com/"
db = fight_db.FightDB(db_name=BOT_PATH+"test.db")

page_rank_faktor = 0.5

def visualize_tree():
    text = ""
    archetypes = db.get_archetypes()

    for archetype in archetypes:
        if db.get_ships_parentid(archetype) is None:
            text += archetype + "\n"
            text = visualize_tree_inner(text, archetype)

    return text

def visualize_tree_inner(text, base_archetype, indent=0):
    indent += 4

    for archetype in db.archetypes_children(base_archetype):
        text += " " * indent + archetype + "\n"
        text = visualize_tree_inner(text, archetype, indent)

    return text

def ship_wins_map():
    ships = db.get_archetypes()
    matchups = {}
    for i, ship1 in enumerate(ships):
        for j in range(i + 1, len(ships)):
            ship2 = ships[j]
            # Process the matchup between ship1 and ship2
            matchup_key = (ship1, ship2)
            matchups[matchup_key] = db.get_average_match(ship1, ship2)

def page_rank(ship, index):
    sum = 0
    for i in range(10):
        sum += page_rank_coeff_a()

def page_rank_coeff_a(v,w):
    return (1-page_rank_faktor)/db.get_archetypes().__len__()+page_rank_faktor*page_rank_coeff_p(v,w)

def page_rank_coeff_p():
    return 0

