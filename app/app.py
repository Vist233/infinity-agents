import uuid
from flask import Flask, render_template, request, session, send_file, jsonify, url_for, after_this_request, current_app
from flask_socketio import SocketIO, emit
import os
import tempfile
import subprocess
import shutil
import json
from datetime import datetime
import sys
from agents import paperai_agent, chater_agent
import threading
import traceback
from agno.agent import Agent
import base64
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

app = Flask(__name__)
convId = str(uuid.uuid4())
app.secret_key = os.environ.get("FLASK_SECRET_KEY", convId)
socketio = SocketIO(app, async_mode='eventlet')
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_REQUEST_BYTES", 12 * 1024 * 1024))  # default 12MB

active_tasks = {}
active_tasks_lock = threading.Lock()
packager_executor = ThreadPoolExecutor(max_workers=int(os.environ.get("PACKAGER_CONCURRENCY", 2)))
MAX_TRAIT_IMAGE_BASE64 = int(os.environ.get("MAX_TRAIT_IMAGE_BASE64", 6 * 1024 * 1024))  # 6MB base64 string length
MAX_WORKSPACE_FILE_BASE64 = int(os.environ.get("MAX_WORKSPACE_FILE_BASE64", 4 * 1024 * 1024))  # 4MB per file
MAX_TOTAL_WORKSPACE_BASE64 = int(os.environ.get("MAX_TOTAL_WORKSPACE_BASE64", 10 * 1024 * 1024))  # 10MB total
PYINSTALLER_TIMEOUT = int(os.environ.get("PYINSTALLER_TIMEOUT_SEC", 300))  # default 5 minutes


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
            try:
                if should_stop and hasattr(response_stream, "close"):
                    response_stream.close()
            except Exception as close_exc:
                print(f"Error closing response stream: {close_exc}")
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




ALLOWED_IMAGE_EXTS = {"jpg", "jpeg", "png", "bmp", "webp", "heic", "tif", "tiff"}


def _write_packager_script(destination_path, trait_image_data_url):
    """Builds a non-interactive copy of traitRecognizePackager.py."""
    script_template = """import os
from openai import OpenAI
import base64
import json
import csv


DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
trait_image_url = __TRAIT_IMAGE_DATA_URL__
WORKSPACE = input("Please enter your image directory (default is current directory): ") or "./"
WORKSPACE = os.path.abspath(WORKSPACE)


def judge_image_type(trait_image_url):
    lower_url = trait_image_url.lower()
    if lower_url.endswith((".jpg", ".jpeg", ".jpe")):
        return "jpeg"
    if lower_url.endswith(".png"):
        return "png"
    if lower_url.endswith(".bmp"):
        return "bmp"
    if lower_url.endswith(".webp"):
        return "webp"
    if lower_url.endswith(".heic"):
        return "heic"
    if lower_url.endswith((".tif", ".tiff")):
        return "tiff"
    return ""


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_url(image_path):
    image_base64 = encode_image(image_path)
    image_type = judge_image_type(image_path)
    if image_type == "":
        raise ValueError("Unsupported image type")
    return f"data:image/{{image_type}};base64,{{image_base64}}"


def getClassify(trait_image_url, case_image_url):
    completion = client.chat.completions.create(
        model="qwen3-vl-plus",
        messages=[
            {
                "role": "system",
                "content": "请你按照{}的格式返回结果".format(
                    {"reason": "string", "class": "string"}
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": trait_image_url}},
                    {"type": "image_url", "image_url": {"url": case_image_url}},
                    {"type": "text", "text": "请你根据第一张图片的分类信息，得到第二张图片属于哪一个类并说明理由。"},
                ],
            }
        ],
        response_format={"type": "json_object"}
    )
    result = json.loads(completion.choices[0].message.content)
    return result.get("class", ""), result.get("reason", "")


client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def main():
    csv_filename = "image_classification_results.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["filename", "class", "reason"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for root, dirs, files in os.walk(WORKSPACE):
            for filename in files:
                if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".tif", ".tiff")):
                    image_url = get_image_url(os.path.join(root, filename))

                    try:
                        class_result, reason = getClassify(trait_image_url, image_url)

                        writer.writerow({
                            "filename": filename,
                            "class": class_result,
                            "reason": reason
                        })

                        print(f"Processed: {filename} -> Class: {class_result}")

                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        writer.writerow({
                            "filename": filename,
                            "class": "ERROR",
                            "reason": str(e)
                        })

    print(f"Results saved to {csv_filename}")


if __name__ == "__main__":
    main()
"""
    script_content = script_template.replace(
        "__TRAIT_IMAGE_DATA_URL__",
        json.dumps(trait_image_data_url),
    )
    with open(destination_path, "w", encoding="utf-8") as script_file:
        script_file.write(script_content)


def _strip_data_url_prefix(data):
    if not isinstance(data, str):
        return data
    if "," in data:
        return data.split(",", 1)[1]
    return data


