import sqlite3
import json
from ai_analyzer import analyze_job

DB_PATH = "data/jobs.db"


def process_jobs():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find jobs that have not been analyzed yet
    cursor.execute("""
        SELECT id, company, job_title, job_description
        FROM jobs
        WHERE job_description IS NOT NULL
          AND TRIM(job_description) != ''
          AND match_score IS NULL
    """)

    jobs = cursor.fetchall()

    print(f"\nJobs waiting for AI analysis: {len(jobs)}")

    for job_id, company, job_title, job_description in jobs:

        print(f"\nAnalyzing: {company} - {job_title}")

        try:
            result = analyze_job(job_description)

            cursor.execute("""
                UPDATE jobs
                SET
                    match_score = ?,
                    resume = ?,
                    job_category = ?,
                    ai_reason = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                result["match_score"],
                result["recommended_resume"],
                result["job_category"],
                result["reason"],
                job_id
            ))

            conn.commit()

            print(f"Score: {result['match_score']}")
            print(f"Resume: {result['recommended_resume']}")
            print(f"Category: {result['job_category']}")

        except Exception as e:
            print(f"ERROR: {e}")

    conn.close()

    print("\n=== AI PROCESSING COMPLETE ===")


if __name__ == "__main__":
    process_jobs()