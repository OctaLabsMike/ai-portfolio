# Rate card (fictional)

Daily rates, **PLN net, B2B contract**, `[min, max]`. Same values as in the n8n workflow. All data is fictional.

| role | junior | mid | senior | lead |
|---|---|---|---|---|
| backend_developer | 600–800 | 900–1150 | 1250–1550 | 1550–1850 |
| frontend_developer | 550–750 | 850–1100 | 1150–1450 | 1450–1750 |
| fullstack_developer | 600–800 | 900–1200 | 1250–1600 | 1600–1900 |
| devops_engineer | 650–850 | 1000–1250 | 1350–1700 | 1700–2000 |
| data_engineer | 600–800 | 950–1200 | 1300–1650 | 1650–1950 |
| qa_engineer | 450–650 | 700–950 | 1000–1250 | 1250–1500 |
| business_analyst | 500–700 | 800–1050 | 1100–1400 | 1400–1700 |
| project_manager | 550–750 | 850–1100 | 1200–1500 | 1500–1800 |

## Seniority mapping

| Stated in the document | Level |
|---|---|
| junior, młodszy, intern, trainee | `junior` |
| mid, regular, medior | `mid` |
| senior, starszy, expert | `senior` |
| lead, tech lead, team lead, principal, architect | `lead` |

If seniority is not stated, it is a missing required field (step 2). Ask; do not derive it from years of experience.

## Role mapping

Map by what the person will do, not by the exact title:

| Title examples | role |
|---|---|
| Backend / Java / .NET / Python / Go / Node.js developer | `backend_developer` |
| Frontend / React / Angular / Vue developer | `frontend_developer` |
| Fullstack developer | `fullstack_developer` |
| DevOps / Cloud / Platform / SRE engineer | `devops_engineer` |
| Data engineer, ETL / big data developer | `data_engineer` |
| QA / test engineer, tester, test automation engineer | `qa_engineer` |
| Business / system analyst | `business_analyst` |
| Project manager, delivery manager | `project_manager` |

Not in the rate card → **pricing review required**. Examples: data scientist, ML engineer, Scrum Master, UX/UI designer, mobile developer, SAP consultant, security engineer. Never pick the "closest" role.

## Contract value

```
estimated contract value = daily rate × 21 working days × duration_months × headcount
```

Calculate it for both ends of the range. Example: data_engineer / senior, 12 months, 2 people:
- min: 1300 × 21 × 12 × 2 = 655 200 PLN
- max: 1650 × 21 × 12 × 2 = 831 600 PLN
