
import sqlite3
import os



DATABASE_PATH = "HintAI/data/hintai.db"



# ==========================================
# CONNEXION
# ==========================================

def get_connection():

    os.makedirs(
        "HintAI/data",
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE_PATH
    )



# ==========================================
# CREATION TABLES
# ==========================================

def init_database():

    conn = get_connection()

    cursor = conn.cursor()



    # utilisateurs

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        user_id TEXT PRIMARY KEY,
        username TEXT,

        credits INTEGER DEFAULT 30,
        xp INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0

    )
    """)



    # exercices

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercises (

        exercise_id TEXT PRIMARY KEY,

        user_id TEXT,

        subject TEXT,
        level TEXT,

        content TEXT,

        created_at TEXT

    )
    """)



    # messages chat

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (

        message_id TEXT PRIMARY KEY,

        exercise_id TEXT,

        role TEXT,

        content TEXT,

        created_at TEXT

    )
    """)



    # compétences

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (

        skill_id TEXT PRIMARY KEY,

        user_id TEXT,

        name TEXT,

        level INTEGER

    )
    """)



    conn.commit()

    conn.close()



# ==========================================
# AJOUT MESSAGE
# ==========================================

def save_message(
    message_id,
    exercise_id,
    role,
    content,
    created_at
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
    """
    INSERT INTO chat_history
    VALUES (?,?,?,?,?)
    """,
    (
        message_id,
        exercise_id,
        role,
        content,
        created_at
    )
    )


    conn.commit()

    conn.close()



# ==========================================
# RECUPERATION HISTORIQUE
# ==========================================

def get_history(exercise_id):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
    """
    SELECT role,content
    FROM chat_history

    WHERE exercise_id=?

    ORDER BY created_at

    """,
    (exercise_id,)
    )


    data = cursor.fetchall()


    conn.close()


    return data



# Initialisation automatique

init_database()

