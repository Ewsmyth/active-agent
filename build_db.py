import os
import sqlite3

def build_database():
    # Check if the database file exists
    if not os.path.exists('active-agent-db.db'):
        # Connect to SQLite database (creates if not exists)
        conn = sqlite3.connect('active-agent-db.db')
        c = conn.cursor()
        
        # Create a table for users
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY,
                     username TEXT UNIQUE,
                     password TEXT
                     )''')

        # Create a table for posts
        c.execute('''CREATE TABLE IF NOT EXISTS posts (
                     id INTEGER PRIMARY KEY,
                     comment TEXT CHECK(length(comment) <= 120),
                     picture TEXT CHECK(length(picture) <= 255)
                     )''')
        
        # Commit changes and close connection
        conn.commit()
        conn.close()

if __name__ == "__main__":
    build_database()
