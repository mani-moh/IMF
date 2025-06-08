import bcrypt
import sqlite3

conn = sqlite3.connect('imf.sqlite')
cursor = conn.cursor()
words = input("enter: username password firstname lastname\n").split()
hashed_password = bcrypt.hashpw(words[1].encode(), bcrypt.gensalt())
cursor.execute('''
    INSERT INTO users (username, hashed_password, first_name, last_name) VALUES (?, ?, ?, ?)
''',(words[0], hashed_password, words[2], words[3]))
conn.commit()
conn.close()