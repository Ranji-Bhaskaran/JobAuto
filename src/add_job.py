import sqlite3
from datetime import date

DB_PATH = "data/jobs.db"


def add_job():
    company = input("Company: ").strip()
    job_title = input("Job title: ").strip()
    location = input("Location: ").strip()
    job_url = input("Job URL: ").strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check for duplicate URL
    cursor.execute(
        "SELECT id FROM jobs WHERE job_url = ?",
        (job_url,)
    )

    existing = cursor.fetchone()

    if existing:
        print(f"\nJob already exists with ID: {existing[0]}")
        conn.close()
        return

    cursor.execute("""
        INSERT INTO jobs (
            company,
            job_title,
            location,
            job_url,
            source,
            application_status,
            date_found
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        company,
        job_title,
        location,
        job_url,
        "Manual Test",
        "Not Applied",
        date.today().isoformat()
    ))

    conn.commit()

    job_id = cursor.lastrowid

    conn.close()

    print(f"\nJob added successfully!")
    print(f"Job ID: {job_id}")


if __name__ == "__main__":
    add_job()