import sqlite3
from pathlib import Path

DB_PATH = Path("data/jobs.db")


def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company TEXT NOT NULL,
            job_title TEXT NOT NULL,
            location TEXT,

            job_url TEXT UNIQUE,

            source TEXT,
            job_category TEXT,
            work_type TEXT,
            work_arrangement TEXT,

            salary TEXT,
            visa_eligibility TEXT,

            match_score INTEGER,
            technical_match INTEGER,
            education_match INTEGER,
            seniority_match INTEGER,
            location_match INTEGER,
            visa_concern INTEGER,
            eligible INTEGER,

            priority TEXT,
            resume TEXT,

            application_status TEXT,
            applied_date TEXT,
            follow_up_date TEXT,

            interview_stage TEXT,
            rejection_date TEXT,

            job_description TEXT,

            key_matches TEXT,
            key_gaps TEXT,
            resume_keywords TEXT,
            ai_reason TEXT,

            tailored INTEGER DEFAULT 0,
            cover_letter INTEGER DEFAULT 0,

            date_found TEXT,
            notes TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    create_database()