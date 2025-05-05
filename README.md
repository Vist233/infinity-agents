# Infinity Agents

An AI agent platform featuring paper searching/summarization and a trait recognition tool, with real-time streaming responses via WebSockets. Built using `agno` and Flask.

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

Infinity Agents is an AI-based tool designed to assist with research and specific image analysis tasks. It combines conversational AI agents with a specialized tool for generating image classification programs.

## Features

- **Paper AI**: Give it a topic, it will search articles using ArXiv, PubMed, and DuckDuckGo, then summarize the most relevant ones for you. (Access via main chat interface)
- **Chater**: A general conversational AI, optionally enhanced with Retrieval-Augmented Generation (RAG) using uploaded documents. (Access via main chat interface)
- **Trait Recognizer**:
    - **Standard Generator**: Upload a 'standard' image defining classification criteria. The tool uses a Vision Language Model (VLM) to understand the criteria and generates a standalone `.exe` program. This `.exe` can then be run locally to classify other images based on the provided standard, outputting results to a `results.csv` file.
    - **Pre-built Programs**: Download `.exe` programs previously generated for common tasks (e.g., cabbage classification from `fixedQuantityProg`).
    - Access this tool via the `/trait_recognizer` URL (e.g., `http://127.0.0.1:8080/trait_recognizer`).

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Vist233/Infinity_Bio-Agents.git
    cd Infinity_Bio-Agents
    ```
2.  Install the required dependencies (including `eventlet` for WebSockets and `pyinstaller` for the Trait Recognizer):
    ```bash
    pip install -r requirements.txt
    ```
3.  **API Keys:**
    *   **Chat Agents:** Set the environment variable `DEEPSEEK_API_KEY` or modify `app/config.py`.
    *   **Trait Recognizer:** Set the environment variable `DASHSCOPE_API_KEY` or modify the `TRAIT_API_KEY` variable in `app/app.py`. This currently defaults to an Aliyun Dashscope key. Ensure the key corresponds to a model with vision capabilities (like Qwen-VL).

## Usage

1.  Run the Flask-SocketIO application:
    ```bash
    python app/app.py
    ```
    The application uses `eventlet` for handling WebSocket connections.

2.  **Access Interfaces:**
    *   **Chat Agents:** Open your browser to `http://127.0.0.1:8080` or `http://127.0.0.1:8080/chat`.
    *   **Trait Recognizer:** Open your browser to `http://127.0.0.1:8080/trait_recognizer`.

## Run it locally

(Instructions remain largely the same, just ensure API keys are set as described in Installation)

1.  Install dependencies: `pip install -r requirements.txt`
2.  Set API keys (see Installation).
3.  Run the app: `python app/app.py`
4.  Access at `http://127.0.0.1:8080` (for chat) or `http://127.0.0.1:8080/trait_recognizer` (for trait tool).

## Run it in Docker

(Note: Running the Trait Recognizer's `.exe` generation *within* Docker requires `pyinstaller` and its dependencies inside the container. The generated `.exe` will be for the container's OS (Linux), not necessarily for Windows unless using specific cross-compilation techniques which are complex.)

1.  Clone the repository.
2.  Build the Docker image:
    ```bash
    # Ensure API keys are handled (e.g., passed as build args or runtime env vars)
    docker build -t infinite-agents .
    ```
3.  Run the container:
    ```bash
    # Pass API keys as environment variables
    docker run -p 8080:8080 \
      -e DEEPSEEK_API_KEY="your_deepseek_key" \
      -e DASHSCOPE_API_KEY="your_dashscope_key" \
      infinite-agents
    ```
4.  Access the application interfaces at `http://localhost:8080/chat` and `http://localhost:8080/trait_recognizer`.

## Testing

This project uses `pytest` for unit testing.

1.  Ensure you have installed the development dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the tests from the root directory:
    ```bash
    pytest tests/
    ```
Tests are automatically run via GitHub Actions on pushes and pull requests to the `main` branch (see `.github/workflows/ci.yml`).

## License

This project is licensed under the Apache-2.0 license.

