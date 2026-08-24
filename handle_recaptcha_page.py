import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
PROFILE_DIR = str(ROOT_DIR / "browser_profile")

def run():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to Instagram Login page...")
        page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
        time.sleep(4)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "captcha_page.png"))
        print(f"Saved captcha_page.png. Page URL: {page.url}")

        # Check all frames on page
        print(f"Total frames on page: {len(page.frames)}")
        for idx, f in enumerate(page.frames):
            print(f"Frame #{idx}: name='{f.name}', url='{f.url}'")

        # Click recaptcha checkbox in frame
        for f in page.frames:
            try:
                anchor = f.locator("#recaptcha-anchor, .recaptcha-checkbox-border, div.recaptcha-checkbox-checkmark").first
                if anchor.is_visible(timeout=2000):
                    print(f"✓ Found anchor in frame {f.url}! Clicking now...")
                    anchor.click()
                    time.sleep(5)
                    break
            except Exception:
                pass

        page.screenshot(path=str(ROOT_DIR / "downloads" / "captcha_clicked_state.png"))
        print(f"Saved screenshot to captcha_clicked_state.png")

        context.close()

if __name__ == "__main__":
    run()
