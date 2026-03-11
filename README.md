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
| **Partner Performance** | KPI cards, trend chart, reach/CTR by vendor, audience segment charts, Partner → Channel → Program drill-down table |
| **Creative Performance** | KPI cards, CTR/reach by asset, frequency vs. CTR scatter, audience segment charts, asset detail table |
| **Geographic Deep Dive** | Hex map by state, specialty scatter/bubble plot with highlighted comparisons |

## Data

| Table | Description |
|---|---|
| `App_Data.csv` | 2.14M HCP activity events (impressions, clicks, conversions) — January 2026 |
| `BRI_LOOKUP.csv` | Dimension table mapping placement slugs to channel/program/partner names |

See [`raw_data/DATA_DICTIONARY.md`](raw_data/DATA_DICTIONARY.md) for full schema, join logic, and KPIs.

## What's Next

See [`IMPROVEMENTS.md`](IMPROVEMENTS.md) for the full backlog. Top priorities:
- Conversion funnel (11 conversions in data are currently invisible)
- Doximity engagement rate (`content_view / headline_view`)
- Frequency distribution (% of HCPs at 1x / 2–3x / 4–5x / 6x+)
- Coverage % (reach vs. target list size)

## Production Deployment

The app targets Snowflake's GitHub integration for deployment. Swap mock data generation for a Snowpark session query:

```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()
df = session.sql("SELECT * FROM app_data").to_pandas()
```
