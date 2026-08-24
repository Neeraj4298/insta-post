import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Explicit 'Post' Menu Click & Reel Upload        ")
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

        # Step 1: Click + Create
        print("Clicking + Create on sidebar...")
        create_btn = page.locator("svg[aria-label='New post']").first
        create_btn.click()
        time.sleep(2)

        # Step 2: Click Post item
        print("Clicking 'Post' sub-item...")
        post_item = page.locator("span:has-text('Post')").first
        if post_item.is_visible(timeout=3000):
            post_item.click()
            print("✓ Clicked Post menu item via locator!")
            time.sleep(3)
        else:
            print("Clicking Post at mouse coordinates (x=60, y=628)...")
            page.mouse.click(60, 628)
            time.sleep(3)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "upload_dialog_opened.png"))
        print("Saved upload_dialog_opened.png")

        # Step 3: Set input video file
        print("Attaching video file to upload dialog...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Set reel video file successfully!")
        time.sleep(6)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "reel_file_attached.png"))

        # Step 4: Crop -> Next
        print("Clicking Next (Step 1: Crop)...")
        n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n1.is_visible(timeout=5000):
            n1.click()
            time.sleep(3)

        # Step 5: Filters -> Next
        print("Clicking Next (Step 2: Filters - No Edits)...")
        n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n2.is_visible(timeout=5000):
            n2.click()
            time.sleep(3)

        # Step 6: Share (Publish)
        print("Clicking Share (Step 3: Publish Reel)...")
        share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
        if share_btn.is_visible(timeout=5000):
            share_btn.click()
            print("✓ Clicked Share button!")

        print("Waiting 20 seconds for Instagram to upload and process the Reel...")
        time.sleep(20)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_reel_published_brave.png"))
        print("\n==================================================")
        print(" 🎉 REEL PUBLISHED SUCCESSFULLY ON INSTAGRAM!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
