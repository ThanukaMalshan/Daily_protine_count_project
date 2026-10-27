import sqlite3

def get_connection():
    return sqlite3.connect("protein_tracker.db")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_name TEXT UNIQUE,
            weight REAL,
            height REAL,
            goal TEXT,
            target_protein REAL,
            target_calories REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT UNIQUE,
            protein_per_100g REAL,
            calories_per_100g REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_name TEXT,
            food_name TEXT,
            grams REAL,
            total_protein REAL,
            total_calories REAL,
            meal_type TEXT,
            log_date TEXT DEFAULT (DATE('now', 'localtime'))
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_default_foods():
    conn = get_connection()
    cursor = conn.cursor()
    defaults = [
        ("chicken breast", 31.0, 165.0),
        ("rice", 2.7, 130.0),
        ("dhal", 8.0, 116.0),
        ("egg", 13.0, 155.0),
        ("milk", 3.4, 42.0)
    ]
    for food, p, c in defaults:
        cursor.execute("INSERT OR IGNORE INTO food_master (food_name, protein_per_100g, calories_per_100g) VALUES (?, ?, ?)", (food, p, c))
    conn.commit()
    conn.close()

def save_user_profile(profile_name, weight, height, goal, target_protein, target_calories):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_profile (id, profile_name, weight, height, goal, target_protein, target_calories)
        VALUES (
            (SELECT id FROM user_profile WHERE profile_name = ?),
            ?, ?, ?, ?, ?, ?
        )
    """, (profile_name, profile_name, weight, height, goal, target_protein, target_calories))
    conn.commit()
    conn.close()

def get_all_profiles():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_name, weight, height, goal, target_protein, target_calories FROM user_profile")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_food_item(food_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT protein_per_100g, calories_per_100g FROM food_master WHERE food_name = ?", (food_name,))
    row = cursor.fetchone()
    conn.close()
    return row

def add_new_food(food_name, p_100g, c_100g):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO food_master (food_name, protein_per_100g, calories_per_100g) VALUES (?, ?, ?)", (food_name, p_100g, c_100g))
    conn.commit()
    conn.close()

def get_all_foods():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT food_name, protein_per_100g, calories_per_100g FROM food_master")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_food_item(food_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_master WHERE food_name = ?", (food_name,))
    conn.commit()
    conn.close()

def add_daily_log(profile_name, food_name, grams, total_protein, total_calories, meal_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO daily_log (profile_name, food_name, grams, total_protein, total_calories, meal_type) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (profile_name, food_name, grams, total_protein, total_calories, meal_type))
    conn.commit()
    conn.close()

def get_today_summary(profile_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(total_protein), SUM(total_calories) 
        FROM daily_log 
        WHERE profile_name = ? AND log_date = DATE('now', 'localtime')
    """, (profile_name,))
    row = cursor.fetchone()
    conn.close()
    return (row[0] or 0.0, row[1] or 0.0)

def get_today_logs(profile_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, meal_type, food_name, grams, total_protein, total_calories 
        FROM daily_log 
        WHERE profile_name = ? AND log_date = DATE('now', 'localtime')
    """, (profile_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_streak(profile_name):
    return 1

def delete_profile(profile_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_profile WHERE profile_name = ?", (profile_name,))
    conn.commit()
    conn.close()

def delete_log(log_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_log WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()

def get_range_totals(profile_name, days):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT log_date, SUM(total_protein), SUM(total_calories) 
        FROM daily_log 
        WHERE profile_name = ? AND log_date >= DATE('now', '-' || ? || ' days', 'localtime')
        GROUP BY log_date
    """, (profile_name, days))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: (row[1], row[2]) for row in rows}