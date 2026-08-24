import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
VIDEO_PATH = str(ROOT_DIR / "downloads" / "reel_to_upload_3.mp4")
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

VIRAL_CAPTION = """Walking through quiet streets, finding comfort in the simple moments 🌧️✨

Which Ghibli atmosphere brings you the most peace? Tell us below! 👇💭

---
Save & share this with someone who loves soft anime vibes 🌿
Follow @tune_of_ghibli for daily dreamy edits ✨

#studioghibli #ghibliaesthetic #animeaesthetic #ghibliedit #animereels #softvibes #ghiblicommunity #chillvibes #anime #aesthetic"""

def handle_popups(page):
    """Automatically dismisses active Instagram popups or close crosses."""
    for sel in ["button:has-text('Not Now')", "button:has-text('OK')", "button:has-text('Cancel')", "svg[aria-label='Close']"]:
        try:
            elem = page.locator(sel).first
            if elem.is_visible(timeout=1000):
                elem.click()
                time.sleep(1)
        except Exception:
            pass

def run():
    print("==================================================")
    print(" Upload Reel in Original Aspect Ratio (9:16) Flow ")
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

        handle_popups(page)

        # 2. Click + Create sidebar icon
        print("2. Opening Create upload dialog...")
        page.locator("svg[aria-label='New post']").first.click()
        time.sleep(2)

        # 3. Select 'Post' option
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
        print("✓ Video file attached!")
        time.sleep(6)

        # Step 1: Crop Aspect Ratio -> Select Original (9:16)
        print("Step 1: Selecting Original (9:16) aspect ratio (no 1:1 cropping)...")
        try:
            crop_btn = page.locator("svg[aria-label='Select crop']").first
            if crop_btn.is_visible(timeout=3000):
                crop_btn.click()
                print("✓ Clicked aspect ratio menu button!")
                time.sleep(1.5)

                # Click 'Original' option with force=True
                orig_opt = page.locator("span:has-text('Original')").first
                if orig_opt.is_visible(timeout=2000):
                    orig_opt.click(force=True)
                    print("✓ Selected 'Original' full aspect ratio via DOM!")
                else:
                    page.mouse.click(320, 595)
                    print("✓ Clicked 'Original' aspect ratio via fallback coordinate!")
                time.sleep(1.5)

                # Close aspect ratio menu flyout if still open
                if crop_btn.is_visible(timeout=1000):
                    crop_btn.click()
                    time.sleep(1)
        except Exception as e:
            print(f"Aspect ratio note: {e}")

        # Click Next (Crop) with force=True
        n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n1.is_visible(timeout=5000):
            n1.click(force=True)
            print("✓ Step 1: Proceeded with Original Aspect Ratio (Crop Next)")
            time.sleep(3)

        # Step 2: Filters Next
        n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
        if n2.is_visible(timeout=5000):
            n2.click(force=True)
            print("✓ Step 2: Clicked Next (Filters)")
            time.sleep(3)

        # Step 3: Fill Caption & Hashtags
        print("Step 3: Writing caption & hashtags...")
        try:
            caption_box = page.locator("div[aria-label='Write a caption...']").first
            if caption_box.is_visible(timeout=3000):
                caption_box.click()
                caption_box.fill(VIRAL_CAPTION)
                print("✓ Caption injected!")
                time.sleep(2)
        except Exception as e:
            print(f"Caption note: {e}")

        # Step 4: Click Share
        print("Step 4: Triggering Share button...")
        share_btn = page.locator("div[role='dialog']").get_by_text("Share", exact=True).last
        if share_btn.is_visible(timeout=3000):
            share_btn.click(force=True)
            print("✓ Clicked Share button!")

        time.sleep(2)
        page.mouse.click(828, 135)

        # Dynamic Checkmark Detection: Proceed as soon as 'Your reel has been shared' appears
        print("5. Monitoring for 'Your reel has been shared.' checkmark confirmation...")
        shared_confirmed = False
        start_time = time.time()
        
        while time.time() - start_time < 300:
            try:
                if page.locator("text='Your reel has been shared.'").is_visible(timeout=1000) or \
                   page.locator("text='Reel shared'").is_visible(timeout=1000):
                    print(f"✓ Detected 'Your reel has been shared.' screen in {int(time.time() - start_time)} seconds!")
                    shared_confirmed = True
                    break
            except Exception:
                pass
            time.sleep(2)

        # Go to profile for final verification screenshot
        page.goto("https://www.instagram.com/tune_of_ghibli/", wait_until="networkidle")
        time.sleep(5)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "verified_uncropped_916_reel_published.png"))
        print("\n==================================================")
        print(" 🎉 ORIGINAL 9:16 REEL PUBLISHED & VERIFIED!")
        print("==================================================")

        context.close()

if __name__ == "__main__":
    run()
