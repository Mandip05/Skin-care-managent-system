import sqlite3
import os
from datetime import datetime
from pathlib import Path
import shutil
import logging

class DatabaseManager:
    def __init__(self, db_name="wecare.db"):
        self.db_name = db_name
        self.backup_folder = "wecare_backups"
        self.init_database()

    def init_database(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        full_name TEXT NOT NULL,
                        phone TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        product_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        brand TEXT NOT NULL,
                        category TEXT NOT NULL,
                        subcategory TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        cost_price REAL NOT NULL,
                        origin TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS customers (
                        customer_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT,
                        phone TEXT,
                        address TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS purchases (
                        purchase_id TEXT PRIMARY KEY,
                        customer_id TEXT,
                        product_id TEXT,
                        quantity INTEGER NOT NULL,
                        total REAL NOT NULL,
                        payment_method TEXT NOT NULL,
                        purchase_date TEXT NOT NULL,
                        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                        FOREIGN KEY (product_id) REFERENCES products(product_id)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recovery_codes (
                        username TEXT,
                        code TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (username) REFERENCES users(username)
                    )
                """)
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                                  ('admin', 'password123', 'admin@wecare.com', 'Administrator', '12345'))
                conn.commit()
                logging.info("Database initialized successfully")
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")

    def backup_database(self):
        try:
            Path(self.backup_folder).mkdir(exist_ok=True)
            backup_file = f"{self.backup_folder}/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy(self.db_name, backup_file)
            logging.info(f"Database backed up to {backup_file}")
        except Exception as e:
            logging.error(f"Database backup error: {e}")