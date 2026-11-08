import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / "vectordb" / "chroma.sqlite3"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("Collections")
print("=" * 60)

cursor.execute("SELECT * FROM collections;")

for row in cursor.fetchall():
    print(row)

print("\n")

print("=" * 60)
print("Embedding Count")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM embeddings;")

print(cursor.fetchone()[0])

conn.close()