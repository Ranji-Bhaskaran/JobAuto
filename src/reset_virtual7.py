import sqlite3

conn = sqlite3.connect("data/jobs.db")
cur = conn.cursor()

cur.execute("""
    UPDATE jobs
    SET match_score = NULL
    WHERE job_title LIKE '%Kubernetes Administrator%'
""")

conn.commit()
print(f"Rows reset: {cur.rowcount}")
conn.close()