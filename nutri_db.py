import sqlite3

# Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect("nutri.db")
c = conn.cursor()

# ==============================
# Users Table
# ==============================
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    height REAL,
    weight REAL,
    activity TEXT,
    bmi REAL,
    bmr REAL,
    daily_cal REAL
)
""")

# ==============================
# Food Logs Table
# ==============================
c.execute("""
CREATE TABLE IF NOT EXISTS food_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    food_name TEXT,
    quantity REAL,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# ==============================
# Commit and Close
# ==============================
conn.commit()
conn.close()

print("nutri.db created successfully!")