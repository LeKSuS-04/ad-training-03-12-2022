import sqlite3
from flask import g


DATABASE = 'data/data.db'


def get_db():
    db = g.get('database', None)
    if db is None:
        db = g.database = sqlite3.connect(DATABASE)
    return db


def init_db():
    with sqlite3.connect(DATABASE) as db:
        cur = db.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY NOT NULL,
            password TEXT NOT NULL
        );
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS shporas (
            id TEXT PRIMARY KEY NOT NULL,
            owner TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            is_public INTEGER NOT NULL,
            is_protected INTEGER NOT NULL,
            password TEXT
        );
        ''')
        
