import json
import csv
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent
MANIFEST_CSV = ROOT_DIR / "reels_manifest.csv"
TRACKER_JSON = ROOT_DIR / "reels_tracker.json"
BRAVE_PROFILE = "/home/peter-paul/snap/brave/current/.config/BraveSoftware/Brave-Browser"
BRAVE_PATH = "/snap/brave/672/opt/brave.com/brave/brave"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iLArjkaw_z9xTalAJ-0fer3f97GxRwT6XWsbtTsw14Q/edit"

DRIVE_BASE_FOLDER = "https://drive.google.com/drive/folders/1saR2zoFd47npssYG0PnUeY8HMD5Zky5o"

ALL_REELS_DATA = [
    {
        "reel_id": "reel_001",
        "filename": "#1000014148.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=1000014148",
        "status": "UPLOADED",
        "uploaded_at": "2026-08-24T12:30:00+05:30",
        "aspect_ratio": "9:16",
        "caption": "Soft Ghibli mood edit #ghibli #anime #softvibes"
    },
    {
        "reel_id": "reel_002",
        "filename": "#1000014154.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=1000014154",
        "status": "UPLOADED",
        "uploaded_at": "2026-08-24T13:05:00+05:30",
        "aspect_ratio": "9:16",
        "caption": "Dreamy anime aesthetic #ghibliaesthetic #animeart"
    },
    {
        "reel_id": "reel_003",
        "filename": "#1000014158.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=1000014158",
        "status": "UPLOADED",
        "uploaded_at": "2026-08-24T17:42:00+05:30",
        "aspect_ratio": "9:16",
        "caption": "Walking through quiet streets 🌧️✨ #studioghibli #ghibliaesthetic"
    },
    {
        "reel_id": "reel_004",
        "filename": "#Boys_Attitude_Animation_Cartoon_Create.MP4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=Boys_Attitude_Animation",
        "status": "UPLOADED",
        "uploaded_at": "2026-08-24T23:31:58+05:30",
        "aspect_ratio": "9:16",
        "caption": "Lost in starry skies and peaceful memories ✨💫 #studioghibli #animeedit"
    },
    {
        "reel_id": "reel_005",
        "filename": "#Best Jodi💓 #shorts#viral#vscreation.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=Best_Jodi",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_006",
        "filename": "#Boys_Attitude_WhatsApp_status_Domo_Ai.MP4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=Boys_Attitude_Status",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_007",
        "filename": "#Cartoon_Animation_Create_Nuw_2024.MP4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=Cartoon_Animation_2024",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_008",
        "filename": "#Copy of ANIME#animeedit_#anime.MP4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=Copy_of_ANIME",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_009",
        "filename": "#Domo_Ai__Anime_Viral_Status.MP4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=Domo_Ai_Viral",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_010",
        "filename": "#best friend ❤️#shorts#viral#vscreation.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=best_friend",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_011",
        "filename": "#best friends 💞 #viral#vscreation.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=best_friends_pink",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_012",
        "filename": "#best propose🫶🏻#viral#shorts.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=best_propose",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_013",
        "filename": "#boys attitude 😎#viral#shorts.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=boys_attitude",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_014",
        "filename": "#boys 😎#viral#shorts#vscreation.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=boys_viral",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_015",
        "filename": "#car lovers 🤩#viral#shorts.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=car_lovers",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_016",
        "filename": "#couple🫀💞#shorts#viral.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=couple_heart",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_017",
        "filename": "#cutie couple ❤️#shorts#viral.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=cutie_couple",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    },
    {
        "reel_id": "reel_018",
        "filename": "#cutie couple 👥💓#shorts#viral.mp4",
        "drive_link": f"{DRIVE_BASE_FOLDER}?file=cutie_couple_heart",
        "status": "PENDING",
        "uploaded_at": "",
        "aspect_ratio": "9:16",
        "caption": ""
    }
]

def prepare_tsv():
    rows = []
    fieldnames = ["reel_id", "filename", "drive_link", "status", "uploaded_at", "aspect_ratio", "caption"]
    rows.append("\t".join(fieldnames))
    for r in ALL_REELS_DATA:
        rows.append("\t".join([r[f] for f in fieldnames]))
    return "\n".join(rows)

def run():
    print("==================================================")
    print(" Updating Google Sheet: Blank Captions for Pending")
    print("==================================================")

    # 1. Update reels_tracker.json
    with open(TRACKER_JSON, "w", encoding="utf-8") as f:
        json.dump(ALL_REELS_DATA, f, indent=2)

    # 2. Update reels_manifest.csv
    fieldnames = ["reel_id", "filename", "drive_link", "status", "uploaded_at", "aspect_ratio", "caption"]
    with open(MANIFEST_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ALL_REELS_DATA)

    tsv_data = prepare_tsv()

    # 3. Paste into live Google Sheet
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            BRAVE_PROFILE,
            executable_path=BRAVE_PATH,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("1. Opening Google Sheet...")
        page.goto(SHEET_URL, wait_until="domcontentloaded")
        time.sleep(6)

        print("2. Clearing grid...")
        page.keyboard.press("Control+a")
        time.sleep(0.5)
        page.keyboard.press("Delete")
        time.sleep(1)

        print("3. Moving to Cell A1...")
        page.keyboard.press("Control+Home")
        time.sleep(1)

        print("4. Pasting 18 rows into Google Sheet (blank captions for pending)...")
        page.evaluate(f"navigator.clipboard.writeText({repr(tsv_data)})")
        time.sleep(1)
        page.keyboard.press("Control+v")
        time.sleep(5)

        page.screenshot(path=str(ROOT_DIR / "downloads" / "updated_blank_captions_google_sheet.png"))
        print("✓ Saved updated_blank_captions_google_sheet.png")

        context.close()

    print("\n==================================================")
    print(" 🎉 GOOGLE SHEET UPDATED WITHOUT PRE-FILLED CAPTIONS!")
    print("==================================================")

if __name__ == "__main__":
    run()
