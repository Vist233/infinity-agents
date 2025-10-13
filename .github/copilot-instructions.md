# GitHub Copilot Instructions

This document provides guidance for AI coding agents to effectively contribute to the **Infinity Agents** codebase.

## Big Picture Architecture

This is a Flask-based web application that provides a chat interface to interact with different AI agents. The core of the application is built using the `agno` library, which orchestrates the behavior of these agents.

- **`app/app.py`**: The main entry point of the Flask application. It handles HTTP requests, WebSocket events, and manages the lifecycle of agent interactions. It uses `flask-socketio` for real-time communication to stream agent responses to the frontend.
- **`app/agents.py`**: Defines the AI agents available in the application. Currently, it includes:
    - `paperai_agent`: A research assistant that uses `PubmedTools` to search for and summarize academic papers.
    - `chater_agent`: A general-purpose conversational agent.
- **`app/templates/main.html`**: The single-page frontend for the chat interface.
- **`agno` library**: The framework used to build and run the AI agents. It integrates with models like DeepSeek and provides tools for agents to use.

The data flow for a user message is as follows:
1. The user sends a message from the web interface (`main.html`).
2. A WebSocket event (`send_message`) is triggered in `app/app.py`.
3. The appropriate agent (`paperai_agent` or `chater_agent`) is selected based on the user's choice.
4. A `DialogueManager` instance calls the agent's `run` method with the user's input.
5. The agent's response is streamed back to the frontend chunk by chunk via WebSocket events (`ai_message_chunk`).

## Developer Workflows

### Setup and Running

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set API Key**: The application requires a `DEEPSEEK_API_KEY`. You can set it as an environment variable:
    ```bash
    export DEEPSEEK_API_KEY="your_api_key_here"
    ```
    Alternatively, you can modify `app/agents.py` directly, but using an environment variable is preferred.

3.  **Run the application**:
    ```bash
    python app/app.py
    ```
    The chat interface will be available at `http://127.0.0.1:8080/chat`.

### Testing

Run the test suite using `pytest`:
```bash
pytest tests/
```

### Docker

The application can be run in a Docker container.

1.  **Build the image**:
    ```bash
    docker build -t infinite-agents .
    ```
2.  **Run the container**:
    ```bash
    docker run -p 8080:8080 -e DEEPSEEK_API_KEY="your_key" infinite-agents
    ```

## Project-Specific Conventions

- **Agent Definition**: New agents should be defined in `app/agents.py` following the pattern of `paperai_agent` and `chater_agent`. Each agent is an instance of the `agno.agent.Agent` class.
- **Agent Integration**: To make a new agent available in the UI, you need to:
    1. Import the agent in `app/app.py`.
    2. Create a new `DialogueManager` instance for it.
    3. Add it to the `handle_send_message` function to select the agent based on a new `agent_type`.
    4. Update the frontend in `app/templates/main.html` to include the new agent in the selection dropdown.
- **Streaming Responses**: The application is designed to stream responses. When modifying agent interactions, ensure that the streaming behavior is maintained by iterating over the response from the agent's `run` method and emitting `ai_message_chunk` events.
- **Dependencies**: Add any new Python dependencies to `requirements.txt`.
