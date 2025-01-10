import sqlite3
import aiosqlite
import os  # Missing import for os.path.exists and os.getenv

DATABASE = os.getenv("DATABASE", "messages.db")

def init_db():
    # Ensure database file exists
    __create_db_file()
    
    # Check if table exists
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT count(name) FROM sqlite_master 
            WHERE type='table' AND name='messages'
        """)
        
        # Create table only if it doesn't exist
        if cursor.fetchone()[0] == 0:
            db.execute("""
                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state TEXT NOT NULL,
                    bot TEXT NOT NULL, 
                    notification BOOLEAN NOT NULL,
                    chat_id INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.commit()
            
def __create_db_file():
    # Check if database file exists
    if not os.path.exists(DATABASE):
        # Create empty file
        open(DATABASE, 'a').close()

async def save_data_to_db(bot, chat_id, notification, state):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("""
            INSERT INTO messages (state, bot, notification, chat_id)
            VALUES (?, ?, ?, ?)
        """, (state, bot, notification, chat_id))
        await db.commit()