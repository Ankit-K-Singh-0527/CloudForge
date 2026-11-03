
# CloudForge

**Developer-first deployment automation and infrastructure orchestration platform.**

CloudForge simplifies application deployment by orchestrating established DevOps tools through a unified web dashboard and command-line interface.

## Overview

CloudForge connects source-code management, containerization,
infrastructure provisioning and cloud deployment into one
coordinated workflow.

Developers can provide a local project or GitHub repository,
configure their deployment, review infrastructure changes,
and manage the application through CloudForge.

## Core Capabilities

- GitHub repository and local project integration
- Automatic language and framework detection
- Dockerfile generation and validation
- Docker image building and registry publishing
- Terraform-based infrastructure provisioning
- AWS EC2 and ECR integration
- Automated deployment orchestration
- Deployment logs and health verification
- Deployment history and rollback
- Web dashboard and CLI
- Secure execution through CloudForge Runner

## Technology Stack

### Frontend
- React
- TypeScript
- Tailwind CSS
- Vite

### Backend
- Python
- Flask
- SQLAlchemy

### Database
- PostgreSQL

### DevOps and Cloud
- Docker
- Terraform
- AWS
- Boto3
- Git and GitHub API

### Developer Tools
- Typer
- Rich
- Pytest
- Playwright

## Architecture

CloudForge consists of four major application components:

1. Web Dashboard
2. Flask Backend
3. CloudForge Runner
4. CloudForge CLI

These components communicate through a shared backend API
and deployment orchestration system.

## Project Status

Under active development.

## Supported Deployment Targets

Initial target:
- AWS EC2
- Amazon ECR

Initial application support:
- Python / Flask
- Node.js

## Security

CloudForge is designed around secure credential handling,
controlled Runner execution, deployment approvals,
and infrastructure lifecycle protection.

## Development

Setup and development instructions will be added as
the implementation progresses.

## License

To be decided.
