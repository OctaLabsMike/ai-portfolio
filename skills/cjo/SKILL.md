---
name: cjo
description: Job order builder for IT staffing. Turns a client's requirements document (pasted text, .docx or .pdf) into a complete HTML job order ready to paste into an ATS. Extracts requirements into a fixed schema, asks the user about missing required fields instead of guessing, when the client asks for our rate, offers a price from the Excel rate card, a job-board market check or a manual rate, applies a margin and shows the max candidate rate. Use when the user shares a client brief, role request, RFP or hiring requirements and wants a job order, ATS posting, offer or rate estimate, or mentions "cjo" or "job order".
---

# cjo – job order builder

Client requirements document → structured requirements → (questions about gaps) → pricing → HTML job order.

This is the Claude version of the n8n workflow `workflows/02-requirements-extraction.json`. Both follow the same rules: **the model extracts, fixed rules validate and price, a human fills the gaps.**

**Output language: always English**, whatever the language of the client document. Translate where needed.

## Mandatory checkpoints – never skip

The HTML job order is generated **only after every checkpoint that applies has been answered by the user**, each in its own turn:

| # | Checkpoint | When it applies |
|---|---|---|
| 1 | Missing required fields (step 2) | `missing_info` is not empty |
| 2 | **Rate source**: rate card / market check / manual (step 3a) | `client_budget` is empty – **always**, even if nothing was missing in step 1 |
| 3 | **Margin** (step 3b) | a rate was chosen (any source, incl. client budget) |

After the user answers one checkpoint, go to the next one. Do not generate the job order in the same turn as a checkpoint answer unless it was the last checkpoint. If you are about to render HTML, check this table first.

## Step 1 – Extract requirements

Read the input. It can be pasted text, an uploaded .docx or an uploaded .pdf (extract the text first). Fill this schema using **only information stated in the document. Do not guess.**

```json
{
  "client": "",
  "position": "",
  "headcount": 0,
  "seniority": "",
  "min_experience_years": 0,
  "location": "",
  "work_mode": "",
  "work_mode_details": "",
  "start_date": "",
  "duration_months": 0,
  "client_budget": "",
  "job_description": "",
  "must_have_skills": [],
  "nice_to_have_skills": [],
  "languages_required": [],
  "languages_nice_to_have": [],
  "missing_info": [],
  "human_review": null
}
```

Formatting rules:
- `start_date`: ISO `YYYY-MM-DD`.
- `work_mode`: exactly one of `remote`, `hybrid`, `onsite`. Office days and similar details go to `work_mode_details`.
- `min_experience_years`: a number ("5+ years" → 5). Not stated → 0.
- `client_budget`: rate or budget stated by the client, with currency and unit. **If the client asks for our rate, leave it empty.**
- `job_description`: 1–2 sentence summary of the role and responsibilities.
- `must_have_skills` / `nice_to_have_skills`: skills and experience areas, without languages and without years of experience. Keep alternatives as one item exactly as written ("Azure Data Factory or Databricks"); never split "or".
- `languages_required`: with level if stated ("English B2"). `languages_nice_to_have`: languages described as an advantage or a plus.
- Not stated → empty string, empty array or 0.

## Step 2 – Check required fields and ask about gaps

Required fields: `client`, `position`, `headcount`, `seniority`, `location`, `work_mode`, `start_date`, `duration_months`, `job_description`, `must_have_skills`.

`client_budget` is **not** required: an empty value means "the client asks for our rate", which is handled in step 3.

1. For every required field that is empty (`""`, `0`, `[]`), add `{ "field": "<name>", "question": "<one short question>" }` to `missing_info`.
2. If `missing_info` is not empty, **stop and ask before generating anything.** Start with a 2–3 line summary of what was extracted.
   - **If an interactive question tool is available, use it** (one question per missing field, at most 3 per call; for more, ask in batches).
     - Fixed-value fields → single-select: `work_mode` (remote / hybrid / onsite), `seniority` (junior / mid / senior / lead).
     - Open fields → 2–3 sensible options plus an option to type their own answer, e.g. `start_date`: "ASAP", "First Monday of next month", "Other – I'll type the date"; `headcount`: "1", "2", "Other". If the user picks "Other", ask for the value in chat.
     - Options are only suggestions for the user to pick from. Never treat an option as the answer unless the user chose it, and never pre-fill a field from them.
   - **Without such a tool**, ask in chat: numbered questions, reply as `field: value` lines (or plain answers in the same order).
3. Merge the answers into the schema. Questions left unanswered stay in `missing_info`. In `raw_answers`, record the selected options and typed values; `source` is `chat` whether the answers came from the pop-up or from text.
4. Set `human_review` (audit trail, same shape as in n8n):
   - nothing was missing → `null`
   - questions were asked → `{ "source": "chat" | "chat_partial", "at": "<ISO timestamp>", "raw_answers": "<user's reply verbatim>" }`

