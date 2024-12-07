# Infinity Agents

An AI agent for excuting code and paper summary.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

Infinity Agents is an AI-based tool designed to excute the code in your local computer and search the paper. This repository contains multiple scripts and notebooks to assist in coding and analysis.

Actually this AI Agent is design for those don't how to coding and need to search a lot of paper.

## Features

- **Code Helper**:It will create a workspace in your computer. you could upload and download the files in your workspace. If you want to do something just tell it to the Code Helper, it will excute it in workspace automatically.
- **Paper AI**:Give it a topic, it will search 15 paper in pubmed and summary the most relative 5 paper for you.


## Run it locally

1. To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

2. set the enviroment YI_API_KEY as your YI api key or change the API_KEY varible in app/codeAI.py and app/paperAI.py

```
# Get the API key from environment variables OR set your API key here
API_KEY = os.environ.get("YI_API_KEY", "XXXXXXXXXXXXXXX Your Yi api goes here")
```

## Run it in Docker(Safer compared to locally)

To use the AI agent in web, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/Vist233/Infinity_Bio-Agents.git
    cd Infinity_Bio-Agents
    ```

2. To use the app, run:
    ```bash
    docker build -t iba .
    docker exc iba
    ```

look at your http://127.0.0.1:5000

## License

This project is licensed under the Apache-2.0 license.

