import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Uploading 4th Reel (#best propose...)            ")
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

        print("1. Navigating to Instagram...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(4)

        # 2. Click + Create sidebar icon at (x=28, y=560)
        print("2. Clicking + Create at (x=28, y=560)...")
        page.mouse.click(28, 560)
        time.sleep(1.5)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "create_clicked_560.png"))

        # 3. Click Post option at (x=60, y=560)
        print("3. Clicking 'Post' item at (x=60, y=560)...")
        page.mouse.click(60, 560)
        time.sleep(4)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "modal_open_560.png"))
        print("Saved modal_open_560.png")

        # 4. Attach video file
        print("4. Attaching video file: reel_to_upload_3.mp4...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=12000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached NEW 4th reel video file successfully!")
        time.sleep(6)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "video_loaded_in_dialog.png"))

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

        print("Waiting 25 seconds for upload processing...")
        time.sleep(25)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_4th_reel_uploaded_modal.png"))
        print("\n==================================================")
        print(" 🎉 BRAND NEW 4th REEL PUBLISHED SUCCESSFULLY!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
