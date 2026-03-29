# ===============================
# TEMPORARY MIGRATION SCRIPT
# Purpose:
# Move course data from courses.json → lms.db
# Run ONLY ONCE, then DELETE this code
# ===============================
import json
import sqlite3

conn = sqlite3.connect("lms.db")
cursor = conn.cursor()

with open("courses.json") as f:
    courses = json.load(f)

for course in courses:
    cursor.execute("""
        INSERT INTO courses (title, description, price, image, duration, age)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        course["title"],
        course["description"],
        course["price"],
        course["image"],
        course["duration"],
        course["age"]
    ))

conn.commit()
conn.close()

print("Data migrated successfully!")



# ===============================
# IMPORTANT:
# After successful run:
# 1. Check database
# 2. DELETE this script
# ===============================