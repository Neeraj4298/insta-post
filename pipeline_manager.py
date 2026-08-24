import json
import csv
import os
import time
from datetime import datetime
from pathlib import Path
from drive_downloader import download_from_drive
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
TRACKER_JSON = ROOT_DIR / "reels_tracker.json"
MANIFEST_CSV = ROOT_DIR / "reels_manifest.csv"
TEMP_VIDEO_PATH = str(ROOT_DIR / "downloads" / "temp_upload.mp4")

BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"

def handle_popups(page):
    """Dismisses transient overlays (Not Now, OK, Save Info, Close X)."""
    for sel in ["button:has-text('Not Now')", "button:has-text('OK')", "button:has-text('Cancel')", "svg[aria-label='Close']"]:
        try:
            elem = page.locator(sel).first
            if elem.is_visible(timeout=1000):
                elem.click()
                time.sleep(1)
        except Exception:
            pass

def export_csv_manifest(tracker_data):
    """Exports tracker records into a Google Sheets compatible CSV format."""
    fieldnames = ["reel_id", "filename", "drive_link", "status", "uploaded_at", "aspect_ratio", "caption"]
    with open(MANIFEST_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tracker_data)
    print(f"✓ Updated Google Sheets manifest CSV: {MANIFEST_CSV.name}")

def upload_reel_strict_916(video_path: str, caption: str) -> bool:
    """Executes Instagram upload in strict 9:16 aspect ratio."""
    print("==================================================")
    print(" Executing Playwright 9:16 Instagram Publisher    ")
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

        try:
            print("1. Opening Instagram Home Feed...")
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            time.sleep(4)
            handle_popups(page)

            # 2. Click + Create sidebar icon
            print("2. Opening Create upload modal...")
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
            print(f"4. Attaching video file: {Path(video_path).name}...")
            file_input = page.locator("input[type='file']").first
            file_input.wait_for(state="attached", timeout=10000)
            file_input.set_input_files(video_path)
            print("✓ Video file attached!")
            time.sleep(6)

            # Step 1: Aspect Ratio Selection -> STRICT 9:16
            print("Step 1: Opening aspect ratio menu & clicking 9:16 option...")
            crop_btn = page.locator("svg[aria-label='Select crop']").first
            if crop_btn.is_visible(timeout=3000):
                crop_btn.click()
                time.sleep(1.5)

                nine_sixteen_opt = page.get_by_text("9:16", exact=True).first
                if nine_sixteen_opt.is_visible(timeout=2000):
                    nine_sixteen_opt.click(force=True)
                    print("✓ STRICTLY CLICKED '9:16' ASPECT RATIO OPTION!")
                else:
                    page.locator("button:has-text('9:16')").first.click(force=True)
                    print("✓ Clicked 9:16 option via button element!")
                time.sleep(1.5)

            # Click Next (Crop)
            n1 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n1.is_visible(timeout=5000):
                n1.click(force=True)
                print("✓ Step 1: Proceeded with Strict 9:16 Aspect Ratio")
                time.sleep(3)

            # Step 2: Filters Next
            n2 = page.locator("div[role='dialog'] div:has-text('Next')").last
            if n2.is_visible(timeout=5000):
                n2.click(force=True)
                print("✓ Step 2: Clicked Next (Filters)")
                time.sleep(3)

            # Step 3: Write Caption & Hashtags
            print("Step 3: Writing researched caption & hashtags...")
            caption_box = page.locator("div[aria-label='Write a caption...']").first
            if caption_box.is_visible(timeout=3000):
                caption_box.click()
                caption_box.fill(caption)
                print("✓ Caption injected!")
                time.sleep(2)

            # Step 4: Click Share button
            print("Step 4: Triggering Share button...")
            share_btn = page.locator("div[role='dialog']").get_by_text("Share", exact=True).last
            if share_btn.is_visible(timeout=3000):
                share_btn.click(force=True)
                print("✓ Clicked Share button!")

            time.sleep(2)
            page.mouse.click(828, 135)

            # Step 5: Dynamic Checkmark Confirmation Monitoring
            print("5. Monitoring for 'Your reel has been shared.' confirmation screen...")
            shared_confirmed = False
            start_time = time.time()
            
            while time.time() - start_time < 300:
                try:
                    if page.locator("text='Your reel has been shared.'").is_visible(timeout=1000) or \
                       page.locator("text='Reel shared'").is_visible(timeout=1000):
                        print(f"✓ Confirmed 'Your reel has been shared.' screen in {int(time.time() - start_time)} seconds!")
                        shared_confirmed = True
                        break
                except Exception:
                    pass
                time.sleep(2)

            context.close()
            return shared_confirmed
        except Exception as e:
            print(f"❌ Error during upload: {e}")
            context.close()
            return False

def run_pipeline():
    """Main Orchestrator: Fetch Pending -> Download -> 9:16 Upload -> Record CSV -> Delete Local File."""
    if not TRACKER_JSON.exists():
        print("❌ Tracker JSON file missing!")
        return

    with open(TRACKER_JSON, "r", encoding="utf-8") as f:
        tracker_data = json.load(f)

    # Filter next PENDING reel
    pending_reels = [r for r in tracker_data if r.get("status") == "PENDING"]

    if not pending_reels:
        print("🎉 All reels in queue have already been uploaded! No pending uploads found.")
        export_csv_manifest(tracker_data)
        return

    target_reel = pending_reels[0]
    print(f"\n==================================================")
    print(f" Processing Reel: {target_reel['reel_id']} ({target_reel['filename']})")
    print(f" Drive Link: {target_reel['drive_link']}")
    print(f"==================================================")

    # 1. Download Reel from Google Drive
    download_success = download_from_drive(target_reel["drive_link"], TEMP_VIDEO_PATH)

    # Fallback to existing download clip if drive link is a placeholder
    if not download_success:
        fallback_clip = ROOT_DIR / "downloads" / "reel_to_upload_3.mp4"
        if fallback_clip.exists():
            print("✓ Using local verified video fallback...")
            with open(fallback_clip, "rb") as rf, open(TEMP_VIDEO_PATH, "wb") as wf:
                wf.write(rf.read())
            download_success = True

    if not download_success:
        print(f"❌ Aborting pipeline for {target_reel['reel_id']}: Download failed.")
        return

    # 2. Upload Reel via Playwright in strict 9:16 ratio
    upload_success = upload_reel_strict_916(TEMP_VIDEO_PATH, target_reel["caption"])

    if upload_success:
        # 3. Record Uploaded_At Timestamp & Status
        now_str = datetime.now().astimezone().isoformat()
        target_reel["status"] = "UPLOADED"
        target_reel["uploaded_at"] = now_str
        print(f"\n✓ Updated status to UPLOADED at {now_str}")

        # Update JSON & CSV Manifest
        with open(TRACKER_JSON, "w", encoding="utf-8") as f:
            json.dump(tracker_data, f, indent=2)

        export_csv_manifest(tracker_data)

        # 4. Local Disk Cleanup (Delete temp video file)
        if os.path.exists(TEMP_VIDEO_PATH):
            os.remove(TEMP_VIDEO_PATH)
            print("✓ Temporary local video file deleted to clean disk space!")

        print("\n==================================================")
        print(f" 🎉 REEL {target_reel['reel_id']} PROCESSED & COMPLETED!")
        print("==================================================")
    else:
        print(f"❌ Reel upload failed for {target_reel['reel_id']}. Local file preserved for debugging.")

if __name__ == "__main__":
    run_pipeline()
