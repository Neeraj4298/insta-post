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
    print(" Playwright reCAPTCHA Auto-Clicker & Reel Upload ")
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
            print("Typing credentials...")
            inputs[0].click()
            inputs[0].type(USERNAME, delay=40)
            time.sleep(1)

            inputs[1].click()
            inputs[1].type(PASSWORD, delay=40)
            time.sleep(1)

            print("Pressing Enter...")
            inputs[1].press("Enter")
            time.sleep(5)

        # Check if reCAPTCHA page loaded
        print("Checking for reCAPTCHA box...")
        page.screenshot(path=str(ROOT_DIR / "downloads" / "captcha_check_screen.png"))

        # Click reCAPTCHA checkbox directly via frame locator and click coordinates
        print("Attempting reCAPTCHA checkbox click...")
        clicked_captcha = False

        # Attempt 1: Frame locator
        try:
            f = page.frame_locator("iframe[src*='recaptcha'], iframe[title*='reCAPTCHA']").first
            chk = f.locator("#recaptcha-anchor, .recaptcha-checkbox-border").first
            if chk.is_visible(timeout=3000):
                chk.click()
                clicked_captcha = True
                print("✓ Clicked reCAPTCHA checkbox via frame_locator!")
                time.sleep(5)
        except Exception as e:
            print(f"Frame locator notice: {e}")

        # Attempt 2: Mouse coordinate click (x=281, y=153)
        if not clicked_captcha:
            print("Attempting mouse coordinate click at (281, 153)...")
            page.mouse.click(281, 153)
            time.sleep(5)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "after_captcha_clicked.png"))
        print(f"Post-captcha page URL: {page.url}")

        # Handle post-login popups
        for txt in ["Save Info", "Save info", "Not Now", "Not now"]:
            try:
                b = page.locator(f"button:has-text('{txt}')")
                if b.is_visible(timeout=2000):
                    b.click()
                    time.sleep(1)
            except Exception:
                pass

        # Go to profile feed or home
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(3)

        # Click Create button
        print("Clicking Create (+) button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], span:has-text('Create')").first
        if create_btn.is_visible(timeout=5000):
            create_btn.click()
            print("✓ Clicked Create button!")
            time.sleep(3)

        # File input for reel upload
        print("Attaching video file...")
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

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_success_published.png"))
        print("\n==================================================")
        print(" 🎉 REEL UPLOAD WORKFLOW COMPLETED!")
        print("==================================================")
        context.close()

if __name__ == "__main__":
    run()
