# PLD Dashboard

Physician Level Data (PLD) Dashboard for Fingerpaint Marketing — Brixadi brand campaign analytics.

A **Streamlit in Snowflake (SiS)** app that visualizes HCP-level ad activity across media vendors (DeepIntent, Doximity, EHS).

## Running Locally

```bash
uv run --with streamlit --with pandas --with plotly streamlit run pld_app_annotated.py
```

> `pld_app_annotated.py` is the active working file. `pld_app.py` is an older unannotated copy — do not edit it.

## Views

| View | Contents |
|---|---|
| **Partner Performance** | KPI cards (incl. Conversions/CVR, Coverage %), conversion funnel, monthly reach & frequency trend, CTR/reach/frequency-distribution bars, CTR % by Stage x Partner heatmap, drill-down table |
| **Creative Performance** | KPI cards, CTR/reach by asset, frequency vs. CTR scatter, CTR % by Segment x Format heatmap, asset detail table |
| **HCP Audience** | KPI cards (Unique HCPs, Lower Funnel %, Most Active Stage, Top Specialty), journey stage bars, hex map by state, specialty scatter/bubble with stage filter |

## Data

| Table | Description |
|---|---|
| `App_Data.csv` | 2.14M HCP activity events (impressions, clicks, conversions) — January 2026 |
| `BRI_LOOKUP.csv` | Dimension table mapping placement slugs to channel/program/partner names |

See [`raw_data/DATA_DICTIONARY.md`](raw_data/DATA_DICTIONARY.md) for full schema, join logic, and KPIs.

## Recent Additions (v2)

- Conversion funnel (Impressions -> Clicks -> Conversions) with CVR KPI
- Doximity engagement rate (`content_view / headline_view`) across all views and heatmaps
- Frequency distribution (% of HCPs at 1x / 2-3x / 4-5x / 6x+)
- Coverage % KPI (unique reach / target universe)
- HCP Audience KPI row and journey stage filter for specialty views
- Inline Heroicons for all section headers (SiS-compatible, no external HTTP)

## Production Deployment

See [`SNOWFLAKE_DEPLOYMENT.md`](SNOWFLAKE_DEPLOYMENT.md) for the full guide covering:
- Expected Snowflake tables (`APP_DATA`, `BRI_LOOKUP`, `HCP_DIM`, `TARGET_LIST`)
- Snowpark connection pattern (drop-in replacement for mock data)
- Column name mappings and join logic
- Feature availability matrix by data source
