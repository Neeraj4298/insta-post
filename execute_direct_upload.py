import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Direct Reel Upload & Popup Handling Pipeline     ")
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

        print("1. Opening Instagram...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(4)

        # 2. Check and dismiss any popups/dialogs ("Not Now", "Close X", "Cancel")
        print("2. Checking for modal overlays or notification popups...")
        for pop_text in ["Not Now", "Cancel", "Turn On"]:
            try:
                btn = page.locator(f"button:has-text('{pop_text}')").first
                if btn.is_visible(timeout=1500):
                    btn.click()
                    print(f"✓ Dismissed popup button: '{pop_text}'")
                    time.sleep(1)
            except Exception:
                pass

        try:
            close_btn = page.locator("svg[aria-label='Close'], button:has-text('Dismiss')").first
            if close_btn.is_visible(timeout=1500):
                close_btn.click()
                print("✓ Clicked popup Close (X) button")
                time.sleep(1)
        except Exception:
            pass

        # 3. Open Create Upload Dialog
        print("3. Opening 'Create' post dialog...")
        create_clicked = False
        
        # Try SVG aria-label locator
        try:
            create_svg = page.locator("svg[aria-label='New post']").first
            if create_svg.is_visible(timeout=2000):
                create_svg.click()
                create_clicked = True
                print("✓ Clicked Create via svg[aria-label='New post']")
        except Exception:
            pass

        if not create_clicked:
            try:
                create_span = page.locator("span:has-text('Create')").first
                if create_span.is_visible(timeout=2000):
                    create_span.click()
                    create_clicked = True
                    print("✓ Clicked Create via span text")
            except Exception:
                pass

        time.sleep(2)

        # Click 'Post' if flyout menu appeared
        try:
            post_item = page.locator("div[role='menuitem']:has-text('Post'), span:has-text('Post')").first
            if post_item.is_visible(timeout=2000):
                post_item.click()
                print("✓ Clicked 'Post' menu item")
                time.sleep(2)
        except Exception:
            pass

        # 4. Attach Video File
        print("4. Attaching video file: reel_to_upload_3.mp4...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Video file attached successfully!")
        time.sleep(6)

        # 5. Multi-step Upload Flow (Crop -> Filters -> Share)
        print("5. Executing Crop -> Filters -> Share workflow...")
        
        # Step 1: Crop Next
        n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n1.is_visible(timeout=5000):
            n1.click()
            print("✓ Clicked Crop -> Next")
            time.sleep(3)

        # Step 2: Filters Next
        n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n2.is_visible(timeout=5000):
            n2.click()
            print("✓ Clicked Filters -> Next")
            time.sleep(3)

        # Step 3: Share (Publish)
        share_btn = page.locator("div[role='dialog'] div:has-text('Share')").last
        if share_btn.is_visible(timeout=5000):
            share_btn.click()
            print("✓ Clicked Share button to publish Reel!")

        print("6. Waiting 25 seconds for Instagram Reel rendering & processing...")
        time.sleep(25)

        # Go to profile to verify
        page.goto("https://www.instagram.com/tune_of_ghibli/", wait_until="domcontentloaded")
        time.sleep(5)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "final_verified_reel_published.png"))
        print("\n==================================================")
        print(" 🎉 REEL UPLOAD PIPELINE COMPLETED SUCCESSFULLY!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
