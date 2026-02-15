# Backend Developer Guide & Rules (STRICT)

**Role:** This document serves as the **Source of Truth** for any AI Agent or Developer working on the `SMBS-HACK-1` backend. You MUST follow these rules.

## 1. Environment & Setup (MANDATORY)

### Virtual Environment

- **Rule:** You MUST operate within the virtual environment.
- **Activation:**
  ```powershell
  # Windows (PowerShell)
  .\venv\Scripts\activate
  ```
- **Dependency Management:**
  - Install via `pip install <package>`.
  - **IMMEDIATELY** update `requirements.txt` after installing a new package: `pip freeze > requirements.txt`.

### Environment Variables

- **Source:** `.env` file (based on `.env.example`).
- **Access:** Use `os.getenv("KEY_NAME")`.
- **Rule:** NEVER hardcode API keys or secrets in the code.

## 2. Architecture & Core Files

The backend is built on **FastAPI** and uses **Inngest** for event-driven workflow orchestration.

### Key Files Map

| File Path             | Responsibility                                                                                                                    |
| :-------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| `app.py`              | **Entry Point**. Initializes `FastAPI` app, CORS, and defines API Routes. Keep logic minimal here; delegate to services.          |
| `workflows/engine.py` | **The Heart**. Contains `execute_workflow`. It traverses the JSON graph, executes nodes, and updates state. **Handle with care.** |
| `agents/architect.py` | **The Brain**. Uses LangChain + GPT-4o to converting natural language prompts into `WorkflowBlueprint` JSON.                      |
| `integrations/`       | **The Tools**. Contains `BaseTool` implementations (e.g., `whatsapp_tool.py`, `razorpay_tool.py`).                                |
| `services/`           | **Business Logic**. `intent_service.py` (Text/Voice processing), `action_service.py` (CRUD operations).                           |
| `lib/supabase.py`     | **Database**. Centralized Supabase client initialization.                                                                         |

## 3. Strict Coding Standards

### A. Async/Await

- **Rule:** All I/O operations (Database, HTTP requests, File access) **MUST** be `async`.
- **Pattern:**

  ```python
  # CORRECT
  async def fetch_data():
      response = await client.get(url)

  # WRONG
  def fetch_data():
      response = requests.get(url)
  ```

### B. Type Hinting

- **Rule:** All function signatures **MUST** have type hints for arguments and return values.
- **Reason:** Helps with static analysis and AI understanding.
  ```python
  async def process_item(item_id: str, count: int = 1) -> dict: ...
  ```

### C. Error Handling

- **Rule:** Use `try/except` blocks in Service/Integration layers to catch operational errors.
- **Rule:** In Router (`app.py`), catch errors and raise `fastapi.HTTPException`.
- **Logging:** Use `print(f"❌ [Module] ...")` for standardized logging visibility in the terminal.

## 4. Deep Dive: The Workflow Engine

The `workflows/engine.py` is the most critical component.

- **Event:** Triggered by `workflow/run_requested` via Inngest.
- **Loop:**
  1.  Loads `WorkflowBlueprint` (JSON with Nodes/Edges).
  2.  Finds the `Start` node.
  3.  Iterates: `Execute Node` -> `Update Logs` -> `Find Next Node` -> `Repeat`.
- **State:** Persists execution status to `workflow_logs` table in Supabase via `step_results` JSON column.
  - _Crucial:_ This `step_results` is what the Frontend monitors in real-time.

## 5. How-To: Extending the System

### Adding a New Integration (e.g., "Slack")

1.  **Create Tool File:** `backend/app/integrations/slack_tool.py`.
    - Class must inherit from `BaseTool` (or implement `execute` method).
    - Must handle specific `task` names (e.g., `send_message`).
2.  **Register Tool:** Update `backend/app/integrations/__init__.py`.
    - Add `from .slack_tool import SlackTool`.
    - Add `"slack": SlackTool()` to `TOOL_REGISTRY`.
3.  **Update Architect:** Modify `agents/architect.py`.
    - Update the system prompt to include "Slack" in the list of available tools and its capabilities.

### Adding an API Endpoint

1.  **Define Route:** In `app.py` (or a router file).
2.  **Request Model:** Create a Pydantic model for the request body if complex.
3.  **Logic:** Call a function in `services/`. **Do not write complex business logic inside the route handler.**

## 6. Common Commands

- **Start Backend:** `uvicorn app:app --reload`
- **Start Inngest:** `npx inngest-cli@latest dev`
