import uuid
from flask import Flask, render_template, request, session
from phi.workflow import RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
import os

from codeAI import CodeAIWorkflow
from paperAI import PaperSummaryGenerator


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
                full_input = f"{conversation_history}\n用户: {user_input}"  # 包含上下文的输入
                for res in self.assistant.run(logs, full_input):
                    if res.event == RunEvent.workflow_completed:
                        logs.append("Workflow completed.\n")
                        response = res.content
        except Exception as e:
            response = f"处理过程中出错: {e}"
            logs.append(f"{response}\n")

        return response

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
UPLOAD_FOLDER = f"ProcessingSpace\\{app.secret_key}"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
    logs = ["系统初始化完成\n"]   #右下角

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
                file_save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(file_save_path)
                uploaded_files.append(filename)
                logs.append(f"文件 '{filename}' 已成功上传至 {file_save_path}")

    return {"logs": logs, "uploaded_files": uploaded_files}, 200

if __name__ == "__main__":
    app.run(debug=True)
