import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import date


DB_PATH = "data/jobs.db"


# =========================================================
# TARGET JOB KEYWORDS
# =========================================================

TARGET_TERMS = [

    # -------------------------
    # CLOUD / DEVOPS
    # -------------------------
    "cloud engineer",
    "cloud operations",
    "cloud support",
    "cloud infrastructure",
    "cloud administrator",
    "cloud automation",
    "aws engineer",
    "aws cloud",
    "devops",
    "devops engineer",
    "devops developer",
    "platform engineer",
    "platform developer",
    "infrastructure engineer",
    "infrastructure automation",
    "site reliability engineer",
    "sre",
    "reliability engineer",
    "systems engineer",
    "cloud security",
    "devsecops",

    # -------------------------
    # KUBERNETES / CONTAINERS
    # -------------------------
    "kubernetes engineer",
    "kubernetes administrator",
    "kubernetes",
    "docker",
    "container engineer",

    # -------------------------
    # SOFTWARE / PYTHON
    # -------------------------
    "python developer",
    "python engineer",
    "python software engineer",
    "software engineer",
    "software developer",
    "backend developer",
    "backend engineer",
    "automation engineer",
    "automation developer",
    "python automation",
    "api developer",
    "application engineer",

    # -------------------------
    # SUPPORT / OPERATIONS
    # -------------------------
    "technical support",
    "technical support engineer",
    "support engineer",
    "application support",
    "application support engineer",
    "cloud support engineer",
    "systems support",
    "system support",
    "it support",
    "it support engineer",
    "it operations",
    "technical operations",
    "operations engineer",

    # -------------------------
    # QA / TESTING
    # -------------------------
    "qa engineer",
    "qa tester",
    "quality assurance",
    "test engineer",
    "software tester",
    "automation tester",
    "qa automation",

    # -------------------------
    # DATA CENTRE / INFRASTRUCTURE
    # -------------------------
    "data centre",
    "data center",
    "data centre technician",
    "data center technician",
    "data centre engineer",
    "data center engineer",
    "infrastructure technician",
    "infrastructure technician",
    "hardware technician",
    "noc engineer",
    "network operations",
    "network operations engineer",
]


# =========================================================
# DEFINITE SENIOR / MANAGEMENT EXCLUSIONS
# =========================================================

EXCLUDED_TITLE_TERMS = [
    "senior",
    "sr.",
    "sr ",
    "lead",
    "team lead",
    "tech lead",
    "technical lead",
    "staff",
    "principal",
    "manager",
    "engineering manager",
    "sre manager",
    "devops manager",
    "cloud manager",
    "director",
    "head of",
    "vice president",
    "vp ",
    "chief",
    "architect manager",
]


# =========================================================
# EXPERIENCE TERMS
#
# These aren't automatically rejected because some companies
# use "experienced" loosely.
#
# Gemini will make the final eligibility decision.
# =========================================================

HIGH_EXPERIENCE_TERMS = [
    "5+ years",
    "6+ years",
    "7+ years",
    "8+ years",
    "9+ years",
    "10+ years",
    "10 years",
]


# =========================================================
# JUNIOR / ENTRY LEVEL TERMS
# =========================================================

ENTRY_LEVEL_TERMS = [
    "graduate",
    "new graduate",
    "recent graduate",
    "entry level",
    "entry-level",
    "junior",
    "jr.",
    "jr ",
    "associate",
    "trainee",
    "apprentice",
    "early career",
    "early-career",
]


# =========================================================
# IRELAND LOCATION TERMS
# =========================================================

IRELAND_TERMS = [
    "ireland",
    "dublin",
    "cork",
    "galway",
    "limerick",
    "kildare",
    "meath",
    "waterford",
    "kilkenny",
    "wicklow",
    "sligo",
    "athlone",
    "maynooth",
    "naas",
]


# =========================================================
# EUROPEAN REMOTE TERMS
# =========================================================

EUROPE_REMOTE_TERMS = [
    "europe",
    "european union",
    "european economic area",
    "eea",
    "eu/eea",
    "emea",
    "europe only",
    "europe-wide",
    "remote - europe",
    "remote europe",
    "remote in europe",
    "based in europe",
    "anywhere in europe",
]


# =========================================================
# WORLDWIDE / UNSPECIFIED REMOTE TERMS
#
# Remotive in particular tags most listings this way
# instead of naming a region. We can't confirm Ireland/EU
# eligibility from this alone, so we let it through and
# Gemini verifies eligibility later from the actual
# job description.
# =========================================================

WORLDWIDE_REMOTE_TERMS = [
    "worldwide",
    "anywhere",
    "global",
    "any location",
    "location independent",
    "remote - worldwide",
    "remote worldwide",
]


# =========================================================
# DEFINITELY NOT USEFUL LOCATION TERMS
# =========================================================

EXCLUDED_LOCATION_TERMS = [
    "united states",
    "usa",
    "u.s.",
    "canada",
    "australia",
    "new zealand",
    "india only",
    "uk only",
    "united kingdom only",
]