If the user explicitly says to generate anyway, do it: unresolved fields are shown as **"TBC"** and listed in the *Open points* box. Never fill them yourself.

## Step 3 – Pricing

All arithmetic and rate-card lookups go through `scripts/lookup_rate.py` (run it with Python; it reads `assets/rate-card.xlsx`). Never calculate rates or contract values by hand and never take rates from general knowledge. Details and formulas: `references/rate-card.md`.

**This step always requires the user's answers (checkpoints 2 and 3). Never pick a rate source or a margin yourself.** Ask with the interactive question tool when available (same rules as step 2), otherwise in chat.

### 3a. Choose the rate source

- **`client_budget` is filled** → the client's budget is the client rate. Source: `client_budget`. Go to 3b.
- **`client_budget` is empty** (client asks for our rate) → first run
  `python scripts/lookup_rate.py lookup --position "<position>" --seniority "<seniority>"`,
  then ask **"Which rate should we use?"** with these options:
  1. Match found → **"Rate card: <rate_min>–<rate_max> PLN/day (<role> / <level>)"**. The amount must be in the label.
     No match → replace this option with **"Skip – mark for pricing review"** and state the script's `reason` in the question text.
  2. **"Market check (job boards)"**
  3. **"Enter manually"**

What each option does:
- **Rate card** → client rate = the rate card range. Source: `rate_card`.
- **Market check** → search justjoin.it, nofluffjobs.com and pracuj.pl for offers matching `position`, `seniority` and the main `must_have_skills`, in Poland, with a stated B2B rate. Collect up to 10 comparable offers (title, portal, rate range, unit, URL). Run
  `python scripts/lookup_rate.py market --offer "18000-24000/month" --offer "150-180/hour" ...`
  (one `--offer` per offer; units `month`, `hour` or `day`). If the result is `sufficient: false`, say so and offer "Enter manually" or "Skip – mark for pricing review". Otherwise show the count, the median candidate range and the sources, then ask **"Use market rate <min>–<max> PLN/day (candidate rate)?"** with options "Yes" / "Enter manually". Job-board rates are what contractors earn, so this is the **candidate rate**. Source: `market`.
- **Enter manually** → ask for the daily rate (single value or range) and **"Is this the client rate or the candidate rate?"**. Source: `manual`.
- **Skip** → no rate. Pricing status: `pricing_review_required`. Skip 3b and add the red **"Pricing review required"** banner with the reason.

### 3b. Margin

Ask **"What margin should we apply?"** with options "15%", "20%", "25%", "Fixed amount per day – I'll type it" and "Other %". Margin % is a percentage of the client rate. Then run:

`python scripts/lookup_rate.py price --rate-min <min> [--rate-max <max>] --basis client|candidate (--margin-pct <p> | --margin-amount <PLN>) --months <duration_months> --headcount <headcount>`

`--basis` is `candidate` for the market source, or for a manual rate given as a candidate rate. Otherwise it is `client`. The script returns the client rate, the **max candidate rate** and the estimated contract value (based on the client rate). Pricing status: `priced`.

Add to the final JSON:
`"pricing": { "status", "source", "role", "level", "client_rate_min", "client_rate_max", "margin", "candidate_rate_min", "candidate_rate_max", "contract_value_min", "contract_value_max", "market_sources": [{ "title", "portal", "rate", "url" }] }`

## Step 4 – Render the HTML job order

Fill `assets/job-order-template.html`:
- Replace every `{{placeholder}}`. Lists marked `<!-- repeat -->` get one `<li>` per item. An empty list gets a single `<li>–</li>`.
- Pricing status `priced` → keep the *Commercials* table and delete the review banner. Delete the *Market sources* row unless the source is `market`. A single rate value (min = max) is shown as one number.
- Pricing status `pricing_review_required` → keep only the review banner inside *Commercials*.
- Delete the *Open points* box if `missing_info` is empty and pricing status is not `pricing_review_required`.
- Keep all styles inline (`style="…"`): ATS rich-text editors strip `<style>` blocks and external CSS.
- Numbers: thousands separated with a space, e.g. `655 200 PLN`. Dates: `YYYY-MM-DD`.

Deliver:
1. The HTML as a downloadable file named `job-order-<client-slug>-<position-slug>.html`. If file output is not available, put it in one code block.
2. Below it, 2–3 short bullets: rate source, client rate / max candidate rate, and open points (if any). Do not print the final JSON unless the user asks for it, and never use HTML tags such as `<details>` in the chat reply: the chat does not render them.

## Example

`examples/` contains a fictional client brief (Baltic Freight Systems, 2 × Senior Data Engineer) and the resulting job order. It is the same test input as in the n8n workflow. *Data engineer* is not in the rate card, so the example shows the no-match path: the rate was entered manually (client rate 1 500 PLN/day, 20% margin).
