import uuid
from flask import Flask, render_template, request, session, send_file
import os
import io
import zipfile
from codeAI import CodeAIWorkflow
from paperAI import PaperSummaryGenerator


class DialogueManager:
    def __init__(self, assistant):
        self.assistant = assistant

    def process_user_input(self, user_input, conversation_history=""):
        response = None
        try:
            # Create a new logs list for each request
            request_logs = []
            request_logs.append(f"User input {user_input} TO {self.assistant}\n")
            response = self.assistant.run(request_logs, user_input)  # Changed from input to user_input
            # Add any new logs to the global logs list
            global logs
            logs.extend(request_logs)
        except Exception as e:
            error_msg = f"处理过程中出错: {e}"
            logs.append(error_msg)
            return error_msg

        return response

app = Flask(__name__)
convId = str(uuid.uuid4())  # Convert UUID to string here
app.secret_key = convId  # Add this line after Flask initialization
logs = ["系统初始化完成\n"]

# 构建文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
Codedb_file = os.path.join(main_dir, "Database", "CodeWorkflows.db")
Paperdb_file = os.path.join(main_dir, "Database", "PaperWorkflows.db")
processing_space_dir = os.path.join(main_dir, 'ProcessingSpace')
WORKING_SPACE = os.path.join(processing_space_dir, convId)  
app.config["WORKING_SPACE"] = WORKING_SPACE


os.makedirs(WORKING_SPACE, exist_ok=True)
os.chdir(WORKING_SPACE)
if not os.path.exists(processing_space_dir):
    os.makedirs(processing_space_dir)
os.chdir(processing_space_dir)

from phi.storage.workflow.sqlite import SqlWorkflowStorage
paperai = PaperSummaryGenerator(
    session_id=str(convId),
    storage=SqlWorkflowStorage(
        table_name=str(convId),
        db_file=Paperdb_file,
    ),
)
codeai = CodeAIWorkflow(
    session_id=str(convId),
    storage=SqlWorkflowStorage(
        table_name=str(convId),
        db_file=Codedb_file,
    ),
)
paperai_manager = DialogueManager(paperai)
codeai_manager = DialogueManager(codeai)




@app.route("/", methods=["GET", "POST"])
def index():
    #lock here
    if "messages" not in session:
        session["messages"] = []
    messages = session["messages"]
    os.chdir(app.config["WORKING_SPACE"])
    
    if request.method == "POST":
        user_input = request.form.get("userInput")
        agent = request.form.get("agent")
        if user_input:
            if agent == "paperai":
                response = paperai_manager.process_user_input(user_input)
            elif agent == "codeai":
                response = codeai_manager.process_user_input(user_input)
            else:
                response = "未指定有效的 Agent。"
            
            if response:
                reply = ''
                if hasattr(response, '__iter__'):
                    for res in response:
                        reply += res.content if hasattr(res, 'content') else str(res)
                else:
                    reply = response.content if hasattr(response, 'content') else str(response)
                
                messages.append({"type": "user", "text": user_input})
                messages.append({"type": "ai", "text": reply})
                session["messages"] = messages
    
    return render_template("main.html", messages=messages, logs=logs) #unlock here





@app.route("/upload", methods=["POST"])
def upload():
    logs = []
    uploaded_files = []

    if "files" in request.files:
        uploaded_files_list = request.files.getlist("files")
        for file in uploaded_files_list:
            if file and file.filename:
                filename = file.filename
                file_save_path = os.path.join(str(app.config["WORKING_SPACE"]), filename)
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
