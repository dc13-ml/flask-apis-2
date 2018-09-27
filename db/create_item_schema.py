import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

# Create a user table
create_table = "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name text, price real)"
cursor.execute(create_table)

connection.commit()
connection.close()
