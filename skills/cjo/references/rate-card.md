# Rate card and pricing rules

The rate card is an Excel file: **`assets/rate-card.xlsx`**. All rates are fictional and for demo purposes only. Edit the Excel file, not this document. `scripts/lookup_rate.py` reads it on every run.

## Excel structure

| Sheet | Columns | Purpose |
|---|---|---|
| `rates` | `role`, `seniority`, `rate_min`, `rate_max`, `currency`, `unit` | Client daily rates, PLN net B2B. One row per role × seniority. |
| `role_aliases` | `alias`, `role`, `priority` | Maps a job title to a role. Lower `priority` is checked first; within a priority, longer aliases win. Matching is whole-word and case-insensitive. |
| `seniority_map` | `term`, `seniority` | Maps a stated seniority (incl. Polish terms) to `junior` / `mid` / `senior` / `lead`. |
| `settings` | `key`, `value` | `working_days_per_month` (21), currency, unit. |

Roles in the demo rate card: `backend_engineer`, `frontend_engineer`, `fullstack_engineer`, `qa_engineer`, `architect` (senior and lead only), `business_analyst`, `system_analyst`, `project_manager`.

If a title matches no alias, or a role has no row for that seniority, there is **no match**. Never pick the "closest" role. Examples of no-match titles: data engineer, DevOps engineer, data scientist, Scrum Master, UX designer, mid-level architect.

`fullstack` has priority 1, so "Fullstack Java Developer" maps to `fullstack_engineer`, not `backend_engineer`. `architect` has priority 2.

## Rate sources

| Source | Rate it gives | `--basis` |
|---|---|---|
| `client_budget` | client rate (from the document) | `client` |
| `rate_card` | client rate | `client` |
| `market` | candidate rate (what contractors earn on job boards) | `candidate` |
| `manual` | user states client or candidate | `client` / `candidate` |

## Market check

- Portals: justjoin.it, nofluffjobs.com, pracuj.pl. Offers in Poland with a stated B2B rate.
- Comparable offer: same role family, same seniority, overlapping main must-have skills.
- Normalization (in the script): month ÷ 21, hour × 8, day as is.
- Result: median of offer minimums – median of offer maximums. At least 3 offers, otherwise insufficient data.
- Always list the sources (title, portal, rate, URL) in the job order.

## Margin and formulas

Margin % is a percentage of the **client rate**:

```
candidate rate = client rate × (1 − margin%)          # basis: client
client rate    = candidate rate ÷ (1 − margin%)       # basis: candidate
```

Fixed margin (PLN per day):

```
candidate rate = client rate − margin
client rate    = candidate rate + margin
```

Contract value is based on the client rate:

```
estimated contract value = client rate × 21 days × duration_months × headcount
```

Example: `backend_engineer / senior`, 1 250–1 550 PLN/day, 20% margin, 12 months, 2 people:
- max candidate rate: 1 000–1 240 PLN/day
- contract value: 630 000–781 200 PLN
