"""
Exports scored jobs from data/jobs.db into your existing master Excel
tracker (Ranjith_Job_Tracker.xlsx by default).

Behaviour:
- Only touches the "Job Tracker" sheet. Never rewrites, resorts, or
  overwrites rows already there — it only APPENDS new rows.
- A job is considered "already in the sheet" if its Job URL already
  appears in column D (or, if the URL is missing, if the same
  Company + Job title pair already appears). Matched jobs are never
  duplicated or re-appended.
- Only exports jobs where match_score IS NOT NULL (i.e. already run
  through process_jobs.py) — both eligible and ineligible are
  included, so you can see near-misses too. Sort/filter in Excel by
  the "Match score" or "Priority" columns however you like.
- Adds a "Keywords to Add" column if the sheet doesn't already have
  one (appended as a new last column, so it never shifts anything
  else).
- Re-applies dropdown validation + conditional formatting so newly
  appended rows behave the same as the original template rows.

Run from the project root:

    python src/excel_export.py

Edit EXCEL_PATH below if your tracker file lives somewhere else or
under a different name.
"""

import json
import sqlite3
from datetime import date
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.datavalidation import DataValidationList

DB_PATH = "data/jobs.db"
EXCEL_PATH = "Ranjith_Job_Tracker.xlsx"
SHEET_NAME = "Job Tracker"

FONT_NAME = "Arial"

# How many blank rows of dropdown/formatting coverage to guarantee
# beyond whatever is currently used. Cheap insurance so you don't run
# out of pre-formatted rows for a while.
ROW_BUFFER = 100


def get_scored_jobs(cursor):
    cursor.execute("""
        SELECT
            company, job_title, location, job_url, resume,
            job_category, date_found, salary, work_type,
            work_arrangement, eligible, match_score,
            resume_keywords
        FROM jobs
        WHERE match_score IS NOT NULL
        ORDER BY match_score DESC
    """)
    return cursor.fetchall()


def build_header_map(ws):
    header_map = {}
    for col in range(1, ws.max_column + 1):
        value = ws.cell(row=1, column=col).value
        if value:
            header_map[value.strip()] = col
    return header_map


def ensure_keywords_column(ws, header_map):
    if "Keywords to Add" in header_map:
        return header_map

    new_col = ws.max_column + 1

    header_font = Font(name=FONT_NAME, bold=True, color="FFFFFF", size=10)
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")

    cell = ws.cell(row=1, column=new_col, value="Keywords to Add")
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.column_dimensions[cell.column_letter].width = 40

    header_map["Keywords to Add"] = new_col
    return header_map


def get_existing_keys(ws, header_map):
    """Returns (set of existing job URLs, set of (company, title) pairs)."""
    url_col = header_map.get("Job URL")
    company_col = header_map.get("Company")
    title_col = header_map.get("Job title")

    urls = set()
    company_title_pairs = set()

    for row in range(2, ws.max_row + 1):
        if url_col:
            url_cell = ws.cell(row=row, column=url_col)
            url_value = url_cell.hyperlink.target if url_cell.hyperlink else url_cell.value
            if url_value:
                urls.add(url_value)

        if company_col and title_col:
            company_value = ws.cell(row=row, column=company_col).value
            title_value = ws.cell(row=row, column=title_col).value
            if company_value and title_value:
                company_title_pairs.add(
                    (str(company_value).strip().lower(), str(title_value).strip().lower())
                )

    return urls, company_title_pairs


def refresh_validations_and_formatting(ws, header_map, last_row):
    resume_col = header_map.get("Resume")
    category_col = header_map.get("Job category")
    status_col = header_map.get("Application status")
    worktype_col = header_map.get("Work type")
    priority_col = header_map.get("Priority")
    visa_col = header_map.get("Visa/work eligibility")

    # Clear and rebuild data validations fresh so ranges cover new rows.
    ws.data_validations = DataValidationList()

    def add_dropdown(col, options_csv):
        if not col:
            return
        dv = DataValidation(type="list", formula1=f'"{options_csv}"', allow_blank=True, showDropDown=False)
        ws.add_data_validation(dv)
        col_letter = ws.cell(row=1, column=col).column_letter
        dv.add(f"{col_letter}2:{col_letter}{last_row}")

    add_dropdown(resume_col, "A,B,C,D")
    add_dropdown(category_col, "Data Centre,Cloud/DevOps,Software/Automation,IT Support/QA,Other")
    add_dropdown(status_col, "Not Applied,Applied,Under Review,Interview Scheduled,Interview Completed,Offer,Offer Accepted,Rejected,Withdrawn")
    add_dropdown(worktype_col, "Full-time,Part-time,Contract,Internship")
    add_dropdown(priority_col, "A,B,C")
    add_dropdown(visa_col, "Eligible,Not Eligible,Sponsorship Required,Check,N/A")

    # Conditional formatting on Application status + Priority.
    if status_col:
        col_letter = ws.cell(row=1, column=status_col).column_letter
        status_range = f"{col_letter}2:{col_letter}{last_row}"

        green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        yellow_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
        blue_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")

        ws.conditional_formatting.add(status_range, CellIsRule(operator="equal", formula=['"Offer"'], fill=green_fill))
        ws.conditional_formatting.add(status_range, CellIsRule(operator="equal", formula=['"Offer Accepted"'], fill=green_fill))
        ws.conditional_formatting.add(status_range, CellIsRule(operator="equal", formula=['"Rejected"'], fill=red_fill))
        ws.conditional_formatting.add(status_range, CellIsRule(operator="equal", formula=['"Interview Scheduled"'], fill=yellow_fill))
        ws.conditional_formatting.add(status_range, CellIsRule(operator="equal", formula=['"Interview Completed"'], fill=yellow_fill))
        ws.conditional_formatting.add(status_range, CellIsRule(operator="equal", formula=['"Applied"'], fill=blue_fill))

    if priority_col:
        col_letter = ws.cell(row=1, column=priority_col).column_letter
        priority_range = f"{col_letter}2:{col_letter}{last_row}"
        prio_a_fill = PatternFill(start_color="F4CCCC", end_color="F4CCCC", fill_type="solid")
        ws.conditional_formatting.add(priority_range, CellIsRule(operator="equal", formula=['"A"'], fill=prio_a_fill, font=Font(bold=True)))


