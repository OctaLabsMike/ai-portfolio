# AI Portfolio – Michał Przygórski

Practical AI tools and business process automation: Claude skills and n8n workflows.
All examples use fictional data (a made-up company, clients and rate card).

## Contents
- `n8n/` – self-hosted n8n (Docker Compose)
- `skills/` – Claude skills (coming soon)
- `workflows/` – n8n workflows

## Running n8n locally
Requirements: Docker with the Compose plugin (tested on Ubuntu 24.04 in WSL2).

```bash
cd n8n
echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)" > .env
docker compose up -d
```

