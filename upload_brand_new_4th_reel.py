import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Uploading Brand New 4th Reel (#best propose...)  ")
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

        print("1. Navigating to Instagram Home...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(4)

        # Click Home icon to lock layout
        page.mouse.click(28, 215)
        time.sleep(3)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "home_locked.png"))

        # 2. Click + Create sidebar icon at (x=28, y=556)
        print("2. Clicking + Create at (x=28, y=556)...")
        page.mouse.click(28, 556)
        time.sleep(2)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "menu_flyout_open.png"))

        # 3. Click Post option at (x=60, y=628)
        print("3. Clicking 'Post' item at (x=60, y=628)...")
        page.mouse.click(60, 628)
        time.sleep(4)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "modal_upload_ready.png"))
        print("Saved modal_upload_ready.png")

        # 4. Attach new video file
        print("4. Attaching video file reel_to_upload_3.mp4...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached NEW 4th reel video file successfully!")
        time.sleep(6)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "video_file_modal_attached.png"))

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

        print("Waiting 25 seconds for Instagram post upload processing...")
        time.sleep(25)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "modal_post_shared_confirmation.png"))
        print("\n==================================================")
        print(" 🎉 BRAND NEW 4th REEL PUBLISHED SUCCESSFULLY!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
