import time
import csv
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
MANIFEST_CSV = ROOT_DIR / "reels_manifest.csv"
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iLArjkaw_z9xTalAJ-0fer3f97GxRwT6XWsbtTsw14Q/edit"

def get_tsv():
    with open(MANIFEST_CSV, "r", encoding="utf-8") as f:
        lines = [line.strip().replace(",", "\t") for line in f.readlines()]
    return "\n".join(lines)

def run():
    tsv_data = get_tsv()

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

        print("2. Exiting formula edit mode & focusing Cell A1...")
        page.keyboard.press("Escape")
        time.sleep(0.5)
        page.keyboard.press("Escape")
        time.sleep(0.5)
        
        # Click Cell A1
        page.mouse.click(80, 220)
        time.sleep(1)

        print("3. Clearing content...")
        page.keyboard.press("Control+a")
        time.sleep(0.5)
        page.keyboard.press("Delete")
        time.sleep(1)

        print("4. Pasting 18 clean rows (blank pending captions)...")
        page.evaluate(f"navigator.clipboard.writeText({repr(tsv_data)})")
        time.sleep(1)
        page.keyboard.press("Control+v")
        time.sleep(5)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_clean_no_prefilled_captions.png"))
        print("✓ Captured final_clean_no_prefilled_captions.png")

        context.close()

if __name__ == "__main__":
    run()
