import sqlite3

with sqlite3.connect("database.db") as con:
    c = con.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE ,
            first_name VARCHAR (20) NOT NULL,
            last_name VARCHAR (20) NOT NULL,
            username VARCHAR (20) NOT NULL,
            position_name VARCHAR (20) NOT NULL
            )""")

con.commit()
con.close()





