import uuid
from flask import Flask, render_template, request, session, send_file, jsonify, url_for
from flask_socketio import SocketIO, emit
import os
from agents import paperai_agent, chater_agent
from agno.agent import Agent
from config import API_KEY
import threading
from werkzeug.utils import secure_filename
import traceback

try:
    from . import package_utils
except ImportError:
    import package_utils

from openai import OpenAI

app = Flask(__name__)
convId = str(uuid.uuid4())
app.secret_key = convId
socketio = SocketIO(app, async_mode='eventlet')
API = os.environ.get('DEEPSEEK_API_KEY') or API_KEY

active_tasks = {}
active_tasks_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
FIXED_PROG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "fixedQuantityProg"))
OUTPUT_EXE_NAME = "spade"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"Upload folder: {UPLOAD_FOLDER}")
print(f"Fixed programs directory: {FIXED_PROG_DIR}")
if not os.path.isdir(FIXED_PROG_DIR):
    print(f"Warning: Fixed programs directory not found at {FIXED_PROG_DIR}")

TRAIT_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-e82df05b5c9443cab084419078b31c32")
TRAIT_API_BASE = os.environ.get("DASHSCOPE_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
TRAIT_MODEL = os.environ.get("DASHSCOPE_MODEL", "qwen2.5-vl-72b-instruct")

trait_client = None
if TRAIT_API_KEY and TRAIT_API_KEY != "your_api_key_here":
    try:
        trait_client = OpenAI(
            api_key=TRAIT_API_KEY,
            base_url=TRAIT_API_BASE
        )
        print("Trait Recognizer OpenAI client initialized.")
    except Exception as e:
        print(f"Error initializing Trait Recognizer OpenAI client: {e}")
else:
    print("Trait Recognizer OpenAI client not initialized (API key missing or placeholder).")


class DialogueManager:
    def __init__(self, assistant, socketio_instance):
        self.assistant = assistant
        self.socketio = socketio_instance

    def process_user_input(self, user_input, sid, ai_message_id):
        with active_tasks_lock:
            active_tasks[ai_message_id] = False
        should_stop = False
        try:
            full_response = ""
            response_stream = None

            if isinstance(self.assistant, Agent):
                try:
                    response_stream = self.assistant.run(user_input, stream=True)
                except Exception as agent_run_error:
                    print(f"Error during agent run: {agent_run_error}")
                    traceback.print_exc()
                    raise agent_run_error
            else:
                raise TypeError(f"Cannot process input for assistant type: {type(self.assistant)}")

            if hasattr(response_stream, '__iter__') and not isinstance(response_stream, str):
                for chunk in response_stream:
                    with active_tasks_lock:
                        if active_tasks.get(ai_message_id, False):
                            print(f"Stopping generation for {ai_message_id}")
                            should_stop = True
                            break

                    content_chunk = None
                    if hasattr(chunk, 'content'):
                        content_chunk = str(chunk.content)
                    elif isinstance(chunk, str):
                        content_chunk = chunk

                    if content_chunk:
                        full_response += content_chunk
                        self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': content_chunk}, room=sid)
                        self.socketio.sleep(0.01)

            elif response_stream is not None:
                with active_tasks_lock:
                    if not active_tasks.get(ai_message_id, False):
                        content = str(response_stream)
                        full_response = content
                        self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': content}, room=sid)
                    else:
                        should_stop = True
            else:
                with active_tasks_lock:
                    if not active_tasks.get(ai_message_id, False):
                        full_response = "Assistant did not generate a response."
                        self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': full_response}, room=sid)
                    else:
                        should_stop = True

            final_text = full_response
            if should_stop:
                final_text += "\n\n*Generation stopped by user.*"
            self.socketio.emit('ai_message_end', {'id': ai_message_id, 'full_text': final_text}, room=sid)

        except Exception as e:
            error_msg = f"An error occurred: {e}"
            print(f"Error during processing for {ai_message_id}:")
            traceback.print_exc()
            self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': f"\n\n**Error:** Processing failed. Please check server logs."}, room=sid)
            self.socketio.emit('ai_message_end', {'id': ai_message_id, 'full_text': full_response + f"\n\n**Error:** Processing failed."}, room=sid)
        finally:
            with active_tasks_lock:
                if ai_message_id in active_tasks:
                    del active_tasks[ai_message_id]


paperai_manager = DialogueManager(paperai_agent, socketio)
chater_manager = DialogueManager(chater_agent, socketio)


@app.route("/")
def index():
    return render_template("main.html", messages=session.get("messages", []))


@app.route("/chat")
def chat_page():
    if "messages" not in session:
        session["messages"] = []
    return render_template("main.html", messages=session.get("messages", []))


@app.route("/trait_recognizer")
def trait_recognizer_page():
    return render_template("trait_recognizer.html")


@app.route("/upload_trait_standard", methods=["POST"])
def upload_trait_standard():
    if not trait_client:
        return jsonify({"error": "Trait Recognizer service not available (OpenAI client not initialized)."}), 503

    output_exe_path = os.path.join(BASE_DIR, OUTPUT_EXE_NAME + ".exe")

    if os.path.exists(output_exe_path):
        try:
            os.remove(output_exe_path)
        except OSError as e:
            print(f"Error removing old file {output_exe_path}: {e}")

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if file:
        filename = secure_filename(file.filename)
        input_image_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            file.save(input_image_path)
            print(f"Uploaded file saved to: {input_image_path}")

            standard_image_base64 = package_utils.resize_image_to_480p_base64(input_image_path)
            if not standard_image_base64:
                raise ValueError("Failed to process uploaded image.")

            process_images_code = f"""
import os
import base64
from openai import OpenAI
import csv
from PIL import Image
import io
import sys
import traceback

API_BASE = "{TRAIT_API_BASE}"
API_KEY = "{TRAIT_API_KEY}"
MODEL = "{TRAIT_MODEL}"

client = None
try:
    client = OpenAI(
        api_key=API_KEY,
        base_url=API_BASE
    )
    print("OpenAI client initialized successfully.")
except Exception as e:
    print(f"Error initializing OpenAI client: {{e}}")

def resize_image_to_480p_base64(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if width > 854 or height > 480:
                ratio = min(854.0/width, 480.0/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return "data:image/jpeg;base64," + img_str
    except FileNotFoundError:
        print(f"Error: Image file not found at {{image_path}}")
    except Exception as e:
        print(f"Error resizing image {{image_path}}: {{e}}")
    return None

def extract_result(text):
    if not isinstance(text, str):
        print("Error: Input to extract_result is not a string.")
        return "ExtractionError"
    try:
        if '$' in text:
            start = text.find('$') + 1
            end = text.rfind('$')
            if start < end:
                return text[start:end].strip()
    except Exception as e:
        print(f"Error extracting result: {{e}}")
    return "ExtractionFailed"

def process_image_with_standard(client, model, standard_image_b64, current_image_b64):
    if not client:
        print("Error: OpenAI client not initialized.")
        return "ClientError"
    if not standard_image_b64 or not current_image_b64:
        print("Error: Missing image data for API call.")
        return "ImageDataError"

    try:
        print(f"Sending request to model: {{model}}")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {{
                    "role": "system",
                    "content": "You are an expert image analysis assistant. Compare the second image against the criteria shown in the first image."
                }},
                {{
                    "role": "user",
                    "content": [
                        {{
                            "type": "text",
                            "text": "请根据第一张图片中的判断标准，判断第二张图片所归属的类型。请严格按照标准判断。\\n\\n输出格式要求：\\n1. 第一行简要描述判断过程或理由。\\n2. 第二行输出最终的判断结果，并将结果用美元符号包裹，例如：$判断结果$。"
                        }},
                        {{
                            "type": "image_url",
                            "image_url": {{
                                "url": standard_image_b64
                            }}
                        }},
                        {{
                            "type": "image_url",
                            "image_url": {{
                                "url": current_image_b64
                            }}
                        }}
                    ]
                }}
            ],
            max_tokens=150
        )

        full_result = completion.choices[0].message.content
        print(f"Raw response received: {{full_result[:100]}}...")
        result = extract_result(full_result)
        print(f"Extracted result: {{result}}")
        return result
    except Exception as e:
        print(f"Error during API call or processing: {{e}}")
        traceback.print_exc()
        return "APIError"

def main():
    standard_image_b64_embedded = "{standard_image_base64}"
    output_csv_path = 'results.csv'
    processed_count = 0
    error_count = 0

    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    print(f"Script running in directory: {{script_dir}}")
    print(f"Looking for images in: {{script_dir}}")

    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['filename', 'result'])

            for filename in os.listdir(script_dir):
                file_path = os.path.join(script_dir, filename)
                if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    print(f"Processing image: {{filename}}")
                    try:
                        current_image_b64 = resize_image_to_480p_base64(file_path)
                        if not current_image_b64:
                            print(f"Skipping {{filename}} due to resizing error.")
                            writer.writerow([filename, "ResizeError"])
                            error_count += 1
                            continue

                        result = process_image_with_standard(client, MODEL, standard_image_b64_embedded, current_image_b64)
                        writer.writerow([filename, result])
                        processed_count += 1
                        print(f"Finished processing {{filename}}. Result: {{result}}")

                    except Exception as e:
                        print(f"Error processing file {{filename}}: {{e}}")
                        traceback.print_exc()
                        writer.writerow([filename, f"FileProcessingError: {{e}}"])
                        error_count += 1

    except Exception as e:
        print(f"Fatal error during CSV writing or file iteration: {{e}}")
        traceback.print_exc()
        error_count += 1

    print(f"\\nProcessing complete.")
    print(f"Successfully processed images: {{processed_count}}")
    print(f"Errors encountered: {{error_count}}")
    print(f"Results saved to {{output_csv_path}}")

if __name__ == "__main__":
    main()
    input("\\nPress Enter to exit...")
"""
            print("Starting PyInstaller packaging...")
            final_exe_path = package_utils.package_to_exe(process_images_code, 'temp_spade_code', OUTPUT_EXE_NAME)
            print(f"Packaging complete. Executable at: {final_exe_path}")

            os.remove(input_image_path)

            if os.path.exists(final_exe_path):
                print(f"Sending file: {final_exe_path}")
                return send_file(final_exe_path, as_attachment=True, download_name=OUTPUT_EXE_NAME + ".exe")
            else:
                print(f"Error: Generated executable not found at {final_exe_path}")
                return jsonify({"error": "Failed to create the executable file after packaging."}), 500

        except Exception as e:
            print(f"Error during trait standard upload/processing:")
            traceback.print_exc()
            if os.path.exists(input_image_path):
                try:
                    os.remove(input_image_path)
                except OSError as rm_err:
                    print(f"Error cleaning up upload file {input_image_path}: {rm_err}")
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    else:
        return jsonify({"error": "File processing failed."}), 400


@app.route('/get_fixed_programs')
def get_fixed_programs():
    programs = []
    if not os.path.isdir(FIXED_PROG_DIR):
        print(f"Error: Fixed programs directory not found: {FIXED_PROG_DIR}")
        return jsonify({"success": False, "error": "Fixed programs directory not found on server."}), 404

    try:
        programs = sorted(
            [f for f in os.listdir(FIXED_PROG_DIR) if f.lower().endswith('.exe')],
            key=lambda x: os.path.getmtime(os.path.join(FIXED_PROG_DIR, x)),
            reverse=True
        )
        return jsonify({
            "success": True,
            "programs": programs
        })
    except Exception as e:
        print(f"Error listing fixed programs in {FIXED_PROG_DIR}: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Server error listing programs: {str(e)}"
        }), 500


