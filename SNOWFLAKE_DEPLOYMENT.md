# Snowflake Deployment Guide — PLD Dashboard

This document is for the Snowflake/data engineer responsible for wiring the PLD Dashboard to live Snowflake tables. It covers the expected table schemas, join logic, column normalization, and the Snowpark connection pattern to drop into `pld_app_annotated.py`.

---

## Architecture Overview

The app runs inside **Streamlit in Snowflake (SiS)**. All data is loaded via the Snowpark Python session — no external HTTP calls, no file I/O. The prototype currently uses mock data (`generate_mock_data()`) or local CSVs (`load_real_data()`); both are replaced by a single `load_data()` function using `get_active_session()`.

```
Snowflake Tables
  APP_DATA          ← core event table (one row per HCP ad activity)
  BRI_LOOKUP        ← placement dimension (channel / program / partner / segment)
  HCP_DIM           ← HCP dimension (specialty, state) — required for geo views
  TARGET_LIST       ← campaign target universe — required for Coverage % KPI
```

---

## Table Schemas

### `APP_DATA`
**One row per HCP ad event.** Primary source for all impression, click, conversion, and engagement metrics.

| Column | Snowflake Type | Notes |
|---|---|---|
| `ACTIVITY_ID` | VARCHAR | Unique event identifier (MD5 hash) |
| `HASH_NPI` | NUMBER | Anonymized HCP identifier. Renamed to `NPI` on load. |
| `ACTIVITY_DATE` | TIMESTAMP_NTZ | Truncated to `YYYY-MM-DD` string on load for monthly grouping. |
| `ACTIVITY_TYPE` | VARCHAR | Strip extraneous quotes on load. See vendor behavior below. |
| `PLACEMENT_NAME` | VARCHAR | Vendor-assigned numeric prefix + BRI slug. Strip leading `{digits}-` before joining to BRI_LOOKUP. |
| `FP_ASSET_ID` | VARCHAR | Fingerpaint creative asset ID. Prefix encodes format family: `DM`=Programmatic Banner, `NA`=Native Display, `AL`=DocNews Alert. |
| `VENDOR` | VARCHAR | Strip extraneous quotes on load. Map raw values to friendly names (see below). |

**`ACTIVITY_TYPE` values by vendor:**

| Value | Vendor | Meaning |
|---|---|---|
| `Impression` | DeepIntent | Standard display impression served |
| `Click` | DeepIntent, EHS | HCP clicked the ad |
| `Conversion` | DeepIntent | Downstream conversion event |
| `headline_view` | Doximity | DocNews Alert headline was shown |
| `content_view` | Doximity | HCP expanded the DocNews Alert content |

> **Critical:** Never compute CTR across all vendors together. Doximity has no `Impression` or `Click` rows — its metric is **Engagement Rate** = `content_view / headline_view`. EHS has clicks only — CTR is undefined. DeepIntent uses standard `Click / Impression` CTR.

**`VENDOR` raw → friendly name mapping:**

| Raw value | Friendly name |
|---|---|
| `deepin` | DeepIntent |
| `Doximity` | Doximity |
| `e-Healthcare Solutions, LLC.` | EHS |

---

### `BRI_LOOKUP`
**Placement dimension table.** Maps BRI placement slugs to channel, program, partner, and audience segment metadata. 1,273 rows.

| Column | Snowflake Type | App column name | Notes |
|---|---|---|---|
| `PLACEMENT_NAME` | VARCHAR | `placement_name` | **Join key.** Matches the stripped slug from `APP_DATA.PLACEMENT_NAME` after removing the leading numeric prefix. |
| `CHANNEL` | VARCHAR | `CHANNEL` | High-level channel bucket. CSV source name: `Channel Categorization (Report Slide)` |
| `SEGMENT` | VARCHAR | `Segment` | Prescriber journey stage. See segment order below. |
| `PROGRAM` | VARCHAR | `PROGRAM` | Human-readable program name. CSV source name: `CTD Program Friendly Name` |
| `PARTNER` | VARCHAR | `PARTNER` | Human-readable partner name. CSV source name: `CTD Partner Friendly Name` |
| `TARGETING_TYPE` | VARCHAR | `TARGETING TYPE` | HCP targeting method (e.g., HCP-Target-List, Claims-Based, Site-Retargeting) |
| `TARGETING_DETAILS` | VARCHAR | `TARGETING DETAILS` | Additional targeting detail. Nullable. |

