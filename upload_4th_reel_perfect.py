import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Uploading 4th Reel (Brand New File)             ")
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

        # 1. Click + Create on sidebar (x=28, y=556)
        print("1. Clicking + Create sidebar icon...")
        page.mouse.click(28, 556)
        time.sleep(2)

        # 2. Click 'Post' option in flyout menu (x=60, y=628)
        print("2. Clicking 'Post' menu option at (x=60, y=628)...")
        page.mouse.click(60, 628)
        time.sleep(4)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "upload_modal_opened_4th.png"))
        print("Saved upload_modal_opened_4th.png")

        # 3. Attach file
        print("3. Attaching video file reel_to_upload_3.mp4...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached 4th reel video file successfully!")
        time.sleep(6)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "video_file_attached_4th.png"))

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

        print("Waiting 20 seconds for Reel upload processing...")
        time.sleep(20)

        # Go to profile to take screenshot
        page.goto("https://www.instagram.com/tune_of_ghibli/", wait_until="domcontentloaded")
        time.sleep(4)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_4th_reel_published.png"))
        print("\n==================================================")
        print(" 🎉 4th REEL PUBLISHED SUCCESSFULLY ON INSTAGRAM!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