@app.route('/download_fixed/<path:filename>')
def download_fixed(filename):
    if '/' in filename or '\\' in filename:
        return jsonify({"error": "Invalid filename."}), 400
    safe_filename = secure_filename(filename)
    if not safe_filename.lower().endswith('.exe'):
        return jsonify({"error": "Invalid file type requested."}), 400

    file_path = os.path.join(FIXED_PROG_DIR, safe_filename)
    print(f"Attempting to send fixed file: {file_path}")

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        print(f"Error: Fixed file not found or is not a file: {file_path}")
        return jsonify({"error": "File not found."}), 404

    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(f"Error sending fixed file {safe_filename}: {e}")
        traceback.print_exc()
        return jsonify({"error": "Could not send file."}), 500


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')


@socketio.on('send_message')
def handle_send_message(data):
    user_input = data.get("userInput")
    agent_type = data.get("agent")
    sid = request.sid

    if not user_input or not agent_type:
        emit('error_message', {'error': 'Missing input or agent type.'}, room=sid)
        return

    ai_message_id = f"ai-msg-{uuid.uuid4()}"
    print(f"Received message from {sid}. Agent: {agent_type}. Assigning ID: {ai_message_id}")

    socketio.emit('ai_message_start', {'id': ai_message_id}, room=sid)

    manager = None
    if agent_type == "paperai":
        manager = paperai_manager
    elif agent_type == "chater":
        manager = chater_manager
    else:
        emit('error_message', {'error': 'Invalid agent selected.'}, room=sid)
        socketio.emit('ai_message_end', {'id': ai_message_id, 'full_text': '*Error: Invalid agent selected.*'}, room=sid)
        return

    print(f"Starting background task for {ai_message_id}")
    socketio.start_background_task(manager.process_user_input, user_input, sid, ai_message_id)


@socketio.on('stop_generation')
def handle_stop_generation(data):
    ai_message_id = data.get('id')
    sid = request.sid
    if ai_message_id:
        with active_tasks_lock:
            if ai_message_id in active_tasks:
                print(f"Received stop request for {ai_message_id} from {sid}")
                active_tasks[ai_message_id] = True
            else:
                print(f"Received stop request for inactive/unknown task: {ai_message_id}")
    else:
        print(f"Received stop request without message ID from {sid}")


if __name__ == "__main__":
    host = '0.0.0.0'
    port = 8080
    print(f"Starting Flask-SocketIO server on http://{host}:{port}")
    print(f"Access Chat UI at: http://127.0.0.1:{port}/chat")
    print(f"Access Trait Recognizer UI at: http://127.0.0.1:{port}/trait_recognizer")
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False)
