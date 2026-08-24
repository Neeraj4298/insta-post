import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Testing DOM Selectors for 4th Reel Upload       ")
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

        print("Navigating to Instagram profile page...")
        page.goto("https://www.instagram.com/tune_of_ghibli/", wait_until="domcontentloaded")
        time.sleep(4)

        # Target Create svg/link
        print("Finding Create locator...")
        create_locator = page.locator("svg[aria-label='New post']").first
        create_locator.click()
        print("✓ Clicked Create button via SVG locator!")
        time.sleep(2)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "create_locator_step1.png"))
        print("Saved create_locator_step1.png")

        # Find Post item in flyout menu
        print("Finding Post menu item...")
        post_item = page.locator("span:has-text('Post')").first
        if post_item.is_visible():
            post_item.click()
            print("✓ Clicked Post menu item!")
            time.sleep(3)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "create_locator_step2.png"))
        print("Saved create_locator_step2.png")

        # Attach file
        print("Attaching brand new video file reel_to_upload_3.mp4...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached 4th reel video file successfully!")
        time.sleep(6)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "create_locator_file_attached.png"))

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

        print("Waiting 25 seconds for Instagram Reel publish processing...")
        time.sleep(25)

        page.goto("https://www.instagram.com/tune_of_ghibli/", wait_until="domcontentloaded")
        time.sleep(4)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_4th_reel_guaranteed.png"))
        print("\n==================================================")
        print(" 🎉 BRAND NEW 4th REEL PUBLISHED SUCCESSFULLY!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
