# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**Physician Level Data (PLD) Dashboard** built for Fingerpaint Marketing. A **Streamlit in Snowflake (SiS)** application displaying HCP (Healthcare Professional) campaign analytics for the Brixadi brand.

> **Active working file: `pld_app_annotated.py`** — this is the version being developed. `pld_app.py` is an older, unannotated copy; do not edit it.

The prototype uses mock data; production will query live Snowflake tables.

## Running the App

```bash
uv run --with streamlit --with pandas --with plotly streamlit run pld_app_annotated.py
```

> In production the app runs inside **Streamlit in Snowflake (SiS)**: no external network calls, no file I/O, limited package library. Sidebar radio is used instead of `st.tabs` (not available in SiS).

## Architecture

Everything lives in `pld_app_annotated.py`. Key sections:

- **Design tokens**: `BRAND` dict (colors), `SEGMENT_FUNNEL_ORDER` list (prescriber journey stage order), `PLOTLY_HOVERLABEL` dict (shared tooltip style applied to every Plotly figure).
- **Mock data generation** (`generate_mock_data`): Seeded random data (500 NPIs, 4000 activity rows). Cached with `@st.cache_data`. Will be replaced by Snowpark SQL queries in production. Segments use real BRI_LOOKUP taxonomy with weighted distribution.
- **Analytics functions**: Pure DataFrame computations — `compute_partner_metrics`, `compute_trend_data`, `compute_hierarchy`, `compute_geo_analysis`, `compute_creative_metrics`, `compute_segment_metrics`, `compute_segment_by_format`.
- **Hex map** (`US_HEX_MAP`, `build_hex_map_figure`): Custom pointy-top hexagonal US state grid via Plotly `go.Scatter`. Not a choropleth — each state is a manually placed hex.
- **Three views** (sidebar radio):
  - **Partner Performance**: KPI cards → trend chart → CTR/reach bars by vendor → CTR % by Stage × Partner heatmap → hierarchical drill-down (Partner → Channel → Program)
  - **Creative Performance**: KPI cards → CTR/reach by asset → frequency vs. CTR scatter → CTR % by Segment × Format heatmap → asset detail table
  - **HCP Audience**: Reach by Journey Stage bar + CTR by Journey Stage bar → state hex map or specialty scatter/bubble plot with `st.session_state.highlighted` comparisons

## Segment Taxonomy

Segments come from the `Segment` column in BRI_LOOKUP. Canonical order is defined in `SEGMENT_FUNNEL_ORDER`:

```python
SEGMENT_FUNNEL_ORDER = [
    "Unaware", "Educate", "Aware", "Trialing",
    "Adopting", "Advocating", "Deciles Ai", "Site Visitors",
]
```

The first 6 are prescriber journey stages (used in HCP Audience page journey charts). Deciles Ai and Site Visitors are separate targeting pools — excluded from journey charts, included in heatmaps.

## Color Conventions

- **Reach** → `BRAND["primary"]` (`#47254A`, dark purple)
- **CTR** → `BRAND["accent"]` (`#FC8549`, orange)
- **Format families** (Creative page stacked chart) → Programmatic Banner = primary, DocNews Alert = plum (`#880068`), Native Display = secondary (`#BFA8D1`)
- **Heatmaps** → colorscale light→dark purple: `[[0, "#E8DEEE"], [0.5, "#8A5CA8"], [1, "#47254A"]]`; `zmin`/`zmax` pinned to global range so filters don't reset the scale
- Fingerpaint Marketing SVG logo is embedded inline in the sidebar (no external HTTP — required for SiS)

## Tooltip Styling

All Plotly figures use a shared `PLOTLY_HOVERLABEL` constant (defined near `BRAND`):

```python
PLOTLY_HOVERLABEL = dict(
    bgcolor="rgba(255,255,255,0.8)",
    bordercolor="#e2e8f0",
    font=dict(color=BRAND["neutral"], size=12),
    align="left",
)
```

Applied via `fig.update_traces(hoverlabel=PLOTLY_HOVERLABEL)` before every `st.plotly_chart()` call. To restyle tooltips globally, edit this one dict. All `hovertemplate` strings put labels and values on separate lines (`Label:<br>value`).

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
