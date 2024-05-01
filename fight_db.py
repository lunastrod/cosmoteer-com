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
    
    def get_counters(self, ship_name):
        counters = {}
        
        # Get all fights where the specified ship is involved
        print(ship_name, FIGHT_RESULT.WIN)
        if not self.ship_exists(ship_name):
            raise ValueError(f"Ship '{ship_name}' does not exist in the database")

        self.cur.execute("SELECT shipname1, author_name FROM Fights WHERE (shipname2 = ? AND result = ?)", (ship_name, FIGHT_RESULT.WIN))
        fight_data = self.cur.fetchall()
        print(fight_data)
        # Iterate over each fight data
        for ship1, author_name in fight_data:
            if ship1 in counters:
                counters[ship1].append(author_name)
            else:
                counters[ship1] = [author_name]
        return counters
    
    def simulate_fight(self, shipname1, shipname2):
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
    #print(db.get_counters("ion rammer"))
    print(db.get_counters("ion cruiser"))
    db.close()