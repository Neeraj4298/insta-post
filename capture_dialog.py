import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
PROFILE_DIR = str(ROOT_DIR / "browser_profile")

def inspect_dialog():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to Instagram...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(3)

        user_input = page.locator("input[name='username'], input[type='text']").first
        if user_input.is_visible(timeout=3000):
            print("Logging in...")
            user_input.fill(USERNAME)
            page.fill("input[name='password'], input[type='password']", PASSWORD)
            page.locator("input[name='password'], input[type='password']").first.press("Enter")
            time.sleep(6)

        # Click Create
        print("Clicking Create button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], a:has-text('Create'), span:has-text('Create')").first
        if create_btn.is_visible(timeout=3000):
            create_btn.click()
            print("✓ Clicked Create button!")

        for i in range(1, 6):
            time.sleep(2)
            sc_path = str(ROOT_DIR / "downloads" / f"step_{i}.png")
            page.screenshot(path=sc_path)
            print(f"Captured screenshot step_{i}.png at {page.url}")

            # Check for reCAPTCHA inside frame or main page
            if page.locator("iframe[title*='reCAPTCHA']").is_visible():
                print(f"reCAPTCHA iframe detected at step {i}!")
                captcha_frame = page.frame_locator("iframe[title*='reCAPTCHA']").first
                chk = captcha_frame.locator("#recaptcha-anchor, .recaptcha-checkbox-border").first
                if chk.is_visible():
                    print("Clicking reCAPTCHA checkbox...")
                    chk.click()
                    time.sleep(3)

            # Check if file input appeared
            if page.locator("input[type='file']").is_visible():
                print(f"File input visible at step {i}! Setting file...")
                page.locator("input[type='file']").first.set_input_files(VIDEO_PATH)
                time.sleep(3)

                # Next 1
                n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
                if n1.is_visible():
                    n1.click()
                    time.sleep(2)

                # Next 2
                n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
                if n2.is_visible():
                    n2.click()
                    time.sleep(2)

                # Share
                s = page.locator("div[role='dialog'] div:has-text('Share')").last
                if s.is_visible():
                    s.click()
                    print("✓ Clicked Share!")
                    time.sleep(15)
                break

        context.close()

if __name__ == "__main__":
    inspect_dialog()
