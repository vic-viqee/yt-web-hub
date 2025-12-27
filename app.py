import os
import threading
import uuid
from queue import Queue
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import core_logic

app = Flask(__name__)
app.secret_key = "super_secret_key"

job_queue = Queue()
JOBS = {} 

def worker():
    while True:
        job_id = job_queue.get()
        if job_id is None: break

        job = JOBS[job_id]

        # 1. Check if cancelled while waiting in queue
        if job['status'] == 'cancelled':
            job_queue.task_done()
            continue

        JOBS[job_id]['status'] = 'processing'
        JOBS[job_id]['progress'] = 0
        
        # Callback for updates
        def update_progress(percent, size_str, title, duration):
            JOBS[job_id]['progress'] = int(percent)
            JOBS[job_id]['size'] = size_str
            JOBS[job_id]['title'] = title
            JOBS[job_id]['duration'] = duration
        
        # Callback to check cancel status
        def should_cancel():
            return JOBS[job_id]['status'] == 'cancelled'

        try:
            file_path, info = core_logic.run_download(
                job['url'], job['mode'], job['quality'], 
                progress_callback=update_progress,
                check_cancel=should_cancel
            )
            
            if info: JOBS[job_id]['title'] = info.get('title', JOBS[job_id]['title'])
            
            if job['mode'] == 'split' and file_path and info:
                JOBS[job_id]['status'] = 'splitting'
                JOBS[job_id]['progress'] = 100
                core_logic.process_split(file_path, info, check_cancel=should_cancel)

            JOBS[job_id]['status'] = 'completed'
            JOBS[job_id]['progress'] = 100
        
        except core_logic.CancelledError:
            JOBS[job_id]['status'] = 'cancelled'
            JOBS[job_id]['error'] = "Cancelled by user"
        except Exception as e:
            JOBS[job_id]['status'] = 'failed'
            JOBS[job_id]['error'] = str(e)
        finally:
            job_queue.task_done()

t = threading.Thread(target=worker, daemon=True)
t.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_jobs():
    urls = request.form.get('urls', '').splitlines()
    mode = request.form.get('mode', 'video')
    quality = request.form.get('quality', 'best')

    for url in urls:
        if not url.strip(): continue
        job_id = str(uuid.uuid4())[:8]
        JOBS[job_id] = {
            'id': job_id, 'url': url.strip(), 'mode': mode, 'quality': quality, 
            'status': 'pending', 'progress': 0, 'size': 'Calc...', 
            'title': 'Fetching info...', 'duration': '--:--', 'error': None
        }
        job_queue.put(job_id)

    resp = Response("", status=204)
    resp.headers['HX-Trigger'] = 'updateQueue' 
    return resp

# ✅ NEW ROUTE: Cancel/Remove Job
@app.route('/cancel/<job_id>', methods=['POST'])
def cancel_job(job_id):
    if job_id in JOBS:
        # Mark as cancelled immediately
        JOBS[job_id]['status'] = 'cancelled'
        
        # If it was just pending (not running), we can optionally delete it from the list entirely
        # For now, we mark it 'cancelled' so the UI updates to show it's gone/stopped
    
    resp = Response("", status=204)
    resp.headers['HX-Trigger'] = 'updateQueue'
    return resp

@app.route('/status')
def status_api():
    # Filter out cancelled jobs so they "disappear" from the list (Remove feature)
    # OR keep them to show "Cancelled".
    # User asked to "Remove", so let's filter out 'cancelled' jobs entirely.
    active_jobs = [j for j in JOBS.values() if j['status'] != 'cancelled']
    return render_template('components/job_list.html', jobs=active_jobs[::-1])

@app.route('/files_list')
def files_api():
    base_dir = "downloads"
    files_tree = {'video': [], 'audio': [], 'splits': []}
    for category in files_tree.keys():
        cat_path = os.path.join(base_dir, category)
        if os.path.exists(cat_path):
            for root, dirs, files in os.walk(cat_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, base_dir)
                    files_tree[category].append({'name': file, 'path': rel_path})
    return render_template('components/file_list.html', files=files_tree)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory('downloads', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)