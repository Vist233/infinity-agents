import uuid
from flask import Flask, render_template, request, session
import os
from paperAI import PaperSummaryGenerator
from phi.storage.workflow.sqlite import SqlWorkflowStorage

class DialogueManager:
    def __init__(self, assistant):
        self.assistant = assistant

    def process_user_input(self, user_input, conversation_history=""):
        response = None
        try:
            # Create a new logs list for each request
            request_logs = []
            request_logs.append(f"User input {user_input} TO {self.assistant}\n")
            response = self.assistant.run(request_logs, user_input)
            # Add any new logs to the global logs list
            global logs
            logs.extend(request_logs)
        except Exception as e:
            error_msg = f"处理过程中出错: {e}"
            logs.append(error_msg)
            return error_msg

        return response

app = Flask(__name__)
convId = str(uuid.uuid4())
app.secret_key = convId
logs = ["系统初始化完成\n"]

# 构建文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
Paperdb_file = os.path.join(main_dir, "Database", "PaperWorkflows.db")

# Ensure Database directory exists for PaperAI
db_dir = os.path.join(main_dir, "Database")
os.makedirs(db_dir, exist_ok=True)

paperai = PaperSummaryGenerator(
    session_id=str(convId),
    storage=SqlWorkflowStorage(
        table_name=str(convId),
        db_file=Paperdb_file,
    ),
)
paperai_manager = DialogueManager(paperai)

@app.route("/", methods=["GET", "POST"])
def index():
    if "messages" not in session:
        session["messages"] = []
    messages = session["messages"]

    if request.method == "POST":
        user_input = request.form.get("userInput")
        agent = request.form.get("agent")
        if user_input:
            if agent == "paperai":
                response = paperai_manager.process_user_input(user_input)
            else:
                response = "Invalid agent selected."

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

    return render_template("main.html", messages=messages)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
