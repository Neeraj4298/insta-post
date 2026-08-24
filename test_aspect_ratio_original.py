import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def run():
    print("==================================================")
    print(" Testing Original Aspect Ratio (9:16) Selector    ")
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
        page.locator("svg[aria-label='New post']").first.click()
        time.sleep(2)

        # 3. Select Post
        post_svg = page.locator("svg[aria-label='Post']").first
        if post_svg.is_visible(timeout=3000):
            post_svg.click()
        else:
            page.mouse.click(60, 628)
        time.sleep(3)

        # 4. Attach Video File
        file_input = page.locator("input[type='file']").first
        file_input.wait_for(state="attached", timeout=10000)
        file_input.set_input_files(VIDEO_PATH)
        print("✓ Video file attached!")
        time.sleep(6)

        # Step 1: Aspect Ratio Selection (Select 'Original' 9:16)
        print("Step 1: Selecting Original (9:16) Aspect Ratio...")
        try:
            # Click crop/aspect ratio selector icon at bottom left of modal
            crop_btn = page.locator("svg[aria-label='Select crop']").first
            if crop_btn.is_visible(timeout=3000):
                crop_btn.click()
                print("✓ Clicked aspect ratio selector icon!")
                time.sleep(1.5)

                # Select 'Original' or 9:16 ratio option
                orig_opt = page.locator("button:has-text('Original'), span:has-text('Original'), svg[aria-label='Photo outline']").first
                if orig_opt.is_visible(timeout=2000):
                    orig_opt.click()
                    print("✓ Selected 'Original' aspect ratio!")
                    time.sleep(1)
        except Exception as e:
            print(f"Aspect ratio selection note: {e}")

        page.screenshot(path=str(ROOT_DIR / "downloads" / "crop_aspect_ratio_original.png"))
        print("✓ Saved crop_aspect_ratio_original.png")

        context.close()

if __name__ == "__main__":
    run()
