# Docker Architecture Overview

## 📊 Container Architecture

```mermaid
graph TB
    subgraph "Docker Container: smbs-hack-1"
        subgraph "Frontend Service"
            A[Next.js App<br/>Port 3000]
        end

        subgraph "Backend Service"
            B[FastAPI App<br/>Port 8000]
        end

        C[Entrypoint Script<br/>docker-entrypoint.sh]
        C -->|Starts| A
        C -->|Starts| B
    end

    D[Host Machine<br/>localhost:3000] -->|HTTP| A
    E[Host Machine<br/>localhost:8000] -->|HTTP| B

    A -->|API Calls| B

    subgraph "External Services"
        F[Supabase Database]
        G[OpenAI API]
        H[Twilio WhatsApp]
    end

    B -->|Database Queries| F
    B -->|AI Processing| G
    B -->|WhatsApp Messages| H

    style A fill:#61dafb,stroke:#333,stroke-width:2px
    style B fill:#009688,stroke:#333,stroke-width:2px
    style C fill:#ffa726,stroke:#333,stroke-width:2px
```

## 🏗️ Build Process

```mermaid
graph LR
    subgraph "Stage 1: Frontend Builder"
        A1[Node.js 20 Alpine] --> A2[Install Dependencies]
        A2 --> A3[Build Next.js]
        A3 --> A4[Production Build]
    end

    subgraph "Stage 2: Backend Builder"
        B1[Python 3.11 Slim] --> B2[Install System Deps]
        B2 --> B3[Install Python Packages]
        B3 --> B4[Compiled Dependencies]
    end

    subgraph "Stage 3: Final Image"
        C1[Python 3.11 Slim] --> C2[Install Node.js]
        C2 --> C3[Copy Backend Code]
        C3 --> C4[Copy Frontend Build]
        A4 -.->|Copy| C4
        B4 -.->|Copy| C3
        C4 --> C5[Add Entrypoint]
        C5 --> C6[Final Container Image]
    end

    style A4 fill:#61dafb,stroke:#333,stroke-width:2px
    style B4 fill:#009688,stroke:#333,stroke-width:2px
    style C6 fill:#4caf50,stroke:#333,stroke-width:2px
```

## 🔄 Runtime Flow

```mermaid
sequenceDiagram
    participant User
    participant Docker
    participant Entrypoint
    participant Frontend
    participant Backend
    participant External

    User->>Docker: docker-compose up
    Docker->>Entrypoint: Start container
    Entrypoint->>Backend: uvicorn app:app --port 8000 &
    Entrypoint->>Frontend: npm start --port 3000 &

    Note over Frontend,Backend: Both services running

    User->>Frontend: Visit localhost:3000
    Frontend->>User: Serve React UI

    User->>Frontend: User interaction
    Frontend->>Backend: API call to localhost:8000
    Backend->>External: Query Supabase/OpenAI
    External->>Backend: Return data
    Backend->>Frontend: JSON response
    Frontend->>User: Update UI
```

## 📦 File Structure in Container

```
/app/
├── backend/
│   └── app/
│       ├── app.py
│       ├── services/
│       ├── integrations/
│       ├── workflows/
│       └── .env
├── frontend/
│   ├── .next/              (built files)
│   ├── public/
│   ├── node_modules/
│   └── package.json
└── docker-entrypoint.sh
```

## 🌐 Network Flow

```mermaid
graph LR
    subgraph "Host Machine"
        A[Browser]
    end

    subgraph "Docker Container"
        B[Port 3000<br/>Frontend]
        C[Port 8000<br/>Backend]
    end

    subgraph "Internet"
        D[Supabase]
        E[OpenAI]
        F[Twilio]
    end

    A -->|localhost:3000| B
    A -->|localhost:8000/docs| C
    B -->|Internal| C
    C -->|HTTPS| D
    C -->|HTTPS| E
    C -->|HTTPS| F

    style B fill:#61dafb
    style C fill:#009688
```

## 🔐 Environment Variables Flow

```mermaid
graph TB
    A[.env file on host] -->|Mounted| B[Container]
    C[docker-compose.yml] -->|Defines| D[Environment Variables]
    D -->|Injected into| B

    B -->|Used by| E[Backend App]
    B -->|Used by| F[Frontend App]

    E -->|Connects to| G[External Services]

    style A fill:#ffa726
    style D fill:#ffa726
```

## 🚀 Deployment Options

```mermaid
graph TB
    A[Single Container<br/>Current Setup] -->|Good for| B[Development<br/>Small Projects]

    C[Multi-Container<br/>Recommended for Production] -->|Separates| D[Frontend Container]
    C -->|Separates| E[Backend Container]
    C -->|Adds| F[Nginx Reverse Proxy]
    C -->|Adds| G[Redis Cache]

    D -->|Scales| H[Multiple Frontend Instances]
    E -->|Scales| I[Multiple Backend Instances]

    style A fill:#4caf50
    style C fill:#2196f3
```

## 📈 Scaling Strategy

For production, consider this architecture:

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx/Traefik]
    end

    subgraph "Frontend Tier"
        F1[Frontend 1]
        F2[Frontend 2]
        F3[Frontend 3]
    end

    subgraph "Backend Tier"
        B1[Backend 1]
        B2[Backend 2]
        B3[Backend 3]
    end

    subgraph "Data Tier"
        DB[(Supabase)]
        CACHE[(Redis)]
    end

    LB -->|Route| F1
    LB -->|Route| F2
    LB -->|Route| F3

    F1 -->|API| B1
    F2 -->|API| B2
    F3 -->|API| B3

    B1 --> DB
    B2 --> DB
    B3 --> DB

    B1 --> CACHE
    B2 --> CACHE
    B3 --> CACHE
```
