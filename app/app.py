import uuid
from flask import Flask, render_template, request, session, send_file
from phi.workflow import RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
import os
import io
import zipfile

from app.config import SECRET_KEY, DATABASE_DIR
from .codeAI import CodeAIWorkflow
from .paperAI import PaperSummaryGenerator


class DialogueManager:
    def __init__(self, assistant):
        self.assistant = assistant

    def process_user_input(self, user_input, conversation_history, logs):
        logs.append(f"用户发送: {user_input}\n")
        response = ""

        try:
            if self.assistant == paperai:
                self.assistant.session_id = f"generate-summary-on-{user_input}"

                for res in self.assistant.run(logs, user_input):
                    if res.event == RunEvent.workflow_completed:
                        logs.append("Workflow completed.\n")
                        response = res.content
            elif self.assistant == codeai:
                #full_input = f"{conversation_history}\n用户: {user_input}"  # 包含上下文的输入
                for res in self.assistant.run(logs, user_input):
                    if res.event == RunEvent.workflow_completed:
                        logs.append("Workflow completed.\n")
                        response = res.content
        except Exception as e:
            response = f"处理过程中出错: {e}"
            logs.append(f"{response}\n")

        return response

app = Flask(__name__)
app.secret_key = SECRET_KEY
logs = ["系统初始化完成\n"]  # 右下角

# Initialize processing workspace
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Get the API key from environment variables OR set your API key here
API_KEY = os.environ.get("YI_API_KEY", "1352a88fdd3844deaec9d7dbe4b467d5")

# 构建目标目录路径
processing_space_dir = os.path.join(parent_dir, 'ProcessingSpace')
database_dir = DATABASE_DIR
print(f"Parent directory: {parent_dir}")

# 创建目录并切换到该目录
if not os.path.exists(processing_space_dir):
    os.makedirs(processing_space_dir)
os.chdir(processing_space_dir)

# Generate a new session ID
WORKING_SPACE = f"{app.secret_key}"
os.makedirs(WORKING_SPACE, exist_ok=True)
os.chdir(WORKING_SPACE)
app.config["WORKING_SPACE"] = WORKING_SPACE

# Create database directory before initializing storage
os.makedirs(database_dir, exist_ok=True)

paperai = PaperSummaryGenerator(
    storage=SqlWorkflowStorage(
        table_name="generate_summary_workflows",
        db_file="tmp/workflows.db",
    ),
)
codeai = CodeAIWorkflow(
    session_id=app.secret_key,
    storage=SqlWorkflowStorage(
        table_name=app.secret_key,
        db_file="./../Database/CodeWorkflows.db",
    ),
)
paperai_manager = DialogueManager(paperai)
codeai_manager = DialogueManager(codeai)

@app.route("/", methods=["GET", "POST"])
def index():
    if "messages" not in session:
        session["messages"] = []
    messages = session["messages"]

    if request.method == "POST":
        user_input = request.form.get("userInput")
        agent = request.form.get("agent")  # 判断是调用 paperai 还是 codeai
        if user_input:
            # 获取对话上下文
            conversation_history = "\n".join(
                f"用户: {msg['text']}" if msg["type"] == "user" else f"AI: {msg['text']}"
                for msg in messages
            )

            if agent == "paperai":
                response = paperai_manager.process_user_input(user_input, conversation_history, logs)
            elif agent == "codeai":
                response = codeai_manager.process_user_input(user_input, conversation_history, logs)
            else:
                response = "未指定有效的 Agent。"

            messages.append({"type": "user", "text": user_input})
            messages.append({"type": "ai", "text": response})
            session["messages"] = messages

    return render_template("main.html", messages=messages, logs=logs)

@app.route("/upload", methods=["POST"])
def upload():
    logs = []
    uploaded_files = []

    if "files" in request.files:
        uploaded_files_list = request.files.getlist("files")
        for file in uploaded_files_list:
            if file and file.filename:
                filename = file.filename
                file_save_path = os.path.join(app.config["WORKING_SPACE"], filename)
                file.save(file_save_path)
                uploaded_files.append(filename)
                logs.append(f"文件 '{filename}' 已成功上传至 {file_save_path}")

    return {"logs": logs, "uploaded_files": uploaded_files}, 200

@app.route("/download", methods=["GET"])
def download():
    """将 WORKING_SPACE 中的所有文件打包为 ZIP 并提供下载"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(app.config["WORKING_SPACE"]):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=app.config["WORKING_SPACE"])
                zip_file.write(file_path, arcname)
    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="uploaded_files.zip",
        mimetype="application/zip",
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
