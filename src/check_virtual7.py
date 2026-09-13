import sqlite3

conn = sqlite3.connect("data/jobs.db")
cur = conn.cursor()

cur.execute("""
    SELECT company, job_title, match_score, eligible, resume,
           key_matches, key_gaps, ai_reason
    FROM jobs
    WHERE job_title LIKE '%Kubernetes Administrator%'
""")

for row in cur.fetchall():
    company, title, score, eligible, resume, key_matches, key_gaps, reason = row
    print(f"Company     : {company}")
    print(f"Title       : {title}")
    print(f"Score       : {score}")
    print(f"Eligible    : {eligible}")
    print(f"Resume      : {resume}")
    print(f"Key matches : {key_matches}")
    print(f"Key gaps    : {key_gaps}")
    print(f"Reason      : {reason}")

conn.close()