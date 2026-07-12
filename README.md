# The Hormuz Break-Even Line

**A trade-flow analysis of the 2026 Strait of Hormuz crisis.**

When Iran closed the Strait of Hormuz on 4 March 2026, every Gulf exporter lost barrels. Only some lost money.

Saudi Arabia is the **largest** crude exporter through the strait — its oil revenue **rose**. The UAE is the **third largest** — its revenue **fell**. Iraq, Kuwait and Qatar all fell. Oman and Iran rose. Production scale explains none of this.

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

With **P₀ = $64/bbl** (Feb 2026) and a time-weighted **P₁ = $101.70/bbl** across the conflict window (28 Feb – 8 May 2026):

> ### r\* = 62.9%
> Move more than 63% of your pre-war barrels and the price gain outruns the volume loss. Move less and nothing saves you.

Only two Gulf exporters own pipelines that reach open water without transiting the strait. **9.3 of 14.2 mb/d — 65% of Hormuz crude — had no route out of the Gulf at all.**

---

## Results

| Exporter | Bypass route | Hormuz crude | Spare bypass | Retention (rated) | Retention (real) | Ex-ante call | Observed |
|---|---|---:|---:|---:|---:|---|---|
| Saudi Arabia | East–West (Petroline) | 5.28 mb/d | 3.5 | 66% | 80% | **up** ✓ | up |
| Iraq | — none — | 3.24 | 0.0 | 0% | 30% | **down** ✓ | down |
| UAE | ADCOP (Habshan–Fujairah) | 1.83 | 1.4 | 76% | 45% | **up** ✗ | down |
| Iran | controls the strait | 1.51 | — | 100% | 100% | **up** ✓ | up |
| Kuwait | — none — | 1.43 | 0.0 | 0% | 40% | **down** ✓ | down |
| Qatar | — none — | 0.71 | 0.0 | 0% | 35% | **down** ✓ | down |

- **Ex-ante** (pipeline capacity only, knowable in 2024): **5 / 6**
- **Ex-post** (realised volumes — an accounting check, not a forecast): **6 / 6**
- **Every zero-bypass exporter lost revenue. No exception.**

### The one miss is the finding

The UAE owns ADCOP. On paper it left the country at 76% retention — comfortably above the line. It lost anyway, landing at **45%**.

Rated capacity is not deliverable capacity. The IEA notes that the logistics and supply chains required to re-route at scale *"have not been robustly tested."* The model assumed a pipe drawn on a map could be filled. It could not.

**For anyone mapping a supply chain, that is the transferable warning: a resilience estimate built off an infrastructure inventory will overstate what a corridor can actually absorb.**

---

## Import-side exposure

89.4% of Hormuz crude goes to Asia. The exposure index combines dependence (share of a country's crude arriving through the strait) with buffer (how long its stockpile could replace *those specific barrels*).

| Importer | Via Hormuz | Stockpile | Days of cover | Index |
|---|---:|---:|---:|---:|
| China | 47% | 1,541 mb | 285 | 98 |
| India | 44% | 250 mb | 119 | 96 |
| Europe | 8% | 1,285 mb | 1,606 | 34 |
| United States | 2% | 1,700 mb | 4,250 | 0 |

India scores near China not because it is more dependent, but because it holds **250 mb** against China's 1,541.

Japan (74% of crude via Hormuz) and South Korea (70%) are *more* dependent than anything scored here. Neither publishes inventory data in this dataset, so both are **excluded rather than imputed**. The gap is left visible on purpose.

---

## Run it

```bash
python analysis.py          # regenerates every figure from data/
open output/hormuz_dashboard.html
```

Requires `pandas`, `numpy`. No number in the dashboard is entered by hand — it is all emitted from `analysis.py` into `output/results.json` and injected at build.

```
data/
  exporters.csv        Hormuz shares (EIA/Vortexa Q1-2025) + bypass capacity (IEA 2026)
  destinations.csv     Destination flows + strategic inventories
  brent_timeline.csv   Brent spot + Hormuz transit volumes, Jan–Jul 2026
  redistribution.csv   Observed revenue outcomes (NYT, war start → 8 May 2026)
analysis.py            Break-even model, bypass gap, HHI, exposure index
dashboard.html         Interactive dashboard (template)
output/                results.json · exporter_model.csv · hormuz_dashboard.html
```

Every row in every CSV carries its own `source_note` column.

---

## Limits

This is a sign test on six observations. It is suggestive, not powered.

- **Partial equilibrium.** Price is treated as exogenous to any single exporter — a strong assumption for Saudi Arabia, which is large enough to move it.
- **Directional only.** The NYT reports revenue *signs* for Gulf states, not magnitudes, so the model cannot be scored on error, only on direction.
- **Output-cut figures are trade-press estimates**, not audited production data.
- **Crude and condensate only.** LNG (Qatar's force majeure) and refined products move on different economics and would change Qatar's picture materially.
- **Bypass "spare" capacity** uses the IEA's 3.5–5.5 mb/d range, midpoint-allocated. The UAE result is sensitive to this allocation — which is precisely the point the miss is making.

The conflict and the data are both still moving. Figures reflect reporting as of **12 July 2026**; the corridor remains contested.

---

## Sources

- **U.S. Energy Information Administration** — *Global Energy Security Data*, Q1 2026; Strait of Hormuz chokepoint briefs (Vortexa tanker tracking)
- **International Energy Agency** — *Strait of Hormuz* factsheet; *Oil Market Report*, March 2026
- **The New York Times** — trade-flow analysis, war start to 8 May 2026
- **Congressional Research Service** — *Iran Conflict and the Strait of Hormuz* (R45281)
- **FREE Network** — *The Hormuz Blockade: Winners, Losers, and Vulnerabilities*, March 2026

---

Nayan Bhogaraju · B.S. Economics, Georgia Institute of Technology
