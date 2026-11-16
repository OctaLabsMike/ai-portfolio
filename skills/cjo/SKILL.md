---
name: cjo
description: Job order builder for IT staffing. Turns a client's requirements document (pasted text, .docx or .pdf) into a complete HTML job order ready to paste into an ATS. Extracts requirements into a fixed schema, asks the user about missing required fields instead of guessing, prices the role from the internal B2B rate card when the client asks for our rate, and flags roles outside the rate card for human review. Use when the user shares a client brief, role request, RFP or hiring requirements and wants a job order, ATS posting, offer or rate estimate, or mentions "cjo" or "job order".
---

# cjo – job order builder

Client requirements document → structured requirements → (questions about gaps) → pricing → HTML job order.

This is the Claude version of the n8n workflow `workflows/02-requirements-extraction.json`. Both follow the same rules: **the model extracts, fixed rules validate and price, a human fills the gaps.**

**Output language: always English**, whatever the language of the client document. Translate where needed.

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

- **`client_budget` is filled** → use it as the commercial basis and skip the rate card. Pricing status: `client_budget`.
- **`client_budget` is empty** → price from `references/rate-card.md`:
  1. Map `position` to a `role` key and `seniority` to a level (`junior` / `mid` / `senior` / `lead`) using the mapping rules in that file.
  2. Look up the `[min, max]` daily rate (PLN net, B2B).
  3. Estimated contract value = rate × 21 days × `duration_months` × `headcount`, for both min and max.
  4. Show the calculation in the job order so it can be audited.
  5. Pricing status: `rate_card`.
- **Role or seniority not in the rate card** (or ambiguous) → do not guess a rate. Pricing status: `pricing_review_required`, and add a red **"Pricing review required"** banner to the job order with the reason.

Rates come only from the rate card file, never from general knowledge.

## Step 4 – Render the HTML job order

Fill `assets/job-order-template.html`:
- Replace every `{{placeholder}}`. Lists marked `<!-- repeat -->` get one `<li>` per item. An empty list gets a single `<li>–</li>`.
- Keep only the pricing block for the current status (`client_budget`, `rate_card` or `pricing_review_required`) and delete the other two.
- Delete the *Open points* box if `missing_info` is empty and pricing status is not `pricing_review_required`.
- Keep all styles inline (`style="…"`): ATS rich-text editors strip `<style>` blocks and external CSS.
- Numbers: thousands separated with a space, e.g. `655 200 PLN`. Dates: `YYYY-MM-DD`.

Deliver:
1. The HTML as a downloadable file named `job-order-<client-slug>-<position-slug>.html`. If file output is not available, put it in one code block.
2. Below it, 2–3 lines: pricing status, open points (if any) and the final JSON in a collapsed or short code block for traceability.

## Example

`examples/` contains a fictional client brief (Baltic Freight Systems, 2 × Senior Data Engineer) and the resulting job order. It is the same test input as in the n8n workflow.
