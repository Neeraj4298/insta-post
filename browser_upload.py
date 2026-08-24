import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

USERNAME = "tune_of_ghibli"
PASSWORD = "Dob@28082003"
VIDEO_PATH = str(Path(__file__).resolve().parent / "downloads" / "reel_to_upload.mp4")

def run():
    print("==================================================")
    print("   Automated Instagram Reel Upload via Playwright  ")
    print("==================================================")
    print(f"Target Account: @{USERNAME}")
    print(f"Video Path: {VIDEO_PATH}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print("\nNavigating to Instagram...")
        page.goto(f"https://www.instagram.com/{USERNAME}/", wait_until="networkidle")
        time.sleep(3)

        # Check if login required
        if "login" in page.url or page.locator("input[name='username']").is_visible():
            print("Logging in...")
            page.goto("https://www.instagram.com/accounts/login/")
            time.sleep(2)
            page.fill("input[name='username']", USERNAME)
            page.fill("input[name='password']", PASSWORD)
            page.click("button[type='submit']")
            time.sleep(6)

        # Handle modal popups ('Not Now', 'Save Info')
        for txt in ["Not Now", "Not now", "Save Info", "Save info"]:
            try:
                btn = page.locator(f"button:has-text('{txt}')")
                if btn.is_visible(timeout=2000):
                    btn.click()
                    time.sleep(1)
            except Exception:
                pass

        page.goto(f"https://www.instagram.com/{USERNAME}/", wait_until="networkidle")
        time.sleep(3)

        print(f"On Instagram profile: {page.url}")

        # Locate Create (+) button on sidebar
        create_selectors = [
            "svg[aria-label='New post']",
            "svg[aria-label='Create']",
            "a:has-text('Create')",
            "span:has-text('Create')",
            "div:has-text('Create')"
        ]

        clicked = False
        for sel in create_selectors:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=2000):
                    print(f"Clicking Create element with selector: {sel}")
                    loc.click()
                    clicked = True
                    break
            except Exception:
                pass

        if not clicked:
            print("Trying direct click on sidebar '+' icon...")
            page.click("div[role='dialog']", timeout=3000)

        time.sleep(3)

        # File input for video upload
        print("Uploading file to input element...")
        file_input = page.locator("input[type='file']").first
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Video file attached!")
        time.sleep(6)

        # Handle 'OK' / 'Discard' / Ratio prompts if any
        try:
            ok_btn = page.locator("button:has-text('OK')").first
            if ok_btn.is_visible(timeout=2000):
                ok_btn.click()
                time.sleep(1)
        except Exception:
            pass

        # Click Next (crop screen)
        print("Clicking Next (Step 1)...")
        next1 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if next1.is_visible():
            next1.click()
            time.sleep(3)

        # Click Next (filters/edits screen)
        print("Clicking Next (Step 2 - No Edits)...")
        next2 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if next2.is_visible():
            next2.click()
            time.sleep(3)

        # Click Share (final step)
        print("Clicking Share (Final Step)...")
        share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
        if share_btn.is_visible():
            share_btn.click()
            print("✓ Clicked Share button!")

        print("Waiting for post confirmation...")
        time.sleep(15)

        print("\n==================================================")
        print(" 🎉 REEL UPLOAD FLOW COMPLETED!")
        print("==================================================")
        browser.close()

if __name__ == "__main__":
    run()
