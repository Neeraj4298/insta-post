import time
import csv
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
MANIFEST_CSV = ROOT_DIR / "reels_manifest.csv"
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iLArjkaw_z9xTalAJ-0fer3f97GxRwT6XWsbtTsw14Q/edit"

def prepare_tsv_data():
    """Converts reels_manifest.csv into tab-separated values for Google Sheets paste."""
    rows = []
    with open(MANIFEST_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append("\t".join(row))
    return "\n".join(rows)

def run():
    print("==================================================")
    print(" Populating Live Google Sheet: tune_of_ghibli     ")
    print("==================================================")

    tsv_data = prepare_tsv_data()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            BRAVE_PROFILE,
            executable_path=BRAVE_PATH,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("1. Opening Google Sheet...")
        page.goto(SHEET_URL, wait_until="domcontentloaded")
        time.sleep(6)

        print("2. Focusing Cell A1...")
        page.keyboard.press("Control+Home")
        time.sleep(1)

        print("3. Pasting tracking records into Google Sheet...")
        # Write formatted TSV directly to clipboard & paste
        page.evaluate(f"navigator.clipboard.writeText({repr(tsv_data)})")
        time.sleep(1)
        page.keyboard.press("Control+v")
        time.sleep(4)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "live_google_sheet_populated.png"))
        print("✓ Captured live_google_sheet_populated.png")

        print("\n==================================================")
        print(" 🎉 GOOGLE SHEET POPULATED SUCCESSFULLY!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
