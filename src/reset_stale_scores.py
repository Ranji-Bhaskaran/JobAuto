import sqlite3

conn = sqlite3.connect("data/jobs.db")
cur = conn.cursor()

cur.execute("""
    UPDATE jobs
    SET match_score = NULL
    WHERE match_score IS NOT NULL
      AND (resume_keywords IS NULL OR TRIM(resume_keywords) = '')
""")

conn.commit()
print(f"Rows reset for reprocessing: {cur.rowcount}")
conn.close()