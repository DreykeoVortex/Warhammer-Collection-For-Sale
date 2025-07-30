import os
from collections import defaultdict
from datetime import datetime

# --- Configuration ---
PHOTOS_DIRECTORY = "PicsSell/PicsSell"
OUTPUT_HTML_FILE = "collection_gallery.html"
GALLERY_TITLE = "A 25-Year Warhammer & Collectibles Legacy Collection"
INTRODUCTION = """
Welcome to a curated gallery of a personal collection amassed over 25 years of passion for the worlds of Warhammer. 
This collection represents a significant piece of tabletop gaming history, featuring thousands of figures from Warhammer Fantasy, Epic, and other classic games. 
Many of these models are out-of-production (OOP) metal sculpts, highly sought after by collectors. With an estimated modern retail replacement value of **well over $100,000**, this is a rare opportunity to acquire a massive, multi-army collection in a single lot.
"""
CONTACT_EMAIL = "dkpantheon@gmail.com"
SALE_TERMS = """
The entire collection is being sold as **one single lot**. Offers for individual armies or figures will not be considered.

**Location:** Bonney Lake, WA.
**Delivery:** I am willing to personally deliver the collection within a few hours' drive.
**Shipping:** Due to the significant size and weight of the collection (est. 300 lbs), shipping must be fully arranged and paid for by the buyer.
"""

class GalleryGenerator:
    def __init__(self):
        self.photos_dir = PHOTOS_DIRECTORY
        self.output_file = OUTPUT_HTML_FILE

    def generate_gallery(self):
        print(f"🖼️  Starting gallery generation from '{self.photos_dir}'...")
        if not os.path.exists(self.photos_dir):
            print(f"❌ ERROR: Photos directory not found at '{self.photos_dir}'")
            return

        photos_by_session = self._group_photos_by_session()
        
        if not photos_by_session:
            print("❌ ERROR: No photos found to generate a gallery.")
            return

        html_content = self._build_html(photos_by_session)

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"\n✅ Success! Your gallery has been created: {self.output_file}")
            print("To use, simply open this HTML file in your web browser.")
            print("You can share this single file along with the 'PicsSell' folder with any potential buyer.")
        except IOError as e:
            print(f"❌ ERROR: Could not write to output file: {e}")

    def _group_photos_by_session(self):
        """Groups photos by detecting significant time gaps between shots."""
        print("Sorting photos and detecting photo sessions by time gaps...")
        sessions = defaultdict(list)
        
        # --- Step 1: Extract timestamps for all photos ---
        photo_timestamps = []
        for photo in os.listdir(self.photos_dir):
            if photo.lower().endswith('.jpg') and photo.startswith('PXL_'):
                parts = photo.split('_')
                if len(parts) >= 3:
                    date_str = parts[1]  # YYYYMMDD
                    time_str = parts[2][:6]  # HHMMSS
                    try:
                        timestamp = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
                        photo_timestamps.append((timestamp, photo))
                    except ValueError:
                        continue # Ignore files with malformed dates/times

        if not photo_timestamps:
            print("No timestamped photos found to process.")
            return {}

        # --- Step 2: Sort photos chronologically ---
        photo_timestamps.sort()

        # --- Step 3: Group into sessions based on time gaps ---
        if not photo_timestamps:
            return sessions

        # Define the time gap threshold for a new session (e.g., 30 minutes)
        session_threshold_minutes = 30
        
        current_session_photos = [photo_timestamps[0][1]]
        last_photo_time = photo_timestamps[0][0]

        for i in range(1, len(photo_timestamps)):
            current_photo_time, current_photo_name = photo_timestamps[i]
            time_difference_minutes = (current_photo_time - last_photo_time).total_seconds() / 60

            if time_difference_minutes > session_threshold_minutes:
                # Time gap is large, so finalize the previous session
                if current_session_photos:
                    session_date = last_photo_time.strftime("%B %d, %Y")
                    session_num = len([s for s in sessions if s.startswith(session_date)]) + 1
                    session_key = f"{session_date} - Session {session_num}"
                    sessions[session_key] = current_session_photos
                
                # Start a new session
                current_session_photos = [current_photo_name]
            else:
                # Time gap is small, continue the current session
                current_session_photos.append(current_photo_name)
            
            last_photo_time = current_photo_time
        
        # Add the very last session
        if current_session_photos:
            session_date = last_photo_time.strftime("%B %d, %Y")
            session_num = len([s for s in sessions if s.startswith(session_date)]) + 1
            session_key = f"{session_date} - Session {session_num}"
            sessions[session_key] = current_session_photos

        print(f"Found {len(photo_timestamps)} photos and organized them into {len(sessions)} distinct sessions.")
        return sessions

    def _build_html(self, sessions):
        """Constructs the full HTML document as a string."""
        
        sessions_html = ""
        for session_name, photos in sessions.items():
            photo_tiles = ""
            for photo in photos:
                # Use a smaller, web-friendly thumbnail if possible, but for simplicity link to the original
                thumbnail_path = f"{self.photos_dir}/{photo}"
                full_path = f"{self.photos_dir}/{photo}"
                photo_tiles += f"""
                <div class="photo-tile">
                    <a href="{full_path}" target="_blank">
                        <img src="{thumbnail_path}" alt="{photo}" loading="lazy">
                        <div class="photo-overlay">{photo}</div>
                    </a>
                </div>
                """
            
            sessions_html += f"""
            <div class="session-container">
                <h2>{session_name} <span class="photo-count">({len(photos)} photos)</span></h2>
                <div class="photo-grid">
                    {photo_tiles}
                </div>
            </div>
            """
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{GALLERY_TITLE}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f0f2f5;
            color: #1c1e21;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 24px 32px;
            margin-bottom: 24px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            border: 1px solid #dddfe2;
        }}
        .header h1 {{
            font-size: 28px;
            margin: 0 0 12px 0;
            color: #1877f2;
        }}
        .header p {{
            font-size: 16px;
            line-height: 1.5;
            margin: 0;
            white-space: pre-wrap;
        }}
        .header a {{
            color: #1877f2;
            font-weight: bold;
            text-decoration: none;
        }}
        .session-container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }}
        .session-container h2 {{
            font-size: 22px;
            border-bottom: 1px solid #dddfe2;
            padding-bottom: 12px;
            margin: 0 0 20px 0;
        }}
        .photo-count {{
            font-weight: normal;
            color: #606770;
        }}
        .photo-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 12px;
        }}
        .photo-tile a {{
            display: block;
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .photo-tile a:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        .photo-tile img {{
            width: 100%;
            height: 150px;
            object-fit: cover;
            display: block;
        }}
        .photo-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: rgba(0, 0, 0, 0.6);
            color: white;
            padding: 8px;
            font-size: 12px;
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            opacity: 0;
            transition: opacity 0.2s ease;
        }}
        .photo-tile a:hover .photo-overlay {{
            opacity: 1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{GALLERY_TITLE}</h1>
            <p>{INTRODUCTION}</p>
            <p>{SALE_TERMS.strip()}</p>
            <p><strong>Contact:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
        </div>
        
        {sessions_html}

    </div>
</body>
</html>
"""
        return html

if __name__ == '__main__':
    generator = GalleryGenerator()
    generator.generate_gallery() 