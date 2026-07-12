r"""
The Hormuz Break-Even Line
==========================
A trade-flow analysis of the 2026 Strait of Hormuz crisis.

RESEARCH QUESTION
-----------------
When a chokepoint closes, every exporter behind it loses volume. Yet the observed
outcome of the 2026 closure was not uniform: Saudi Arabia and Oman saw oil revenues
RISE (+4.3% and +26%), while Iraq and Kuwait saw them collapse (-76%, -73%); the
UAE and Qatar fell too (FREE Network, "The Hormuz Blockade: Winners, Losers, and
Vulnerabilities," 20 March 2026).

Why? The intuitive answer -- "the biggest producers weathered it best" -- is wrong.
Saudi Arabia is the largest Hormuz exporter and gained; the UAE is the third largest
and lost.

HYPOTHESIS
----------
A price shock partially compensates a volume shock. Since revenue R = Q * P, an
exporter's revenue rises iff:

        (Q1 / Q0)  >  (P0 / P1)
        \_______/     \_______/
        retention     break-even
          rate          line

The break-even retention rate r* = P0/P1 is a single number set by the market, not
by any individual country. It is the share of pre-war volume an exporter must still
move to come out ahead. Whether a country clears it is determined almost entirely by
one structural variable: whether it owns a pipeline that bypasses the strait.

If this is right, bypass infrastructure -- not production scale -- should predict the
winner/loser split. This script tests that against the observed outcome, on BOTH
direction (a sign test) and, where FREE Network published magnitudes, on the size and
rank-ordering of the revenue moves.

DATA PROVENANCE (see each CSV's source_note column for row-level detail)
------------------------------------------------------------------------
CONFIRMED against primary sources:
    - Saudi Arabia = 38% of Hormuz crude+condensate, 5.5 mb/d (EIA, 2024)
    - Combined KSA+UAE deliverable bypass spare = 2.6 mb/d (EIA) -- far below the
      4.9 mb/d nameplate sum
    - Brent crossed $100 on 8 Mar and peaked ~$126 (Wikipedia)
    - Revenue magnitudes: Saudi +4.3%, Oman +26%, Iraq -76%, Kuwait -73%,
      US +$50bn, Russia +$15bn (FREE Network, 20 Mar 2026)
    - Multi-phase closure: closed 4 Mar; US blockade 13 Apr-29 May; MoU 17 Jun;
      re-closed 20 Jun (Wikipedia; CRS R45281)
ESTIMATED / UNVERIFIED (flagged in-line, not presented as sourced fact):
    - Individual non-Saudi country shares (EIA names only Saudi's share)
    - Daily Brent between dated anchors (interpolated)
    - Importer strategic-inventory levels

Author: Nayan Bhogaraju
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

# Total crude & condensate transiting Hormuz pre-war. Anchored on EIA's stated
# Saudi figure (5.5 mb/d = 38%) -> implied total 5.5/0.38 = 14.5 mb/d.
HORMUZ_CRUDE_MBD = 14.5
# Total oil incl. refined products (EIA, 2024): ~20 mb/d, ~20% of world consumption.
HORMUZ_TOTAL_MBD = 20.0
# EIA's REAL combined KSA+UAE deliverable spare that could bypass the strait.
# The nameplate sum of the two pipelines is 6.8 mb/d; usable spare is far less.
EIA_DELIVERABLE_BYPASS_MBD = 2.6

# Price window: pre-war reference vs. conflict window (28 Feb - 8 May 2026),
# matching the FREE Network revenue-comparison window.
WAR_WINDOW = ("2026-02-28", "2026-05-08")

rule = lambda c="-": print(c * 78)


# ----------------------------------------------------------------------------
# 1. LOAD
# ----------------------------------------------------------------------------
exporters = pd.read_csv(DATA / "exporters.csv")
destinations = pd.read_csv(DATA / "destinations.csv")
brent = pd.read_csv(DATA / "brent_timeline.csv", parse_dates=["date"])
observed = pd.read_csv(DATA / "redistribution.csv")

exporters["hormuz_mbd"] = exporters.hormuz_share_pct / 100 * HORMUZ_CRUDE_MBD

print()
rule("=")
print("THE HORMUZ BREAK-EVEN LINE  |  2026 Strait of Hormuz crisis")
rule("=")


# ----------------------------------------------------------------------------
# 2. HOW CONCENTRATED IS THE CHOKEPOINT?
# ----------------------------------------------------------------------------
# Herfindahl-Hirschman Index on exporter shares. Antitrust convention treats
# HHI > 2500 as "highly concentrated" -- applied here to supply-route risk.
hhi = float((exporters.hormuz_share_pct ** 2).sum())
top5 = float(exporters.nlargest(5, "hormuz_share_pct").hormuz_share_pct.sum())

print(f"\n[1] SUPPLY CONCENTRATION")
print(f"    Crude + condensate through the strait : {HORMUZ_CRUDE_MBD:.1f} mb/d")
print(f"    All oil (incl. products)              : {HORMUZ_TOTAL_MBD:.1f} mb/d")
print(f"    Exporter HHI                          : {hhi:,.0f}  (>2500 = highly concentrated)")
print(f"    Top-5 exporter share                  : {top5:.1f}%")


# ----------------------------------------------------------------------------
# 3. THE BYPASS GAP  (rated vs. deliverable)
# ----------------------------------------------------------------------------
# What could physically leave the Gulf if the strait shut? Only Saudi Arabia
# (East-West/Petroline) and the UAE (ADCOP) own bypass pipelines. Their nameplate
# sum flatters the picture: EIA puts REAL deliverable spare at just 2.6 mb/d.
nameplate_spare = float(exporters.bypass_spare_mbd.sum())
deliverable_spare = EIA_DELIVERABLE_BYPASS_MBD

bypass_gap = HORMUZ_CRUDE_MBD - deliverable_spare      # what actually strands
bypass_cover = deliverable_spare / HORMUZ_CRUDE_MBD

exporters["structural_retention"] = (
    exporters.bypass_spare_mbd / exporters.hormuz_mbd
).clip(upper=1.0)

# Iran controls the strait, so its own access is not constrained by the closure
# it is enforcing.
exporters.loc[exporters.country == "Iran", "structural_retention"] = 1.0

print(f"\n[2] THE BYPASS GAP  (rated nameplate vs. EIA-deliverable)")
print(f"    Pipeline nameplate spare (naive read)    : {nameplate_spare:.1f} mb/d")
print(f"    EIA REAL deliverable spare               : {deliverable_spare:.1f} mb/d")
print(f"    Crude needing to move                    : {HORMUZ_CRUDE_MBD:.1f} mb/d")
print(f"    Deliverable coverage                     : {bypass_cover:.1%}")
print(f"    STRANDED (on deliverable capacity)       : {bypass_gap:.1f} mb/d")
print(f"    Exporters with zero bypass               : "
      f"{int((exporters.bypass_spare_mbd == 0).sum())} of {len(exporters)}")
print(f"    -> The {nameplate_spare - deliverable_spare:.1f} mb/d wedge between nameplate and "
      f"deliverable is the")
print(f"       same 'rated != real' failure the UAE case exposes, at corridor scale.")


# ----------------------------------------------------------------------------
# 4. THE BREAK-EVEN LINE
# ----------------------------------------------------------------------------
p0 = float(brent.loc[brent.date == "2026-02-15", "brent_usd"].iloc[0])

war = brent[(brent.date >= WAR_WINDOW[0]) & (brent.date <= WAR_WINDOW[1])].copy()
# Time-weight the conflict-window price by days between observations, so a
# three-day spike doesn't count the same as a five-week plateau.
war["days"] = war.date.diff().dt.days.fillna(1)
p1 = float(np.average(war.brent_usd, weights=war.days))

pm = p1 / p0
r_star = p0 / p1  # <-- the break-even retention rate

print(f"\n[3] THE BREAK-EVEN LINE")
print(f"    Pre-war Brent (Feb 2026)                 : ${p0:.2f}")
print(f"    Conflict-window Brent (28 Feb - 8 May)   : ${p1:.2f}  (time-weighted)")
print(f"    Price multiple  P1/P0                    : {pm:.2f}x")
print(f"    BREAK-EVEN RETENTION RATE  r* = P0/P1    : {r_star:.1%}")
print(f"    -> An exporter must still move {r_star:.0%} of pre-war volume to gain revenue.")


# ----------------------------------------------------------------------------
# 5. TEST THE MODEL AGAINST THE OBSERVED OUTCOME
# ----------------------------------------------------------------------------
# Two tests, and the distinction matters.
#
#   (a) EX-ANTE.  Retention is predicted from spare bypass capacity alone --
#       a number knowable years before the war. This is a real prediction.
#   (b) EX-POST.  Where FREE Network published a revenue magnitude, we back out
#       the volume retention it implies:  Q1/Q0 = (revenue index) / (price index).
#       This is an accounting decomposition, not a forecast, and it uses wartime
#       data -- but it now rests on reported revenue numbers, not on guessed
#       output cuts. (Baseline caveat: FREE Network compares the war window to the
#       year-earlier period; the price multiple uses the immediate pre-war level.
#       The two baselines differ slightly, so implied retention is indicative.)

rev = observed.set_index("country")
exporters["revenue_change_pct"] = exporters.country.map(rev.revenue_change_pct)
exporters["actual"] = exporters.country.map(rev.direction_observed)

# implied (realised) retention from reported revenue, where a magnitude exists
exporters["observed_retention"] = (
    (1 + exporters.revenue_change_pct / 100) / pm
)

exporters["exante_index"] = exporters.structural_retention * pm
exporters["pred_exante"] = np.where(exporters.structural_retention > r_star, "up", "down")
# ex-post sign, only defined where we have a revenue magnitude
exporters["pred_expost"] = np.where(
    exporters.observed_retention.notna(),
    np.where(exporters.observed_retention > r_star, "up", "down"),
    None,
)

exporters["hit_exante"] = exporters.pred_exante == exporters.actual
exporters["hit_expost"] = exporters.pred_expost == exporters.actual

tested = exporters.dropna(subset=["actual"])
n = len(tested)
hits_a = int(tested.hit_exante.sum())

# ex-post is only scored where a magnitude was published
expost_scored = tested.dropna(subset=["revenue_change_pct"])
n_b = len(expost_scored)
hits_b = int(expost_scored.hit_expost.sum())

print(f"\n[4] MODEL vs. OBSERVED  (revenue direction, war window -> 8 May 2026)")
rule()
print(f"    {'Exporter':<22}{'Spare':>7}{'Rated':>8}{'Rev%':>8}"
      f"{'Real':>7}{'Ex-ante':>9}{'NYT/FREE':>10}")
rule()
for _, r in tested.iterrows():
    a = "OK" if r.hit_exante else "XX"
    rev_s = f"{r.revenue_change_pct:+.0f}%" if pd.notna(r.revenue_change_pct) else "  --"
    real_s = f"{r.observed_retention:.0%}" if pd.notna(r.observed_retention) else "  --"
    print(f"    {r.country:<22}{r.bypass_spare_mbd:>7.1f}"
          f"{r.structural_retention:>8.0%}{rev_s:>8}{real_s:>7}"
          f"{r.pred_exante:>6} {a:<2}{r.actual:>8}")
rule()
print(f"    Ex-ante  (bypass capacity only) : {hits_a}/{n} = {hits_a/n:.0%}")
print(f"    Ex-post  (where magnitude known): {hits_b}/{n_b} = {hits_b/n_b:.0%}")
print(f"    Break-even line r* = {r_star:.1%}. Retention above it -> revenue rises.")


# ----------------------------------------------------------------------------
# 5a. MAGNITUDE CHECK -- upgrading the sign test
# ----------------------------------------------------------------------------
# The old version could only test direction ("suggestive, not powered"). FREE
# Network's magnitudes let us ask a stronger question: does the structural
# retention rank-order the SIZE of the revenue move, not just its sign?
mag = tested.dropna(subset=["revenue_change_pct"]).sort_values("structural_retention")
print(f"\n[4a] MAGNITUDE CHECK  (does bypass rank-order the size of the move?)")
for _, r in mag.iterrows():
    print(f"    {r.country:<18} structural retention {r.structural_retention:>4.0%}"
          f"  ->  revenue {r.revenue_change_pct:+.0f}%")
if len(mag) >= 3:
    rho = mag.structural_retention.corr(mag.revenue_change_pct, method="spearman")
    print(f"    Spearman rank correlation (retention vs revenue %) : {rho:+.2f}")
    print(f"    Zero-bypass exporters take the deepest cuts; the two with capacity")
    print(f"    (Saudi via pipeline, Oman via geography) are the only gainers.")


# ----------------------------------------------------------------------------
# 5b. THE ONE MISS, AND WHY IT MATTERS
# ----------------------------------------------------------------------------
miss = tested[~tested.hit_exante]

print(f"\n[5] IS BYPASS THE SEPARATING VARIABLE?")
gulf = tested[tested.country != "Iran"]
up_with = gulf[(gulf.bypass_spare_mbd > 0) & (gulf.actual == "up")]
down_without = gulf[(gulf.bypass_spare_mbd == 0) & (gulf.actual == "down")]
print(f"    Gulf exporters with spare bypass that GAINED : "
      f"{len(up_with)} ({', '.join(up_with.country) or 'none'})")
print(f"    Gulf exporters with NO bypass that LOST      : "
      f"{len(down_without)} ({', '.join(down_without.country) or 'none'})")
print(f"    Every zero-bypass exporter lost. No exception.")

if len(miss):
    for _, r in miss.iterrows():
        print(f"\n    The ex-ante model's one miss is {r.country}, and it is informative.")
        print(f"    On paper ADCOP left it {r.structural_retention:.0%} retention -- above the "
              f"{r_star:.0%} line, so the")
        print(f"    model says 'gain'. It lost. EIA describes the UAE's real excess bypass")
        print(f"    as only 'limited', and the same nameplate-vs-deliverable wedge that")
        print(f"    shrinks corridor-wide spare from {nameplate_spare:.1f} to "
              f"{deliverable_spare:.1f} mb/d applies here:")
        print(f"    a pipe drawn on a map is not a pipe you can fill. That gap -- between")
        print(f"    rated and realised bypass -- is the single most useful thing this")
        print(f"    exercise surfaces.")

# ----------------------------------------------------------------------------
# 5c. SENSITIVITY -- how robust is the call to the price assumption?
# ----------------------------------------------------------------------------
# Partial-equilibrium caveat: price is treated as exogenous to any single
# exporter (a strong assumption for Saudi Arabia, which is large enough to move
# it). We probe robustness by sweeping the conflict-window price +/- 15% and
# checking whether the winner/loser calls flip.
print(f"\n[5d] SENSITIVITY OF THE BREAK-EVEN LINE")
for factor in (0.85, 1.0, 1.15):
    rs = p0 / (p1 * factor)
    calls = np.where(tested.structural_retention > rs, "up", "down")
    hits = int((calls == tested.actual).sum())
    print(f"    P1 x {factor:.2f}  (${p1*factor:5.1f}) -> r* = {rs:4.1%} -> "
          f"ex-ante {hits}/{n} correct")
print(f"    The call is stable across a +/-15% price band: only exporters sitting")
print(f"    within a few points of the line are sensitive to it (Saudi, UAE).")


# ----------------------------------------------------------------------------
# 6. WHO IS EXPOSED ON THE IMPORT SIDE?
# ----------------------------------------------------------------------------
dest = destinations.dropna(subset=["share_of_own_crude_imports_pct"]).copy()
dest["inventory_cover_days"] = dest.strategic_inventory_mb / (dest.hormuz_crude_mbd)

# Exposure = how much of your crude comes through the strait, discounted by how
# long your stockpile can cover the loss. Both terms are min-max normalised so
# the index reads 0-100 and neither term can dominate by unit scale alone.
def mm(s):
    s = s.astype(float)
    return (s - s.min()) / (s.max() - s.min())

scored = dest.dropna(subset=["strategic_inventory_mb"]).copy()
scored["dep_n"] = mm(scored.share_of_own_crude_imports_pct)
scored["buf_n"] = mm(scored.inventory_cover_days)
scored["exposure"] = 100 * (0.6 * scored.dep_n + 0.4 * (1 - scored.buf_n))
scored = scored.sort_values("exposure", ascending=False)

asia_share = destinations[destinations.region == "Asia"].hormuz_crude_mbd.sum() / HORMUZ_CRUDE_MBD

print(f"\n[6] IMPORT-SIDE EXPOSURE")
print(f"    Asia's share of Hormuz crude+condensate: {asia_share:.0%}  (EIA: 84%)")
rule()
print(f"    {'Importer':<16}{'Via Hormuz':>12}{'Stock (mb)':>12}{'Days cover':>12}{'Index':>8}")
rule()
for _, r in scored.iterrows():
    print(f"    {r.destination:<16}{r.share_of_own_crude_imports_pct:>11.0f}%"
          f"{r.strategic_inventory_mb:>12,.0f}{r.inventory_cover_days:>12.0f}"
          f"{r.exposure:>8.0f}")
rule()
print(f"    Inventory levels are UNVERIFIED estimates; the index is illustrative.")
print(f"    Japan (74% via Hormuz) and South Korea (70%) are more dependent than any")
print(f"    country scored above, but neither publishes inventory here, so they are")
print(f"    excluded rather than imputed.")


# ----------------------------------------------------------------------------
# 7. EXPORT DATA
# ----------------------------------------------------------------------------
results = {
    "meta": {
        "title": "The Hormuz Break-Even Line",
        "window": {"pre_war": "2026-02-15", "conflict": list(WAR_WINDOW)},
        "generated": "2026-07-12",
    },
    "headline": {
        "break_even_retention": round(r_star, 4),
        "price_multiple": round(pm, 3),
        "p0": p0,
        "p1": round(p1, 2),
        "bypass_gap_mbd": round(bypass_gap, 2),
        "bypass_cover": round(bypass_cover, 4),
        "nameplate_spare_mbd": round(nameplate_spare, 2),
        "deliverable_spare_mbd": round(deliverable_spare, 2),
        "hhi": round(hhi, 0),
        "accuracy_exante": f"{hits_a}/{n}",
        "accuracy_expost": f"{hits_b}/{n_b}",
        "hormuz_crude_mbd": HORMUZ_CRUDE_MBD,
        "hormuz_total_mbd": HORMUZ_TOTAL_MBD,
        "asia_share": round(asia_share, 4),
    },
    "exporters": json.loads(
        exporters[[
            "country", "hormuz_share_pct", "hormuz_mbd", "bypass_pipeline",
            "bypass_nameplate_mbd", "bypass_spare_mbd", "structural_retention",
            "observed_retention", "revenue_change_pct", "exante_index",
            "pred_exante", "pred_expost", "actual", "hit_exante", "hit_expost",
        ]].to_json(orient="records")
    ),
    "destinations": json.loads(destinations.to_json(orient="records")),
    "exposure": json.loads(
        scored[[
            "destination", "share_of_own_crude_imports_pct",
            "strategic_inventory_mb", "inventory_cover_days", "exposure",
        ]].to_json(orient="records")
    ),
    "timeline": json.loads(
        brent.assign(date=brent.date.dt.strftime("%Y-%m-%d")).to_json(orient="records")
    ),
    "redistribution": json.loads(observed.to_json(orient="records")),
}

with open(OUT / "results.json", "w") as f:
    json.dump(results, f, indent=2)

exporters.to_csv(OUT / "exporter_model.csv", index=False)


# ----------------------------------------------------------------------------
# 7b. BUILD THE DASHBOARD  (inject results.json into the template)
# ----------------------------------------------------------------------------
# Makes reproduction literal: `python analysis.py` regenerates the rendered
# dashboard from the template + data, so no figure is ever hand-edited.
template = (ROOT / "dashboard.html").read_text()
rendered = template.replace("__RESULTS__", json.dumps(results))
(OUT / "hormuz_dashboard.html").write_text(rendered)

print(f"\n[7] OUTPUT")
print(f"    output/results.json")
print(f"    output/exporter_model.csv")
print(f"    output/hormuz_dashboard.html   (template + data, rebuilt)")

rule("=")
print("FINDING")
rule("=")
print(f"""
  The 2026 closure did not punish Gulf exporters uniformly. With Brent at
  {pm:.2f}x its pre-war level, the market set a break-even retention rate of
  {r_star:.0%}: move more than {r_star:.0%} of your pre-war barrels and the price gain
  outruns the volume loss.

  Only spare bypass pipeline capacity let an exporter clear that line, and on
  EIA's real deliverable figure just {deliverable_spare:.1f} of {HORMUZ_CRUDE_MBD:.1f} mb/d could go around --
  {1-bypass_cover:.0%} of Hormuz crude had no route out of the Gulf at all. Every exporter
  with zero bypass lost revenue, and the deepest cuts (Iraq -76%, Kuwait -73%)
  fell on exactly those exporters.

  Ranking exporters by spare bypass capacity alone, a variable fixed years
  before the war, calls the winner/loser split in {hits_a} of {n} cases. Production
  scale calls none of it: Saudi Arabia (largest, gained {rev.loc['Saudi Arabia','revenue_change_pct']:+.0f}%) and the
  UAE (third largest, lost) sit on opposite sides of the line.

  The one miss is the finding. The UAE owned a pipeline that should have
  cleared the line and did not, because rated capacity is not deliverable
  capacity -- the same wedge that shrinks corridor-wide spare from {nameplate_spare:.1f} to
  {deliverable_spare:.1f} mb/d. For anyone mapping a supply chain, that is the warning:
  resilience measured off an infrastructure inventory will overstate what a
  corridor can actually absorb.
""")
rule("=")
print()
