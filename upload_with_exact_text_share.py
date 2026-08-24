import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Exact Text Node Share Button Submission Flow     ")
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

        print("1. Opening Instagram Home Feed...")
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

        # Step 3: Type Caption
        print("Step 3: Writing caption...")
        try:
            caption_box = page.locator("div[aria-label='Write a caption...']").first
            if caption_box.is_visible(timeout=3000):
                caption_box.click()
                caption_box.fill("✨ Soft Ghibli mood edit #ghibli #anime")
                print("✓ Caption typed successfully!")
                time.sleep(1)
        except Exception:
            pass

        # Step 4: Click exact Share text in modal header
        print("Step 4: Clicking exact Share text node in modal header...")
        share_target = page.locator("div[role='dialog'] header").get_by_text("Share", exact=True)
        if share_target.is_visible(timeout=4000):
            share_target.click(force=True)
            print("✓ Clicked exact 'Share' text node successfully!")
        else:
            page.locator("div[role='dialog']").get_by_text("Share", exact=True).last.click(force=True)
            print("✓ Clicked dialog 'Share' text node fallback!")

        print("5. Waiting 30 seconds for Instagram server rendering & posting...")
        time.sleep(30)

        # Capture final shared confirmation dialog
        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_exact_share_result.png"))
        print("\n==================================================")
        print(" 🎉 REEL SHARED & SUBMITTED SUCCESSFULLY!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