def find_legend_row(ws):
    for row in range(1, ws.max_row + 1):
        value = ws.cell(row=row, column=1).value
        if value and str(value).strip().startswith("Legend:"):
            return row
    return None


def find_next_content_row(ws, header_map, legend_row):
    company_col = header_map.get("Company")
    if not company_col:
        return (legend_row or ws.max_row + 1)

    upper_bound = legend_row if legend_row else ws.max_row + 1

    for row in range(2, upper_bound):
        if not ws.cell(row=row, column=company_col).value:
            return row

    # No blank template rows left before the legend (or no legend at all).
    return upper_bound


def export():
    excel_path = Path(EXCEL_PATH)
    if not excel_path.exists():
        print(f"ERROR: {EXCEL_PATH} not found. Edit EXCEL_PATH at the "
              f"top of this script, or place the file at that path.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    jobs = get_scored_jobs(cursor)
    conn.close()

    print(f"Scored jobs in DB: {len(jobs)}")

    wb = openpyxl.load_workbook(excel_path)

    if SHEET_NAME not in wb.sheetnames:
        print(f"ERROR: sheet '{SHEET_NAME}' not found in {EXCEL_PATH}. "
              f"Sheets present: {wb.sheetnames}")
        return

    ws = wb[SHEET_NAME]
    header_map = build_header_map(ws)
    header_map = ensure_keywords_column(ws, header_map)

    existing_urls, existing_pairs = get_existing_keys(ws, header_map)

    legend_row = find_legend_row(ws)
    next_row = find_next_content_row(ws, header_map, legend_row)

    thin = Side(style="thin", color="B7B7B7")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    added = 0
    skipped_existing = 0

    for job in jobs:
        (company, title, location, job_url, resume, job_category,
         date_found, salary, work_type, work_arrangement, eligible,
         match_score, resume_keywords_json) = job

        already_present = False
        if job_url and job_url in existing_urls:
            already_present = True
        elif not job_url and (str(company).strip().lower(), str(title).strip().lower()) in existing_pairs:
            already_present = True

        if already_present:
            skipped_existing += 1
            continue

        # Ran out of blank template rows before the legend — insert a
        # fresh row right at the legend's position so the legend stays
        # pinned to the bottom instead of new data landing after it.
        if legend_row and next_row >= legend_row:
            ws.insert_rows(legend_row, amount=1)
            legend_row += 1

        row = next_row

        def set_cell(col_name, value):
            col = header_map.get(col_name)
            if not col:
                return
            cell = ws.cell(row=row, column=col, value=value)
            cell.font = Font(name=FONT_NAME, size=10)
            cell.border = border
            cell.alignment = Alignment(vertical="center", wrap_text=False)

        set_cell("Company", company)
        set_cell("Job title", title)
        set_cell("Location", location)

        col = header_map.get("Job URL")
        if col and job_url:
            cell = ws.cell(row=row, column=col, value=job_url)
            cell.hyperlink = job_url
            cell.font = Font(name=FONT_NAME, size=10, color="0563C1", underline="single")
            cell.border = border

        set_cell("Resume", resume)
        set_cell("Job category", job_category)
        set_cell("Date found", date_found or date.today().isoformat())
        set_cell("Application status", "Not Applied")
        set_cell("Salary", salary or "")
        set_cell("Work type", work_type or work_arrangement or "")
        set_cell("Visa/work eligibility", "Eligible" if eligible else "Not Eligible")
        set_cell("Match score", match_score)

        try:
            keywords_list = json.loads(resume_keywords_json) if resume_keywords_json else []
        except (json.JSONDecodeError, TypeError):
            keywords_list = []
        set_cell("Keywords to Add", ", ".join(keywords_list))

        next_row += 1
        added += 1

    last_row = max(next_row - 1, ws.max_row) + ROW_BUFFER
    refresh_validations_and_formatting(ws, header_map, last_row)

    wb.save(excel_path)

    print(f"Rows added   : {added}")
    print(f"Already there: {skipped_existing}")
    print(f"Saved to     : {excel_path}")


if __name__ == "__main__":
    export()