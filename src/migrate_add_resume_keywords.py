"""
One-time migration: adds a `resume_keywords` column to the jobs table.

This is separate from `key_gaps`, which stays as-is (broad context on
why a score/eligibility came out the way it did — including hard
blockers like years-of-experience or language requirements that no
resume wording can fix).

`resume_keywords` is narrower and specifically safe to act on: exact
terms/phrasing from the job description that line up with skills the
candidate genuinely already has, just not worded that way on the
resume yet. Nothing here should ever be a skill the candidate doesn't
actually have.

Run once from the project root:

    python src/migrate_add_resume_keywords.py
"""

import sqlite3

DB_PATH = "data/jobs.db"


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(jobs)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "resume_keywords" in existing_columns:
        print("resume_keywords column already exists — nothing to do.")
        conn.close()
        return

    cursor.execute("ALTER TABLE jobs ADD COLUMN resume_keywords TEXT")
    conn.commit()
    conn.close()

    print("Migration complete: resume_keywords column added.")


if __name__ == "__main__":
    migrate()