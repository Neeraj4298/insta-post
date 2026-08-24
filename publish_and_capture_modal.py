import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Publishing New Reel & Capturing Modal Result     ")
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

        # Click Plus icon on sidebar (x=28, y=556)
        print("Clicking sidebar Plus icon at (x=28, y=556)...")
        page.mouse.click(28, 556)
        time.sleep(3)

        # Set input file
        print("Attaching NEW video file to upload dialog...")
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Attached video file successfully!")
        time.sleep(6)

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

        # Capture screenshots during upload processing
        for i in range(1, 6):
            time.sleep(5)
            sc_file = str(ROOT_DIR / "downloads" / f"publish_status_{i}.png")
            page.screenshot(path=sc_file)
            print(f"Captured publish_status_{i}.png")

            # Check if 'Your reel has been shared' modal text appears
            if page.locator("text='Your reel has been shared'").is_visible() or page.locator("text='Your post has been shared'").is_visible():
                print("🎉 Instagram confirmed: 'Your reel has been shared!'")
                break

        print("\n==================================================")
        print(" REEL PUBLISH SEQUENCE COMPLETED!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
