import os
import httpx
import subprocess
from flask import Flask, render_template, jsonify, url_for, request
import re

app = Flask(__name__)
script_process = None

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return "index.html not found", 404

@app.route("/edu")
def edu():
    try:
        return render_template("edu.html")
    except Exception as e:
        return "edu.html not found", 404

@app.route("/qa")
def qa():
    try:
        return render_template("q&a.html")
    except Exception as e:
        return "q&a.html not found", 404
    
@app.route("/lab_pe")
def lab_pe():  
    try:
        return render_template("lab_pe.html")
    except Exception as e:
        return f"lab_pe.html not found", 404  

@app.route("/toggle_script", methods=['POST'])
def toggle_script():
    global script_process
    if request.json.get('action') == 'start':
        if script_process is None:
            script_process = subprocess.Popen(['../venv/bin/python', 'main.py'])
            return jsonify({'status': 'started'})
    elif request.json.get('action') == 'stop':
        if script_process is not None:
            script_process.terminate()
            script_process = None
            return jsonify({'status': 'stopped'})
    return jsonify({'status': 'unchanged'})




@app.route('/save_code', methods=['POST'])
def save_code():
    try:
        code = request.json.get('code', '')
        function_name = request.json.get('function_name', '')
        
        with open('python/integration.py', 'r', encoding='utf-8') as file:
            content = file.read()
            
        import re
        pattern = rf'(def\s+{function_name}\s*\([^)]*\):(?:(?!\ndef\s+).)*)'
        updated_content = re.sub(pattern, code.strip(), content, flags=re.DOTALL)
        
        with open('python/integration.py', 'w', encoding='utf-8') as file:
            file.write(updated_content)
            
        return jsonify({'success': True, 'message': 'Code saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_function')
def get_function():
    try:
        with open('python/integration.py', 'r', encoding='utf-8') as file:
            content = file.read()
            function_pattern = re.compile(r'(def\s+on_question_received\s*\([^)]*\):(?:(?!\ndef\s+).)*)', re.DOTALL)
            match = function_pattern.search(content)
            if match:
                return match.group(1)
    except Exception as e:
        return str(e)
    return "Function not found"

@app.route('/save_function', methods=['POST'])
def save_function():
    data = request.get_json()
    new_instructions = data.get('instructions', '')
    
    try:
        with open('python/integration.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        pattern = r'(instructions\s*=\s*)["\'].*?["\']'
        updated_content = re.sub(pattern, f'\\1"{new_instructions}"', content)
        
        with open('python/integration.py', 'w', encoding='utf-8') as file:
            file.write(updated_content)
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/audio/play', methods=['POST'])
def play_audio():
    """Generate and play TTS audio from text using OpenAI."""
    from flask import request
    import json
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Import and use the text_to_speech module
        from text_to_speech import AudioResponse
        
        audio_response = AudioResponse(text)
        # This will generate and play the audio
        audio_response.get_audio()
        
        return jsonify({"status": "success", "message": "Audio played"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
