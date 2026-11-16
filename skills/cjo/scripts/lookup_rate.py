#!/usr/bin/env python3
"""Deterministic pricing for the cjo skill.

lookup  – map position + seniority to the rate card (assets/rate-card.xlsx)
market  – normalize job-board offers to daily rates and summarize them
price   – apply margin and calculate client rate, candidate rate and contract value

All output is JSON on stdout.
"""
import argparse
import json
import re
import statistics
from pathlib import Path

from openpyxl import load_workbook

DEFAULT_XLSX = Path(__file__).resolve().parent.parent / "assets" / "rate-card.xlsx"


def read_sheet(wb, name):
    rows = list(wb[name].iter_rows(values_only=True))
    head = [str(h).strip() for h in rows[0]]
    return [dict(zip(head, r)) for r in rows[1:] if any(v is not None for v in r)]


def contains(text, term):
    return re.search(r"(?<![\w.])" + re.escape(term.lower()) + r"(?![\w])", text.lower()) is not None


def settings(wb):
    return {r["key"]: r["value"] for r in read_sheet(wb, "settings")}


def cmd_lookup(a):
    wb = load_workbook(a.xlsx, read_only=True, data_only=True)
    aliases = sorted(read_sheet(wb, "role_aliases"), key=lambda r: (r["priority"], -len(r["alias"])))
    role = next((r["role"] for r in aliases if contains(a.position, r["alias"])), None)
    terms = sorted(read_sheet(wb, "seniority_map"), key=lambda r: -len(r["term"]))
    level = next((r["seniority"] for r in terms if contains(a.seniority, r["term"])), None)

    out = {"position": a.position, "seniority": a.seniority, "role": role, "level": level}
    if role is None:
        return {**out, "match": False, "reason": f"position '{a.position}' does not map to any role in the rate card"}
    if level is None:
        return {**out, "match": False, "reason": f"seniority '{a.seniority}' does not map to junior/mid/senior/lead"}
    hit = next((r for r in read_sheet(wb, "rates") if r["role"] == role and r["seniority"] == level), None)
    if hit is None:
        return {**out, "match": False, "reason": f"no rate for {role} / {level} in the rate card"}
    return {**out, "match": True, "rate_min": hit["rate_min"], "rate_max": hit["rate_max"],
            "currency": hit["currency"], "unit": hit["unit"]}


def cmd_market(a):
    wb = load_workbook(a.xlsx, read_only=True, data_only=True)
    days = settings(wb)["working_days_per_month"]
    factor = {"day": 1, "hour": 8, "month": 1 / days}
    offers = []
    for o in a.offer:
        m = re.fullmatch(r"\s*([\d.]+)\s*-\s*([\d.]+)\s*/\s*(day|hour|month)\s*", o)
        if not m:
            raise SystemExit(f"bad --offer '{o}', expected e.g. '18000-24000/month'")
        lo, hi, unit = float(m[1]), float(m[2]), m[3]
        offers.append({"input": o, "daily_min": round(lo * factor[unit]), "daily_max": round(hi * factor[unit])})
    res = {"offers": offers, "count": len(offers), "working_days_per_month": days}
    if len(offers) < 3:
        return {**res, "sufficient": False, "reason": "fewer than 3 comparable offers"}
    return {**res, "sufficient": True,
            "candidate_rate_min": round(statistics.median(o["daily_min"] for o in offers)),
            "candidate_rate_max": round(statistics.median(o["daily_max"] for o in offers))}


def cmd_price(a):
    wb = load_workbook(a.xlsx, read_only=True, data_only=True)
    days = settings(wb)["working_days_per_month"]
    rmin, rmax = a.rate_min, a.rate_max if a.rate_max is not None else a.rate_min

    def to_candidate(client):
        return client * (1 - a.margin_pct / 100) if a.margin_pct is not None else client - a.margin_amount

    def to_client(cand):
        return cand / (1 - a.margin_pct / 100) if a.margin_pct is not None else cand + a.margin_amount

    if a.basis == "client":
        client = (rmin, rmax)
        cand = (to_candidate(rmin), to_candidate(rmax))
    else:
        cand = (rmin, rmax)
        client = (to_client(rmin), to_client(rmax))
    client, cand = tuple(round(x) for x in client), tuple(round(x) for x in cand)
    mult = days * a.months * a.headcount
    return {
        "basis": a.basis,
        "margin": f"{a.margin_pct:g}% of client rate" if a.margin_pct is not None else f"{a.margin_amount:g} PLN/day",
        "client_rate_min": client[0], "client_rate_max": client[1],
        "candidate_rate_min": cand[0], "candidate_rate_max": cand[1],
        "contract_value_min": client[0] * mult, "contract_value_max": client[1] * mult,
        "calculation": f"client rate × {days} days × {a.months} months × {a.headcount} people",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--xlsx", default=str(DEFAULT_XLSX))
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("lookup")
    s.add_argument("--position", required=True)
    s.add_argument("--seniority", required=True)

    s = sub.add_parser("market")
    s.add_argument("--offer", action="append", required=True, help="'min-max/unit', unit: day|hour|month")

    s = sub.add_parser("price")
    s.add_argument("--rate-min", type=float, required=True)
    s.add_argument("--rate-max", type=float)
    s.add_argument("--basis", choices=["client", "candidate"], required=True)
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--margin-pct", type=float)
    g.add_argument("--margin-amount", type=float)
    s.add_argument("--months", type=int, required=True)
    s.add_argument("--headcount", type=int, required=True)

    a = p.parse_args()
    if getattr(a, "xlsx", None) and not Path(a.xlsx).exists():
        raise SystemExit(f"rate card not found: {a.xlsx}")
    result = {"lookup": cmd_lookup, "market": cmd_market, "price": cmd_price}[a.cmd](a)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
