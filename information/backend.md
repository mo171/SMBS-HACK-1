# Backend Documentation

## 1. Architecture Overview

The backend is a service-oriented application built with **FastAPI**. It leverages **Inngest** for durable, event-driven workflow execution and **Supabase** for persistence.

### Core Tech Stack

- **Framework:** FastAPI (Python 3.11)
- **Event Engine:** Inngest (Serverless queue & orchestration)
- **Database:** Supabase (PostgreSQL)
- **AI/LLM:** LangChain + OpenAI (GPT-4o)

## 2. Directory Structure (`backend/app/`)

- **`app.py`**: Main entry point. Initializes FastAPI, CORS, and routes.
- **`agents/`**: Contains AI logic (e.g., `WorkflowArchitect`) that interprets natural language.
- **`workflows/`**: Core workflow engine logic (`engine.py`) and schema definitions (`schema.py`).
- **`integrations/`**: specific tool implementations (WhatsApp, Razorpay, etc.) and the `TOOL_REGISTRY`.
- **`services/`**: Business logic services (e.g., `intent_service`, `action_service`).
- **`routers/`**: API route definitions grouped by feature (e.g., `messages`, `dashboard`).

## 3. Core Business Endpoints

These are the most critical endpoints for the frontend to interact with.

### 1. `/intent-parser` (POST)

- **Purpose:** Converting Voice/Text -> Actionable Intent.
- **Input:** `audio_file` (Blob) or `text`, `session_id`.
- **Logic:**
  1.  Transcribes audio (Whisper).
  2.  Uses `intent_service` (GPT-4) to extract intent (e.g., `CREATE_INVOICE`) and entities.
  3.  Executes the action via `action_service`.
- **Output:** JSON with `status`, `reply`, and `analysis` (the extracted data).

### 2. `/workflow/draft` (POST)

- **Purpose:** Generates a workflow blueprint from a text prompt.
- **Input:** `prompt` (str), `user_id` (str).
- **Logic:** Calls `WorkflowArchitect` to generate a JSON graph of Nodes and Edges.
- **Output:** `workflow_id` of the created draft.

### 3. `/workflow/execute` (POST)

- **Purpose:** Manually triggers a workflow run.
- **Input:** `blueprint` (JSON), `payload` (JSON - trigger data).
- **Logic:** Pushes an event `workflow/run_requested` to Inngest.
- **Output:** `run_id` (used for live monitoring).

### 4. `/whatsapp` (POST)

- **Purpose:** Twilio Webhook for incoming WhatsApp messages.
- **Logic:** Acts similarly to `intent-parser` but specialized for text interactions and Twilio responses.

## 4. Key Logic & Agents

### Workflow Architect (`agents/architect.py`)

This agent is responsible for "drawing" the workflow.

- **Model:** `gpt-4o` with `structured_output`.
- **Function:** `draft_workflow(prompt)`
- **Logic:** usage of system prompts to map user intent (e.g., "Post to Instagram") to specific Service Nodes (`instagram`) and Tasks (`publish_post`). It also auto-generates variable references (e.g., `{{trigger_data.image_url}}`).

### Workflow Engine (`workflows/engine.py`)

This is the heart of the automation. It runs asynchronously via Inngest.

- **Trigger:** `workflow/run_requested`.
- **Execution Loop:**
  1.  Validates the Blueprints.
  2.  Iterates through nodes (Graph traversal).
  3.  **Router Logic:** Decides which path to take based on conditions.
  4.  **Action Logic:** Calls `perform_action()`, which looks up tools in `TOOL_REGISTRY`.
- **State Management:** Updates `workflow_logs` table in Supabase after EVERY step. This allows the frontend to show real-time progress.

## 5. Adding New Integrations

To add a new tool (e.g., "Slack"):

1.  **Create Tool File:** Create `backend/app/integrations/slack_tool.py`.
2.  **Inherit BaseTool:** Implement the `execute(task, params)` method.
3.  **Register:** Add it to `backend/app/integrations/__init__.py` in the `TOOL_REGISTRY` dict.
    ```python
    TOOL_REGISTRY = {
        # ...
        "slack": SlackTool(),
    }
    ```
4.  **Update Architect:** Update the system prompt in `agents/architect.py` ensuring the AI knows about the new "slack" service and its tasks.