# =========================================================
# HTTP SESSION
# =========================================================

SESSION = requests.Session()

SESSION.headers.update({
    "User-Agent": "JobApplicationAutomation/1.0"
})


# =========================================================
# HTML CLEANING
# =========================================================

def clean_html(text):

    if not text:
        return ""

    soup = BeautifulSoup(
        text,
        "html.parser"
    )

    return soup.get_text(
        "\n",
        strip=True
    )


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize(text):

    if not text:
        return ""

    return " ".join(
        str(text).lower().split()
    )


# =========================================================
# TARGET ROLE CHECK
# =========================================================

def relevant_title(title):

    title = normalize(title)

    if not title:
        return False

    # First remove obvious management/senior roles.
    for term in EXCLUDED_TITLE_TERMS:

        if term in title:
            return False

    # Then check whether it belongs to one of
    # the candidate's target tracks.
    for term in TARGET_TERMS:

        if term in title:
            return True

    return False


# =========================================================
# ENTRY LEVEL DETECTION
# =========================================================

def is_entry_level(title):

    title = normalize(title)

    return any(
        term in title
        for term in ENTRY_LEVEL_TERMS
    )


# =========================================================
# IRELAND LOCATION
# =========================================================

def is_ireland_location(location):

    location = normalize(location)

    return any(
        term in location
        for term in IRELAND_TERMS
    )


# =========================================================
# EUROPE REMOTE LOCATION
# =========================================================

def is_europe_remote_location(location):

    location = normalize(location)

    return any(
        term in location
        for term in EUROPE_REMOTE_TERMS
    )


# =========================================================
# WORLDWIDE / UNSPECIFIED REMOTE
# =========================================================

def is_worldwide_remote_location(location):

    location = normalize(location)

    return any(
        term in location
        for term in WORLDWIDE_REMOTE_TERMS
    )


# =========================================================
# BAD LOCATION
# =========================================================

def is_excluded_location(location):

    location = normalize(location)

    return any(
        term in location
        for term in EXCLUDED_LOCATION_TERMS
    )


# =========================================================
# LOCATION DECISION
# =========================================================

def determine_location(location, remote=False):

    location = normalize(location)

    if is_excluded_location(location):

        return False, None

    if is_ireland_location(location):

        return True, "Ireland"

    if remote and is_europe_remote_location(location):

        return True, "Remote Europe"

    # Some APIs simply say "Remote", "Worldwide", or "Anywhere"
    # instead of naming a region (Remotive does this a lot).
    #
    # We allow it into the database if it is genuinely
    # remote, but Gemini will later determine whether
    # Ireland/EU work eligibility is actually possible.

    if remote and not location:

        return True, "Remote - location unspecified"

    if remote and location == "remote":

        return True, "Remote - location unspecified"

    if remote and is_worldwide_remote_location(location):

        return True, "Remote - Worldwide (needs eligibility check)"

    return False, None


# =========================================================
# DUPLICATE CHECK
# =========================================================

def job_exists(
    cursor,
    job_url,
    company,
    title,
    location
):

    if job_url:

        cursor.execute(
            """
            SELECT id
            FROM jobs
            WHERE job_url = ?
            """,
            (job_url,)
        )

        if cursor.fetchone():

            return True

    cursor.execute(
        """
        SELECT id
        FROM jobs
        WHERE LOWER(company) = LOWER(?)
          AND LOWER(job_title) = LOWER(?)
          AND LOWER(COALESCE(location, '')) = LOWER(?)
        """,
        (
            company,
            title,
            location or "",
        ),
    )

    return cursor.fetchone() is not None


# =========================================================
# SAVE JOB
# =========================================================

