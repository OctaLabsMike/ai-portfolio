# cjo – job order builder (Claude skill)

A Claude skill that turns a client's requirements document into a complete HTML job order, ready to paste into an ATS.

The same process also exists as an n8n workflow: **[workflows/02-requirements-extraction.json](../../workflows/)**. This shows one process built two ways: a skill that a salesperson uses in a chat, and an automation that runs without one.

## What it does

| Step | What happens |
|---|---|
| 1. Extract | Reads pasted text, .docx or .pdf and fills a fixed schema (client, position, headcount, seniority, location, work mode, dates, budget, skills, languages). |
| 2. Ask about gaps | Required fields that are missing are **not guessed**. Claude asks the user first. This is the chat version of the n8n *Wait* form. |
| 3. Price | If the client asks for our rate, the role and seniority are looked up in the rate card: daily B2B rate range plus estimated contract value (rate × 21 days × months × headcount). If the role is not in the rate card, the job order is marked **"Pricing review required"**. |
| 4. Render | Fills the HTML template. All styles are inline, so the result can be pasted into an ATS rich-text editor. |

## Files

```
cjo/
├── SKILL.md                          # instructions Claude follows
├── references/rate-card.md           # fictional rate card + role/seniority mapping
├── assets/job-order-template.html    # HTML template (inline CSS)
└── examples/
    ├── baltic-freight-requirements.md / .docx   # fictional client brief
    └── baltic-freight-job-order.html            # resulting job order
```

## How to test

1. Download `cjo.zip` (the `cjo/` folder with `SKILL.md`, `references/`, `assets/`) and upload it in Claude: **Settings → Capabilities → Skills → Upload skill**. Code execution must be enabled.
2. Start a new chat, attach `examples/baltic-freight-requirements.docx` and type: *"Create a job order from this."*
3. Claude extracts the requirements and asks for the **start date** (as a pop-up with options if available, otherwise in chat).
4. Answer, for example `start_date: 2027-01-11`. Claude returns the HTML job order. Compare it with `examples/baltic-freight-job-order.html`.

Other tests to try:
- Change "Senior Data Engineer" to "Senior Data Scientist". The role is not in the rate card, so Claude should flag *Pricing review required* instead of inventing a rate.
- Replace "Please provide your B2B daily rate" with "Budget: up to 1 400 PLN/day net B2B". Claude should use the client's budget and skip the rate card.

## Design choices

- **The model extracts; rules validate and price.** The required-field list and the rate card are fixed, so results are reproducible.
- **Missing data goes to a human, not to a guess.** The `human_review` field keeps an audit trail, in the same shape as in n8n.
- **Output is always in English**, whatever the language of the client document.

All data (company, rates) is fictional.
