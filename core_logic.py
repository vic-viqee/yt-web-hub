import os
import re
import sys
import subprocess
import logging
from yt_dlp import YoutubeDL

# ------------------------------------------------
# 📜 Logging & Setup
# ------------------------------------------------
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class CancelledError(Exception):
    """Custom exception to stop processes safely."""
    pass

def notify_desktop(message):
    if os.name == 'nt':
        try:
            ps_cmd = f"New-BurntToastNotification -Text 'YT Web Hub', '{message}'"
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        except Exception:
            pass
    print(f"🔔 {message}")

def sanitize_filename(name):
    return re.sub(r"[\\/:*?\"<>|]", "_", name)

def format_duration(seconds):
    if not seconds: return "--:--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

# ------------------------------------------------
# 📥 The Downloader Engine
# ------------------------------------------------
def run_download(url, mode, quality, progress_callback=None, check_cancel=None):
    """
    Handles downloading with cancel support.
    """
    base_dir = "downloads"
    if mode == "audio": output_dir = os.path.join(base_dir, "audio")
    elif mode == "split": output_dir = os.path.join(base_dir, "splits", "temp_raw")
    else: output_dir = os.path.join(base_dir, "video")
    os.makedirs(output_dir, exist_ok=True)

    quality_map = {
        "best": "bestvideo+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "audio": "bestaudio/best"
    }
    selected_format = quality_map.get(quality, "bestvideo+bestaudio/best")

    if mode == "playlist":
        out_tmpl = f"{output_dir}/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"
        noplaylist_flag = False
    else:
        out_tmpl = f"{output_dir}/%(title)s.%(ext)s"
        noplaylist_flag = True

    # --- PROGRESS HOOK WITH CANCEL CHECK ---
    def progress_hook(d):
        # 1. Check if user cancelled
        if check_cancel and check_cancel():
            raise CancelledError("User cancelled download.")

        if d['status'] == 'downloading' and progress_callback:
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                clean_p = re.sub(r'\x1b\[[0-9;]*m', '', p)
                size_str = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str') or "?? MB"
                clean_size = re.sub(r'\x1b\[[0-9;]*m', '', str(size_str))
                info = d.get('info_dict', {})
                title = info.get('title', 'Unknown Title')
                duration = format_duration(info.get('duration', 0))
                progress_callback(float(clean_p), clean_size, title, duration)
            except Exception:
                pass

    ydl_opts = {
        "format": selected_format,
        "outtmpl": out_tmpl,
        "noplaylist": noplaylist_flag,
        "merge_output_format": "mp4" if mode != "audio" else None,
        "writethumbnail": False,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [progress_hook],
    }
    if mode == "audio":
        ydl_opts["postprocessors"] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]

    print(f"⬇️ Starting: {url}")
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if mode == "split":
                filename = ydl.prepare_filename(info)
                if not filename.endswith(".mp4"):
                    filename = os.path.splitext(filename)[0] + ".mp4"
                return filename, info
            
            notify_desktop(f"Download Complete: {mode}")
            return None, None

    except CancelledError:
        print(f"🚫 Download Cancelled: {url}")
        raise # Re-raise to be caught by app.py
    except Exception as e:
        logging.error(f"Download Failed: {e}")
        raise e

# ------------------------------------------------
# ✂️ The Splitter Engine
# ------------------------------------------------
def process_split(input_path, info, check_cancel=None):
    # Check cancel before starting
    if check_cancel and check_cancel(): raise CancelledError("Cancelled before split.")

    timestamps = []
    if "chapters" in info and info["chapters"]:
        for ch in info["chapters"]: timestamps.append((ch["title"], ch["start_time"], ch["end_time"]))
    if not timestamps:
        description = info.get("description", "")
        matches = re.findall(r"(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)", description)
        for match in matches: timestamps.append((match[1].strip(), match[0], None))
    if not timestamps: return

    video_name = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.join("downloads", "splits", sanitize_filename(video_name))
    os.makedirs(output_dir, exist_ok=True)

    notify_desktop(f"Splitting started: {video_name}")

    for i, (title, start, end) in enumerate(timestamps):
        # Check cancel between splits
        if check_cancel and check_cancel():
            raise CancelledError("User cancelled splitting.")

        safe_title = sanitize_filename(title)
        output_file = os.path.join(output_dir, f"{i+1:02d}_{safe_title}.mp4")
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", str(start), "-i", input_path, "-c", "copy"]
        if end:
            cmd.insert(5, "-to")
            cmd.insert(6, str(end))
        cmd.append(output_file)
        subprocess.run(cmd)

    notify_desktop(f"Splitting Complete! ({len(timestamps)} parts)")