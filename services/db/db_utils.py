import sqlite3
import aiosqlite
import os

DATABASE = os.getenv("DATABASE", "sqlite")


def init_db():
    # Check if table exists
    with sqlite3.connect(f"services/db/{DATABASE}.db") as db:
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


async def save_data_to_db(bot, chat_id, notification, state):
    async with aiosqlite.connect(f"services/db/{DATABASE}.db") as db:
        await db.execute("""
            INSERT INTO messages (state, bot, notification, chat_id)
            VALUES (?, ?, ?, ?)
        """, (state, bot, notification, chat_id))
        await db.commit()
