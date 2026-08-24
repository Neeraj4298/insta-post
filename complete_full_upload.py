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
    print(" Complete End-to-End Instagram Reel Upload       ")
    print("==================================================")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to Instagram Login...")
        page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
        time.sleep(3)

        # Fill credentials
        u_input = page.locator("input[name='username'], input[type='text']").first
        if u_input.is_visible(timeout=5000):
            print("Entering username & password...")
            u_input.fill(USERNAME)
            time.sleep(1)
            p_input = page.locator("input[name='password'], input[type='password']").first
            p_input.fill(PASSWORD)
            time.sleep(1)
            p_input.press("Enter")
            print("Submitted login. Waiting 8s...")
            time.sleep(8)

        # Handle reCAPTCHA if present
        for frame in page.frames:
            try:
                chk = frame.locator("#recaptcha-anchor, .recaptcha-checkbox-border").first
                if chk.is_visible(timeout=2000):
                    print("✓ Found reCAPTCHA checkbox! Clicking...")
                    chk.click()
                    time.sleep(5)
            except Exception:
                pass

        # Handle popups ('Save Info', 'Not Now')
        for txt in ["Save Info", "Save info", "Not Now", "Not now"]:
            try:
                b = page.locator(f"button:has-text('{txt}')")
                if b.is_visible(timeout=2000):
                    b.click()
                    time.sleep(1)
            except Exception:
                pass

        page.screenshot(path=str(ROOT_DIR / "downloads" / "logged_in_state.png"))
        print(f"Logged in page URL: {page.url}")

        # Locate Create button on sidebar
        print("Locating Create (+) button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], span:has-text('Create')").first
        if create_btn.is_visible(timeout=5000):
            create_btn.click()
            print("✓ Clicked Create button!")
            time.sleep(3)

        # Set video file
        print("Attaching video file...")
        file_input = page.locator("input[type='file']").first
        if file_input.is_visible(timeout=5000):
            file_input.set_input_files(VIDEO_PATH)
            print("✓ Set reel video file!")
            time.sleep(5)

            # Step 1: Crop -> Next
            print("Clicking Next (Step 1)...")
            n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n1.is_visible(timeout=3000):
                n1.click()
                time.sleep(3)

            # Step 2: Filters -> Next
            print("Clicking Next (Step 2)...")
            n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n2.is_visible(timeout=3000):
                n2.click()
                time.sleep(3)

            # Step 3: Share
            print("Clicking Share (Final)...")
            share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
            if share_btn.is_visible(timeout=3000):
                share_btn.click()
                print("✓ Reel posted successfully!")
                time.sleep(15)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_reel_post.png"))
        context.close()

if __name__ == "__main__":
    run()
