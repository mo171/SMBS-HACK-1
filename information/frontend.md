# Frontend Documentation

## 1. Overview

The frontend is a modern **Next.js 16** application that serves as the interface for building workflows, managing agents, and monitoring executions.

### Core Tech Stack

- **Framework:** Next.js 16 (App Router)
- **State Management:** Zustand
- **Visualization:** React Flow (for Workflow Builder)
- **UI Library:** TailwindCSS + Shadcn UI + Lucide React
- **API Client:** Axios (moving away from fetch)

## 2. Directory Structure (`frontend/my-app/src`)

- **`app/`**: Next.js App Router pages (routes).
- **`components/`**: Reusable UI components.
  - **`workflow/`**: Specific components for the drag-and-drop builder.
  - **`ui/`**: Primitives (buttons, inputs, dialogs).
- **`store/`**: Global state stores (Zustand).
  - **`workflowStore.js`**: Critical store for managing the graph state.
- **`lib/`**: Utilities (Supabase client, API helpers).

## 3. Workflow Builder

The Workflow Builder is the most complex part of the frontend. It allows users to visually construct automation logic.

### Core Components (`components/workflow/`)

1.  **`WorkflowCanvas.jsx`**: The main stage.
    - Wraps `ReactFlow` provider.
    - Handles drag-and-drop, zooming, and panning.
    - **Modes:** Toggles between `Edit Mode` (building) and `Monitor Mode` (live viewing).
    - **Execution:** Contains the `handleExecuteWorkflow` function which POSTs the blueprint to the backend.

2.  **`WorkflowNode.jsx`**: Custom Node Renderer.
    - Displays the node UI based on `node.data.service` (e.g., WhatsApp = Green, ICONS).
    - Shows dynamic progress bars and status indicators during `Monitor Mode`.

3.  **`Sidebar.jsx`** (or `WorkflowSidebar.jsx`):
    - The "Palette" of available tools.
    - Draggable items that users drop onto the canvas.
    - Also contains the **AI Input** field to call the backend `/workflow/draft` endpoint.

4.  **`NodeConfigPanel.jsx`**:
    - Slide-out panel when a node is clicked.
    - Allows editing specific `params` (e.g., Template ID for WhatsApp, SQL query for Database).
    - Updates `workflowStore` immediately on change.

## 4. State Management (`store/workflowStore.js`)

We use **Zustand** to manage the complex graph state outside of the React render cycle where possible for performance.

### Key Actions

- `setNodes`, `setEdges`: Updates the graph structure.
- `workflowMeta`: Stores global settings like `loop_seconds`.
- `initLiveMonitor(runId)`: **Crucial Function.**
  - Connects to Supabase Realtime for the `workflow_logs` table.
  - Subscribes to updates where `run_id` matches.
  - Updates `nodeStates` in real-time, causing the Canvas to re-render nodes with "Running", "Completed", or "Failed" statuses.

## 5. Integrations & API

- **Base URL:** `process.env.NEXT_PUBLIC_API_URL` (usually http://localhost:8000).
- **Supabase:** `process.env.NEXT_PUBLIC_SUPABASE_URL`.
- **Authentication:** Handled via Supabase Auth (if implemented) or anonymous for now.

## 6. How to Add a New UI Node

1.  **Update `WorkflowNode.jsx`**: Add the icon and color config to `NODE_CONFIG`.
2.  **Update `Sidebar.jsx`**: Add a draggable item for the new tool.
3.  **Update `NodeConfigPanel.jsx`**: Add a form section for the new tool's specific parameters.
