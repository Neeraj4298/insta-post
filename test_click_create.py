import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
VIDEO_PATH = str(Path(__file__).resolve().parent / "downloads" / "reel_to_upload.mp4")

def upload():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print("Navigating to Instagram login...")
        page.goto("https://www.instagram.com/accounts/login/")
        page.wait_for_selector("input[name='username']")

        page.fill("input[name='username']", USERNAME)
        page.fill("input[name='password']", PASSWORD)
        page.click("button[type='submit']")
        print("Submitted login form.")
        time.sleep(5)

        # Handle popups
        for txt in ["Not Now", "Not now", "Save Info", "Save info"]:
            try:
                page.click(f"button:has-text('{txt}')", timeout=3000)
                time.sleep(1)
            except Exception:
                pass

        print(f"Logged in. Current URL: {page.url}")

        # Find Create button by clicking the SVG icon or link on sidebar
        print("Looking for Create button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create']").first
        if not create_btn.is_visible(timeout=3000):
            create_btn = page.locator("span:has-text('Create')").first

        print("Clicking Create button...")
        create_btn.click()
        time.sleep(3)

        # Wait for file input inside dialog
        print("Waiting for file input...")
        page.wait_for_selector("input[type='file']", timeout=10000)
        file_input = page.locator("input[type='file']").first
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Video file uploaded!")
        time.sleep(5)

        # Step 1: Crop -> Click Next
        print("Clicking Next (Crop)...")
        page.locator("button:has-text('Next'), div:has-text('Next')").filter(has_not=page.locator("div div")).last.click()
        time.sleep(3)

        # Step 2: Filters -> Click Next
        print("Clicking Next (Filters)...")
        page.locator("button:has-text('Next'), div:has-text('Next')").filter(has_not=page.locator("div div")).last.click()
        time.sleep(3)

        # Step 3: Share
        print("Clicking Share...")
        page.locator("button:has-text('Share'), div:has-text('Share')").last.click()
        print("✓ Clicked Share button!")

        time.sleep(15)
        print("Upload completed!")
        browser.close()

if __name__ == "__main__":
    upload()
