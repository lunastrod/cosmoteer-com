import fight_db

BOT_PATH = "/home/astrod/Desktop/Bots/cosmoteer-com/"
db = fight_db.FightDB(db_name=BOT_PATH+"test.db")

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