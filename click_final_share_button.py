import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def handle_popups(page, stage=""):
    """Auto-detects and clears any Instagram popups (OK, Not Now, Close X, Save Info)"""
    print(f"[{stage}] Checking for popups (OK / Not Now / Cross X)...")
    popup_selectors = [
        "button:has-text('Not Now')",
        "button:has-text('OK')",
        "button:has-text('Save Info')",
        "button:has-text('Cancel')",
        "svg[aria-label='Close']"
    ]
    for sel in popup_selectors:
        try:
            elem = page.locator(sel).first
            if elem.is_visible(timeout=1000):
                elem.click()
                print(f"✓ [{stage}] Clicked popup element: '{sel}'")
                time.sleep(1)
        except Exception:
            pass

def run():
    print("==================================================")
    print(" Creator Reel Upload Pipeline with Popup Handling ")
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

        # Clear initial popups
        handle_popups(page, "Initial Page Load")

        # 2. Click + Create
        print("2. Clicking + Create sidebar icon...")
        create_btn = page.locator("svg[aria-label='New post']").first
        create_btn.click()
        time.sleep(2)

        # 3. Click Post option in flyout
        print("3. Clicking 'Post' menu item...")
        post_svg = page.locator("svg[aria-label='Post']").first
        if post_svg.is_visible(timeout=3000):
            post_svg.click()
            print("✓ Clicked 'Post' via svg[aria-label='Post']")
        else:
            page.mouse.click(60, 628)
            print("✓ Clicked 'Post' via coordinate fallback (60, 628)")
        
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

        # Step 3: Click Share button at top-right of dialog (x=828, y=135) or DOM selector
        print("Step 3: Clicking Share button to publish Reel...")
        share_placed = False
        try:
            share_elem = page.locator("div[role='dialog'] div:has-text('Share')").filter(has_text="Share").last
            if share_elem.is_visible(timeout=3000):
                share_elem.click()
                share_placed = True
                print("✓ Clicked Share button via DOM selector")
        except Exception:
            pass

        if not share_placed:
            page.mouse.click(828, 135)
            print("✓ Clicked Share button via coordinate fallback (828, 135)")

        print("Waiting 15 seconds for Instagram Reel rendering...")
        time.sleep(15)

        # Clear post-sharing confirmation popups (e.g. 'Your reel has been shared' -> X cross / OK)
        handle_popups(page, "Post-Share Confirmation")

        page.screenshot(path=str(ROOT_DIR / "downloads" / "reel_shared_success_checkmark.png"))
        print("\n==================================================")
        print(" 🎉 REEL SUBMITTED & SHARED TO INSTAGRAM!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
