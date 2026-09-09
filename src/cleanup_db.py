"""
One-time cleanup for jobs.db.

Removes:
  1. The legend row that got imported from the xlsx legend cell
     (import_excel.py doesn't currently distinguish it from a real job).
  2. Stale rows saved by an earlier, less-strict version of
     job_discovery.py that would be rejected under the current
     EXCLUDED_TITLE_TERMS rules (e.g. "SRE Manager").

Matched by content, not hardcoded row id, so this is safe to run
even if your local ids differ from what was in the uploaded copy.
Run once from the project root:

    python src/cleanup_db.py
"""

import sqlite3

DB_PATH = "data/jobs.db"


def cleanup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    removed = 0

    # 1. The legend-row import bug.
    cursor.execute(
        """
        DELETE FROM jobs
        WHERE company LIKE 'Legend:%'
        """
    )
    removed += cursor.rowcount

    # 2. Rows that would be excluded under the CURRENT
    #    EXCLUDED_TITLE_TERMS but got saved by an older
    #    version of job_discovery.py.
    excluded_terms = [
        "senior", "sr.", "lead", "staff", "principal",
        "manager", "director", "head of", "vice president",
        "chief", "vp ",
    ]

    cursor.execute("SELECT id, job_title FROM jobs")
    rows = cursor.fetchall()

    stale_ids = []
    for job_id, title in rows:
        if not title:
            continue
        lowered = title.lower()
        if any(term in lowered for term in excluded_terms):
            stale_ids.append(job_id)

    if stale_ids:
        cursor.executemany(
            "DELETE FROM jobs WHERE id = ?",
            [(i,) for i in stale_ids],
        )
        removed += len(stale_ids)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    remaining = cursor.fetchone()[0]

    conn.close()

    print("\n=== DB CLEANUP COMPLETE ===")
    print(f"Rows removed   : {removed}")
    print(f"Rows remaining : {remaining}")


if __name__ == "__main__":
    cleanup()