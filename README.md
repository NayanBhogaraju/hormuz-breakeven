# The Hormuz Break-Even Line

**A trade-flow analysis of the 2026 Strait of Hormuz crisis.**

When Iran declared the Strait of Hormuz closed on 4 March 2026, every Gulf exporter lost barrels. Only some lost money.

Saudi Arabia is the **largest** crude exporter through the strait — its oil revenue **rose ~10%**. The UAE is the **third largest** — its revenue **fell ~25%**. Iraq and Kuwait lost 76% and 73%. Oman rose 80%. Production scale explains none of this.

This project asks what does, and finds a single structural variable that calls the split in five of six cases: **spare bypass pipeline capacity** — a number that was fixed years before the war started.

---

## The model

Revenue is volume times price: `R = Q · P`.

A closure cuts `Q`. It also raises `P` for everyone still selling. So an exporter's revenue rises if and only if:

```
    Q₁ / Q₀   >   P₀ / P₁
   ─────────      ─────────
   retention     break-even
      rate          line
```

The right-hand side is set by the market, not by any individual country. It is the share of pre-war volume an exporter must still move to come out ahead.

With **P₀ = $61/bbl** (the pre-conflict-risk baseline, before the war premium — Brent rose $61→$72 over Jan–Feb *as* the closure was anticipated) and a time-weighted **P₁ = $104.73/bbl** across the conflict window (28 Feb – 8 May 2026):

> ### r\* ≈ 58.2%
> Move more than ~58% of your pre-war barrels and the price gain outruns the volume loss. Move less and nothing saves you.

Only two Gulf exporters own pipelines that reach open water without transiting the strait. On EIA's real deliverable figure, just **2.6 of 14.5 mb/d — 18% of Hormuz crude — could actually go around.**

---

## Results

| Exporter | Bypass route | Hormuz crude | Spare bypass | Retention (rated) | Revenue | Ex-ante call | Observed |
|---|---|---:|---:|---:|---:|---|---|
| Saudi Arabia | East–West (Petroline) | 5.51 mb/d | 3.5 | 64% | **+10%** | **up** ✓ | up |
| Iraq | — none — | 3.26 | 0.0 | 0% | **−76%** | **down** ✓ | down |
| UAE | ADCOP (Habshan–Fujairah) | 1.84 | 1.4 | 76% | **−25%** | **up** ✗ | down |
| Iran | controls the strait | 1.52 | — | 100% | up | **up** ✓ | up |
| Kuwait | — none — | 1.45 | 0.0 | 0% | **−73%** | **down** ✓ | down |
| Qatar | — none — | 0.71 | 0.0 | 0% | down | **down** ✓ | down |

*(Oman, which loads outside the strait, is not a Hormuz exporter but is the other clear winner: **+80%**.)*

- **Ex-ante** (pipeline capacity only, knowable in 2024): **5 / 6**
- **Ex-post** (realised retention derived from reported revenue): **4 / 4** where a magnitude exists.
- **Magnitude check:** structural retention rank-orders the *size* of the revenue moves, not just their sign — Spearman ρ = **+0.74** (the UAE is the outlier that drags it — the same one miss).
- **Every zero-bypass exporter lost revenue. No exception**, and the deepest cuts fell on exactly those exporters.

### The one miss is the finding

The UAE owns ADCOP. On paper it left the country at 76% retention — comfortably above the line. It lost anyway.

Rated capacity is not deliverable capacity. EIA describes the UAE's real excess bypass as only *"limited,"* and the same gap shrinks corridor-wide deliverable spare to **2.6 mb/d against a 4.9 mb/d nameplate sum**. The model assumed a pipe drawn on a map could be filled. It could not.

**For anyone mapping a supply chain, that is the transferable warning: a resilience estimate built off an infrastructure inventory will overstate what a corridor can actually absorb.**

---

## Import-side exposure

