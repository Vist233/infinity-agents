import uuid
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
import os
from paperAI import paperai_agent
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.utils.log import logger
from config import API_KEY

app = Flask(__name__)
convId = str(uuid.uuid4())
app.secret_key = convId
socketio = SocketIO(app, async_mode='eventlet')
logs = ["系统初始化完成\n"]
API = os.environ.get('DEEPSEEK_API_KEY') or API_KEY

# --- DialogueManager ---
class DialogueManager:
    def __init__(self, assistant, socketio_instance):
        self.assistant = assistant
        self.socketio = socketio_instance

    def process_user_input(self, user_input, sid):
        try:
            request_logs = []
            assistant_name = getattr(self.assistant, 'description', self.assistant.__class__.__name__)
            request_logs.append(f"User input '{user_input}' TO {assistant_name}\n")
            logger.info(f"Processing input for SID: {sid} with {assistant_name}")

            ai_message_id = f"ai-msg-{uuid.uuid4()}"
            self.socketio.emit('ai_message_start', {'id': ai_message_id}, room=sid)

            full_response = ""
            response_stream = None

            if isinstance(self.assistant, Agent):
                try:
                    response_stream = self.assistant.run(user_input, stream=True)
                except Exception as agent_run_error:
                    logger.error(f"Error running agent {assistant_name}: {agent_run_error}", exc_info=True)
                    raise agent_run_error
            else:
                logger.error(f"Unknown assistant type: {type(self.assistant)}")
                raise TypeError(f"Cannot process input for assistant type: {type(self.assistant)}")

            if hasattr(response_stream, '__iter__') and not isinstance(response_stream, str):
                for chunk in response_stream:
                    content_chunk = str(chunk.content)
                    if content_chunk:
                        full_response += content_chunk
                        self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': content_chunk}, room=sid)
                        self.socketio.sleep(0.01)
            elif response_stream is not None:
                content = str(response_stream)
                full_response = content
                self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': content}, room=sid)
            else:
                logger.warning(f"No response stream generated for input '{user_input}' with {assistant_name}")
                full_response = "Assistant did not generate a response."
                self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': full_response}, room=sid)

            self.socketio.emit('ai_message_end', {'id': ai_message_id, 'full_text': full_response}, room=sid)

            global logs
            logs.extend(request_logs)
            logs.append(f"AI Response for '{user_input}': {full_response[:100]}...")
            logger.info(f"Finished processing for SID: {sid}")

        except Exception as e:
            error_msg = f"处理过程中出错: {e}"
            logs.append(error_msg)
            logger.error(f"Error processing input for SID {sid}: {e}", exc_info=True)
            if 'ai_message_id' in locals():
                self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': f"\n\n**Error:** {error_msg}"}, room=sid)
                self.socketio.emit('ai_message_end', {'id': ai_message_id, 'full_text': full_response + f"\n\n**Error:** {error_msg}"}, room=sid)
            else:
                self.socketio.emit('error_message', {'error': error_msg}, room=sid)

# --- Agent Initialization ---
current_dir = os.path.dirname(os.path.abspath(__file__))
main_dir = os.path.dirname(current_dir)
Chatdb_file = os.path.join(main_dir, "Database", "ChatWorkflows.db")

db_dir = os.path.join(main_dir, "Database")
os.makedirs(db_dir, exist_ok=True)

paperai_manager = DialogueManager(paperai_agent, socketio)

chater = Agent(
    model=DeepSeek(api_key=API),
    markdown=True,
    description="A general conversational AI assistant.",
)
chater_manager = DialogueManager(chater, socketio)

# --- Routes and SocketIO Events ---
@app.route("/")
def index():
    if "messages" not in session:
        session["messages"] = []
    return render_template("main.html", messages=session["messages"])

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('send_message')
def handle_send_message(data):
    user_input = data.get("userInput")
    agent_type = data.get("agent")
    sid = request.sid

    if user_input and agent_type:
        logger.info(f"Received message from {sid}: Agent={agent_type}, Input='{user_input}'")

        if agent_type == "paperai":
            socketio.start_background_task(paperai_manager.process_user_input, user_input, sid)
        elif agent_type == "chater":
            socketio.start_background_task(chater_manager.process_user_input, user_input, sid)
        else:
            emit('error_message', {'error': 'Invalid agent selected.'}, room=sid)
    else:
        logger.warning(f"Invalid message received from {sid}: {data}")
        emit('error_message', {'error': 'Missing input or agent type.'}, room=sid)

if __name__ == "__main__":
    logger.info("Starting Flask-SocketIO server...")
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, use_reloader=True)