**`SEGMENT` canonical order** (prescriber journey stages 1–6, then separate targeting pools):

```
Unaware → Educate → Aware → Trialing → Adopting → Advocating → Deciles Ai → Site Visitors
```

**Join logic — `PLACEMENT_NAME` slug construction:**

```python
# APP_DATA.PLACEMENT_NAME arrives prefixed: "438090045-bbn-002-dm008-a-_bri_hcp_..."
# BRI_LOOKUP.placement_name is the slug only: "bbn-002-dm008-a-_bri_hcp_..."
# Strip leading digits + dash before joining:
app["slug"] = app["PLACEMENT_NAME"].str.replace(r"^\d+-", "", regex=True).str.strip()
merged = app.merge(bri, left_on="slug", right_on="placement_name", how="left")
```

**Expected join coverage:** ~98.8% of `APP_DATA` rows will match. The ~1.2% unmatched rows are Doximity AL010-A Wave Six placements not present in `BRI_LOOKUP` — all `BRI_LOOKUP` columns will be `NULL` for these rows. This is expected and handled gracefully by the app (segments/channels shown as "Unknown").

---

### `HCP_DIM`
**HCP dimension table.** Maps anonymized NPI to specialty and geographic attributes. Required to enable the hex map and specialty views on the HCP Audience page.

| Column | Snowflake Type | Notes |
|---|---|---|
| `HASH_NPI` | NUMBER | Join key to `APP_DATA.HASH_NPI`. Renamed to `NPI` on load. |
| `SPECIALTY` | VARCHAR | HCP medical specialty (e.g., Cardiology, Oncology, PCP, Neurology) |
| `STATE` | VARCHAR | US state abbreviation, 2 characters (e.g., `CA`, `NY`, `TX`) |
| `HCP_NAME` | VARCHAR | Optional. Display only — not used in any analytics computation. |

> **If this table is unavailable:** `SPECIALTY` and `STATE` will default to `"Unknown"` for all HCPs. The HCP Audience hex map and specialty bubble/scatter views will be blank or disabled. Partner Performance, Creative Performance, and HCP Audience journey charts are unaffected.

---

### `TARGET_LIST`
**Campaign target universe.** The set of HCPs the campaign was designed to reach. Used to compute **Coverage % = Unique Reach / Target Universe**, shown as a KPI card on the Partner Performance page.

| Column | Snowflake Type | Notes |
|---|---|---|
| `HASH_NPI` | NUMBER | Anonymized HCP NPI |
| `CAMPAIGN_ID` | VARCHAR | Campaign identifier used as a filter key (e.g., `'BRI_2026'`) |

> **If this table is unavailable:** Coverage % KPI falls back to a manual `st.number_input` in the sidebar. Remove the fallback once the live query is confirmed working.

---

## Snowpark Connection Pattern

Replace the `generate_mock_data()` / `load_real_data()` call in `pld_app_annotated.py` with the following:

