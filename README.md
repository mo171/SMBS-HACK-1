# SMBS-HACK-1

## 1. Setup

### Docker

For detailed instructions on how to run the application using Docker, please refer to [information/RUN_INSTRUCTIONS.md](information/RUN_INSTRUCTIONS.md).

### Webhooks (Ngrok)

To enable external services (like WhatsApp, Razorpay) to communicate with your local backend, you need to expose your local server.

1.  Install [ngrok](https://ngrok.com/).
2.  Run ngrok on port 8000:
    ```bash
    ngrok http 8000
    ```
3.  Update your webhook URLs in the respective service dashboards (e.g., Twilio, Razorpay) with the generated ngrok URL (e.g., `https://your-ngrok-url.ngrok-free.app`).

### Database Setup

1.  Go to your Supabase project dashboard's **SQL Editor**.
2.  Open `backend/app/db.sql` in your local editor.
3.  Copy the entire content and paste it into the Supabase SQL Editor.
4.  Run the query to create all necessary tables and relationships.

### Environment Variables

Ensure you have the following `.env` files configured with your credentials.

#### Backend (`backend/app/.env`)

Create this file based on `.env.example`.

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://...
SUPABASE_KEY=... # Service Role Key
SUPABASE_ANON_KEY=...

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# Inngest
INNGEST_EVENT_KEY=local
INNGEST_SIGNING_KEY=local
```

#### Frontend (`frontend/my-app/.env.local`)

Create this file if it doesn't exist.

```bash
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 2. Core Idea

**SMBS-HACK-1** is an intelligent workflow automation platform designed to streamline business processes through visual orchestration and AI agents. It empowers users to build, manage, and monitor complex automation flows that connect disjointed services into cohesive systems.

### Core Features

- **Visual Workflow Builder**: An intuitive, node-based drag-and-drop interface (powered by React Flow) to design automation logic without coding.
- **AI Agents**: Flexible AI nodes capable of performing tasks, making decisions, and generating content using LLMs.
- **Multi-Platform Chat**: A unified interface to manage and respond to customer conversations from platforms like WhatsApp and Instagram.
- **Human-in-the-Loop**: Integrated approval workflows that allow human intervention and review before critical actions (like posting content) are executed.
- **Comprehensive Integrations**: Seamless connectivity with major third-party services include Google Sheets, Razorpay, WhatsApp, Bluesky, and social media platforms.

## 3. Tech Stack

### Frontend

- **Framework**: [Next.js 16](https://nextjs.org/) (React)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand)
- **Styling**: [TailwindCSS](https://tailwindcss.com/) & [Shadcn UI](https://ui.shadcn.com/)
- **Visualization**: [React Flow](https://reactflow.dev/)
- **HTTP Client**: Axios

### Backend

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Event Orchestration**: [Inngest](https://www.inngest.com/)
- **AI Orchestration**: [LangChain](https://www.langchain.com/)
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL)

### Infrastructure

- **Containerization**: Docker
- **Tunneling**: Ngrok

## 4. Know More

For deeper dives into the architecture and implementation details:

- [Frontend Documentation](information/frontend.md)
- [Backend Documentation](information/backend.md)
- [Database Documentation](information/db.md)
