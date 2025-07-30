import os
from collections import defaultdict
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO

# --- Configuration ---
PHOTOS_DIRECTORY = "PicsSell/PicsSell"
# Change output back to collection_gallery.html to match GitHub Pages URL
OUTPUT_HTML_FILE = "collection_gallery.html"
# NEW: Directory for low-quality placeholders
PLACEHOLDER_DIR = "placeholders"
# NEW: Directory for 400-px wide thumbnails
THUMBNAIL_DIR = "thumbnails"

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

class AdvancedGalleryGenerator:
    def __init__(self):
        self.photos_dir = PHOTOS_DIRECTORY
        self.output_file = OUTPUT_HTML_FILE
        self.placeholder_dir = PLACEHOLDER_DIR
        # NEW: thumbnails directory path
        self.thumbnail_dir = THUMBNAIL_DIR

    def generate_gallery(self):
        print("🚀 Starting Advanced Gallery Generation...")

        # Step 1: Ensure directories exist
        if not os.path.exists(self.photos_dir):
            print(f"❌ ERROR: Photos directory not found at '{self.photos_dir}'")
            return
        if not os.path.exists(self.placeholder_dir):
            os.makedirs(self.placeholder_dir)
            print(f"📁 Created placeholder directory: '{self.placeholder_dir}'")
        if not os.path.exists(self.thumbnail_dir):
            os.makedirs(self.thumbnail_dir)
            print(f"📁 Created thumbnail directory: '{self.thumbnail_dir}'")

        # Step 2: Generate low-quality placeholders
        self._generate_placeholders()
        # Step 2b: Generate crisp 400-px thumbnails for main display
        self._generate_thumbnails()

        # Step 3: Group photos into sessions
        photos_by_session = self._group_photos_by_session()
        if not photos_by_session:
            print("❌ ERROR: No photos found to generate a gallery.")
            return

        # Step 4: Build the final HTML
        html_content = self._build_html(photos_by_session)

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"\n✅ Success! Your advanced gallery is ready: {self.output_file}")
            print("   This is now your main `index.html` file.")
        except IOError as e:
            print(f"❌ ERROR: Could not write to output file: {e}")

    def _generate_placeholders(self):
        print("🎨 Generating low-quality image placeholders for fast loading...")
        all_photos = [f for f in os.listdir(self.photos_dir) if f.lower().endswith('.jpg')]
        for photo in all_photos:
            placeholder_path = os.path.join(self.placeholder_dir, photo)
            if not os.path.exists(placeholder_path):
                try:
                    with Image.open(os.path.join(self.photos_dir, photo)) as img:
                        # Create a tiny, blurry version
                        img.thumbnail((50, 50))
                        buffered = BytesIO()
                        img.save(buffered, format="JPEG", quality=10)
                        img_str = base64.b64encode(buffered.getvalue()).decode()

                        # Save as a data URI text file
                        with open(placeholder_path + ".txt", "w") as f:
                            f.write("data:image/jpeg;base64," + img_str)

                except Exception as e:
                    print(f"  - Could not create placeholder for {photo}: {e}")

    def _generate_thumbnails(self):
        """Create 400-pixel wide thumbnails used as the visible grid images."""
        print("🖼️  Generating 400px thumbnails for clear initial display…")
        for photo in [f for f in os.listdir(self.photos_dir) if f.lower().endswith('.jpg')]:
            thumb_path = os.path.join(self.thumbnail_dir, photo)
            if os.path.exists(thumb_path):
                continue  # Thumbnail already exists
            try:
                with Image.open(os.path.join(self.photos_dir, photo)) as img:
                    # Preserve aspect ratio, resize based on width
                    w_percent = 400 / float(img.size[0])
                    h_size = int((float(img.size[1]) * float(w_percent)))
                    img = img.resize((400, h_size), Image.LANCZOS)
                    img.save(thumb_path, format="JPEG", quality=80, optimize=True)
            except Exception as e:
                print(f"  - Could not create thumbnail for {photo}: {e}")

    def _group_photos_by_session(self):
        sessions = defaultdict(list)
        photo_timestamps = []
        for photo in os.listdir(self.photos_dir):
            if photo.lower().endswith('.jpg') and photo.startswith('PXL_'):
                parts = photo.split('_')
                if len(parts) >= 3:
                    try:
                        timestamp = datetime.strptime(f"{parts[1]}{parts[2][:6]}", "%Y%m%d%H%M%S")
                        photo_timestamps.append((timestamp, photo))
                    except ValueError: continue

        photo_timestamps.sort()

        if not photo_timestamps: return {}

        session_threshold_minutes = 30
        current_session_photos = [photo_timestamps[0][1]]
        last_photo_time = photo_timestamps[0][0]

        for i in range(1, len(photo_timestamps)):
            current_photo_time, photo_name = photo_timestamps[i]
            if (current_photo_time - last_photo_time).total_seconds() / 60 > session_threshold_minutes:
                if current_session_photos:
                    session_date = last_photo_time.strftime("%B %d, %Y")
                    session_num = len([s for s in sessions if s.startswith(session_date)]) + 1
                    sessions[f"{session_date} - Session {session_num}"] = current_session_photos
                current_session_photos = []
            current_session_photos.append(photo_name)
            last_photo_time = current_photo_time

        if current_session_photos:
            session_date = last_photo_time.strftime("%B %d, %Y")
            session_num = len([s for s in sessions if s.startswith(session_date)]) + 1
            sessions[f"{session_date} - Session {session_num}"] = current_session_photos

        print(f"✅ Grouped {len(photo_timestamps)} photos into {len(sessions)} distinct sessions.")
        return sessions

    def _build_html(self, sessions):
        sessions_html = ""
        for session_name, photos in sessions.items():
            photo_tiles = ""
            for photo in photos:
                placeholder_path = os.path.join(self.placeholder_dir, photo + ".txt")
                try:
                    with open(placeholder_path, "r") as f:
                        placeholder_data = f.read()
                except IOError:
                    placeholder_data = ""  # Default empty placeholder

                full_path = f"./{self.photos_dir}/{photo}"
                thumb_path = f"./{self.thumbnail_dir}/{photo}"
                photo_tiles += f"""
                <div class="photo-tile">
                    <img src="{thumb_path}" loading="lazy" alt="{photo}" onclick="openModal('{full_path}')">
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

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{GALLERY_TITLE}</title>
    <style>
        /* [CSS styles from previous version, with additions for lazy loading and modal] */
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; background-color: #f0f2f5; color: #1c1e21; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #ffffff; border-radius: 8px; padding: 24px 32px; margin-bottom: 24px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); border: 1px solid #dddfe2; }}
        .header h1 {{ font-size: 28px; margin: 0 0 12px 0; color: #1877f2; }}
        .header p {{ font-size: 16px; line-height: 1.5; margin: 12px 0; white-space: pre-wrap; }}
        .header a {{ color: #1877f2; font-weight: bold; text-decoration: none; }}
        .session-container {{ background-color: #ffffff; border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); }}
        .session-container h2 {{ font-size: 22px; border-bottom: 1px solid #dddfe2; padding-bottom: 12px; margin: 0 0 20px 0; }}
        .photo-count {{ font-weight: normal; color: #606770; }}
        .photo-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }}
        .photo-tile img {{ width: 100%; height: 160px; object-fit: cover; display: block; border-radius: 8px; cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease; }}
        /* We no longer need blur filters for placeholders */
        .photo-tile img:hover {{ transform: scale(1.05); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); }}
        /* Modal styles */
        .modal {{ display: none; position: fixed; z-index: 1000; padding-top: 50px; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90vh; }}
        .close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; transition: 0.3s; }}
        .close:hover, .close:focus {{ color: #bbb; text-decoration: none; cursor: pointer; }}
    </style>
</head>
<body>
    <div id="imageModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modalImg">
    </div>
    <div class="container">
        <div class="header">
            <h1>{GALLERY_TITLE}</h1>
            <p>{INTRODUCTION.strip()}</p>
            <p>{SALE_TERMS.strip()}</p>
            <p><strong>Contact:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
        </div>
        {sessions_html}
    </div>
    <script>
        // --- LAZY LOADING SCRIPT ---
        document.addEventListener("DOMContentLoaded", function() {{
            const lazyImages = [].slice.call(document.querySelectorAll("img.lazyload"));
            if ("IntersectionObserver" in window) {{
                let lazyImageObserver = new IntersectionObserver(function(entries, observer) {{
                    entries.forEach(function(entry) {{
                        if (entry.isIntersecting) {{
                            let lazyImage = entry.target;
                            lazyImage.src = lazyImage.dataset.src;
                            lazyImage.classList.remove("lazyload");
                            lazyImage.classList.add("lazyloaded");
                            lazyImageObserver.unobserve(lazyImage);
                        }}
                    }});
                }});
                lazyImages.forEach(function(lazyImage) {{
                    lazyImageObserver.observe(lazyImage);
                }});
            }} else {{
                // Fallback for older browsers
                lazyImages.forEach(function(lazyImage) {{
                    lazyImage.src = lazyImage.dataset.src;
                }});
            }}
        }});
        // --- MODAL SCRIPT ---
        const modal = document.getElementById("imageModal");
        const modalImg = document.getElementById("modalImg");
        function openModal(src) {{
            modal.style.display = "block";
            modalImg.src = src;
        }}
        function closeModal() {{
            modal.style.display = "none";
        }}
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    generator = AdvancedGalleryGenerator()
    generator.generate_gallery() 