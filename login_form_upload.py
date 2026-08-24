import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
PROFILE_DIR = str(ROOT_DIR / "browser_profile")

def upload_now():
    print("==================================================")
    print(" Executing Instagram Reel Upload Flow             ")
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

        # Target inputs by label/placeholder/type
        print("Filling login form...")
        u_box = page.locator("input[aria-label*='username'], input[placeholder*='username'], input[name='username']").first
        if not u_box.is_visible():
            u_box = page.locator("input[type='text'], input[type='email']").first
        
        u_box.click()
        u_box.fill(USERNAME)
        time.sleep(1)

        p_box = page.locator("input[aria-label*='Password'], input[placeholder*='Password'], input[name='password']").first
        if not p_box.is_visible():
            p_box = page.locator("input[type='password']").first

        p_box.click()
        p_box.fill(PASSWORD)
        time.sleep(1)

        print("Clicking Log in button...")
        login_btn = page.locator("button[type='submit'], button:has-text('Log in')").first
        login_btn.click()

        print("Login submitted. Waiting 10 seconds for main feed...")
        time.sleep(10)

        # Check for reCAPTCHA iframe after submit
        for frame in page.frames:
            try:
                chk = frame.locator("#recaptcha-anchor, .recaptcha-checkbox-border").first
                if chk.is_visible(timeout=2000):
                    print("✓ Found reCAPTCHA checkbox after login! Clicking...")
                    chk.click()
                    time.sleep(5)
            except Exception:
                pass

        # Handle post-login popups
        for txt in ["Save Info", "Save info", "Not Now", "Not now"]:
            try:
                b = page.locator(f"button:has-text('{txt}')")
                if b.is_visible(timeout=2000):
                    b.click()
                    time.sleep(1)
            except Exception:
                pass

        page.screenshot(path=str(ROOT_DIR / "downloads" / "post_login_state.png"))
        print(f"Current Page URL: {page.url}")

        # Click Create (+) button
        print("Clicking Create (+) button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], span:has-text('Create'), a[href='#']").first
        if create_btn.is_visible(timeout=5000):
            create_btn.click()
            print("✓ Clicked Create button!")
            time.sleep(3)
        else:
            print("Trying JavaScript click on Create menu item...")
            page.evaluate("""() => {
                const els = Array.from(document.querySelectorAll('a, button, div, span'));
                const el = els.find(e => e.textContent.trim() === 'Create' || e.querySelector('svg[aria-label="New post"]'));
                if (el) el.click();
            }""")
            time.sleep(3)

        # Set video file
        print("Attaching video file to upload dialog...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached video file successfully!")
        time.sleep(6)

        # Step 1: Crop -> Next
        print("Clicking Next (Step 1: Crop)...")
        n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n1.is_visible(timeout=3000):
            n1.click()
            time.sleep(3)

        # Step 2: Filters -> Next
        print("Clicking Next (Step 2: Filters - No Edits)...")
        n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n2.is_visible(timeout=3000):
            n2.click()
            time.sleep(3)

        # Step 3: Share
        print("Clicking Share (Publish Reel)...")
        share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
        if share_btn.is_visible(timeout=3000):
            share_btn.click()
            print("✓ Clicked Share button!")

        print("Waiting 20 seconds for video upload and post processing...")
        time.sleep(20)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_reel_published.png"))
        print("\n==================================================")
        print(" 🎉 REEL PUBLISHED SUCCESSFULLY!")
        print("==================================================")
        context.close()

if __name__ == "__main__":
    upload_now()
