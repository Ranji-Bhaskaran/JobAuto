import sqlite3
import pandas as pd
from pathlib import Path

EXCEL_PATH = "Ranjith_Job_Tracker.xlsx"
DB_PATH = Path("data/jobs.db")


def import_jobs():
    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name="Job Tracker"
    )

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Keep only actual job rows
    df = df[df["Company"].notna()]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    imported = 0
    skipped = 0

    for _, row in df.iterrows():

        company = str(row.get("Company", "")).strip()
        job_title = str(row.get("Job title", "")).strip()
        location = str(row.get("Location", "")).strip()

        job_url = row.get("Job URL")

        if pd.isna(job_url):
            job_url = None
        else:
            job_url = str(job_url).strip()

                # Check whether this job already exists
        if job_url:
            cursor.execute(
                "SELECT id FROM jobs WHERE job_url = ?",
                (job_url,)
            )
        else:
            # If there is no URL, use company + job title + location
            cursor.execute(
                """
                SELECT id
                FROM jobs
                WHERE company = ?
                  AND job_title = ?
                  AND location = ?
                """,
                (company, job_title, location)
            )

        if cursor.fetchone():
            skipped += 1
            continue

        cursor.execute("""
            INSERT INTO jobs (
                company,
                job_title,
                location,
                job_url,
                job_category,
                salary,
                resume,
                application_status,
                priority,
                applied_date,
                follow_up_date,
                date_found,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company,
            job_title,
            location,
            job_url,
            row.get("Job category"),
            row.get("Salary"),
            row.get("Resume"),
            row.get("Application status"),
            row.get("Priority"),
            row.get("Applied date"),
            row.get("Follow-up date"),
            row.get("Date found"),
            row.get("Notes")
        ))

        imported += 1

    conn.commit()

    # Count total jobs
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total = cursor.fetchone()[0]

    conn.close()

    print("\n=== IMPORT COMPLETE ===")
    print(f"New jobs imported : {imported}")
    print(f"Duplicates skipped : {skipped}")
    print(f"Total jobs in DB   : {total}")


if __name__ == "__main__":
    import_jobs()