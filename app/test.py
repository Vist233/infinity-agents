from flask import Flask, render_template, request
from phi.workflow import RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
import os
from app.paperAI import PaperSummaryGenerator

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    messages = []
    logs = ["系统初始化完成\n"]
    uploaded_files = []

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
                for res in assistant.run(user_input):
                    if res.event == RunEvent.workflow_completed:
                        logs.append("Workflow completed.\n")
                        response = res.content

                messages.append({"type": "user", "text": user_input})
                messages.append({"type": "ai", "text": response})
                logs.append(f"AI 回复: {response}\n")

            except Exception as e:
                error_message = f"处理过程中出错: {e}"
                logs.append(f"{error_message}\n")
                messages.append({"type": "ai", "text": error_message})

    return render_template("main.html",
                           messages=messages,
                           logs=logs,
                           uploaded_files=uploaded_files)

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
