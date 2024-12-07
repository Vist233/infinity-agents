# Infinity Bio-Agents

An AI agent for bioinformatics to deal with various bio-problems.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

Infinity Bio-Agents is an AI-based tool designed to address various bioinformatics problems. This repository contains multiple scripts and notebooks to assist in bioinformatics research and analysis.

## Features

- **Python**: Core functionalities and algorithms.
- **Jupyter Notebook**: Interactive data analysis and visualization.
- **Perl**: Additional bioinformatics utilities.
- **Java**: Supplementary tools.
- **HTML**: Visualization and reporting.

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

## Usage

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

