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
        self.con.commit()
    
    def insert_fight(self, shipname1, shipname2, author, author_name, result):
        # Check if shipname1 and shipname2 exist in the database
        if not self.ship_exists(shipname1):
            raise ValueError(f"Ship '{shipname1}' does not exist in the database")
        if not self.ship_exists(shipname2):
            raise ValueError(f"Ship '{shipname2}' does not exist in the database")
        
        self.cur.execute("SELECT id FROM Fights WHERE (shipname1 = ? AND shipname2 = ? AND author = ?) OR (shipname1 = ? AND shipname2 = ? AND author = ?)", 
                         (shipname1, shipname2, author, shipname2, shipname1, author))
        existing_fight = self.cur.fetchone()
        
        if existing_fight:# Remove the existing fight
            print("Removing existing fight")
            self.cur.execute("DELETE FROM Fights WHERE id = ?", (existing_fight[0],))
        
        # Insert the new fight
        self.cur.execute("INSERT INTO Fights (shipname1, shipname2, author, author_name, result) VALUES (?, ?, ?, ?, ?)", (shipname1, shipname2, author, author_name, result))
        self.con.commit()

    def ship_exists(self, shipname):
        self.cur.execute("SELECT 1 FROM Fights WHERE shipname1 = ? OR shipname2 = ?", (shipname, shipname))
        return bool(self.cur.fetchone())

    def remove_fight(self, shipname1, shipname2, author):
        # Remove the fight between shipname1 and shipname2 with the specified author
        self.cur.execute("DELETE FROM Fights WHERE (shipname1 = ? AND shipname2 = ? AND author = ?) OR (shipname1 = ? AND shipname2 = ? AND author = ?)", 
                         (shipname1, shipname2, author, shipname2, shipname1, author))
        self.con.commit()
    
    def add_ship(self, shipname, author, author_name):
        # Add a fight where the ship fights against itself
        if not self.ship_exists(shipname):
            self.cur.execute("INSERT INTO Fights (shipname1, shipname2, author, author_name, result) VALUES (?, ?, ?, ?, ?)", (shipname, shipname, author, author_name, FIGHT_RESULT.DRAW))
            self.con.commit()
    
    def get_fights(self):
        self.cur.execute("SELECT * FROM Fights")
        return self.cur.fetchall()
    
    def get_matchups(self, ship_name):
        wins={}
        draws={}
        losses={}
        # Get all fights where the specified ship is involved
        if not self.ship_exists(ship_name):
            raise ValueError(f"Ship '{ship_name}' does not exist in the database")
        self.cur.execute("SELECT shipname1, shipname2, author_name, result FROM Fights WHERE (shipname1 = ? OR shipname2 = ?)", (ship_name, ship_name))
        fight_data = self.cur.fetchall()
        # Iterate over each fight data
        for ship1,ship2, author_name, result in fight_data:
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
    def get_unknown_matchups(self, shipname):
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
        wins, draws, losses = self.get_matchups(shipname)
        matchups= wins.keys() | draws.keys() | losses.keys()
        for ship in ships:
            if ship not in matchups:
                ships.remove(ship)
        return ships



    def export_csv(self, filename):
        # Export the database to a CSV file
        self.cur.execute("SELECT shipname1, shipname2, result, author_name FROM Fights")
        with open(filename, "w",encoding="utf-8") as f:
            f.write("shipname1,shipname2,result,author_name\n")
            for row in self.cur.fetchall():
                f.write(",".join(map(str, row)) + "\n")
    
    def simulate_fight(self, shipname1, shipname2):
        # check if the ships exist
        if not self.ship_exists(shipname1):
            raise ValueError(f"Ship '{shipname1}' does not exist in the database")
        if not self.ship_exists(shipname2):
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
        self.cur.execute("SELECT DISTINCT shipname1 FROM Fights")
        return [row[0] for row in self.cur.fetchall()]
    
    def close(self):
        self.con.close()

if(__name__=="__main__"):
    db = FightDB()
    print(db.get_fights())
    db.close()