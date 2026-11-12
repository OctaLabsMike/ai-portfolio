# AI Portfolio – Michał Przygórski

I build practical AI tools for business teams: Claude skills, AI agents and n8n workflows that automate sales and recruitment processes.

This repository contains clean-room versions of tools I designed and used in a previous role, rebuilt from scratch. All examples use fictional data (a made-up company, clients and rate card).

**Contact:** [LinkedIn](https://www.linkedin.com/in/michalprzygorski/)

## Projects

| Project | What it does | Status |
|---|---|---|
| [cjo – job order builder](skills/) | Client requirements document + rate card → complete job offer in HTML, ready for an ATS | in progress |
| [PSF – candidate submission forms](skills/) | CV + tender requirements → filled personal submission form | Planned |
| [rmap – client relationship map](skills/) | Emails + web research → map of decision-makers, relationship strength and next steps | Planned |
| [cjo as an n8n workflow](workflows/) | The job order process automated in n8n, with a mock ATS API | in progress |

## Results of the original tools

The production versions were used by a team of 4 salespeople:

- job orders generated in under a minute,
- tender candidate forms cut from 1 hour to 15 minutes per candidate,
- a full client relationship briefing in about 15 minutes.

## Tech stack

Claude (skills, plugins, API) · n8n · Docker · WSL2 (Ubuntu 24.04) · Microsoft 365 connectors

## Repository structure

- `n8n/` – self-hosted n8n (Docker Compose)
- `skills/` – Claude skills
- `workflows/` – exported n8n workflows (JSON)

## Running n8n locally

Requirements: Docker with the Compose plugin (tested on Ubuntu 24.04 in WSL2).

```bash
cd n8n
docker compose up -d
```

Then open http://localhost:5678.

