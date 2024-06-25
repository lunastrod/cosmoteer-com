import sqlite3

class FIGHT_RESULT:
    DRAW = 0
    WIN = 1
    LOSE = -1 #do not store lose in the database, instead, switch the shipname1 and shipname2

class FightDB:
    def __init__(self, db_name="test.db"):
        self.con = sqlite3.connect(db_name)
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Fights (
                                id INTEGER PRIMARY KEY,
                                shipname1 TEXT NOT NULL,
                                shipname2 TEXT NOT NULL,
                                author TEXT NOT NULL,
                                author_name TEXT NOT NULL,
                                result INTEGER NOT NULL
                            );""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Archetypes (
                                        id INTEGER PRIMARY KEY,
                                        shipname TEXT NOT NULL,
                                        parentid TEXT,
                                        description TEXT
                                    );""")
        self.con.commit()

    def insert_fight(self, shipname1, shipname2, author, author_name, result):
        # Check if shipname1 and shipname2 exist in the database
        if not self.archetype_exists(shipname1):
            raise ValueError(f"Ship '{shipname1}' does not exist in the database")
        if not self.archetype_exists(shipname2):
            raise ValueError(f"Ship '{shipname2}' does not exist in the database")


        if self.ship_is_leaf(shipname1):
            if self.ship_is_leaf(shipname2):
                self.cur.execute("SELECT * FROM Fights WHERE (shipname1 = ? AND shipname2 = ? AND author = ?) OR (shipname1 = ? AND shipname2 = ? AND author = ?)",
                                 (shipname1, shipname2, author, shipname2, shipname1, author))
                existing_fight = self.cur.fetchone()

                if existing_fight and existing_fight is not None:# Remove the existing fight
                    print("Removing existing fight")
                    self.cur.execute("DELETE FROM Fights WHERE id = ?", (existing_fight[0],))

                # Insert the new fight
                self.cur.execute("INSERT INTO Fights (shipname1, shipname2, author, author_name, result) VALUES (?, ?, ?, ?, ?)", (shipname1, shipname2, author, author_name, result))
            else:
                for ship in self.archetypes_children(shipname2):
                    self.insert_fight(shipname1, ship, author, author_name, result)
        else:
            for ship in self.archetypes_children(shipname1):
                self.insert_fight(ship, shipname2, author, author_name, result)
        self.con.commit()

    def archetype_exists(self, shipname):
        self.cur.execute("SELECT 1 FROM Archetypes WHERE shipname = ?", (shipname,))
        return bool(self.cur.fetchone())

    def ship_is_leaf(self, shipname):
        self.cur.execute("SELECT 1 FROM Archetypes WHERE parentid = ?", (self.get_ship_id(shipname),))
        return not bool(self.cur.fetchone())

    def get_ship_id(self, shipname):
        if shipname is None:
            return None
        self.cur.execute("SELECT id FROM Archetypes WHERE shipname=?", (shipname,))
        return self.cur.fetchone()[0]

    def get_ships_parentid(self, shipname):
        if shipname is None:
            return None
        self.cur.execute("SELECT parentid FROM Archetypes WHERE shipname=?", (shipname,))
        parent = self.cur.fetchone()
        if parent is None:
            return None
        return parent[0]

    def archetypes_children(self, shipname):
        self.cur.execute("SELECT shipname FROM Archetypes WHERE parentid=?", (self.get_ship_id(shipname),))
        children = self.cur.fetchall()
        if children is None:
            children = ()
        else:
            # Extract the first element from each tuple
            children = [child[0] for child in children]
        return children

    def remove_fight(self, shipname1, shipname2, author):
        # Remove the fight between shipname1 and shipname2 with the specified author
        self.cur.execute("DELETE FROM Fights WHERE (shipname1 = ? AND shipname2 = ? AND author = ?) OR (shipname1 = ? AND shipname2 = ? AND author = ?)",
                         (shipname1, shipname2, author, shipname2, shipname1, author))
        self.con.commit()

    def add_ship(self, shipname, parent_name=None, description=None):
        # Add a fight where the ship fights against itself
        if not self.archetype_exists(shipname):
            #self.cur.execute("INSERT INTO Fights (shipname1, shipname2, author, author_name, result) VALUES (?, ?, ?, ?, ?)", (shipname, shipname, author, author_name, FIGHT_RESULT.DRAW))
            parent_id = self.get_ship_id(parent_name)
            self.cur.execute("INSERT INTO Archetypes (shipname, parentid, description) VALUES (?, ?, ?)", (shipname, parent_id, description))
            self.con.commit()

    def get_fights(self):
        self.cur.execute("SELECT * FROM Fights")
        return self.cur.fetchall()

    def get_matchups(self, ship_name, player_name=None):
        wins={}
        draws={}
        losses={}
        # Get all fights where the specified ship is involved
        if not self.archetype_exists(ship_name):
            raise ValueError(f"Ship '{ship_name}' does not exist in the database")
        self.cur.execute("SELECT shipname1, shipname2, author_name, result FROM Fights WHERE (shipname1 = ? OR shipname2 = ?)", (ship_name, ship_name))
        fight_data = self.cur.fetchall()
        # Iterate over each fight data
        for ship1,ship2, author_name, result in fight_data:
            if player_name is None or author_name == player_name:
                if result == FIGHT_RESULT.DRAW:
                    opponent = ship1 if ship1 != ship_name else ship2
                    if opponent in draws:
                        draws[opponent].append(author_name)
                    else:
                        draws[opponent] = [author_name]
                else:
                    # Check if the ship is shipname1 or shipname2, shipname1 is the ship that won
                    if ship1 == ship_name:
                        if ship2 in wins:
                            wins[ship2].append(author_name)
                        else:
                            wins[ship2] = [author_name]
                    else:
                        if ship1 in losses:
                            losses[ship1].append(author_name)
                        else:
                            losses[ship1] = [author_name]

        return wins, draws, losses
    def get_unknown_matchups(self, shipname, player_name=None):
        """
        # Get all ships that the specified ship has not fought against
        # check if the ship exists
        if not self.ship_exists(shipname):
            raise ValueError(f"Ship '{shipname}' does not exist in the database")
        ships=self.get_ships()
        for ship in ships:
            self.cur.execute("SELECT * FROM Fights WHERE (shipname1 = ? AND shipname2 = ?) OR (shipname1 = ? AND shipname2 = ?)", (shipname, ship, ship, shipname))
            if self.cur.fetchone():
                ships.remove(ship)
        return ships
        """
        ships=self.get_ships()
        wins, draws, losses = self.get_matchups(shipname, player_name)
        matchups= wins.keys() | draws.keys() | losses.keys()
        unknown_matchups = [ship for ship in ships if ship not in matchups]
        return unknown_matchups



    def export_csv(self, filename):
        # Export the database to a CSV file
        """
        self.cur.execute("SELECT shipname1, shipname2, result, author_name FROM Fights")
        with open(filename, "w",encoding="utf-8") as f:
            f.write("shipname1,shipname2,result,author_name\n")
            for row in self.cur.fetchall():
                f.write(",".join(map(str, row)) + "\n")"""

        self.cur.execute("SELECT shipname, parentid, description FROM Archetypes")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("---Archetypes---" + "\n")
            f.write("shipname,parentid,description\n")
            for row in self.cur.fetchall():
                f.write(",".join(map(str, row)) + "\n")
            f.write("\n")

            f.write("---Fights---" + "\n")
            self.cur.execute("SELECT shipname1, shipname2, result, author_name FROM Fights")
            f.write("shipname1,shipname2,result,author_name\n")
            for row in self.cur.fetchall():
                f.write(",".join(map(str, row)) + "\n")


    def export_db(self, filename):
        # copy the database to a new file
        with open(filename, "wb") as f:
            for line in self.con.iterdump():
                f.write(bytes(line, "utf-8"))


    def simulate_fight(self, shipname1, shipname2):
        # check if the ships exist
        if not self.archetype_exists(shipname1):
            raise ValueError(f"Ship '{shipname1}' does not exist in the database")
        if not self.archetype_exists(shipname2):
            raise ValueError(f"Ship '{shipname2}' does not exist in the database")
        # Check if the fight is in the database
        result_authors = {}
        #search the winners
        self.cur.execute("SELECT author_name FROM Fights WHERE (shipname1 = ? AND shipname2 = ? AND result = ?)", (shipname1, shipname2, FIGHT_RESULT.WIN))
        winners = self.cur.fetchall()
        #search the losers
        self.cur.execute("SELECT author_name FROM Fights WHERE (shipname1 = ? AND shipname2 = ? AND result = ?)", (shipname2, shipname1, FIGHT_RESULT.WIN))
        losers = self.cur.fetchall()
        #search the draws
        self.cur.execute("SELECT author_name FROM Fights WHERE ((shipname1 = ? AND shipname2 = ? AND result = ?) OR (shipname1 = ? AND shipname2 = ? AND result = ?))", (shipname1, shipname2, FIGHT_RESULT.DRAW, shipname2, shipname1, FIGHT_RESULT.DRAW))
        draws = self.cur.fetchall()

        result_authors[FIGHT_RESULT.WIN] = winners
        result_authors[FIGHT_RESULT.DRAW] = draws
        result_authors[FIGHT_RESULT.LOSE] = losers

        return result_authors

    def get_ships(self):
        self.cur.execute("SELECT DISTINCT shipname FROM Archetypes")
        ships = [row[0] for row in self.cur.fetchall()]
        leaf_ships = [ship for ship in ships if self.ship_is_leaf(ship)]
        return leaf_ships

    def get_archetypes(self):
        self.cur.execute("SELECT DISTINCT shipname FROM Archetypes")
        return [row[0] for row in self.cur.fetchall()]

    def rename_ship(self, old_name, new_name=None, new_parent_name=None, new_description=None):
        #check if the ship exists
        if not self.archetype_exists(old_name):
            raise ValueError(f"Ship '{old_name}' does not exist in the database")
        current_name = old_name
        return_message = "Changes of " + old_name + ": "

        if new_name!=None:
            #check if the new name already exists
            if self.archetype_exists(new_name):
                raise ValueError(f"Ship '{new_name}' already exists in the database")
            # Rename the ship in the database
            self.cur.execute("UPDATE Fights SET shipname1 = ? WHERE shipname1 = ?", (new_name, old_name))
            self.cur.execute("UPDATE Fights SET shipname2 = ? WHERE shipname2 = ?", (new_name, old_name))
            self.cur.execute("UPDATE Archetypes SET shipname = ? WHERE shipname = ?", (new_name, old_name))
            current_name = new_name
            return_message += " renamed to " + new_name + ", "

        if new_parent_name!=None:
            #check if the new name exists
            if not self.archetype_exists(new_parent_name):
                raise ValueError(f"Ship '{new_parent_name}' does not exist in the database")
            #Checks to preserve the tree structure
            if new_parent_name == current_name:
                raise ValueError(f"Ship cant be its own parent")
            for child in self.archetypes_children(current_name):
                if child == new_parent_name:
                    raise ValueError(f"Cant have a child as parent")

            # Rename the parent in the database
            self.cur.execute("UPDATE Archetypes SET parentid = ? WHERE shipname = ?", (self.get_ship_id(new_parent_name), current_name))
            return_message += " parent changed to " + new_parent_name + ", "

        if new_description!=None:
            self.cur.execute("UPDATE Archetypes SET description = ? WHERE shipname = ?", (new_description, old_name))
            return_message += " description changed to " + new_description

        self.con.commit()
        return return_message

    def close(self):
        self.con.close()

if(__name__=="__main__"):
    db = FightDB()
    print(db.get_fights())
    db.close()