```python
from snowflake.snowpark.context import get_active_session


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and join all Snowflake tables into the single DataFrame the app expects.

    Returns a DataFrame with columns:
        ACTIVITY_ID, NPI, PLACEMENT_NAME, VENDOR, CHANNEL, PROGRAM, PARTNER,
        ACTIVITY_TYPE, ACTIVITY_DATE (YYYY-MM-DD), FP_ASSET_ID,
        Segment, TARGETING TYPE, TARGETING DETAILS,
        SPECIALTY, STATE
    """
    session = get_active_session()

    app = session.sql("SELECT * FROM app_data").to_pandas()
    bri = session.sql("SELECT * FROM bri_lookup").to_pandas()
    hcp = session.sql("SELECT hash_npi, specialty, state FROM hcp_dim").to_pandas()

    # ── Clean dirty values ────────────────────────────────────────────────────
    app["ACTIVITY_TYPE"] = app["ACTIVITY_TYPE"].str.strip().str.strip('"')
    app["VENDOR"]        = app["VENDOR"].str.strip().str.strip('"')

    # ── Normalize vendor names ────────────────────────────────────────────────
    vendor_map = {
        "deepin":                        "DeepIntent",
        "Doximity":                      "Doximity",
        "e-Healthcare Solutions, LLC.":  "EHS",
    }
    app["VENDOR"] = app["VENDOR"].map(vendor_map).fillna(app["VENDOR"])

    # ── Rename NPI column (Snowflake uses HASH_NPI; app uses NPI) ─────────────
    app = app.rename(columns={"HASH_NPI": "NPI"})
    hcp = hcp.rename(columns={"HASH_NPI": "NPI"})

    # ── Rename BRI_LOOKUP columns to match app expectations ───────────────────
    bri = bri.rename(columns={
        "CHANNEL":  "CHANNEL",   # already clean if Snowflake column is normalized
        "PROGRAM":  "PROGRAM",
        "PARTNER":  "PARTNER",
        # If Snowflake column names still match the CSV originals, use these:
        # "Channel Categorization (Report Slide)": "CHANNEL",
        # "CTD Program Friendly Name":             "PROGRAM",
        # "CTD Partner Friendly Name":             "PARTNER",
    })

    # ── Build join slug: strip leading numeric prefix from PLACEMENT_NAME ─────
    app["slug"] = (
        app["PLACEMENT_NAME"]
        .str.replace(r"^\d+-", "", regex=True)
        .str.strip()
        .str.strip('"')
    )
    bri["placement_name"] = bri["placement_name"].str.strip()

    # ── Join APP_DATA → BRI_LOOKUP ────────────────────────────────────────────
    merged = app.merge(bri, left_on="slug", right_on="placement_name", how="left")

    # ── Join → HCP_DIM for specialty and state ────────────────────────────────
    merged = merged.merge(hcp[["NPI", "SPECIALTY", "STATE"]], on="NPI", how="left")
    merged["SPECIALTY"] = merged["SPECIALTY"].fillna("Unknown")
    merged["STATE"]     = merged["STATE"].fillna("Unknown")

    # ── Truncate timestamp to YYYY-MM-DD string ───────────────────────────────
    merged["ACTIVITY_DATE"] = merged["ACTIVITY_DATE"].astype(str).str[:10]

    return merged


@st.cache_data
def load_target_universe(campaign_id: str = "BRI_2026") -> int:
    """Return the count of distinct target HCPs for the given campaign."""
    session = get_active_session()
    return session.sql(
        f"SELECT COUNT(DISTINCT HASH_NPI) FROM target_list "
        f"WHERE campaign_id = '{campaign_id}'"
    ).collect()[0][0]
```

---

## Column Name Reference (CSV → Snowflake → App)

| App column | Raw CSV name | Expected Snowflake column |
|---|---|---|
| `NPI` | `HASH(NPI)` | `HASH_NPI` |
| `ACTIVITY_DATE` | string timestamp | `TIMESTAMP_NTZ` or `DATE` |
| `CHANNEL` | `Channel Categorization (Report Slide)` | `CHANNEL` |
| `PROGRAM` | `CTD Program Friendly Name` | `PROGRAM` |
| `PARTNER` | `CTD Partner Friendly Name` | `PARTNER` |
| `Segment` | `Segment` | `SEGMENT` |
| `SPECIALTY` | mock-generated / `"Unknown"` in CSV | `HCP_DIM.SPECIALTY` |
| `STATE` | mock-generated / `"Unknown"` in CSV | `HCP_DIM.STATE` |

---

## Swapping Mock Data for Production

1. In `pld_app_annotated.py`, locate the sidebar data source toggle (~line 1490):
   ```python
   data_source = st.sidebar.radio("Data Source", ["Mock Data", "Real Data (CSV)"])
   ```
2. Replace the entire data-loading block with a direct call to `load_data()` above.
3. Replace the `target_universe` sidebar `st.number_input` with `load_target_universe()`.
4. Remove the sidebar "Data Source" radio and "Campaign Settings" section entirely.
5. Once validated in SiS, delete `generate_mock_data()` and `load_real_data()`.

---

## Feature Availability by Data Source

| Feature | Mock Data | Real CSV | Snowflake (no HCP_DIM) | Snowflake (full) |
|---|---|---|---|---|
| Partner Performance | ✅ | ✅ | ✅ | ✅ |
| Creative Performance | ✅ | ✅ | ✅ | ✅ |
| HCP Audience – Journey charts | ✅ | ✅ | ✅ | ✅ |
| HCP Audience – Hex Map | ✅ | ❌ | ❌ | ✅ |
| HCP Audience – Specialty views | ✅ | ❌ | ❌ | ✅ |
| Coverage % KPI (auto) | ❌ (manual) | ❌ (manual) | ❌ (manual) | ✅ |
