import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
PROFILE_DIR = str(ROOT_DIR / "browser_profile")

def click_captcha_and_upload():
    print("==================================================")
    print(" Clicking Meta reCAPTCHA & Uploading Reel        ")
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

        print(f"Loaded page URL: {page.url}")

        # Find and click reCAPTCHA checkbox inside any frame
        frames = page.frames
        print(f"Total page frames: {len(frames)}")

        clicked = False
        for frame in frames:
            try:
                cb = frame.locator("#recaptcha-anchor, .recaptcha-checkbox-border, div.recaptcha-checkbox-checkmark").first
                if cb.is_visible(timeout=3000):
                    print(f"✓ Found reCAPTCHA checkbox in frame: {frame.name or frame.url}! Clicking now...")
                    cb.click()
                    clicked = True
                    time.sleep(5)
                    break
            except Exception as e:
                pass

        if not clicked:
            print("Fallback: trying main frame iframe locator...")
            try:
                frame_loc = page.frame_locator("iframe[src*='recaptcha']").first
                chk = frame_loc.locator("#recaptcha-anchor").first
                if chk.is_visible(timeout=3000):
                    chk.click()
                    print("✓ Clicked reCAPTCHA anchor via frame_locator!")
                    time.sleep(5)
            except Exception as e:
                print(f"Frame locator click error: {e}")

        # Screenshot after clicking captcha
        page.screenshot(path=str(ROOT_DIR / "downloads" / "after_captcha_click.png"))
        print(f"Saved screenshot: {ROOT_DIR / 'downloads' / 'after_captcha_click.png'}")

        # If submit button appears on captcha page, click it
        submit_btn = page.locator("button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Next')").first
        if submit_btn.is_visible(timeout=3000):
            print("Clicking post-captcha Submit/Next button...")
            submit_btn.click()
            time.sleep(6)

        # Check if login input is visible
        u_input = page.locator("input[name='username'], input[type='text']").first
        if u_input.is_visible(timeout=3000):
            print("Logging in...")
            u_input.fill(USERNAME)
            p_input = page.locator("input[name='password'], input[type='password']").first
            p_input.fill(PASSWORD)
            p_input.press("Enter")
            time.sleep(8)

        # Handle popups
        for label in ["Not Now", "Not now", "Save Info", "Save info"]:
            try:
                btn = page.locator(f"button:has-text('{label}')")
                if btn.is_visible(timeout=2000):
                    btn.click()
                    time.sleep(1)
            except Exception:
                pass

        page.goto(f"https://www.instagram.com/{USERNAME}/", wait_until="networkidle")
        time.sleep(3)

        # Click Create (+) button
        print("Clicking Create button...")
        create_btn = page.locator("svg[aria-label='New post'], svg[aria-label='Create'], a:has-text('Create'), span:has-text('Create')").first
        if create_btn.is_visible(timeout=3000):
            create_btn.click()
            time.sleep(3)

        # File input for reel upload
        print("Attaching video file...")
        file_input = page.locator("input[type='file']").first
        if file_input.is_visible(timeout=5000):
            file_input.set_input_files(VIDEO_PATH)
            print("✓ Set input video file!")
            time.sleep(5)

            # Step 1: Crop -> Next
            n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n1.is_visible():
                n1.click()
                time.sleep(3)

            # Step 2: Edit -> Next
            n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n2.is_visible():
                n2.click()
                time.sleep(3)

            # Step 3: Share
            s = page.locator("div[role='dialog'] div:has-text('Share')").last
            if s.is_visible():
                s.click()
                print("✓ Clicked Share button!")
                time.sleep(15)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_captcha_flow.png"))
        context.close()

if __name__ == "__main__":
    click_captcha_and_upload()