def save_job(
    cursor,
    company,
    title,
    location,
    url,
    source,
    description="",
    work_arrangement=None
):

    if not company:
        company = "Unknown"

    if not title:
        return False

    if job_exists(
        cursor,
        url,
        company,
        title,
        location
    ):

        return False

    cursor.execute(
        """
        INSERT INTO jobs (
            company,
            job_title,
            location,
            job_url,
            source,
            work_arrangement,
            application_status,
            date_found,
            job_description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            company,
            title,
            location,
            url,
            source,
            work_arrangement,
            "Not Applied",
            date.today().isoformat(),
            description,
        ),
    )

    return True


# =========================================================
# ARBEITNOW
# =========================================================

def discover_arbeitnow(cursor):

    print("\nSearching Arbeitnow...")

    url = (
        "https://www.arbeitnow.com/"
        "api/job-board-api"
    )

    response = SESSION.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    jobs = response.json().get(
        "data",
        []
    )

    raw_count = len(jobs)
    title_matched = 0
    location_valid = 0
    found = 0

    for job in jobs:

        title = job.get(
            "title",
            ""
        )

        company = job.get(
            "company_name",
            "Unknown"
        )

        location = job.get(
            "location",
            ""
        )

        remote = bool(
            job.get(
                "remote",
                False
            )
        )

        job_url = job.get(
            "url"
        )

        description = clean_html(
            job.get(
                "description",
                ""
            )
        )

        if not relevant_title(title):

            continue

        title_matched += 1

        valid, location_type = determine_location(
            location,
            remote
        )

        if not valid:

            continue

        location_valid += 1

        work_arrangement = (
            "Remote"
            if remote
            else "On-site / Hybrid"
        )

        if save_job(
            cursor,
            company,
            title,
            location,
            job_url,
            "Arbeitnow",
            description,
            work_arrangement
        ):

            found += 1

            level = (
                "Entry-level"
                if is_entry_level(title)
                else "Non-entry"
            )

            print(
                f"  + {company} | "
                f"{title} | "
                f"{location} | "
                f"{location_type} | "
                f"{level}"
            )

    print(
        f"Arbeitnow: {raw_count} fetched -> "
        f"{title_matched} title-matched -> "
        f"{location_valid} location-valid -> "
        f"{found} new"
    )

    return found


# =========================================================
# REMOTIVE
# =========================================================

def discover_remotive(cursor):

    print("\nSearching Remotive...")

    url = (
        "https://remotive.com/"
        "api/remote-jobs"
        "?limit=1000"
    )

    response = SESSION.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    jobs = response.json().get(
        "jobs",
        []
    )

    raw_count = len(jobs)
    title_matched = 0
    location_valid = 0
    found = 0

    for job in jobs:

        title = job.get(
            "title",
            ""
        )

        company = job.get(
            "company_name",
            "Unknown"
        )

        candidate_location = job.get(
            "candidate_required_location",
            ""
        )

        job_url = job.get(
            "url"
        )

        description = clean_html(
            job.get(
                "description",
                ""
            )
        )

        if not relevant_title(title):

            continue

        title_matched += 1

        valid, location_type = determine_location(
            candidate_location,
            True
        )

        if not valid:

            continue

        location_valid += 1

        if save_job(
            cursor,
            company,
            title,
            candidate_location,
            job_url,
            "Remotive",
            description,
            "Remote"
        ):

            found += 1

            print(
                f"  + {company} | "
                f"{title} | "
                f"{candidate_location} | "
                f"{location_type}"
            )

    print(
        f"Remotive: {raw_count} fetched -> "
        f"{title_matched} title-matched -> "
        f"{location_valid} location-valid -> "
        f"{found} new"
    )

    if raw_count < 100:
        print(
            "  WARNING: Remotive returned an unusually small "
            "batch — check if their API changed again."
        )

    return found


# =========================================================
# REMOTE OK
# =========================================================

def discover_remoteok(cursor):

    print("\nSearching Remote OK...")

    url = (
        "https://remoteok.com/api"
    )

    response = SESSION.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    raw_count = max(len(data) - 1, 0)
    title_matched = 0
    found = 0

    # First item is API metadata.
    for job in data[1:]:

        title = job.get(
            "position",
            ""
        )

        company = job.get(
            "company",
            "Unknown"
        )

        location = (
            job.get("location")
            or "Remote"
        )

        job_url = (
            job.get("url")
            or job.get("apply_url")
        )

        description = clean_html(
            job.get(
                "description",
                ""
            )
        )

        if not relevant_title(title):

            continue

        title_matched += 1

        # Remote OK is a remote-only source.
        #
        # We keep it because the job may be compatible
        # with Ireland/EU, but Gemini must verify this
        # from the actual job description.

        if save_job(
            cursor,
            company,
            title,
            location,
            job_url,
            "Remote OK",
            description,
            "Remote"
        ):

            found += 1

            print(
                f"  + {company} | "
                f"{title} | "
                f"{location}"
            )

    print(
        f"Remote OK: {raw_count} fetched -> "
        f"{title_matched} title-matched -> "
        f"{found} new"
    )

    return found


# =========================================================
# DISCOVERY
# =========================================================

def discover_jobs():

    print("\n=================================")
    print("     AUTOMATIC JOB DISCOVERY")
    print("=================================")

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    total = 0

    sources = [
        (
            "Arbeitnow",
            discover_arbeitnow
        ),
        (
            "Remotive",
            discover_remotive
        ),
        (
            "Remote OK",
            discover_remoteok
        ),
    ]

    for source_name, function in sources:

        try:

            count = function(
                cursor
            )

            conn.commit()

            total += count

        except Exception as e:

            print(
                f"\nERROR collecting "
                f"{source_name}: {e}"
            )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        """
    )

    database_total = cursor.fetchone()[0]

    conn.close()

    print("\n=================================")
    print("       DISCOVERY COMPLETE")
    print("=================================")

    print(
        f"New jobs found : {total}"
    )

    print(
        f"Jobs in DB     : {database_total}"
    )


if __name__ == "__main__":

    discover_jobs()