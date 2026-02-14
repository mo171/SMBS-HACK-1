# Frontend Developer Guide & Rules (STRICT)

**Role:** This document serves as the **Source of Truth** for any AI Agent or Developer working on the `SMBS-HACK-1` frontend. You MUST follow these rules.

## 1. Environment & Tech Stack (MANDATORY)

- **Framework:** **Next.js 16** (App Router).
  - **Rule:** Use `src/app` directory structure.
  - **Rule:** Explicitly use `"use client";` at the top of components that use hooks (`useState`, `useEffect`, etc.).
- **Language:** JavaScript (ES6+).
- **Styling:** **TailwindCSS** + **Shadcn UI**.
  - **Rule:** Use `className` with Tailwind utility classes.
  - **Rule:** Use `cn()` utility for conditional class merging.
  - **Forbidden:** Do NOT use CSS Modules or `style={{}}` (unless for dynamic coordinate values).
- **Icons:** `lucide-react`.

## 2. Architecture & Core Concepts

### Directory Structure (`src/`)

| Directory              | Responsibility                                                                                         |
| :--------------------- | :----------------------------------------------------------------------------------------------------- |
| `app/`                 | **Routes**. `page.js`, `layout.js` define the URL structure.                                           |
| `components/`          | **UI**. Reusable components.                                                                           |
| `components/workflow/` | **Workflow Builder**. Specific components (`WorkflowCanvas`, `WorkflowNode`) for the drag-drop editor. |
| `store/`               | **State**. global Zustand stores (`workflowStore.js`, `authStore.js`).                                 |
| `lib/`                 | **Utils**. API clients (`axios`), Supabase client.                                                     |

### State Management (Zustand)

- **Pattern:** We use **Zustand** for global state, especially for the Workflow Graph.
- **Store:** `useWorkflowStore.js` holds `nodes`, `edges`, and `monitoring` state.
- **Rule:** Do not prop-drill complex state. Use the store hook: `const { nodes, setNodes } = useWorkflowStore()`.

## 3. Strict Coding Standards

### A. Component Pattern

- **Functional Components:** Use `const Component = () => {}` or `export default function Component() {}`.
- **Props:** Destructure props in the function signature.
- **Hooks:** Keep hooks at the top level.

### B. API Interaction

- **Library:** **Axios**.
- **Rule:** Do NOT use native `fetch` unless absolutely necessary (e.g., streaming).
- **Base URL:** Use `process.env.NEXT_PUBLIC_API_URL`.
- **Pattern:**

  ```javascript
  import axios from "axios";

  const fetchData = async () => {
    try {
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/endpoint`,
        data,
      );
      return res.data;
    } catch (error) {
      console.error("❌ Error:", error);
    }
  };
  ```

### C. The Workflow Builder (React Flow)

- **Library:** `@xyflow/react` (New React Flow).
- **Key Components:**
  - `WorkflowCanvas.jsx`: Wraps the `ReactFlow` provider. Handles the "Edit Mode" vs "Monitor Mode" toggle.
  - `WorkflowNode.jsx`: Custom node renderer. MUST handle `data.service` to display correct icons/colors.
- **Real-time Monitoring:**
  - The `initLiveMonitor(runId)` action in `workflowStore.js` subscribes to Supabase Realtime.
  - It updates `nodeStates` which `WorkflowNode` listens to.

## 4. How-To: Common Tasks

### A. Add a New UI Node Type

1.  **Component:** Update `WorkflowNode.jsx`. Add the service key to `NODE_CONFIG` with icon and color.
2.  **Sidebar:** Update `Sidebar.jsx`. Add a draggable item with `onDragStart`.
3.  **Config Panel:** Update `NodeConfigPanel.jsx`. Add input fields for specific parameters (e.g., "Slack Channel ID").

### B. Add a New Page

1.  **File:** Create `src/app/new-page/page.jsx`.
2.  **Layout:** Ensure it uses the shared layout if needed.
3.  **Link:** Add to the Sidebar navigation.

## 5. Common Commands

- **Run Backend First:** Ensure FastAPI is running on port 8000.
- **Run Frontend:** `pnpm run dev` (Port 3000).
