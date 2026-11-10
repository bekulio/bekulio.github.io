"""
final_simulation.py  -  Self-contained.

Run (files in the same directory, or pass paths):
    python final_simulation.py --results expc_1.csv --cbs downloadFile.xlsx

Method ("national-spread qualification"):
  1. A FROZEN LIST of entries:
       - every locality with population >= MIN_POP is its own entry
       - every regional council is ONE pooled entry (all its localities)
       - the external-envelopes row (code 9999) is ONE entry
       - small localities that are not in a regional council are NOT on the list
  2. A party qualifies if its pooled vote share is >= LOCAL_THRESHOLD % in at least PASS_PCT % of entries.
  3. Seats (120) are split by D'Hondt among qualifying parties, using ALL votes nationwide.

Baseline = D'Hondt with a 3.25% national threshold (approximation of the current system, no surplus agreements).
Outputs: tables on screen + seats_comparison.png (saved next to this script).
Inputs: election results CSV (CEC format, Hebrew headers) and the CBS localities XLSX ("general information").
"""
import argparse
import heapq
import math
import os

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEATS = 120
LOCAL_THRESHOLD = 3.25   # % inside an entry
NATIONAL_THRESHOLD = 3.25
ENVELOPES_CODE = 9999    # "external envelopes" row in the CEC file
NAMES = {'מחל': 'Likud', 'דרך': 'Yashar', 'ודם': 'Joint List', 'רק': 'Together', 'אמת': 'Democrats',
         'עם': "Ra'am", 'ל': 'Yisrael Beiteinu', 'ג': 'UTJ', 'ב': 'Otzma', 'שס': 'Shas',
         'ט': 'Rel.Zionism', 'די': 'Reservists+NEP', 'ך': 'Amcha', 'ני': 'Noam'}


def dhondt(votes, seats=SEATS):
    out = {p: 0 for p in votes}
    heap = [(-v, p) for p, v in votes.items() if v > 0]
    heapq.heapify(heap)
    for _ in range(seats):
        if not heap:
            break
        _, p = heapq.heappop(heap)
        out[p] += 1
        heapq.heappush(heap, (-votes[p] / (out[p] + 1), p))
    return out


def load(results_path, cbs_path):
    r = pd.read_csv(results_path, encoding="utf-8-sig")
    r = r.loc[:, ~r.columns.str.startswith("Unnamed")]
    cols = list(r.columns[7:])
    parties = [NAMES.get(c, "List_" + c) for c in cols]
    r = r.rename(columns=dict(zip(cols, parties))).rename(columns={"סמל ישוב": "code"})
    r = r.groupby("code", as_index=False)[parties].sum()

    c = pd.read_excel(cbs_path, sheet_name=0, header=10).dropna(how="all")
    c = c.rename(columns={"סמל היישוב": "code", "שם יישוב": "name", "מחוז": "district",
                          "מעמד מוניציפלי": "status", "אוכלוסייה - סך הכל": "population"})
    c["population"] = pd.to_numeric(c["population"], errors="coerce").fillna(0)
    c["council"] = np.where(c["status"].isin(["עירייה", "מועצה מקומית"]), "", c["status"])
    df = r.merge(c[["code", "population", "council"]], on="code", how="left")
    return df, parties


def build_entries(df, parties, min_pop, use_envelopes=True):
    d = df.copy()

    def entry(row):
        if row["code"] == ENVELOPES_CODE:
            return "envelopes" if use_envelopes else None
        if pd.isna(row["population"]):
            return None                       # no CBS record (e.g. Bedouin tribes): not on the list
        if row["population"] >= min_pop:
            return f"loc:{int(row['code'])}"
        if isinstance(row["council"], str) and row["council"]:
            return f"council:{row['council']}"
        return None                           # small local council etc.: not on the list

    d["entry"] = d.apply(entry, axis=1)
    return d.dropna(subset=["entry"]).groupby("entry")[parties].sum()


def evaluate(entries, parties, nat, pass_pct):
    valid = entries.sum(axis=1)
    shares = entries.div(valid, axis=0) * 100
    passes = (shares >= LOCAL_THRESHOLD).sum()
    n = len(entries)
    need = math.ceil(pass_pct / 100 * n - 1e-9)
    surv = [p for p in parties if passes[p] >= need]
    seats = dhondt({p: nat[p] for p in surv}) if surv else {}
    return passes, n, need, surv, seats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="expc_1.csv")
    ap.add_argument("--cbs", default="downloadFile.xlsx")
    ap.add_argument("--min-pop", type=int, default=10000)
    ap.add_argument("--pass-pct", type=float, default=60.0)
    ap.add_argument("--no-envelopes", action="store_true")
    a = ap.parse_args()

    df, parties = load(a.results, a.cbs)
    nat = df[parties].sum()
    natsh = nat / nat.sum() * 100
    print(f"Valid votes: {int(nat.sum()):,}")

    base = dhondt({p: nat[p] for p in parties if natsh[p] >= NATIONAL_THRESHOLD})
    entries = build_entries(df, parties, a.min_pop, not a.no_envelopes)
    passes, n, need, surv, seats = evaluate(entries, parties, nat, a.pass_pct)
    print(f"\nList: {n} entries | need >= {need} entries ({a.pass_pct}%) with >= {LOCAL_THRESHOLD}% | min_pop={a.min_pop}")
    print(f"\n{'Party':20s}{'Vote%':>7s}{'Entries':>9s}{'Pass%':>7s}{'Margin':>8s}{'New':>6s}{'Current':>9s}")
    shown = natsh.sort_values(ascending=False).index[:14]
    for p in shown:
        print(f"{p:20s}{natsh[p]:7.2f}{int(passes[p]):9d}{passes[p] / n * 100:7.1f}{int(passes[p]) - need:8d}"
              f"{seats.get(p, 0):6d}{base.get(p, 0):9d}")
    print(f"(Margin = entries above (+) or below (-) the requirement.)")
    print(f"Voters whose party gets no seats: {100 - sum(natsh[p] for p in surv):.1f}%")

    print("\nSensitivity - qualifying parties by (min_pop, pass%):")
    for mp in (10000, 5000):
        ent = build_entries(df, parties, mp, not a.no_envelopes)
        for pct in (50, 55, 60, 65, 70):
            _, n2, need2, surv2, seats2 = evaluate(ent, parties, nat, pct)
            txt = ", ".join(f"{p} {seats2[p]}" for p in sorted(surv2, key=lambda x: -nat[x])) or "none"
            print(f"  min_pop={mp:6d} entries={n2:3d} pass>={pct}%: {txt}")

    here = os.path.dirname(os.path.abspath(__file__))
    top = [p for p in natsh.sort_values(ascending=False).index[:11]]
    x = np.arange(len(top))
    plt.figure(figsize=(11, 5))
    plt.bar(x - 0.2, [base.get(p, 0) for p in top], 0.4, label="Current system (D'Hondt, 3.25%)")
    plt.bar(x + 0.2, [seats.get(p, 0) for p in top], 0.4, label=f"National-spread rule ({a.pass_pct:.0f}%)")
    plt.xticks(x, top, rotation=35, ha="right")
    plt.ylabel("Seats (of 120)")
    plt.title("Knesset seats: current system vs national-spread rule (2026 results)")
    plt.legend()
    plt.tight_layout()
    out = os.path.join(here, "seats_comparison.png")
    plt.savefig(out, dpi=150)
    print(f"\nChart saved: {out}")


if __name__ == "__main__":
    main()