84% of Hormuz crude goes to Asia. The exposure index combines dependence (share of a country's crude arriving through the strait) with buffer (how long its stockpile could replace *those specific barrels*).

| Importer | Via Hormuz | Stockpile | Days of cover | Index |
|---|---:|---:|---:|---:|
| China | 47% | 1,541 mb | 308 | 98 |
| India | 44% | 250 mb | 125 | 96 |
| Europe | 8% | 1,285 mb | 1,606 | 23 |
| United States | 7% | 1,700 mb | 3,400 | 0 |

India scores near China not because it is more dependent, but because it holds **250 mb** against China's 1,541. *(Inventory levels here are unverified estimates — the index is illustrative, not precise.)*

Japan (74% of crude via Hormuz) and South Korea (70%) are *more* dependent than anything scored here. Neither publishes inventory data in this dataset, so both are **excluded rather than imputed**. The gap is left visible on purpose.

---

## Run it

```bash
python analysis.py          # regenerates every figure AND rebuilds the dashboard
open output/hormuz_dashboard.html
```

Requires `pandas`, `numpy`. No number in the dashboard is entered by hand — it is emitted from `analysis.py` into `output/results.json` and injected into the template at build time.

```
data/
  exporters.csv        Hormuz shares + bypass capacity
  destinations.csv     Destination flows + strategic inventories
  brent_timeline.csv   Brent spot + Hormuz transit volumes, Jan–Jul 2026
  redistribution.csv   Observed revenue outcomes (FREE Network, war window)
analysis.py            Break-even model, bypass gap, HHI, exposure, sensitivity
dashboard.html         Interactive dashboard (template, __RESULTS__ injected)
output/                results.json · exporter_model.csv · hormuz_dashboard.html
```

Every row in every CSV carries its own `source_note` column stating whether the figure is **confirmed** against a primary source or an **estimate**.

---

## Data provenance

This is real, ongoing history, not a scenario. The crisis, Operation Epic Fury, CRS report R45281, the 17 June memorandum, and the FREE Network brief are all verifiable. The dataset separates what is sourced from what is estimated:

**Confirmed against primary sources**
- Saudi Arabia = 38% of Hormuz crude+condensate, 5.5 mb/d; 84% of flow to Asia; combined KSA+UAE deliverable bypass 2.6 mb/d; US 0.5 mb/d = 7% of US crude imports — **EIA** Strait of Hormuz brief (2024)
- Brent crossed $100 on 8 March, peaked ~$126; multi-phase closure (closed 4 Mar; US blockade 13 Apr–29 May; MoU 17 Jun; re-closed 20 Jun) — **Wikipedia**, *2026 Strait of Hormuz crisis*
- Revenue: Saudi +10%, Oman +80%, UAE −25% — **Goldman Sachs** (via Bloomberg); Iraq −76% (~$1.73bn), Kuwait −73% (~$864mn), US +$50bn, Russia +$15bn — **FREE Network**, *The Hormuz Blockade: Winners, Losers, and Vulnerabilities* (20 Mar 2026)
- Pre-war Brent ~$61 (early Jan) rising to $72 by 27 Feb on war risk; $72.48 on 28 Feb, $112.57 on 27 Mar — **Wikipedia / EIA**
- East-West pipeline pushed toward 7.0 mb/d during the crisis — **S&P Global** (10 Mar 2026)

**Estimates (flagged in-line, not presented as sourced fact)**
- Individual non-Saudi country shares — EIA names only Saudi's share; the rest approximate 2024 export volumes
- Daily Brent between dated anchors — interpolated from reported event levels
- Importer strategic-inventory levels — unverified; the exposure index is illustrative

---

## Limits, and how they're handled

This is a sign test on six observations, now with magnitudes for four of them. It is suggestive, not powered.

- **Partial equilibrium.** Price is treated as exogenous to any single exporter — strong for Saudi Arabia. Probed two ways: a **±15% sweep of P₁**, and swapping the baseline **P₀ from the counterfactual $61 to the pre-strike $72**. The zero-bypass losers and Iran are called under every assumption; only Saudi Arabia flips — its narrow +10% gain would be mis-called on the $72 baseline. That fragility is shown, not hidden.
- **Small sample.** Goldman Sachs / FREE Network published revenue *magnitudes* for the key exporters, so the test is no longer sign-only — structural retention rank-orders the moves (ρ = +0.74). Still six observations.
- **Realised retention is derived**, not sourced: `Q₁/Q₀ = revenue index ÷ price index`, replacing the earlier guessed output cuts. The revenue window and the price baseline differ slightly, so implied retention is indicative.
- **Crude and condensate only.** LNG (~20% of world seaborne LNG, and Qatar's force majeure) moves on different economics and would change Qatar's picture materially.
- **Bypass spare** uses EIA's real deliverable figure (2.6 mb/d combined), not a nameplate sum (4.9). The UAE result — the model's one miss — is exactly where nameplate and deliverable diverge.

The conflict and the data are both still moving. Figures reflect reporting as of **12 July 2026**; the corridor remains contested.

---

## Sources

- **U.S. Energy Information Administration** — *Strait of Hormuz* chokepoint brief (2024)
- **Wikipedia** — *2026 Strait of Hormuz crisis* and *Economic impact of the 2026 Iran war* (prices, closure timeline)
- **Goldman Sachs, via Bloomberg** — per-country revenue changes (Saudi +10%, Oman +80%, UAE −25%)
- **FREE Network** — *The Hormuz Blockade: Winners, Losers, and Vulnerabilities*, 20 March 2026 (Iraq, Kuwait)
- **Congressional Research Service** — *Iran Conflict and the Strait of Hormuz* (R45281)
- **S&P Global · Al Jazeera · NPR** — pipeline capacity, prices, and the 17 June memorandum

---

Nayan Bhogaraju · B.S. Economics, Georgia Institute of Technology
