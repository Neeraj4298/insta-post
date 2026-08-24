import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Direct Create Click & 4th Reel Upload           ")
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

        # Click Create span or link
        print("Clicking Create button...")
        create_btn = page.locator("span:has-text('Create')").first
        create_btn.click()
        time.sleep(2)

        # Click Post menu item if flyout appears
        post_item = page.locator("span:has-text('Post')").first
        if post_item.is_visible(timeout=3000):
            print("Clicking Post menu item...")
            post_item.click()
            time.sleep(2)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "direct_modal_open.png"))
        print("Saved direct_modal_open.png")

        # Set file
        print("Attaching video file: reel_to_upload_3.mp4...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached 4th reel video file successfully!")
        time.sleep(6)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "direct_file_attached.png"))

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

        print("Waiting 25 seconds for upload and post completion...")
        time.sleep(25)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "direct_4th_reel_shared.png"))
        print("\n==================================================")
        print(" 🎉 4th REEL PUBLISHED SUCCESSFULLY!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
