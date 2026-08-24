import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Sidebar Navigation Create Click & Reel Upload    ")
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

        # Click Create button specifically inside sidebar navigation
        print("Locating sidebar Create button...")
        sidebar_create = page.locator("div[role='navigation'] a:has-text('Create'), div[role='navigation'] span:has-text('Create'), div[role='navigation'] svg[aria-label='New post']").first
        
        if sidebar_create.is_visible(timeout=5000):
            print("✓ Found sidebar Create button! Clicking...")
            sidebar_create.click()
            time.sleep(4)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "sidebar_create_clicked.png"))
        print("Saved screenshot: sidebar_create_clicked.png")

        # Set input video file
        print("Attaching video file to upload dialog...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached video file successfully!")
        time.sleep(6)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "reel_file_ready.png"))

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

        print("Waiting 20 seconds for video upload and post processing...")
        time.sleep(20)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_reel_published_sidebar.png"))
        print("\n==================================================")
        print(" 🎉 REEL PUBLISHED SUCCESSFULLY ON INSTAGRAM!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
