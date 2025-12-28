# yt-web-hub
📝 InstructionsCreate a file named README.md in your yt_web_hub folder.Paste the content below.Markdown# 🚀 YT Web Hub (v4.0)

**A self-hosted, mobile-friendly web application to download, split, and manage YouTube videos.**

YT Web Hub is a local tool that combines the power of `yt-dlp` and `FFmpeg` into a modern, responsive Single Page Application (SPA). It allows you to queue downloads from your phone, process playlists, extract audio, and split long videos into chapters automatically—all from a clean web interface.

---

## ✨ Key Features

### 📥 Powerful Downloader
* **Batch Processing:** Paste multiple links (video or playlist) and let the queue handle them one by one.
* **Playlist Support:** Automatically organizes playlist videos into folders (e.g., `Playlist Name/01 - Video.mp4`).
* **Quality Control:** Choose between **Best Available**, **1080p**, **720p**, **480p** (Data Saver), or **360p**.
* **Audio Mode:** One-click extraction to **MP3**.

### ✂️ Smart Splitter
* **Auto-Splitting:** Downloads a long video and chops it into separate files based on **YouTube Chapters** or **Timestamps** in the description.
* **No Re-encoding:** Uses FFmpeg stream copying for instant, lossless splitting.

### 📱 Modern Interface
* **Mobile-First Design:** Built with **Bootstrap 5**, looking like a native app on your phone.
* **Real-Time Progress:** Live progress bars showing **Percentage**, **File Size**, **Title**, and **Duration**.
* **Live Queue:** Cancel or remove jobs instantly with a tap.
* **File Manager:** Browse and download finished files directly to your device.

---

## 🛠️ Tech Stack

* **Backend:** Python 3 (Flask)
* **Frontend:** HTML5, Bootstrap 5
* **Interactivity:** HTMX (for live updates without page reloads)
* **Engines:** * `yt-dlp` (Downloading)
    * `FFmpeg` (Conversion & Splitting)

---

## ⚙️ Prerequisites

Before running the app, ensure you have the following installed:

1.  **Python 3.9+**: [Download Here](https://www.python.org/downloads/)
2.  **FFmpeg**: [Download Here](https://ffmpeg.org/download.html)
    * *Windows users:* Ensure `ffmpeg.exe` is added to your System PATH.
3.  **Git** (Optional, for cloning).

---

## 🚀 Installation & Setup

1.  **Clone or Create Project Folder**
    ```bash
    mkdir yt_web_hub
    cd yt_web_hub
    ```

2.  **Set Up Virtual Environment (Recommended)**
    ```bash
    python -m venv venv
    # Windows:
    source venv/Scripts/activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    Create a `requirements.txt` file with:
    ```text
    Flask
    yt-dlp
    tqdm
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Verify Project Structure**
    Ensure your folder looks like this:
    ```text
    yt_web_hub/
    ├── app.py                 # Main Flask Server
    ├── core_logic.py          # Downloader & Splitter Engine
    ├── requirements.txt
    ├── templates/
    │   ├── index.html         # Main Dashboard
    │   └── components/
    │       ├── job_list.html  # Queue Component
    │       └── file_list.html # File Manager Component
    └── downloads/             # (Auto-created) Output folder
    ```

---

## 🏃 How to Run

### 1. Start the Server
Open your terminal in the project folder and run:
```bash
python app.py
You will see: * Running on http://0.0.0.0:50002. Access Locally (PC)Open your browser and go to:👉 http://localhost:50003. Access from Mobile (Phone/Tablet)Ensure your phone and PC are on the same Wi-Fi.Find your PC's Local IP:Windows: Run ipconfig in terminal. Look for IPv4 Address (e.g., 192.168.1.15).Mac/Linux: Run ifconfig.Open your phone browser and go to:👉 https://www.google.com/search?q=http://192.168.1.15:5000 (Replace with your actual IP).Troubleshooting: If the site doesn't load on mobile, check your Windows Firewall. Allow "Python" through both Public and Private networks.📖 Usage GuideNew Task:Paste YouTube links (one per line) into the text box.Select Mode (Video, Playlist, Audio, Split).Select Quality.Tap Start Download.Manage Queue:Watch the progress bar fill up.See file details (Size, Duration).Tap the Red X to cancel a running job or remove a pending one.Download Files:Scroll down to the Downloads section.Tap any file (Video/Audio) to save it directly to your device's gallery or file system.📂 Project Structure ExplainedFile / FolderDescriptionapp.pyThe "Brain". Handles the web server, job queue, and API routes.core_logic.pyThe "Engine". Contains the code for yt-dlp and ffmpeg operations.templates/Contains the HTML UI files.downloads/Where your files live. Subfolders: video, audio, splits.logs/Check app.log here if something goes wrong.🛡️ LicenseThis project is for educational and personal use.Powered by yt-dlp and FFmpeg.