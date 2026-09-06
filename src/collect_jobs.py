import sqlite3
from job_collector import collect_job_description

DB_PATH = "data/jobs.db"


def collect_jobs():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, company, job_title, job_url
        FROM jobs
        WHERE job_url IS NOT NULL
          AND TRIM(job_url) != ''
          AND (
              job_description IS NULL
              OR TRIM(job_description) = ''
          )
    """)

    jobs = cursor.fetchall()

    print(f"\nJobs waiting for collection: {len(jobs)}")

    for job_id, company, job_title, job_url in jobs:

        print(f"\nCollecting: {company} - {job_title}")
        print(f"URL: {job_url}")

        try:
            description = collect_job_description(job_url)

            if len(description) < 300:
                print("WARNING: Very little content collected.")
                continue

            cursor.execute("""
                UPDATE jobs
                SET
                    job_description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                description,
                job_id
            ))

            conn.commit()

            print(f"Collected {len(description)} characters.")

        except Exception as e:
            print(f"ERROR: {e}")

    conn.close()

    print("\n=== JOB COLLECTION COMPLETE ===")


if __name__ == "__main__":
    collect_jobs()