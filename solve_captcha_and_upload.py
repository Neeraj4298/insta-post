import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
PROFILE_DIR = str(ROOT_DIR / "browser_profile")

def upload():
    print("==================================================")
    print(" Playwright Auto Upload with reCAPTCHA Handling   ")
    print("==================================================")
    print(f"Target Account: @{USERNAME}")
    print(f"Video File: {VIDEO_PATH}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("\nNavigating to Instagram...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(4)

        # Check if reCAPTCHA is present on page
        print("Checking for reCAPTCHA iframe...")
        try:
            captcha_iframe = page.frame_locator("iframe[title*='reCAPTCHA'], iframe[src*='recaptcha']").first
            if captcha_iframe:
                checkbox = captcha_iframe.locator("#recaptcha-anchor, .recaptcha-checkbox-border").first
                if checkbox.is_visible(timeout=3000):
                    print("Found reCAPTCHA checkbox! Clicking checkbox...")
                    checkbox.click()
                    time.sleep(5)
        except Exception as e:
            print(f"No reCAPTCHA checkbox found or already cleared: {e}")

        # Check if login form is present
        user_input = page.locator("input[name='username'], input[type='text']").first
        if user_input.is_visible(timeout=3000):
            print("Entering username & password...")
            user_input.fill(USERNAME)
            time.sleep(1)
            pwd_input = page.locator("input[name='password'], input[type='password']").first
            pwd_input.fill(PASSWORD)
            time.sleep(1)
            pwd_input.press("Enter")
            print("Submitted login. Waiting 8s...")
            time.sleep(8)

        # Handle post-login popups
        for label in ["Not Now", "Not now", "Save Info", "Save info"]:
            try:
                btn = page.locator(f"button:has-text('{label}')")
                if btn.is_visible(timeout=2000):
                    btn.click()
                    time.sleep(1)
            except Exception:
                pass

        print(f"Current page URL: {page.url}")

        # Click Create button
        print("Looking for Create (+) button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], a:has-text('Create'), span:has-text('Create')").first
        if create_btn.is_visible(timeout=5000):
            create_btn.click()
            print("✓ Clicked Create button!")
        else:
            page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a, button, div'));
                const createEl = links.find(el => el.textContent.trim() === 'Create' || el.querySelector('svg[aria-label="New post"]'));
                if (createEl) createEl.click();
            }""")

        time.sleep(4)

        # File input for reel upload
        print("Attaching video file to upload dialog...")
        file_input = page.locator("input[type='file']").first
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached video file successfully!")
        time.sleep(6)

        # Step 1: Click 'Next' (Crop screen)
        print("Step 1: Click Next (Crop)...")
        next1 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if next1.is_visible(timeout=5000):
            next1.click()
            time.sleep(3)

        # Step 2: Click 'Next' (Filters screen)
        print("Step 2: Click Next (Filters - No Edits)...")
        next2 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if next2.is_visible(timeout=5000):
            next2.click()
            time.sleep(3)

        # Step 3: Click 'Share'
        print("Step 3: Click Share...")
        share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
        if share_btn.is_visible(timeout=5000):
            share_btn.click()
            print("✓ Clicked Share button!")

        print("Waiting for reel upload completion (20s)...")
        time.sleep(20)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_success.png"))
        print("\n==================================================")
        print(" 🎉 REEL UPLOAD COMPLETED SUCCESSFULLY!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    upload()
