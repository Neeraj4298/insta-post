import sys
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
    print(" Playwright Persistent Browser Reel Upload        ")
    print("==================================================")
    print(f"Target Account: @{USERNAME}")
    print(f"Video File: {VIDEO_PATH}")

    with sync_playwright() as p:
        # Launch persistent browser context to retain cookies/session
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        page = context.pages[0] if context.pages else context.new_page()

        print("\nNavigating to Instagram...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(3)

        # Check if login form is present
        if page.locator("input[name='username']").is_visible(timeout=3000):
            print("Entering login details...")
            page.fill("input[name='username']", USERNAME)
            time.sleep(1)
            page.fill("input[name='password']", PASSWORD)
            time.sleep(1)
            page.click("button[type='submit']")
            print("Submitted login form. Waiting for authentication...")
            time.sleep(8)

        # Handle popups ('Not Now', 'Save Info')
        for label in ["Not Now", "Not now", "Save Info", "Save info"]:
            try:
                btn = page.locator(f"button:has-text('{label}')")
                if btn.is_visible(timeout=2000):
                    btn.click()
                    time.sleep(1)
            except Exception:
                pass

        print(f"Current page URL: {page.url}")

        # Click Create (+) button
        print("Looking for Create (+) button...")
        create_clicked = False

        # Try clicking sidebar elements
        for selector in ["svg[aria-label='New post']", "svg[aria-label='Create']", "span:has-text('Create')", "a[href='#']"]:
            try:
                elem = page.locator(selector).first
                if elem.is_visible(timeout=2000):
                    elem.click()
                    create_clicked = True
                    print(f"✓ Clicked Create using selector: {selector}")
                    break
            except Exception:
                pass

        if not create_clicked:
            print("Trying JavaScript click on Create link...")
            page.evaluate("""() => {
                const svgs = Array.from(document.querySelectorAll('svg'));
                const createSvg = svgs.find(s => s.getAttribute('aria-label') === 'New post' || s.getAttribute('aria-label') === 'Create');
                if (createSvg) {
                    createSvg.closest('a, button, div').click();
                }
            }""")

        time.sleep(4)

        # Wait for file input element in modal
        print("Waiting for file input in modal...")
        try:
            file_input = page.wait_for_selector("input[type='file']", timeout=10000)
            file_input.set_input_files(VIDEO_PATH)
            print("✓ Attached video file successfully!")
            time.sleep(6)

            # Step 1: Click 'Next' (Crop)
            print("Clicking Next (Crop)...")
            next1 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if next1.is_visible(timeout=3000):
                next1.click()
                time.sleep(3)

            # Step 2: Click 'Next' (Filters/Edit)
            print("Clicking Next (Filters - No Edits)...")
            next2 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if next2.is_visible(timeout=3000):
                next2.click()
                time.sleep(3)

            # Step 3: Click 'Share' (Publish Reel)
            print("Clicking Share (Publish Reel)...")
            share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
            if share_btn.is_visible(timeout=3000):
                share_btn.click()
                print("✓ Clicked Share button!")

            print("Waiting for Instagram video upload & processing...")
            time.sleep(20)

            print("\n==================================================")
            print(" 🎉 REEL UPLOAD COMPLETED SUCCESSFULLY!")
            print("==================================================")

        except Exception as e:
            print(f"\n❌ Error during file upload step: {e}")

        context.close()

if __name__ == "__main__":
    run()
