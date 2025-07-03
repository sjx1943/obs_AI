import sqlite3
import csv

conn = sqlite3.connect('question_bank.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)''')

with open('questions.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        c.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (row[0], row[1]))

conn.commit()
conn.close()