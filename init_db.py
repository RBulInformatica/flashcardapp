import sqlite3
import csv
import os

DB_PATH = "database.db"
CSV_PATH = "afweerbegrippen.csv"  # vervang dit door de naam van je CSV-bestand

def init_db():
    if os.path.exists(DB_PATH):
        print("Database bestaat al. Overslaan.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Maak de tabel aan
    c.execute('''
        CREATE TABLE immuunsysteem (
            Begrip TEXT,
            Betekenis TEXT
        )
    ''')

    # Voeg data toe vanuit CSV
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                c.execute("INSERT INTO immuunsysteem (Begrip, Betekenis) VALUES (?, ?)", (row[0], row[1]))

    conn.commit()
    conn.close()
    print("Database aangemaakt.")

if __name__ == '__main__':
    init_db()
