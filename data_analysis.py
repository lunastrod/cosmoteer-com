import fight_db
import secret_token
import math

BOT_PATH = "/home/astrod/Desktop/Bots/cosmoteer-com/"
db = fight_db.FightDB(db_name=BOT_PATH+"test.db")

# Idk why but I was told 0.85 is a good value for this
page_rank_faktor = 0.5

class Graph:
    num_vertices = 0
    graph = {}
    num_edges = {}
    vertices = []

def get_fights_graph():
    graph = Graph()
    graph.vertices = db.get_ships()
    graph.num_vertices = graph.vertices.__len__()
    sum=0
    for ship1 in graph.vertices:
        for ship2 in graph.vertices:
            graph.graph[(ship1, ship2)] = db.get_average_match(ship2, ship1)
    for ship1 in graph.vertices:
        for ship2 in graph.vertices:
            if db.get_average_match(ship2, ship1)==1:
                sum+=1
        graph.num_edges[ship1] = sum
        sum = 0
        
    return graph

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

def page_rank_ship(ship):
    if not db.archetype_exists(ship):
        raise ValueError(f"Ship '{ship}' does not exist in the database")
    fights_graph = get_fights_graph()

    return page_rank(fights_graph)[ship]

def page_rank(graph):
    page_rank_dic = {}
    for v in graph.vertices:
        page_rank_dic[v] = 1/graph.num_vertices

    # Apparently you can get good results after O(log(n)) iterations.
    num_iterations = 10*math.floor(math.log(graph.num_vertices, 2))

    for i in range(num_iterations):
        page_rank_dic_new = {}
        for w in graph.vertices:
            page_rank_dic_new[w] = 0
            for v in graph.vertices:
                page_rank_dic_new[w] += page_rank_dic[v]*page_rank_coeff_a(graph, v, w)
        page_rank_dic = page_rank_dic_new

    return page_rank_dic

def page_rank_coeff_a(graph, v,w):
    return (1-page_rank_faktor)/graph.num_vertices+page_rank_faktor*page_rank_coeff_p(graph, v, w)

def page_rank_coeff_p(graph, v,w):
    if graph.num_edges[v] == 0:
        return 1/graph.num_vertices

    if graph.graph[(v, w)] == 1:
        return 1/graph.num_edges[v]
    
    return 0

