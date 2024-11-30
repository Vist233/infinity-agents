import uuid
from flask import Flask, render_template, request, session
from phi.workflow import RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
import os
from app.paperAI import PaperSummaryGenerator

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


'''
#测试用
def mock_ai_reply(user_input):
    """
    模拟 AI 回复
    """
    return f"你刚才说的是『{user_input}』吗？"

@app.route("/", methods=["GET", "POST"])
def index():
    # 初始化会话中的对话历史
    if "messages" not in session:
        session["messages"] = []  # 存储用户和 AI 的对话历史
    messages = session["messages"]

    if request.method == "POST":
        user_input = request.form.get("userInput")

        if user_input:
            try:
                # 模拟 AI 回复
                response = mock_ai_reply(user_input)

                # 保存对话记录到会话中
                messages.append({"type": "user", "text": user_input})
                messages.append({"type": "ai", "text": response})
                session["messages"] = messages  # 更新会话

            except Exception as e:
                error_message = f"处理过程中出错: {e}"
                messages.append({"type": "ai", "text": error_message})

    return render_template("main.html", messages=messages)
'''

@app.route("/", methods=["GET", "POST"])
def index():
    if "messages" not in session:
        session["messages"] = []  # 存储用户和 AI 的对话历史
    messages = session["messages"]
    logs = ["系统初始化完成\n"]

    if request.method == "POST":
        user_input = request.form.get("userInput")

        if user_input:
            assistant = PaperSummaryGenerator(
                session_id=f"generate-summary-on-{user_input}",
                storage=SqlWorkflowStorage(
                    table_name="generate_summary_workflows",
                    db_file="tmp/workflows.db",
                ),
            )

            try:
                logs.append(f"用户发送: {user_input}\n")
                response = ""

                conversation_history = "\n".join(
                    f"用户: {msg['text']}" if msg["type"] == "user" else f"AI: {msg['text']}"
                    for msg in messages
                )

                full_input = f"{conversation_history}\n用户: {user_input}"
                for res in assistant.run(logs, full_input):
                    if res.event == RunEvent.workflow_completed:
                        logs.append("Workflow completed.\n")
                        response = res.content

                messages.append({"type": "user", "text": user_input})
                messages.append({"type": "ai", "text": response})
                session["messages"] = messages
                logs.append(f"AI 回复: {response}\n")

            except Exception as e:
                error_message = f"处理过程中出错: {e}"
                logs.append(f"{error_message}\n")
                messages.append({"type": "ai", "text": error_message})

    return render_template("main.html",
                           messages=messages,
                           logs=logs)


@app.route("/upload", methods=["POST"])
def upload():
    logs = []
    uploaded_files = []

    if "files" in request.files:
        uploaded_files_list = request.files.getlist("files")
        for file in uploaded_files_list:
            if file and file.filename:
                filename = file.filename
                file_save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_save_path)
                uploaded_files.append(filename)
                logs.append(f"文件 '{filename}' 已成功上传至 {file_save_path}")

    return {"logs": logs, "uploaded_files": uploaded_files}, 200

if __name__ == "__main__":
    app.run(debug=True)
