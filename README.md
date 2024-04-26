# RAG and Temporal

This project demonstrates how to run a RAG (Retrieval-Augmented Generation) based workflow using Temporal.

## Prerequisites

- Python 3.x
- Temporal Server

## Setup

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

3. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

4. Export your OpenAI key:

    ```bash
    export OPENAI_API_KEY=<your-key>
    ```

## Running the Application

1. Start the Temporal server:

   ```bash
   temporal server start-dev
   ```

2. Start the worker:

   ```bash
   python worker.py
   ```

3. Start the client server:

   ```bash
   python server.py
   ```

## Usage

To send a request to the RAG workflow, use the following command:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"question": "Who lives in Berlin?"}' http://localhost:8000/query
```

Replace `"Who lives in Berlin?"` with your desired question.

## Terminating the Workflow

To terminate a running workflow, use the following command:

```bash
temporal workflow terminate --workflow-id <workflow-id>
```

Replace `<workflow-id>` with the ID of the workflow you want to terminate.