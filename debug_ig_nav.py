import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
PROFILE_DIR = str(ROOT_DIR / "browser_profile")

def inspect_page():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.instagram.com/", wait_until="networkidle")
        time.sleep(3)

        print(f"Current URL: {page.url}")
        page.screenshot(path=str(ROOT_DIR / "downloads" / "current_page.png"))
        print(f"Saved screenshot to {ROOT_DIR / 'downloads' / 'current_page.png'}")

        # Check if username input exists
        u_input = page.locator("input[name='username']")
        print(f"Username input visible: {u_input.is_visible()}")

        if u_input.is_visible():
            print("Performing login...")
            u_input.fill(USERNAME)
            time.sleep(1)
            page.fill("input[name='password']", PASSWORD)
            time.sleep(1)
            page.click("button[type='submit']")
            print("Login submitted. Waiting 8s...")
            time.sleep(8)
            print(f"Post-login URL: {page.url}")
            page.screenshot(path=str(ROOT_DIR / "downloads" / "post_login.png"))

        context.close()

if __name__ == "__main__":
    inspect_page()