"""POST /generate_exe
    {
    "trait_image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD…",
    "trait_image_ext": "jpeg",
    "workspace_files": [
        {"name": "case/a.jpg", "content": "/9j/4AAQ..."},
        {"name": "case/b.png", "content": "iVBORw0KGgoAAA..."}
    ]
    }
"""
@app.route("/generate_exe", methods=["POST"])
def generate_exe():
    request_data = request.get_json(silent=True)
    if not request_data:
        return jsonify({"error": "请求体必须是 JSON"}), 400

    trait_image_base64 = request_data.get("trait_image_base64")
    trait_image_ext = request_data.get("trait_image_ext")
    if not trait_image_base64 or not trait_image_ext:
        return jsonify({"error": "缺少 trait_image_base64 或 trait_image_ext"}), 400

    trait_image_ext = str(trait_image_ext).lower().lstrip(".")
    if trait_image_ext not in ALLOWED_IMAGE_EXTS:
        return jsonify({"error": "不支持的图片格式", "allowed": sorted(ALLOWED_IMAGE_EXTS)}), 400

    trait_image_base64_clean = _strip_data_url_prefix(trait_image_base64)
    if len(trait_image_base64_clean) > MAX_TRAIT_IMAGE_BASE64:
        return jsonify({"error": "trait_image_base64 过大"}), 413

    try:
        base64.b64decode(trait_image_base64_clean, validate=True)
    except Exception:
        return jsonify({"error": "trait_image_base64 无法解析"}), 400

    workspace_files = request_data.get("workspace_files") or []
    total_workspace_len = 0
    for file_entry in workspace_files:
        if not isinstance(file_entry, dict):
            return jsonify({"error": "workspace_files 项格式错误"}), 400
        name = file_entry.get("name") or ""
        if ".." in name or name.startswith(("/", "\\")):
            return jsonify({"error": f"非法文件名: {name}"}), 400
        content = file_entry.get("content", "")
        if not isinstance(content, str):
            return jsonify({"error": f"文件 {name} 的 content 非字符串"}), 400
        if len(content) > MAX_WORKSPACE_FILE_BASE64:
            return jsonify({"error": f"文件 {name} 体积超过限制"}), 413
        total_workspace_len += len(content)
    if total_workspace_len > MAX_TOTAL_WORKSPACE_BASE64:
        return jsonify({"error": "workspace_files 总体积超过限制"}), 413

    temp_dir = tempfile.mkdtemp(prefix="package_gen_")
    cleanup_required = True

    try:
        trait_image_data_url = f"data:image/{trait_image_ext};base64,{trait_image_base64_clean}"
        script_path = os.path.join(temp_dir, "traitRecognizePackager.py")
        _write_packager_script(script_path, trait_image_data_url)

        build_name = f"traitRecognizePackager_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        pyinstaller_cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--name",
            build_name,
            script_path,
        ]

        def _run_packager():
            return subprocess.run(
                pyinstaller_cmd,
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=PYINSTALLER_TIMEOUT,
            )

        future = packager_executor.submit(_run_packager)
        try:
            result = future.result(timeout=PYINSTALLER_TIMEOUT + 5)
        except FuturesTimeoutError:
            future.cancel()
            current_app.logger.error("PyInstaller 执行超时（线程阻塞）")
            return jsonify({"error": "PyInstaller 执行超时"}), 504
        except subprocess.TimeoutExpired as timeout_exc:
            current_app.logger.error("PyInstaller 执行超时: %s", timeout_exc)
            return jsonify({"error": "PyInstaller 执行超时"}), 504

        if result.returncode != 0:
            current_app.logger.error("PyInstaller 打包失败: %s", result.stderr.strip())
            return jsonify({
                "error": "PyInstaller 打包失败",
                "details": result.stderr[-2000:],
            }), 500

        dist_path = os.path.join(temp_dir, "dist", build_name)
        if os.name == "nt":
            dist_path += ".exe"
        download_name = os.path.basename(dist_path)
        if os.name != "nt":
            download_name += ".bin"

        if not os.path.exists(dist_path):
            current_app.logger.error("未找到生成的可执行文件: %s", dist_path)
            return jsonify({"error": "未找到生成的可执行文件"}), 500

        @after_this_request
        def cleanup(response):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return response

        cleanup_required = False
        return send_file(dist_path, as_attachment=True, download_name=download_name)

    except FileNotFoundError as exc:
        current_app.logger.exception("PyInstaller 未找到: %s", exc)
        return jsonify({"error": "未找到 PyInstaller，请先安装依赖"}), 500
    except Exception as exc:
        current_app.logger.exception("生成 EXE 过程出错")
        return jsonify({"error": "生成过程出错", "details": str(exc)}), 500
    finally:
        if cleanup_required:
            shutil.rmtree(temp_dir, ignore_errors=True)


@app.route("/download/<program_name>")
def download_exe(program_name):
    """Download pre-built EXE programs"""
    # Map program names to actual EXE files
    exe_files = {
        "cabbage_classifier": "CabbageClassifier.exe",
        "plant_analyzer": "PlantAnalyzer.exe"
    }
    
    if program_name not in exe_files:
        return "Program not found", 404
    
    # For testing, create a simple placeholder EXE
    exe_path = f"./tools/{exe_files[program_name]}"
    
    # Create a simple executable placeholder if file doesn't exist
    if not os.path.exists(exe_path):
        # Create a simple Windows batch file as placeholder
        with open(exe_path, 'w') as f:
            f.write("@echo off\necho This is a placeholder EXE for testing\necho Place EXE generation logic here\npause")
    
    return send_file(exe_path, as_attachment=True)


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
    port = 8080
    print(f"🚀 Infinity Agents Server started")
    print(f"📍 Chat Interface: http://127.0.0.1:{port}/chat")
    socketio.run(app, host='127.0.0.1', port=port, debug=False, use_reloader=False)
