# cjo – job order builder (Claude skill)

A Claude skill that turns a client's requirements document into a complete HTML job order, ready to paste into an ATS.

The same process also exists as an n8n workflow: **[workflows/02-requirements-extraction.json](../../workflows/)**. This shows one process built two ways: a skill that a salesperson uses in a chat, and an automation that runs without one.

## What it does

| Step | What happens |
|---|---|
| 1. Extract | Reads pasted text, .docx or .pdf and fills a fixed schema (client, position, headcount, seniority, location, work mode, dates, budget, skills, languages). |
| 2. Ask about gaps | Required fields that are missing are **not guessed**. Claude asks the user first. This is the chat version of the n8n *Wait* form. |
| 3. Price | If the client asks for our rate, Claude asks which rate to use: **rate card** (Excel, with the matched amount already in the option), **market check** (similar B2B offers on justjoin.it, nofluffjobs.com and pracuj.pl, with sources) or **manual**. It then asks for a margin (% or PLN/day) and calculates the client rate, the **max candidate rate** and the estimated contract value. |
| 4. Render | Fills the HTML template. All styles are inline, so the result can be pasted into an ATS rich-text editor. |

## Files

```
cjo/
├── SKILL.md                          # instructions Claude follows
├── assets/rate-card.xlsx             # fictional rate card: rates, role aliases, seniority map
├── assets/job-order-template.html    # HTML template (inline CSS)
├── scripts/lookup_rate.py            # rate-card lookup, market normalization, margin math
├── references/rate-card.md           # Excel structure and pricing formulas
└── examples/
    ├── baltic-freight-requirements.md / .docx   # fictional client brief
    └── baltic-freight-job-order.html            # resulting job order
```

## How to test

1. Download `cjo.zip` (the `cjo/` folder with `SKILL.md`, `assets/`, `scripts/`, `references/`) and upload it in Claude: **Settings → Capabilities → Skills → Upload skill**. Code execution must be enabled.
2. Start a new chat, attach `examples/baltic-freight-requirements.docx` and type: *"Create a job order from this."*
3. Claude extracts the requirements and asks for the **start date** (as a pop-up with options if available, otherwise in chat).
4. Answer, for example `2027-01-11`. *Data engineer* is not in the demo rate card, so Claude offers a market check, a manual rate or a pricing review.
5. Pick **Enter manually**, type `1500`, choose *client rate* and a *20%* margin. Compare the result with `examples/baltic-freight-job-order.html` (client rate 1 500, max candidate rate 1 200, contract value 756 000 PLN).

Other tests to try:
- Change "Senior Data Engineer" to "Senior Backend Developer". The first option should read *Rate card: 1250–1550 PLN/day (backend_engineer / senior)*.
- Same document, but pick **Market check**. Claude should list comparable job-board offers with links and propose a median candidate rate. This needs web search enabled in Claude.
- Replace "Please provide your B2B daily rate" with "Budget: up to 1 400 PLN/day net B2B". Claude should use the client's budget and skip the rate card.

## Design choices

- **The model extracts; code validates and prices.** Rate lookups and all arithmetic run in `scripts/lookup_rate.py`, so the same input gives the same numbers. The rate card is an Excel file a sales team can edit without touching the skill.
- **Client rate vs candidate rate.** Rate card and client budget are client rates; job-board offers are candidate rates. The margin connects the two, and the job order shows both.
- **Missing data goes to a human, not to a guess.** The `human_review` field keeps an audit trail, in the same shape as in n8n.
- **Output is always in English**, whatever the language of the client document.

All data (company, rates) is fictional.
