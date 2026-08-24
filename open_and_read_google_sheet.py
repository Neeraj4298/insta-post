import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iLArjkaw_z9xTalAJ-0fer3f97GxRwT6XWsbtTsw14Q/edit"

def run():
    print("Opening Google Sheet in persistent Brave context...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            BRAVE_PROFILE,
            executable_path=BRAVE_PATH,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        page.goto(SHEET_URL, wait_until="domcontentloaded")
        time.sleep(5)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "google_sheet_view.png"))
        print("✓ Captured google_sheet_view.png")

        context.close()

if __name__ == "__main__":
    run()
