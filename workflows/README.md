# n8n workflows

## 02 – Job order creation from document (cjo)

**Status:** in progress · n8n 2.47 (self-hosted, Docker Compose)

Turns a client's requirements document into an ATS-ready job order.

### Flow
1. **Extract** – LLM chain (Claude Haiku 4.5, temperature 0) with a structured output parser pulls role, seniority, skills, location, work mode, dates, budget and languages into a fixed schema.
2. **Validate** – a Code node checks required fields and lists what's missing as questions.
3. **Human review** – if anything is missing, an n8n form (Wait node, 48h) asks a recruiter to fill the gaps; answers are merged back.
4. **Price** – if the client asks for our rate, a deterministic rate-card lookup (role × seniority → daily B2B rate) adds a rate range and estimated contract value. *(in progress)*
5. **Publish** – HTML job order sent to a mock ATS API (separate webhook workflow). *(planned)*

### Design choices
- The LLM only extracts data; pricing is plain code, so rates are reproducible and auditable.
- Missing data goes to a human instead of being guessed.

### Files
- `02-requirements-extraction.json` – workflow export (import via *Workflows → Import from file*)
