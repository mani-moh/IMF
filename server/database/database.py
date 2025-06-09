import sqlite3

def execute(query, params = (), commit = False):
    conn = sqlite3.connect('imf.sqlite')
    cursor = conn.cursor()
    try:
        if not params  == ():
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if commit:
            conn.commit()
        return cursor
    except sqlite3.Error as e:
        print(f"sqlite error: {e}")
        conn.rollback()
    finally:
        conn.close()

def init_db():
    print("Initializing database...")
    execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password BLOB NOT NULL,
    first_name TEXT NOT NULL ,
    last_name TEXT NOT NULL ,
    user_type TEXT DEFAULT 'agent',
    personnel_files_access BOOLEAN DEFAULT False,
    nuclear_codes_access BOOLEAN DEFAULT False,
    biological_files_access BOOLEAN DEFAULT False
);

    ''', commit = True)
    execute('''
                    CREATE TABLE IF NOT EXISTS groups (
                        group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_name TEXT NOT NULL UNIQUE,
                        creator_id INTEGER NOT NULL,
                        FOREIGN KEY (creator_id) REFERENCES users(id)
                    );
                ''', commit=True)
    execute('''
    CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                recipient_id INTEGER,
                group_id INTEGER,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id),
                FOREIGN KEY (recipient_id) REFERENCES users(id),
                FOREIGN KEY (group_id) REFERENCES groups(group_id)
                );
    ''', commit = True)

    execute('''
                CREATE TABLE IF NOT EXISTS group_members (
                    group_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    PRIMARY KEY (group_id, user_id),
                    FOREIGN KEY (group_id) REFERENCES groups(group_id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            ''', commit = True)

if __name__ == '__main__':
    init_db()