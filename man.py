import sqlite3

conn = sqlite3.connect('careconnect.db')  # Use correct DB
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# Create table if missing
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    aadhaar TEXT PRIMARY KEY,
    name TEXT,
    age INTEGER,
    gender TEXT
)
""")

# Try adding the phone column
try:
    cursor.execute("ALTER TABLE patients ADD COLUMN phone TEXT")
    print("✅ 'phone' column added to 'patients' table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ 'phone' column already exists.")
    else:
        raise

conn.commit()
conn.close()
