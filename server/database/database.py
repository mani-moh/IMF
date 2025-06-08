import sqlite3

def execute(query, params = (), commit = False):
    conn = sqlite3.connect('imf.sqlite')
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()
        return cursor
    except sqlite3.Error as e:
        conn.rollback()
    finally:
        conn.close()
