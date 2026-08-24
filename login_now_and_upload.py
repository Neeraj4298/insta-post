import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
PROFILE_DIR = str(ROOT_DIR / "browser_profile")

def login_and_upload():
    print("==================================================")
    print(" Logging in to Instagram & Uploading Reel         ")
    print("==================================================")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to Instagram Login page...")
        page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
        time.sleep(3)

        print("Filling login credentials...")
        page.wait_for_selector("input[name='username']", timeout=10000)
        page.fill("input[name='username']", USERNAME)
        time.sleep(1)
        page.fill("input[name='password']", PASSWORD)
        time.sleep(1)

        print("Clicking Log in button...")
        page.click("button[type='submit']")
        print("Login submitted. Waiting 10 seconds for main feed...")
        time.sleep(10)

        # Handle post-login popups
        for txt in ["Save Info", "Save info", "Not Now", "Not now"]:
            try:
                b = page.locator(f"button:has-text('{txt}')")
                if b.is_visible(timeout=2000):
                    b.click()
                    time.sleep(1)
            except Exception:
                pass

        page.screenshot(path=str(ROOT_DIR / "downloads" / "after_login.png"))
        print(f"Current page URL: {page.url}")

        # Locate Create button on sidebar
        print("Clicking Create (+) button on sidebar...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], a:has-text('Create'), span:has-text('Create')").first
        create_btn.wait_for(state="visible", timeout=10000)
        create_btn.click()
        print("✓ Clicked Create button!")
        time.sleep(3)

        # Attach video file
        print("Attaching video file to upload dialog...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Video file set successfully!")
        time.sleep(6)

        # Step 1: Crop -> Next
        print("Clicking Next (Step 1: Crop)...")
        n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
        n1.click()
        time.sleep(3)

        # Step 2: Filters -> Next
        print("Clicking Next (Step 2: Filters)...")
        n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
        n2.click()
        time.sleep(3)

        # Step 3: Share
        print("Clicking Share (Step 3: Publish)...")
        share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
        share_btn.click()
        print("✓ Clicked Share button!")

        print("Waiting 20 seconds for video upload and processing...")
        time.sleep(20)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_published_reel.png"))
        print("\n==================================================")
        print(" 🎉 REEL PUBLISHED SUCCESSFULLY!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    login_and_upload()
