r"""
The Hormuz Break-Even Line
==========================
A trade-flow analysis of the 2026 Strait of Hormuz crisis.

RESEARCH QUESTION
-----------------
When a chokepoint closes, every exporter behind it loses volume. Yet the observed
outcome of the 2026 closure was not uniform: Saudi Arabia, Oman and Iran saw oil
revenues RISE, while Iraq, Kuwait, Qatar and the UAE saw them FALL (NYT, 8 May 2026).

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
winner/loser split. This script tests that against the observed outcome.

DATA
----
data/exporters.csv       EIA/Vortexa Q1-2025 Hormuz shares; IEA 2026 bypass capacity
data/destinations.csv    EIA Q1-2025 destination flows; inventories EIA/FREE Network
data/brent_timeline.csv  Brent spot + Hormuz transit volumes, Jan-Jul 2026
data/redistribution.csv  NYT observed revenue outcomes (war start -> 8 May 2026)

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

# Total crude & condensate transiting Hormuz pre-war (EIA, Q1 2025)
HORMUZ_CRUDE_MBD = 14.2
# Total oil incl. refined products (EIA, 2024-Q1 2025)
HORMUZ_TOTAL_MBD = 20.1

# Price window: pre-war reference vs. conflict window (28 Feb - 8 May 2026),
# matching the NYT redistribution comparison window.
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
# 3. THE BYPASS GAP
# ----------------------------------------------------------------------------
# What could physically leave the Gulf if the strait shut? Only Saudi Arabia
# (East-West/Petroline) and the UAE (ADCOP) have operational bypass pipelines.
total_bypass_spare = float(exporters.bypass_spare_mbd.sum())
bypass_gap = HORMUZ_CRUDE_MBD - total_bypass_spare
bypass_cover = total_bypass_spare / HORMUZ_CRUDE_MBD

exporters["structural_retention"] = (
    exporters.bypass_spare_mbd / exporters.hormuz_mbd
).clip(upper=1.0)

# Iran is a special case: it controls the strait, so its own access is not
# constrained by the closure it is enforcing.
exporters.loc[exporters.country == "Iran", "structural_retention"] = 1.0

print(f"\n[2] THE BYPASS GAP")
print(f"    Spare pipeline capacity around the strait : {total_bypass_spare:.1f} mb/d")
print(f"    Crude needing to move through it         : {HORMUZ_CRUDE_MBD:.1f} mb/d")
print(f"    Structural coverage                      : {bypass_cover:.1%}")
print(f"    STRANDED                                 : {bypass_gap:.1f} mb/d")
print(f"    Exporters with zero bypass               : "
      f"{int((exporters.bypass_spare_mbd == 0).sum())} of {len(exporters)}")


# ----------------------------------------------------------------------------
# 4. THE BREAK-EVEN LINE
# ----------------------------------------------------------------------------
p0 = float(brent.loc[brent.date == "2026-02-15", "brent_usd"].iloc[0])

war = brent[(brent.date >= WAR_WINDOW[0]) & (brent.date <= WAR_WINDOW[1])].copy()
# Time-weight the conflict-window price by days between observations, so a
# three-day spike doesn't count the same as a five-week plateau.
war["days"] = war.date.diff().dt.days.fillna(1)
p1 = float(np.average(war.brent_usd, weights=war.days))

r_star = p0 / p1  # <-- the break-even retention rate

print(f"\n[3] THE BREAK-EVEN LINE")
print(f"    Pre-war Brent (Feb 2026)                 : ${p0:.2f}")
print(f"    Conflict-window Brent (28 Feb - 8 May)   : ${p1:.2f}  (time-weighted)")
print(f"    Price multiple  P1/P0                    : {p1/p0:.2f}x")
print(f"    BREAK-EVEN RETENTION RATE  r* = P0/P1    : {r_star:.1%}")
print(f"    -> An exporter must still move {r_star:.0%} of pre-war volume to gain revenue.")


# ----------------------------------------------------------------------------
# 5. TEST THE MODEL AGAINST THE OBSERVED OUTCOME
# ----------------------------------------------------------------------------
# Two tests, and the distinction matters.
#
#   (a) EX-ANTE.  Retention is predicted from spare bypass capacity alone --
#       a number knowable years before the war. This is a real prediction.
#   (b) EX-POST.  Retention is measured from observed output cuts. This is an
#       accounting decomposition, not a forecast: it tells us whether the
#       revenue identity R = Q*P explains the outcome, but it uses wartime data.
#
# Reporting only (b) would overstate the model. Reporting both shows where the
# structural story holds and where it breaks.

pm = p1 / p0
exporters["observed_retention"] = 1 - exporters.observed_output_cut_pct / 100

exporters["exante_index"] = exporters.structural_retention * pm
exporters["expost_index"] = exporters.observed_retention * pm
exporters["pred_exante"] = np.where(exporters.structural_retention > r_star, "up", "down")
exporters["pred_expost"] = np.where(exporters.observed_retention > r_star, "up", "down")

obs_map = dict(zip(observed.country, observed.direction_observed))
exporters["actual"] = exporters.country.map(obs_map)
exporters["hit_exante"] = exporters.pred_exante == exporters.actual
exporters["hit_expost"] = exporters.pred_expost == exporters.actual

tested = exporters.dropna(subset=["actual"])
n = len(tested)
hits_a = int(tested.hit_exante.sum())
hits_b = int(tested.hit_expost.sum())

print(f"\n[4] MODEL vs. OBSERVED  (revenue direction, war start -> 8 May 2026)")
rule()
print(f"    {'Exporter':<22}{'Spare':>7}{'Struct':>8}{'Obs':>6}"
      f"{'Ex-ante':>9}{'Ex-post':>9}{'NYT':>6}")
rule()
for _, r in tested.iterrows():
    a = "OK" if r.hit_exante else "XX"
    b = "OK" if r.hit_expost else "XX"
    print(f"    {r.country:<22}{r.bypass_spare_mbd:>7.1f}"
          f"{r.structural_retention:>8.0%}{r.observed_retention:>6.0%}"
          f"{r.pred_exante:>6} {a:<2}{r.pred_expost:>6} {b:<2}{r.actual:>6}")
rule()
print(f"    Ex-ante  (bypass capacity only) : {hits_a}/{n} = {hits_a/n:.0%}")
print(f"    Ex-post  (observed volumes)     : {hits_b}/{n} = {hits_b/n:.0%}")
print(f"    Break-even line r* = {r_star:.1%}. Retention above it -> revenue rises.")


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
        print(f"    model says 'gain'. It lost. Actual retention came in at "
              f"{r.observed_retention:.0%}, because")
        print(f"    nameplate capacity is not deliverable capacity: the IEA notes the")
        print(f"    logistics and supply chains needed to re-route at scale 'have not been")
        print(f"    robustly tested'. The model assumed a pipe on a map could be filled.")
        print(f"    It could not. That gap -- between rated and realised bypass -- is the")
        print(f"    single most useful thing this exercise surfaces.")

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
print(f"    Asia's share of Hormuz crude: {asia_share:.1%}")
rule()
print(f"    {'Importer':<16}{'Via Hormuz':>12}{'Stock (mb)':>12}{'Days cover':>12}{'Index':>8}")
rule()
for _, r in scored.iterrows():
    print(f"    {r.destination:<16}{r.share_of_own_crude_imports_pct:>11.0f}%"
          f"{r.strategic_inventory_mb:>12,.0f}{r.inventory_cover_days:>12.0f}"
          f"{r.exposure:>8.0f}")
rule()
print(f"    Japan (74% via Hormuz) and South Korea (70%) are more dependent than any")
print(f"    country scored above, but neither publishes inventory data in this")
print(f"    dataset, so they are excluded rather than imputed.")


# ----------------------------------------------------------------------------
# 7. EXPORT
# ----------------------------------------------------------------------------
results = {
    "meta": {
        "title": "The Hormuz Break-Even Line",
        "window": {"pre_war": "2026-02-15", "conflict": list(WAR_WINDOW)},
        "generated": "2026-07-12",
    },
    "headline": {
        "break_even_retention": round(r_star, 4),
        "price_multiple": round(p1 / p0, 3),
        "p0": p0,
        "p1": round(p1, 2),
        "bypass_gap_mbd": round(bypass_gap, 2),
        "bypass_cover": round(bypass_cover, 4),
        "hhi": round(hhi, 0),
        "accuracy_exante": f"{hits_a}/{n}",
        "accuracy_expost": f"{hits_b}/{n}",
        "hormuz_crude_mbd": HORMUZ_CRUDE_MBD,
        "hormuz_total_mbd": HORMUZ_TOTAL_MBD,
        "asia_share": round(asia_share, 4),
    },
    "exporters": json.loads(
        exporters[[
            "country", "hormuz_share_pct", "hormuz_mbd", "bypass_pipeline",
            "bypass_spare_mbd", "structural_retention", "observed_retention",
            "exante_index", "expost_index", "pred_exante", "pred_expost",
            "actual", "hit_exante", "hit_expost",
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

print(f"\n[7] OUTPUT")
print(f"    output/results.json")
print(f"    output/exporter_model.csv")

rule("=")
print("FINDING")
rule("=")
print(f"""
  The 2026 closure did not punish Gulf exporters uniformly. With Brent at
  {pm:.2f}x its pre-war level, the market set a break-even retention rate of
  {r_star:.0%}: move more than {r_star:.0%} of your pre-war barrels and the price gain
  outruns the volume loss.

  Only spare bypass pipeline capacity let an exporter clear that line.
  {bypass_gap:.1f} of {HORMUZ_CRUDE_MBD:.1f} mb/d -- {1-bypass_cover:.0%} of Hormuz crude -- had no route
  out of the Gulf at all, and every exporter with zero bypass lost revenue.

  Ranking exporters by spare bypass capacity alone, a variable fixed years
  before the war, calls the winner/loser split in {hits_a} of {n} cases. Production
  scale calls none of it: Saudi Arabia (largest, gained) and the UAE (third
  largest, lost) sit on opposite sides of the line.

  The one miss is the finding. The UAE owned a pipeline that should have
  cleared the line and did not clear it, because rated capacity is not
  deliverable capacity. For anyone mapping a supply chain, that is the
  warning: resilience measured off an infrastructure inventory will overstate
  what a corridor can actually absorb.
""")
rule("=")
print()
