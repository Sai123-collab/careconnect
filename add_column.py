import sqlite3

# Connect to your database
conn = sqlite3.connect('careconnect.db')
cursor = conn.cursor()

# Add 'report_file' column if it doesn't already exist
try:
    cursor.execute('ALTER TABLE checkups ADD COLUMN report_file TEXT')
    print("✅ 'report_file' column added to 'checkups' table.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ Column 'report_file' already exists.")
    else:
        print(f"❌ Error: {e}")

conn.commit()
conn.close()
