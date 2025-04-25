import uuid
from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit
import os
from agents import paperai_agent, chater_agent
from agno.agent import Agent
from config import API_KEY

app = Flask(__name__)
convId = str(uuid.uuid4())
app.secret_key = convId
socketio = SocketIO(app, async_mode='eventlet')
API = os.environ.get('DEEPSEEK_API_KEY') or API_KEY

class DialogueManager:
    def __init__(self, assistant, socketio_instance):
        self.assistant = assistant
        self.socketio = socketio_instance

    def process_user_input(self, user_input, sid):
        try:
            assistant_name = getattr(self.assistant, 'description', self.assistant.__class__.__name__)

            ai_message_id = f"ai-msg-{uuid.uuid4()}"
            self.socketio.emit('ai_message_start', {'id': ai_message_id}, room=sid)

            full_response = ""
            response_stream = None

            if isinstance(self.assistant, Agent):
                try:
                    response_stream = self.assistant.run(user_input, stream=True)
                except Exception as agent_run_error:
                    raise agent_run_error
            else:
                raise TypeError(f"Cannot process input for assistant type: {type(self.assistant)}")

            if hasattr(response_stream, '__iter__') and not isinstance(response_stream, str):
                for chunk in response_stream:
                    content_chunk = str(getattr(chunk, 'content', chunk))
                    if content_chunk:
                        full_response += content_chunk
                        self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': content_chunk}, room=sid)
                        self.socketio.sleep(0.01)
            elif response_stream is not None:
                content = str(response_stream)
                full_response = content
                self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': content}, room=sid)
            else:
                full_response = "Assistant did not generate a response."
                self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': full_response}, room=sid)

            self.socketio.emit('ai_message_end', {'id': ai_message_id, 'full_text': full_response}, room=sid)

        except Exception as e:
            error_msg = f"An error occurred: {e}"
            if 'ai_message_id' not in locals():
                ai_message_id = f"ai-msg-error-{uuid.uuid4()}"
                self.socketio.emit('ai_message_start', {'id': ai_message_id}, room=sid)

            self.socketio.emit('ai_message_chunk', {'id': ai_message_id, 'chunk': f"\n\n**Error:** {error_msg}"}, room=sid)
            self.socketio.emit('ai_message_end', {'id': ai_message_id, 'full_text': full_response + f"\n\n**Error:** {error_msg}"}, room=sid)

paperai_manager = DialogueManager(paperai_agent, socketio)
chater_manager = DialogueManager(chater_agent, socketio)

@app.route("/")
def index():
    if "messages" not in session:
        session["messages"] = []
    return render_template("main.html", messages=session["messages"])

@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('disconnect')
def handle_disconnect():
    pass

@socketio.on('send_message')
def handle_send_message(data):
    user_input = data.get("userInput")
    agent_type = data.get("agent")
    sid = request.sid

    if user_input and agent_type:
        if agent_type == "paperai":
            socketio.start_background_task(paperai_manager.process_user_input, user_input, sid)
        elif agent_type == "chater":
            socketio.start_background_task(chater_manager.process_user_input, user_input, sid)
        else:
            emit('error_message', {'error': 'Invalid agent selected.'}, room=sid)
    else:
        emit('error_message', {'error': 'Missing input or agent type.'}, room=sid)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8080, debug=False, use_reloader=False)
