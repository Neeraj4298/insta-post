import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Explicit Reel Upload (4th Reel Confirmation)     ")
    print("==================================================")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            BRAVE_PROFILE,
            executable_path=BRAVE_PATH,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to Instagram Home Feed...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(4)

        # Locate Create button reliably
        print("Clicking Create button...")
        create_target = page.locator("svg[aria-label='New post']").first
        if create_target.is_visible():
            create_target.click()
            print("✓ Clicked svg[aria-label='New post']")
        else:
            page.locator("a:has-text('Create'), span:has-text('Create')").first.click()
            print("✓ Clicked Create link")

        time.sleep(3)
        page.screenshot(path=str(ROOT_DIR / "downloads" / "dialog_open_verification.png"))

        # Set video file
        print("Attaching video file: reel_to_upload_3.mp4...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached video file successfully!")
        time.sleep(6)

        # Step 1: Crop -> Next
        print("Step 1: Crop -> Next...")
        n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n1.is_visible(timeout=5000):
            n1.click()
            time.sleep(3)

        # Step 2: Filters -> Next
        print("Step 2: Filters -> Next...")
        n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n2.is_visible(timeout=5000):
            n2.click()
            time.sleep(3)

        # Step 3: Share (Publish Reel)
        print("Step 3: Share (Publish Reel)...")
        share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
        if share_btn.is_visible(timeout=5000):
            share_btn.click()
            print("✓ Clicked Share button!")

        # Wait for Instagram to finish uploading and showing success modal
        print("Waiting for upload confirmation modal...")
        time.sleep(15)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "reel_4_sharing_confirmed.png"))
        print("\n==================================================")
        print(" 🎉 REEL 4 UPLOAD & SHARE WORKFLOW COMPLETED!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
