# How to Run the Application

This project is containerized using Docker to ensure a consistent environment for both frontend and backend services, along with the Inngest event system.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

## Quick Start (Windows)

We have provided a PowerShell script to automate the startup process.

1.  Open PowerShell in the project root directory.
2.  Run the start script:
    ```powershell
    .\docker-start.ps1
    ```
3.  Choose option **1** ("Build and start containers") for the first run, or option **2** ("Start existing containers") for subsequent runs.

## Manual Start (All Platforms)

If you prefer to run Docker commands manually or are on a non-Windows system:

1.  **Build and Start:**

    ```bash
    docker-compose up --build -d
    ```

2.  **Stop:**

    ```bash
    docker-compose down
    ```

3.  **View Logs:**
    ```bash
    docker-compose logs -f
    ```

## Accessing Services

Once the containers are running, you can access the services at:

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend:** [http://localhost:8000](http://localhost:8000)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Inngest Dashboard:** [http://localhost:8288](http://localhost:8288)

## Troubleshooting

- **Ports in use:** Ensure ports 3000, 8000, and 8288 are not being used by other applications.
- **Docker not running:** Make sure Docker Desktop is started.
- **Environment Variables:** The start script will automatically create a `.env` file from `.env.example` if it doesn't exist. You **must** edit this file with your actual API keys (OpenAI, Supabase, Twilio, etc.) for the application to work correctly.
