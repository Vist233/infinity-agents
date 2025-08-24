# Infinity Agents

An AI agent platform featuring paper searching/summarization with real-time streaming responses via WebSockets. Built using `agno` and Flask.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Run it locally](#run-it-locally)
- [Run it in Docker](#run-it-in-docker)
- [Testing](#testing)
- [License](#license)

## Introduction

Infinity Agents is an AI-based tool designed to assist with research tasks. It combines conversational AI agents for research assistance.

## Features

- **Paper AI**: Give it a topic, it will search articles using ArXiv, PubMed, and DuckDuckGo, then summarize the most relevant ones for you. (Access via main chat interface)
- **Chater**: A general conversational AI, optionally enhanced with Retrieval-Augmented Generation (RAG) using uploaded documents. (Access via main chat interface)

## Quick Start

1.  **Clone & Install:**
    ```bash
    git clone https://github.com/Vist233/Infinity_Agents.git
    cd Infinity_Agents
    pip install -r requirements.txt
    ```

2.  **Set API Key:**
    ```bash
    # Set environment variable
    export DEEPSEEK_API_KEY="your_api_key_here"
    
    # Or modify app/agents.py line 8
    ```

3.  **Run:**
    ```bash
    python app/app.py
    ```

## Usage

After starting the server, access:

- **Chat Interface**: `http://127.0.0.1:8080/chat`

### Features

- **PaperAI**: Research assistant that searches academic papers
- **Chater**: General conversational AI assistant

## Docker Deployment

```bash
# Build image
docker build -t infinite-agents .

# Run container
docker run -p 8080:8080 -e DEEPSEEK_API_KEY="your_key" infinite-agents
```

Access at: `http://localhost:8080/chat`

## Testing

Run tests with:
```bash
pytest tests/
```

## License

This project is licensed under the Apache-2.0 license.

