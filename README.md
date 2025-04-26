# Infinity Agents

An AI agent for paper searching and summarization, now with real-time streaming responses via WebSockets. Built using `agno`.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

Infinity Agents is an AI-based tool designed to search for academic papers and provide summaries, built using the `agno` framework. This repository contains the necessary components to run the Paper AI agent.

This AI Agent is designed for those who need to search and summarize academic papers efficiently.

## Features

- **Paper AI**: Give it a topic, it will search articles using ArXiv, PubMed, and DuckDuckGo, then summarize the most relevant ones for you.
- **Code AI**: Provide instructions for coding or data analysis tasks (especially bioinformatics related). It breaks down the task, generates Python/Shell code, and executes it. (Note: Currently backend only, UI integration pending).
- **Chater**: A general conversational AI.

## Run it locally

1.  Install the required dependencies (including `eventlet` for WebSockets):
    ```bash
    pip install -r requirements.txt
    ```

2.  Set the environment variable `DEEPSEEK_API_KEY` to your DeepSeek API key, or modify the `API_KEY` variable in `app/config.py`.

    ```python
    # In app/config.py
    API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your API key here")
    ```

3.  Run the Flask-SocketIO application:
    ```bash
    python app/app.py
    ```
    The application now uses `eventlet` for handling WebSocket connections. Access the application at `http://127.0.0.1:8080` (or the configured host/port).

## Run it in Docker

1.  Clone the repository:
    ```bash
    git clone https://github.com/Vist233/Infinity_Bio-Agents.git
    cd Infinity_Bio-Agents
    ```
2.  Build and run the Docker container:
    ```bash
    # Make sure to set your API key, e.g., by editing app/config.py before building
    # Or pass it as an environment variable during run time if the app is configured to read it
    docker build -t infinite-agents .
    # The CMD in Dockerfile now runs `python app/app.py` which starts the SocketIO server
    docker run -p 8080:8080 -e DEEPSEEK_API_KEY="your_api_key_here" infinite-agents
    ```
    Access the application at `http://0.0.0.0:8080`.

## License

This project is licensed under the Apache-2.0 license.

