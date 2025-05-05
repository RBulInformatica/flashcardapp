import sqlite3
import csv

DB_NAME = "database.db"
CSV_FILE = "afweerbegrippen.csv"

# Maak database en tabel aan
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS immuunsysteem (
        Begrip TEXT NOT NULL,
        Betekenis TEXT NOT NULL
    )
""")

# Vul de tabel met data uit CSV
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = [(row['Begrip'], row['Betekenis']) for row in reader]

cursor.executemany("INSERT INTO immuunsysteem (Begrip, Betekenis) VALUES (?, ?)", rows)
conn.commit()
conn.close()

print("Database succesvol opgebouwd vanuit CSV.")
