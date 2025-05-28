import sqlite3
from datetime import datetime

DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'uz',
                    power INTEGER DEFAULT 0,
                    coins INTEGER DEFAULT 0,
                    last_arise TEXT
                )''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        c.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
    conn.close()

def get_language(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    lang = c.fetchone()
    conn.close()
    return lang[0] if lang else 'uz'

def update_language(user_id, language):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
    conn.commit()
    conn.close()

def get_profile(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT power, coins FROM users WHERE user_id = ?', (user_id,))
    profile = c.fetchone()
    conn.close()
    return {"power": profile[0], "coins": profile[1]} if profile else {"power": 0, "coins": 0}

def spend_coins(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT coins FROM users WHERE user_id = ?', (user_id,))
    coins = c.fetchone()
    if coins and coins[0] >= amount:
        c.execute('UPDATE users SET coins = coins - ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_top_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT user_id, power, coins FROM users ORDER BY power DESC LIMIT 10''')
    users = c.fetchall()
    conn.close()
    return users

def can_use_arise(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT last_arise FROM users WHERE user_id = ?', (user_id,))
    last_arise = c.fetchone()
    if last