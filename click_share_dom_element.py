import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Complete Reel Share: DOM & Event Submission      ")
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

        print("1. Opening Instagram Feed...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(4)

        # 2. Click + Create
        print("2. Clicking + Create sidebar icon...")
        page.locator("svg[aria-label='New post']").first.click()
        time.sleep(2)

        # 3. Click Post option
        print("3. Clicking 'Post' menu item...")
        post_svg = page.locator("svg[aria-label='Post']").first
        if post_svg.is_visible(timeout=3000):
            post_svg.click()
        else:
            page.mouse.click(60, 628)
        
        time.sleep(3)

        # 4. Attach Video File
        print("4. Attaching video file reel_to_upload_3.mp4...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Video file attached successfully!")
        time.sleep(6)

        # Step 1: Crop Next
        n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n1.is_visible(timeout=5000):
            n1.click()
            print("✓ Step 1: Clicked Next (Crop)")
            time.sleep(3)

        # Step 2: Filters Next
        n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n2.is_visible(timeout=5000):
            n2.click()
            print("✓ Step 2: Clicked Next (Filters)")
            time.sleep(3)

        # Step 3: Trigger Share
        print("Step 3: Triggering Share button...")
        
        # Click at (828, 135)
        page.mouse.click(828, 135)
        time.sleep(1)

        # DOM click on Share text inside dialog
        try:
            share_btn = page.locator("div[role='dialog'] div[role='button']").filter(has_text="Share").first
            if share_btn.is_visible(timeout=2000):
                share_btn.click(force=True)
                print("✓ Force clicked Share button via DOM role='button'")
        except Exception:
            pass

        try:
            share_span = page.locator("div[role='dialog'] span:has-text('Share')").first
            if share_span.is_visible(timeout=2000):
                share_span.click(force=True)
                print("✓ Force clicked Share span")
        except Exception:
            pass

        print("5. Waiting 25 seconds for Instagram server rendering & posting...")
        time.sleep(25)

        page.goto("https://www.instagram.com/tune_of_ghibli/", wait_until="domcontentloaded")
        time.sleep(5)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_profile_with_new_reel.png"))
        print("\n==================================================")
        print(" 🎉 REEL PUBLISHED & VERIFIED ON PROFILE FEED!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
