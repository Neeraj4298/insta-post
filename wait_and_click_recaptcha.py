import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
PROFILE_DIR = str(ROOT_DIR / "browser_profile")

def run():
    print("==================================================")
    print(" Explicit Wait & reCAPTCHA Auto-Clicker           ")
    print("==================================================")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to Instagram Login page...")
        page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
        time.sleep(3)

        inputs = page.locator("input").all()
        if len(inputs) >= 2:
            print("Entering credentials...")
            inputs[0].click()
            inputs[0].type(USERNAME, delay=30)
            time.sleep(1)

            inputs[1].click()
            inputs[1].type(PASSWORD, delay=30)
            time.sleep(1)

            print("Submitting login form...")
            inputs[1].press("Enter")
            print("Waiting for reCAPTCHA iframe to load...")

        # Wait up to 15 seconds for reCAPTCHA iframe
        try:
            iframe_elem = page.wait_for_selector("iframe[src*='recaptcha'], iframe[title*='reCAPTCHA']", timeout=15000)
            print("✓ reCAPTCHA iframe element loaded on DOM!")
            time.sleep(2)

            # Click anchor inside iframe via frame_locator
            recaptcha_frame = page.frame_locator("iframe[src*='recaptcha'], iframe[title*='reCAPTCHA']").first
            anchor = recaptcha_frame.locator("#recaptcha-anchor, .recaptcha-checkbox-border, #rc-anchor-container").first
            anchor.wait_for(state="visible", timeout=10000)
            anchor.click()
            print("🎉 CLICKED RECAPTCHA CHECKBOX SUCCESSFULLY!")
            time.sleep(6)

        except Exception as e:
            print(f"reCAPTCHA iframe wait notice: {e}")

        page.screenshot(path=str(ROOT_DIR / "downloads" / "checked_captcha_screen.png"))
        print(f"Saved screenshot to checked_captcha_screen.png. Page URL: {page.url}")

        # Check if submit button is present after captcha click
        sub_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Next')").first
        if sub_btn.is_visible(timeout=3000):
            print("Clicking post-captcha submit button...")
            sub_btn.click()
            time.sleep(6)

        # Handle popups
        for txt in ["Save Info", "Save info", "Not Now", "Not now"]:
            try:
                b = page.locator(f"button:has-text('{txt}')")
                if b.is_visible(timeout=2000):
                    b.click()
                    time.sleep(1)
            except Exception:
                pass

        page.goto(f"https://www.instagram.com/{USERNAME}/", wait_until="domcontentloaded")
        time.sleep(3)

        # Locate Create button on profile page
        print("Looking for Create (+) button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], span:has-text('Create')").first
        if create_btn.is_visible(timeout=5000):
            create_btn.click()
            print("✓ Clicked Create button!")
            time.sleep(3)

        # File input for reel upload
        print("Attaching video file to upload dialog...")
        file_input = page.locator("input[type='file']").first
        if file_input.is_visible(timeout=5000):
            file_input.set_input_files(VIDEO_PATH)
            print("✓ Attached video file successfully!")
            time.sleep(6)

            # Step 1: Crop -> Next
            print("Step 1: Crop -> Next...")
            n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n1.is_visible(timeout=3000):
                n1.click()
                time.sleep(3)

            # Step 2: Filters -> Next
            print("Step 2: Filters -> Next...")
            n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n2.is_visible(timeout=3000):
                n2.click()
                time.sleep(3)

            # Step 3: Share
            print("Step 3: Share...")
            share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
            if share_btn.is_visible(timeout=3000):
                share_btn.click()
                print("✓ Clicked Share button!")

            print("Waiting for reel upload completion (20s)...")
            time.sleep(20)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_checked_result.png"))
        print("\n==================================================")
        print(" 🎉 REEL UPLOAD SCRIPT COMPLETED!")
        print("==================================================")
        context.close()

if __name__ == "__main__":
    run()
