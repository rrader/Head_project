from flask import Flask, jsonify, render_template_string
import os

app = Flask(__name__)
STATUS_FILE = "audio_status.txt"

# Initialize status file if it doesn't exist
if not os.path.exists(STATUS_FILE):
    with open(STATUS_FILE, "w") as f:
        f.write("True")

def get_audio_status():
    with open(STATUS_FILE, "r") as f:
        return f.read().strip() == "True"

def set_audio_status(status):
    with open(STATUS_FILE, "w") as f:
        f.write(str(status))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bender Control Panel</title>
    <style>
        body { 
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .button {
            padding: 10px 20px;
            margin: 10px;
            font-size: 16px;
            cursor: pointer;
        }
        #status {
            margin: 20px 0;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <h1>Bender Control Panel</h1>
    <div id="status">Status: <span id="statusText">Checking...</span></div>
    <button class="button" onclick="startAudio()">Start Audio</button>
    <button class="button" onclick="stopAudio()">Stop Audio</button>

    <script>
        function updateStatus() {
            fetch('/audio/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('statusText').textContent = data.status;
                });
        }

        function startAudio() {
            fetch('/audio/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => updateStatus());
        }

        function stopAudio() {
            fetch('/audio/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => updateStatus());
        }

        // Update status every 2 seconds
        updateStatus();
        setInterval(updateStatus, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/audio/stop', methods=['POST'])
def stop_audio():
    set_audio_status(False)
    return jsonify({"status": "stopped"})

@app.route('/audio/start', methods=['POST'])
def start_audio():
    set_audio_status(True)
    return jsonify({"status": "started"})

@app.route('/audio/status', methods=['GET'])
def audio_status():
    status = "running" if get_audio_status() else "stopped"
    return jsonify({"status": status})


def web_server():
    app.run(host='0.0.0.0', port=5000)
