import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect("financials.db")
cursor = conn.cursor()

# Create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS quarterly_financials (
    id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter TEXT NOT NULL,
    revenue_millions INTEGER NOT NULL,
    profit_millions INTEGER NOT NULL,
    UNIQUE(year, quarter)
)
""")

# Sample data
data = [
    (2023, 'Q1', 85000, 23000),
    (2023, 'Q2', 88000, 25000),
    (2023, 'Q3', 92000, 28000),
    (2023, 'Q4', 95000, 29000),
    (2024, 'Q1', 98000, 31000),
    (2024, 'Q2', 101000, 33000),
]

# Insert data, ignoring if it already exists
cursor.executemany("INSERT OR IGNORE INTO quarterly_financials (year, quarter, revenue_millions, profit_millions) VALUES (?, ?, ?, ?)", data)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database 'financials.db' is set up with sample data.")
