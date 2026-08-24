import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
PROFILE_DIR = str(ROOT_DIR / "browser_profile")

def click_coords():
    print("==================================================")
    print(" Playwright Direct reCAPTCHA Click & Upload       ")
    print("==================================================")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(3)

        print("Clicking reCAPTCHA checkbox coordinates (x=281, y=153)...")
        try:
            page.mouse.click(281, 153)
            print("✓ Clicked mouse at (281, 153)!")
            time.sleep(5)
        except Exception as e:
            print(f"Mouse click error: {e}")

        # Also try clicking frame anchor
        try:
            f = page.frame_locator("iframe").first
            f.locator("#recaptcha-anchor, .recaptcha-checkbox-border, div.recaptcha-checkbox-checkmark").first.click()
            print("✓ Clicked frame anchor!")
            time.sleep(5)
        except Exception as e:
            pass

        page.screenshot(path=str(ROOT_DIR / "downloads" / "post_captcha_click.png"))
        print(f"Saved screenshot to {ROOT_DIR / 'downloads' / 'post_captcha_click.png'}")

        # Check if login input is visible
        u_input = page.locator("input[name='username'], input[type='text']").first
        if u_input.is_visible(timeout=5000):
            print("Entering username & password...")
            u_input.fill(USERNAME)
            p_input = page.locator("input[name='password'], input[type='password']").first
            p_input.fill(PASSWORD)
            p_input.press("Enter")
            print("Submitted login. Waiting 8s...")
            time.sleep(8)

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

        # Click Create
        print("Clicking Create button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], span:has-text('Create')").first
        if create_btn.is_visible(timeout=5000):
            create_btn.click()
            time.sleep(3)

        # Set video file
        print("Attaching video file...")
        file_input = page.locator("input[type='file']").first
        if file_input.is_visible(timeout=5000):
            file_input.set_input_files(VIDEO_PATH)
            print("✓ Set video file!")
            time.sleep(5)

            # Step 1: Crop -> Next
            n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n1.is_visible(timeout=3000):
                n1.click()
                time.sleep(3)

            # Step 2: Filters -> Next
            n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n2.is_visible(timeout=3000):
                n2.click()
                time.sleep(3)

            # Step 3: Share
            share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
            if share_btn.is_visible(timeout=3000):
                share_btn.click()
                print("✓ Clicked Share button!")
                time.sleep(15)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_coords_result.png"))
        context.close()

if __name__ == "__main__":
    click_coords()
