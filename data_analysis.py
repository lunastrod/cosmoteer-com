"""Data analysis for the bot."""

import math

import fight_db

db = fight_db.FightDB(db_name="test.db")

# Idk why but I was told 0.85 is a good value for this
PAGE_RANK_FAKTOR = 0.5


class Graph:
    """might be the start of a class, need to add an init function and a set function"""

    num_vertices = 0
    graph = {}
    num_edges = {}
    vertices = []


def get_fights_graph():
    """
    Generates a graph representation of the fights between different ships.

    Returns:
        Graph: A graph object containing the vertices (ships) and the edges (fights) between them.
              The graph is represented as a dictionary where the keys are tuples of ship names,
              and the values are the average match results between the corresponding ships.
              The number of vertices is stored in the `num_vertices` attribute of the graph object.
              The number of edges for each vertex is stored in the `num_edges` attribute
              of the graph object.
              The vertices are stored in the `vertices` attribute of the graph object.
    """
    graph = Graph()
    graph.vertices = db.get_ships()
    graph.num_vertices = len(graph.vertices)
    sum_graph = 0
    for ship1 in graph.vertices:
        for ship2 in graph.vertices:
            graph.graph[(ship1, ship2)] = db.get_average_match(ship2, ship1)
    for ship1 in graph.vertices:
        for ship2 in graph.vertices:
            if db.get_average_match(ship2, ship1) == 1:
                sum_graph += 1
        graph.num_edges[ship1] = sum_graph
        sum_graph = 0

    return graph


def visualize_tree():
    """
    Generates a tree-like representation of the archetypes in the database.

    Returns:
        str: The text representation of the tree.

    This function iterates over all the archetypes in the database and checks
    if they have no parent.
    If an archetype has no parent, it adds it to the text representation of the tree.
    Then, it recursively calls the `visualize_tree_inner` function to generate
    the tree for each archetype.
    The resulting text representation of the tree is returned.
    """
    text = ""
    archetypes = db.get_archetypes()

    for archetype in archetypes:
        if db.get_ships_parentid(archetype) is None:
            text += f"**{archetype}**" + "\n"
            text = visualize_tree_inner(text, archetype, archetype_category=True)

    return text


def visualize_tree_inner(text, base_archetype, indent=0, archetype_category=False):
    """
    Recursively generates a tree-like representation of the archetypes in the database.

    Args:
        text (str): The current text representation of the tree.
        base_archetype (str): The current archetype being processed.
        indent (int, optional): The indentation level. Defaults to 0.

    Returns:
        str: The updated text representation of the tree.
    """
    indent += 4

    for archetype in db.archetypes_children(base_archetype):
        underlined_category = f"__{archetype}__" if archetype_category else archetype
        text += " " * indent + underlined_category + "\n"
        text = visualize_tree_inner(text, archetype, indent)

    return text


def ship_wins_map():
    """
    Generates a dictionary mapping each pair of ships to their average matchup.

    Returns:
        dict: A dictionary where the keys are tuples of the form (ship1, ship2)
        and the values are the average matchup between the two ships.
    """
    ships = db.get_archetypes()
    matchups = {}
    for i, ship1 in enumerate(ships):
        for j in range(i + 1, len(ships)):
            ship2 = ships[j]
            # Process the matchup between ship1 and ship2
            matchup_key = (ship1, ship2)
            matchups[matchup_key] = db.get_average_match(ship1, ship2)


def page_rank_ship(ship):
    """
    Calculates the PageRank of a given ship in the database.

    Args:
        ship (str): The name of the ship to calculate the PageRank for.

    Raises:
        ValueError: If the ship does not exist in the database.

    Returns:
        float: The PageRank of the ship.
    """
    if not db.archetype_exists(ship):
        raise ValueError(f"Ship '{ship}' does not exist in the database")
    fights_graph = get_fights_graph()

    return page_rank(fights_graph)[ship]


def page_rank(graph):
    """
    Calculates the PageRank of a graph.

    Parameters:
        graph (Graph): The graph object.

    Returns:
        dict: A dictionary mapping each vertex in the graph to its PageRank value.

    The PageRank of a vertex is the probability of a random surfer starting at the vertex
    and ending up at the vertex after a large number of random jumps.

    The algorithm used is the Power Iteration method. It iteratively updates the
    PageRank of each vertex based on the PageRank of its neighbors.

    The number of iterations is determined by the number of vertices in the graph.

    The function returns a dictionary where the keys are the vertices and the values
    are the corresponding PageRank values.

    """
    page_rank_dic = {}
    for v in graph.vertices:
        page_rank_dic[v] = 1 / graph.num_vertices

    # Apparently you can get good results after O(log(n)) iterations.
    num_iterations = 10 * math.floor(math.log(graph.num_vertices, 2))

    for _ in range(num_iterations):
        page_rank_dic_new = {}
        for w in graph.vertices:
            page_rank_dic_new[w] = 0
            for v in graph.vertices:
                page_rank_dic_new[w] += page_rank_dic[v] * page_rank_coeff_a(graph, v, w)
        page_rank_dic = page_rank_dic_new

    return page_rank_dic


def page_rank_coeff_a(graph, v, w):
    """
    Calculate the page rank coefficient for a given graph, vertex, and neighbor.

    Parameters:
        graph (Graph): The graph object.
        v (int): The vertex.
        w (int): The neighbor of the vertex.

    Returns:
        float: The page rank coefficient.

    """
    return (1 - PAGE_RANK_FAKTOR) / graph.num_vertices + PAGE_RANK_FAKTOR * page_rank_coeff_p(
        graph, v, w
    )


def page_rank_coeff_p(graph, v, w):
    """
    Calculate the page rank coefficient for the given graph, vertex, and neighbor.

    Args:
        graph (Graph): The graph object.
        v (int): The vertex.
        w (int): The neighbor of the vertex.

    Returns:
        float: The page rank coefficient.

    """
    if graph.num_edges[v] == 0:
        return 1 / graph.num_vertices

    if graph.graph[(v, w)] == 1:
        return 1 / graph.num_edges[v]

    return 0
