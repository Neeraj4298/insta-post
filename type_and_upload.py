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
    print(" Playwright Key Typing & Reel Upload             ")
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

        print("Clicking username field and typing...")
        inputs = page.locator("input").all()
        print(f"Total inputs found: {len(inputs)}")

        if len(inputs) >= 2:
            # First input: username
            inputs[0].click()
            inputs[0].type(USERNAME, delay=50)
            time.sleep(1)

            # Second input: password
            inputs[1].click()
            inputs[1].type(PASSWORD, delay=50)
            time.sleep(1)

            print("Pressing Enter to submit login...")
            inputs[1].press("Enter")
            time.sleep(10)

        # Handle popups
        for txt in ["Save Info", "Save info", "Not Now", "Not now"]:
            try:
                b = page.locator(f"button:has-text('{txt}')")
                if b.is_visible(timeout=2000):
                    b.click()
                    time.sleep(1)
            except Exception:
                pass

        page.screenshot(path=str(ROOT_DIR / "downloads" / "logged_in_typed.png"))
        print(f"Current page URL: {page.url}")

        # Click Create button
        print("Clicking Create (+) button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], span:has-text('Create')").first
        if create_btn.is_visible(timeout=5000):
            create_btn.click()
            print("✓ Clicked Create button!")
            time.sleep(3)
        else:
            print("Using JS click on Create item...")
            page.evaluate("""() => {
                const els = Array.from(document.querySelectorAll('a, button, div, span'));
                const el = els.find(e => e.textContent.trim() === 'Create' || e.querySelector('svg[aria-label="New post"]'));
                if (el) el.click();
            }""")
            time.sleep(3)

        # File input for reel upload
        print("Attaching video file...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
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

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_typed_published.png"))
        print("\n==================================================")
        print(" 🎉 REEL PUBLISHED SUCCESSFULLY!")
        print("==================================================")
        context.close()

if __name__ == "__main__":
    run()
