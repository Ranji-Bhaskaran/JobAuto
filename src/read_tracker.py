import pandas as pd

FILE_PATH = "Ranjith_Job_Tracker.xlsx"

df = pd.read_excel(
    FILE_PATH,
    sheet_name="Job Tracker"
)

# Remove completely empty rows
df = df.dropna(how="all")

# Remove the legend row at the bottom
df = df[df["Company"].notna()]

print("\n=== JOB TRACKER ===")
print(f"Jobs found: {len(df)}\n")

for _, job in df.iterrows():
    print(
        f"{job['Company']} | "
        f"{job['Job title']} | "
        f"{job['Location']} | "
        f"Resume: {job['Resume']} | "
        f"Status: {job['Application status']}"
    )