# PLD Dashboard

Physician Level Data (PLD) Dashboard for Fingerpaint Marketing — Brixadi brand campaign analytics.

A **Streamlit in Snowflake (SiS)** app that visualizes HCP-level ad activity across media vendors (DeepIntent, Doximity, EHS).

## Running Locally

```bash
uv run --with streamlit --with pandas --with plotly streamlit run pld_app.py
```

## Data

| Table | Description |
|---|---|
| `App_Data.csv` | 2.14M HCP activity events (impressions, clicks, conversions) — January 2026 |
| `BRI_LOOKUP.csv` | Dimension table mapping placement slugs to channel/program/partner names |

See [`raw_data/DATA_DICTIONARY.md`](raw_data/DATA_DICTIONARY.md) for full schema, join logic, and KPIs.

## Production Deployment

The app targets Snowflake's GitHub integration for deployment. Swap mock data generation for a Snowpark session query:

```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()
df = session.sql("SELECT * FROM app_data").to_pandas()
```
