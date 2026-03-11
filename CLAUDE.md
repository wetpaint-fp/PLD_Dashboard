# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**Physician Level Data (PLD) Dashboard** built for Fingerpaint Marketing. A **Streamlit in Snowflake (SiS)** application displaying HCP (Healthcare Professional) campaign analytics for the Brixadi brand. The prototype (`pld_app.py`) uses mock data; production will query live Snowflake tables.

## Running the App

```bash
uv run --with streamlit --with pandas --with plotly streamlit run pld_app.py
```

> In production the app runs inside **Streamlit in Snowflake (SiS)**: no external network calls, no file I/O, limited package library. Sidebar radio is used instead of `st.tabs` (not available in SiS).

## Architecture

Everything lives in `pld_app.py`. Key sections:

- **Mock data generation** (`generate_mock_data`): Seeded random data (500 NPIs, 4000 activity rows). Cached with `@st.cache_data`. Will be replaced by Snowpark SQL queries in production.
- **Analytics functions**: Pure DataFrame computations — `compute_partner_metrics`, `compute_trend_data`, `compute_hierarchy`, `compute_geo_analysis`.
- **Hex map** (`US_HEX_MAP`, `build_hex_map_figure`): Custom pointy-top hexagonal US state grid via Plotly `go.Scatter`. Not a choropleth — each state is a manually placed hex.
- **Two views** (sidebar radio):
  - **Partner Performance**: KPI cards → trend chart → reach/CTR bars → hierarchical drill-down (Partner → Channel → Program)
  - **Geographic Deep Dive**: State hex map or specialty scatter/bubble plot with `st.session_state.highlighted` comparisons

## Data Sources

See [`raw_data/DATA_DICTIONARY.md`](raw_data/DATA_DICTIONARY.md) for full schema and join logic.

**Two tables (CSVs locally, Snowflake tables in production):**

- **APP_DATA** (`App_Data.csv`) — 2.14M rows, Jan 2026. One row per HCP ad event. Key columns: `ACTIVITY_ID`, `HASH(NPI)`, `ACTIVITY_DATE`, `ACTIVITY_TYPE`, `PLACEMENT_NAME`, `FP_ASSET_ID`, `VENDOR`
- **BRI_LOOKUP** (`BRI_LOOKUP.csv`) — 1,273 rows. Dimension table mapping BRI placement slugs to friendly channel/program/partner names. Join key: strip leading `{digits}-` from `PLACEMENT_NAME` before joining.

**Critical data behavior:**
- Activity types differ by vendor — Doximity has no impressions (only `headline_view`/`content_view`), EHS has clicks only. Never compute CTR across all vendors together.
- `ACTIVITY_TYPE` and `VENDOR` contain dirty values with extraneous quotes — strip on load.
- 98.8% of rows join to BRI_LOOKUP; 1.2% (Doximity AL010-A Wave Six) will be null on BRI columns.

## Snowflake / SiS Production Pattern

```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()
df = session.sql("SELECT * FROM app_data").to_pandas()
```

Swap mock data generation for the above when deploying to SiS. No other changes needed for a basic table viewer.

## Charting

Both Altair (`st.altair_chart`) and Plotly (`st.plotly_chart`) are available in SiS and can be mixed freely on the same page. Use Altair for standard charts, Plotly for custom layouts (e.g. the hex map).
