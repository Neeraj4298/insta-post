import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Final Verification of New Published Reel on Grid ")
    print("==================================================")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            BRAVE_PROFILE,
            executable_path=BRAVE_PATH,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to @tune_of_ghibli profile page...")
        page.goto("https://www.instagram.com/tune_of_ghibli/", wait_until="networkidle")
        time.sleep(5)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_grid_4_reels_verified.png"))
        print("✓ Captured final_grid_4_reels_verified.png")

        context.close()

if __name__ == "__main__":
    run()
