import sqlite3
import json
from ai_analyzer import analyze_job

DB_PATH = "data/jobs.db"


def process_jobs():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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
                    technical_match = ?,
                    education_match = ?,
                    seniority_match = ?,
                    location_match = ?,
                    visa_concern = ?,
                    eligible = ?,
                    resume = ?,
                    job_category = ?,
                    key_matches = ?,
                    key_gaps = ?,
                    resume_keywords = ?,
                    ai_reason = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                result["match_score"],
                result["technical_match"],
                int(result["education_match"]),
                int(result["seniority_match"]),
                int(result["location_match"]),
                int(result["visa_concern"]),
                int(result["eligible"]),
                result["recommended_resume"],
                result["job_category"],
                json.dumps(result["key_matches"]),
                json.dumps(result["key_gaps"]),
                json.dumps(result["resume_keywords_to_add"]),
                result["reason"],
                job_id
            ))

            conn.commit()

            print(f"Score: {result['match_score']}/100")
            print(f"Eligible: {result['eligible']}")
            print(f"Recommended Resume: {result['recommended_resume']}")
            print(f"Category: {result['job_category']}")
            print(f"Technical Match: {result['technical_match']}")
            print(f"Visa Concern: {result['visa_concern']}")
            print(f"Resume keywords to add: {result['resume_keywords_to_add']}")
            print(f"Reason: {result['reason']}")

        except Exception as e:
            print(f"ERROR: {e}")

    conn.close()

    print("\n=== AI PROCESSING COMPLETE ===")


if __name__ == "__main__":
    process_jobs()