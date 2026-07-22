import sys
import os
import csv
import argparse
from bs4 import BeautifulSoup


def parse_job_html(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "html.parser")

    data = {"source_file": os.path.basename(file_path)}

    # ---- Job Title (same tag works for both templates) ----
    title_tag = soup.find("h1")
    data["job_title"] = title_tag.get_text(strip=True) if title_tag else None

    # ---- Job Description ----
    desc_tag = soup.find("div", class_="job-desc")
    if desc_tag:
        data["job_description"] = desc_tag.get_text(separator="\n", strip=True)
    else:
        job_description = None
        for section in soup.find_all("section", class_="JobDetailContainer"):
            heading = section.find(["h2", "h3", "h4"])
            if heading and "job description" in heading.get_text(strip=True).lower():
                items = section.find_all("div", class_="jobDetailItem")
                job_description = "\n".join(item.get_text(strip=True) for item in items)
                break
        data["job_description"] = job_description or None

    # ---- Job Location ----
    location_tag = soup.find("span", class_="job-location")
    if location_tag:
        data["job_location"] = location_tag.get_text(strip=True)
    else:
        location_tag = soup.find("div", class_="LocationDetail")
        data["job_location"] = location_tag.get_text(strip=True) if location_tag else None

    return data


def print_job(data: dict) -> None:
    print("=" * 60)
    print("SOURCE FILE:", data.get("source_file"))
    print("-" * 60)
    print("JOB TITLE:")
    print(data.get("job_title"))
    print("-" * 60)
    print("JOB LOCATION:")
    print(data.get("job_location"))
    print("-" * 60)
    print("JOB DESCRIPTION:")
    print(data.get("job_description"))
    print("=" * 60)


def parse_folder(folder_path: str) -> list:
    results = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower().endswith((".html", ".htm")):
            full_path = os.path.join(folder_path, filename)
            try:
                results.append(parse_job_html(full_path))
            except Exception as e:
                print(f"⚠️  Skipped {filename}: {e}")
    return results


def write_csv(rows: list, csv_path: str) -> None:
    fieldnames = ["source_file", "job_title", "job_location", "job_description"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"\n✅ Saved {len(rows)} job(s) to {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract job title, description, and location from saved job HTML pages.")
    parser.add_argument("path", help="Path to a single .html file OR a folder containing multiple .html files")
    parser.add_argument("--csv", help="Optional: output CSV file path", default=None)
    args = parser.parse_args()

    if os.path.isdir(args.path):
        jobs = parse_folder(args.path)
        if args.csv:
            write_csv(jobs, args.csv)
        else:
            for job in jobs:
                print_job(job)
    elif os.path.isfile(args.path):
        job_data = parse_job_html(args.path)
        if args.csv:
            write_csv([job_data], args.csv)
        else:
            print_job(job_data)
    else:
        print(f"Path not found: {args.path}")
        sys.exit(1)