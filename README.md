# CloudForge

**A developer-first deployment automation and infrastructure orchestration platform.**

CloudForge aims to simplify application deployment by bringing source management, project detection, containerization, infrastructure provisioning, deployment orchestration and application management into one platform.

Instead of manually coordinating tools such as Git, Docker, Terraform and AWS, developers will be able to manage their deployment workflows through a unified web dashboard and CLI.

> **Development status:** CloudForge is actively under development. The frontend and backend foundations, database connectivity, health endpoints and responsive dashboard shell are implemented. Authentication, project management, Runner execution and automated cloud deployments are planned implementation stages. Dashboard preview data is illustrative and is not live AWS infrastructure data.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Current Technology Stack](#current-technology-stack)
3. [Repository Structure](#repository-structure)
4. [Prerequisites](#prerequisites)
5. [Database Setup](#database-setup)
6. [Clone the Repository](#clone-the-repository)
7. [Backend Setup](#backend-setup)
8. [Frontend Setup](#frontend-setup)
9. [Run CloudForge](#run-cloudforge)
10. [Verify the Installation](#verify-the-installation)
11. [Run Backend Tests](#run-backend-tests)
12. [Database Migrations](#database-migrations)
13. [Environment Variables](#environment-variables)
14. [Useful Development Commands](#useful-development-commands)
15. [Troubleshooting](#troubleshooting)
16. [Development Roadmap](#development-roadmap)
17. [Security Notes](#security-notes)
18. [Contribution Guidelines](#contribution-guidelines)

---

## Project Overview

CloudForge is designed around three primary interfaces:

- **Web Dashboard:** A centralized interface for project setup, deployment configuration, infrastructure review, deployment history, logs and monitoring.
- **CLI:** A terminal-based interface for developers who prefer command-line workflows.
- **Cloud Runner:** A separate execution service responsible for carrying out approved deployment operations in a controlled environment.

All interfaces will communicate with a shared Flask backend and deployment orchestration system.

### Planned deployment workflow

1. Connect a GitHub repository or provide a local project through the supported workflow.
2. Detect the application's language, framework, dependencies and runtime configuration.
3. Generate or validate Docker configuration.
4. Configure the AWS deployment target.
5. Generate Terraform infrastructure configuration and review the proposed plan.
6. Approve infrastructure changes.
7. Build and publish the Docker image to Amazon ECR.
8. Deploy the application to Amazon EC2.
9. Perform health checks and verify deployment success.
10. Inspect logs, resources, deployment history and application status.

CloudForge is an orchestration platform. It integrates established developer and cloud technologies rather than attempting to replace them.

---

## Current Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React, TypeScript, Vite | Web application |
| Styling | Tailwind CSS v4 | Responsive styling and design system |
| UI Components | shadcn/ui, Base UI | Reusable interface components |
| Icons | Lucide React | Icon system |
| Routing | React Router | Application navigation |
| Backend | Python, Flask | REST API and application services |
| Configuration | python-dotenv | Environment configuration |
| Validation | Pydantic | Typed data validation |
| ORM | SQLAlchemy | Database interaction |
| Migrations | Flask-Migrate, Alembic | Database schema migrations |
| Database | PostgreSQL | Persistent application data |
| PostgreSQL Driver | Psycopg | Python database connectivity |
| Testing | Pytest | Backend testing |

### Planned integrations

The following technologies will be introduced as their corresponding features are implemented:

- Docker Engine and Docker SDK
- Terraform Community Edition
- AWS SDK for Python (Boto3)
- Amazon EC2
- Amazon ECR
- AWS IAM
- Python Runner
- Typer and Rich for CLI development
- GitHub integration

Dependencies are introduced progressively rather than requiring developers to install the entire deployment toolchain immediately.

---

## Repository Structure

The repository is organized into independent application components.

```text
CloudForge/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── health.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── extensions.py
│   │
│   ├── migrations/
│   ├── tests/
│   │   └── test_app.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── cli/
├── docs/
├── infrastructure/
├── runner/
├── scripts/
├── tests/
│
├── .gitignore
├── .editorconfig
├── docker-compose.yml
└── README.md
```

**Note:** Some directories are reserved for upcoming implementation stages. Their presence does not mean all corresponding features are currently available.

---

## Prerequisites

Install the following software before setting up the current development version.

| Software | Requirement | Purpose |
|---|---|---|
| Git | Recent version | Clone and manage the repository |
| Python | 3.13.x recommended | Run the Flask backend |
| Node.js | 22.12 or newer | Run and build the frontend |
| npm | Included with Node.js | Install frontend dependencies |
| PostgreSQL database | Hosted Neon database | Persistent backend storage |
| Code editor | VS Code recommended | Development |

### Verify installations

Open PowerShell and run:

```powershell
git --version
python --version
node --version
npm --version
```

Make sure all commands return installed versions.

### Important: No local Docker installation required

The current development setup uses a hosted PostgreSQL database through Neon.

You do not need to install:

- Docker Desktop
- Local PostgreSQL Server
- pgAdmin
- Terraform
- AWS CLI

These tools will become relevant when their corresponding CloudForge features are implemented. Docker and Terraform execution will ultimately belong to CloudForge's controlled Runner environment, not to the developer's browser.

---

## Database Setup

CloudForge currently uses PostgreSQL hosted through [Neon](https://neon.com/).

A developer needs access to a PostgreSQL database because the backend uses SQLAlchemy and Flask-Migrate.

### Step 1: Create a Neon account

1. Visit [https://neon.com/](https://neon.com/).
2. Create an account or sign in.
3. Create a PostgreSQL project.
4. Choose a project name and database region.
5. Open the project's connection details.

### Step 2: Obtain the connection string

Copy the PostgreSQL connection string provided by Neon.

It should follow this general structure:

```text
postgresql://USERNAME:PASSWORD@HOST/DATABASE?sslmode=require
```

CloudForge uses the Psycopg SQLAlchemy driver, so the connection string in the backend environment must use this form:

```text
postgresql+psycopg://USERNAME:PASSWORD@HOST/DATABASE?sslmode=require
```

Replace the placeholders with your actual Neon connection details.

**Important:** Never publish your database password or connection string in GitHub, screenshots, issues or public documentation.

---

## Clone the Repository

Open PowerShell and navigate to the directory where you want to keep the project.

```powershell
git clone https://github.com/Ankit-K-Singh-0527/CloudForge.git
```

Enter the repository:

```powershell
cd CloudForge
```

Switch to the development branch:

```powershell
git switch develop
```

The `develop` branch contains the integrated development work.

---

## Backend Setup

The backend is built with Python and Flask.

### Step 1: Navigate to the backend directory

```powershell
cd backend
```

### Step 2: Create a virtual environment

```powershell
python -m venv .venv
```

A virtual environment isolates CloudForge's Python dependencies from other Python projects on your machine.

### Step 3: Activate the virtual environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, your terminal should show:

```text
(.venv)
```

If PowerShell blocks script execution, you can activate the environment using Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

### Step 4: Install Python dependencies

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the backend dependencies:

```powershell
python -m pip install -r requirements.txt
```

This installs the packages listed in `requirements.txt`, including Flask, SQLAlchemy, Flask-Migrate, Psycopg, Pydantic, python-dotenv and Pytest.

### Step 5: Configure environment variables

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Open the `.env` file in your editor:

```powershell
code .env
```

Configure the required values:

```env
SECRET_KEY=replace-with-a-secure-random-secret
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST/DATABASE?sslmode=require
```

Generate a secure secret key using Python:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the generated value into `SECRET_KEY`.

Replace the database URL with your actual Neon connection string.

**Do not commit `.env` to Git.** It contains private credentials.

### Step 6: Start the backend

Make sure your virtual environment is active and your current directory is:

```text
CloudForge/backend
```

Run:

```powershell
python run.py
```

The Flask backend should start at:

```text
http://127.0.0.1:5000
```

---

## Frontend Setup

The frontend uses React, TypeScript, Vite and Tailwind CSS.

Open a second PowerShell terminal.

### Step 1: Navigate to the frontend directory

From the repository root:

```powershell
cd frontend
```

### Step 2: Install frontend dependencies

```powershell
npm ci
```

This installs the exact dependency versions recorded in `package-lock.json`, providing a more reproducible setup than installing packages individually.

### Step 3: Start the development server

```powershell
npm run dev
```

Vite will display a local development URL, normally:

```text
http://localhost:5173
```

Open the displayed URL in your browser.

---

## Run CloudForge

You should now have two running development servers.

| Component | Command | Default URL |
|---|---|---|
| Flask backend | `python run.py` | http://127.0.0.1:5000 |
| React frontend | `npm run dev` | http://localhost:5173 |

Keep both terminals running while developing.

The frontend and backend are started independently. The frontend currently provides the dashboard shell and interface foundation; full authentication and deployment workflows will be integrated in subsequent development stages.

To stop either development server, press:

```text
Ctrl + C
```

---

## Verify the Installation

CloudForge provides health endpoints to verify that the backend is running and that the database is reachable.

### 1. Check backend health

Open a browser or use PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/v1/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "CloudForge API",
  "message": "Backend is running successfully"
}
```

### 2. Check database connectivity

Run:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/v1/health/ready
```

Expected response:

```json
{
  "status": "ready",
  "database": "connected",
  "service": "CloudForge API"
}
```

### 3. Verify the frontend

Open:

```text
http://localhost:5173
```

You should see the CloudForge dashboard interface.

The responsive sidebar, navigation, header and theme switching are part of the current frontend foundation.

---

## Run Backend Tests

CloudForge uses Pytest for backend testing.

Open a PowerShell terminal and navigate to the backend directory:

```powershell
cd CloudForge/backend
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the test suite:

```powershell
python -m pytest -v
```

The current backend foundation includes tests for:

- Development configuration
- Testing configuration
- Production secret validation
- Invalid configuration handling
- Backend health endpoint
- Database readiness endpoint

All tests should pass before you begin making changes.

---

## Database Migrations

CloudForge uses Flask-Migrate and Alembic to manage database schema changes.

The migration repository is initialized.

When application models are introduced, migrations can be generated and applied from the backend directory.

Generate a migration:

```powershell
flask --app run.py db migrate -m "describe schema changes"
```

Apply migrations:

```powershell
flask --app run.py db upgrade
```

Check whether models contain ungenerated schema changes:

```powershell
flask --app run.py db check
```

**Note:** The initial backend foundation does not yet contain the complete user, workspace, membership and project schema. The first application schema migration will be created as those models are implemented.

Never manually modify a production database schema without creating and reviewing the corresponding migration.

---

## Environment Variables

CloudForge keeps environment-specific configuration outside the source code.

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask application secret |
| `DATABASE_URL` | PostgreSQL connection string |

### Environment file locations

```text
CloudForge/
└── backend/
    ├── .env.example
    ├── .env
    └── run.py
```

`.env.example` is the shareable configuration template.

`.env` contains the developer's actual local credentials and must remain private.

---

## Useful Development Commands

### Backend

Run from `CloudForge/backend`.

| Command | Purpose |
|---|---|
| `python run.py` | Start Flask development server |
| `python -m pytest -v` | Run backend tests |
| `python -m pip list` | Display installed Python packages |
| `python -m pip freeze` | Display installed package versions |
| `flask --app run.py db check` | Check for ungenerated migrations |
| `flask --app run.py db migrate -m "message"` | Generate migration |
| `flask --app run.py db upgrade` | Apply migrations |

### Frontend

Run from `CloudForge/frontend`.

| Command | Purpose |
|---|---|
| `npm ci` | Install locked dependencies |
| `npm run dev` | Start development server |
| `npm run build` | Type-check and create production build |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript checks |
| `npm run format` | Format source files |
| `npm run format:check` | Check formatting without modifying files |
| `npm run preview` | Preview the production build |

---

## Troubleshooting

### 1. Python is not recognized

Verify that Python is installed:

```powershell
python --version
```

If the command is unavailable, install Python and ensure it is added to the system PATH.

### 2. Virtual environment activation fails

Run:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### 3. ModuleNotFoundError

Make sure the virtual environment is activated and install dependencies:

```powershell
python -m pip install -r requirements.txt
```

For backend tests, run the command from `CloudForge/backend`:

```powershell
python -m pytest -v
```

### 4. Database connection fails

Check the following:

- Neon database is available.
- The connection string is correct.
- The URL uses `postgresql+psycopg://`.
- The connection string includes the required SSL configuration.
- Your `.env` file is located inside the backend directory.
- Your database credentials have not expired or changed.

Restart the Flask server after changing `.env`.

### 5. Frontend dependencies fail to install

Verify Node.js and npm:

```powershell
node --version
npm --version
```

Then run:

```powershell
npm ci
```

### 6. Port already in use

If port `5000` or `5173` is already occupied, stop the other process using it or configure an available development port.

### 7. Database migration reports no changes

This can be expected before application models are created. A migration is generated only when there are schema changes to apply.

---

## Development Roadmap

CloudForge is being developed in progressive stages.

| Stage | Focus | Status |
|---|---|---|
| Day 1 | Repository, frontend and backend foundations | Completed |
| Day 2 | Authentication, authorization and database models | Next |
| Day 3 | Project management and GitHub integration | Planned |
| Day 4 | Project detection and configuration | Planned |
| Day 5 | Dockerfile generation and image builds | Planned |
| Day 6 | AWS credentials and Amazon ECR | Planned |
| Day 7 | Terraform generation and plan approval | Planned |
| Day 8 | AWS provisioning and EC2 bootstrap | Planned |
| Day 9 | Runner job system and execution safety | Planned |
| Day 10 | End-to-end application deployment | Planned |
| Day 11 | Health checks, logs and deployment history | Planned |
| Day 12 | Rollback and resource lifecycle | Planned |
| Day 13 | CLI and configuration management | Planned |
| Day 14 | Monitoring and infrastructure visualization | Planned |
| Day 15 | Security, automated testing and CI | Planned |
| Day 16 | Documentation, final integration and demonstration | Planned |

The roadmap describes intended implementation work, not a claim that those capabilities are already available.

---

## Security Notes

Security is a core engineering requirement for CloudForge.

- Never commit `.env` files or credentials.
- Never expose database connection strings or secret keys.
- Use least-privilege access for cloud integrations.
- Validate all API input.
- Protect project and workspace data with backend authorization.
- Redact sensitive values from logs.
- Require explicit approval for destructive infrastructure operations.
- Execute deployment jobs through predefined, validated Runner handlers rather than arbitrary shell commands.

---

## Contribution Guidelines

CloudForge follows a feature-branch development workflow.

Start by updating your local development branch:

```powershell
git switch develop
git pull origin develop
```

Create a feature branch:

```powershell
git switch -c feature/your-feature-name
```

After implementation, run relevant tests and quality checks.

Stage and commit your changes:

```powershell
git add .
git commit -m "feat: describe your changes"
```

Push the feature branch:

```powershell
git push -u origin feature/your-feature-name
```

After verification, merge the feature into `develop` and push the updated development branch.

Keep changes focused, tested and documented. Do not commit secrets, generated environment files, database credentials or temporary build artifacts.

---

## Project Vision

CloudForge aims to make application deployment more accessible, predictable and manageable.

The long-term goal is to provide a unified developer experience in which developers can focus on writing software while CloudForge coordinates the infrastructure and deployment workflow behind it.

**Build. Provision. Deploy. Manage.**

---

**CloudForge — Infrastructure, orchestrated.**