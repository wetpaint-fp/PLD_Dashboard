"""
pld_app_annotated.py
====================
This is a fully annotated copy of pld_app.py for learning purposes.
Every Streamlit concept is explained in detail. The code is identical
to pld_app.py — only the comments differ.

HOW STREAMLIT WORKS — THE CORE MENTAL MODEL
============================================
Streamlit reruns the entire Python script from top to bottom every time:
  - The page first loads
  - A user interacts with any widget (selectbox, radio, button, etc.)
  - st.rerun() is called explicitly

This is called the "execution model." Unlike a traditional web app where
you write event handlers, in Streamlit you just write a script. Streamlit
figures out what changed and only re-renders the parts that need updating.

The consequence: order matters. Elements appear on screen in the order
your code executes. If you put a chart before a filter, it renders above it.
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
# streamlit is the framework itself. Conventionally imported as `st`.
import streamlit as st

# Standard data/math libraries. Streamlit has no opinion on these.
import pandas as pd
import numpy as np
import random
import math

# Plotly is a charting library. Streamlit has a first-class wrapper for it:
# st.plotly_chart(). You build a Plotly figure object, then pass it to st.
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
# st.set_page_config() MUST be the first Streamlit call in your script.
# It controls browser-level settings. You can only call this once.
#
# layout="wide"          → uses the full browser width (vs. centered column)
# initial_sidebar_state  → whether the sidebar starts open or collapsed
st.set_page_config(
    page_title="Fingerpaint Marketing — HCP Analytics",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# BRAND / DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
# This is just a plain Python dict — nothing Streamlit-specific.
# Storing colors here means you change a color in one place and it propagates
# everywhere. A lightweight alternative to a CSS design system.
BRAND = {
    "primary":   "#47254A",  # FPG Legacy Purple
    "secondary": "#BFA8D1",  # FPG Legacy Purple light
    "accent":    "#FC8549",  # FPG Legacy Orange
    "plum":      "#880068",  # FPG Plum
    "neutral":   "#050607",  # FPG Black
    "light":     "#F8F8F8",  # FPG Cotton
    "palette":   ["#FC8549", "#47254A", "#880068", "#FF76BA", "#C2521B", "#556979"],
}


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
# st.markdown() renders HTML/Markdown in the app.
#
# unsafe_allow_html=True is required any time your string contains actual HTML
# tags. Without it, Streamlit escapes the tags and shows them as plain text.
# Streamlit is cautious about this by default because injecting arbitrary HTML
# can be a security risk — but for a controlled internal app it's fine.
#
# This block injects a <style> tag into the page. Streamlit renders inside an
# iframe-like structure, so CSS here only affects this app. The selectors like
# [data-testid="stSidebar"] target Streamlit's internal DOM elements —
# these are undocumented and can break on Streamlit version upgrades.
st.markdown(
    """
<style>
    /* ── Global layout ── */
    /* Reduces the default top padding on the main content area */
    .block-container { padding-top: 1.5rem; }

    /* Styles the sidebar panel itself */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] .stMarkdown h1 { font-size: 1.25rem; }

    /* ── KPI cards ── */
    /* These are custom CSS classes we apply manually via st.markdown() calls.
       Streamlit doesn't have a built-in "card" component, so we build our own
       using raw HTML + these styles. */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,.06);
        transition: box-shadow .2s;
    }
    .kpi-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.08); }
    .kpi-label {
        font-size: .7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
        color: #64748b;
        margin-bottom: .25rem;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #050607;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: .7rem;
        color: #94a3b8;
        margin-top: .35rem;
        font-weight: 500;
    }

    /* ── Section cards ── */
    .section-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,.06);
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: .95rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .06em;
        color: #050607;
        margin-bottom: 1rem;
    }

    /* ── Comparison entity cards ── */
    .entity-card {
        background: #FEF0E9;
        border: 1px solid #FAC2A7;
        border-radius: 10px;
        padding: .85rem 1rem;
        margin-bottom: .5rem;
    }
    .entity-name { font-weight: 700; color: #050607; font-size: .85rem; }
    .entity-stat {
        font-size: .65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .06em;
        color: #64748b;
    }
    .entity-badge {
        display: inline-block;
        background: #ffffff;
        border: 1px solid #FAC2A7;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: .65rem;
        font-weight: 700;
        color: #64748b;
        margin-right: 6px;
    }

    /* ── Data status badge ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: .7rem;
        font-weight: 700;
        border: 1px solid #fde68a;
        background: #fffbeb;
        color: #92400e;
    }
    .status-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #f59e0b;
    }

    /* Hide Streamlit's default chrome for a cleaner look */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# CACHING: @st.cache_data
# ─────────────────────────────────────────────────────────────────────────────
# Because Streamlit reruns your whole script on every interaction, expensive
# operations (loading data, running SQL, doing heavy computation) would re-run
# constantly — which is slow.
#
# @st.cache_data tells Streamlit: "run this function once, store the result,
# and return the cached result on every subsequent call with the same arguments."
# The cache persists for the life of the browser session.
#
# Use @st.cache_data for:
#   - Loading DataFrames (data is serializable)
#   - API calls
#   - Heavy computations
#
# There is also @st.cache_resource for things that shouldn't be copied between
# users (like database connections, ML models). Don't use it for DataFrames.
@st.cache_data
def generate_mock_data() -> pd.DataFrame:
    """
    Generates the mock HCP activity dataset.

    In production, this function body would be replaced with a Snowpark query:
        from snowflake.snowpark.context import get_active_session
        session = get_active_session()
        return session.sql("SELECT * FROM app_data").to_pandas()

    The @st.cache_data decorator means this runs once per session, not once
    per widget interaction.
    """
    random.seed(42)   # Fixed seed = same data every time = reproducible
    np.random.seed(42)


    partners = ["PulsePoint", "Medscape", "Doximity", "Sermo"]
    channels = ["Programmatic Display", "Email", "EHR", "Social"]
    programs = ["Retargeting", "High Value HCPs", "Conquesting", "Newsletter"]

    # Asset IDs mirror the real data structure — vendor-specific creative families.
    # CTR bias is applied per asset below to make creative performance meaningful.
    asset_map = {
        "PulsePoint": [f"DM{str(i).zfill(3)}-A" for i in range(3, 10)],  # DM003-A…DM009-A
        "Medscape":   [f"DM{str(i).zfill(3)}-A" for i in range(3, 10)],
        "Doximity":   ["AL010-A"],
        "Sermo":      [f"NA{str(i).zfill(3)}-A" for i in range(1, 8)],   # NA001-A…NA007-A
    }
    # Per-asset CTR modifier — makes some creatives clearly stronger than others
    asset_ctr_bias = {
        "DM003-A": -0.01, "DM004-A":  0.00, "DM005-A":  0.03,
        "DM006-A":  0.01, "DM007-A": -0.02, "DM008-A":  0.05, "DM009-A":  0.02,
        "NA001-A":  0.04, "NA002-A":  0.06, "NA003-A":  0.01,
        "NA004-A": -0.01, "NA005-A":  0.03, "NA006-A":  0.02, "NA007-A":  0.05,
        "AL010-A":  0.02,
    }
    specialties = [
        "Cardiology", "Oncology", "Dermatology", "Neurology",
        "PCP", "Endocrinology", "Gastroenterology", "Rheumatology",
    ]
    states = [
        "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN",
        "IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV",
        "NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN",
        "TX","UT","VT","VA","WA","WV","WI","WY","DC",
    ]

    # Build 500 fake HCP profiles (NPI number, specialty, state)
    npis = []
    for i in range(500):
        npis.append({
            "id": f"1{random.randint(100000000, 999999999)}",
            "specialty": random.choice(specialties),
            "state": random.choice(states),
        })

    # Build 50 fake placement definitions (maps placement name → partner/channel/program/asset)
    placements = {}
    for i in range(50):
        pname = f"placement_{i}"
        partner = random.choice(partners)
        placements[pname] = {
            "PARTNER_NAME": partner,
            "CHANNEL_CATEGORY": random.choice(channels),
            "PROGRAM_FRIENDLY_NAME": random.choice(programs),
            "FP_ASSET_ID": random.choice(asset_map[partner]),
        }

    # Generate 4000 activity events (one row = one ad served to one HCP)
    rows = []
    base_date = pd.Timestamp("2025-08-01")
    for i in range(4000):
        npi_obj = random.choice(npis)
        pname = f"placement_{random.randint(0, 49)}"
        pd_detail = placements[pname]
        date = base_date + pd.Timedelta(days=random.randint(0, 179))

        # Bias click probability by specialty, state, and asset
        asset_id = pd_detail["FP_ASSET_ID"]
        base_click_prob = 0.05
        if npi_obj["specialty"] == "Oncology":
            base_click_prob += 0.08  # Oncologists click more
        if npi_obj["state"] in ("NY", "CA", "TX", "FL"):
            base_click_prob += 0.03  # High-population states click more
        if npi_obj["specialty"] == "PCP":
            base_click_prob -= 0.02  # PCPs click less
        base_click_prob += asset_ctr_bias.get(asset_id, 0.0)  # Per-creative bias

        is_click = random.random() < base_click_prob

        rows.append({
            "ACTIVITY_ID": f"act_{i}",
            "NPI": npi_obj["id"],
            "PLACEMENT_NAME": pname,
            "VENDOR": pd_detail["PARTNER_NAME"],
            "CHANNEL": pd_detail["CHANNEL_CATEGORY"],
            "PROGRAM": pd_detail["PROGRAM_FRIENDLY_NAME"],
            "FP_ASSET_ID": asset_id,
            # NA assets (Native Display / EHS) are click-only — no impressions tracked.
            # Mirrors real data behaviour: computing CTR on these would be meaningless.
            "ACTIVITY_TYPE": "Click" if (is_click or asset_id.startswith("NA")) else "Impression",
            "ACTIVITY_DATE": date.strftime("%Y-%m-%d"),
            "SPECIALTY": npi_obj["specialty"],
            "STATE": npi_obj["state"],
        })

    return pd.DataFrame(rows)


@st.cache_data
def load_real_data() -> pd.DataFrame:
    """
    Load and join the real App_Data + BRI_LOOKUP CSVs.

    Column normalization maps the raw schema to the same column names the
    dashboard expects, so all analytics functions work without changes.

    In production (SiS), replace the pd.read_csv() calls with Snowpark:
        from snowflake.snowpark.context import get_active_session
        session = get_active_session()
        app = session.sql("SELECT * FROM app_data").to_pandas()
        bri = session.sql("SELECT * FROM bri_lookup").to_pandas()
    """
    app = pd.read_csv("raw_data/App_Data.csv")
    bri = pd.read_csv("raw_data/BRI_LOOKUP.csv")

    # Strip extraneous quotes from dirty vendor/activity fields
    app["ACTIVITY_TYPE"] = app["ACTIVITY_TYPE"].str.strip().str.strip('"')
    app["VENDOR"]        = app["VENDOR"].str.strip().str.strip('"')

    # Map raw vendor codes to friendly names
    vendor_map = {
        "deepin":                      "DeepIntent",
        "Doximity":                    "Doximity",
        "e-Healthcare Solutions, LLC.": "EHS",
    }
    app["VENDOR"] = app["VENDOR"].map(vendor_map).fillna(app["VENDOR"])

    # Build join key: strip leading numeric prefix from PLACEMENT_NAME
    app["slug"] = (
        app["PLACEMENT_NAME"]
        .str.replace(r"^\d+-", "", regex=True)
        .str.strip()
        .str.strip('"')
    )
    bri["placement_name"] = bri["placement_name"].str.strip()

    merged = app.merge(bri, left_on="slug", right_on="placement_name", how="left")

    # Normalize column names to match the dashboard's expected schema
    merged = merged.rename(columns={
        "HASH(NPI)":                          "NPI",
        "Channel Categorization (Report Slide)": "CHANNEL",
        "CTD Program Friendly Name":          "PROGRAM",
    })

    # Truncate timestamp to YYYY-MM-DD for consistency with mock data
    merged["ACTIVITY_DATE"] = merged["ACTIVITY_DATE"].str[:10]

    # SPECIALTY and STATE don't exist in the real dataset.
    # Geographic Deep Dive is disabled when real data is active.
    merged["SPECIALTY"] = "Unknown"
    merged["STATE"]     = "Unknown"

    return merged[[
        "ACTIVITY_ID", "NPI", "PLACEMENT_NAME", "VENDOR", "CHANNEL", "PROGRAM",
        "ACTIVITY_TYPE", "ACTIVITY_DATE", "SPECIALTY", "STATE",
        "FP_ASSET_ID", "Segment", "TARGETING TYPE", "TARGETING DETAILS",
    ]]


# ─────────────────────────────────────────────────────────────────────────────
# HEX MAP DATA & GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────
# This is the grid layout for the US hex map. Each tuple is:
#   (state_abbreviation, column, row)
# These are manually placed positions on a hex grid — not geographic coordinates.
# The grid is a common "tile map" layout used in data visualization to give each
# state equal visual weight (so tiny Rhode Island is as visible as Texas).
US_HEX_MAP = [
    ("ME",11,0),
    ("WI",6,1),("VT",10,1),("NH",11,1),
    ("WA",1,2),("ID",2,2),("MT",3,2),("ND",4,2),("MN",5,2),("IL",6,2),("MI",7,2),("NY",9,2),("MA",10,2),
    ("OR",1,3),("NV",2,3),("WY",3,3),("SD",4,3),("IA",5,3),("IN",6,3),("OH",7,3),("PA",8,3),("NJ",9,3),("CT",10,3),("RI",11,3),
    ("CA",1,4),("UT",2,4),("CO",3,4),("NE",4,4),("MO",5,4),("KY",6,4),("WV",7,4),("VA",8,4),("MD",9,4),("DE",10,4),
    ("AZ",2,5),("NM",3,5),("KS",4,5),("AR",5,5),("TN",6,5),("NC",7,5),("SC",8,5),("DC",9,5),
    ("OK",4,6),("LA",5,6),("MS",6,6),("AL",7,6),("GA",8,6),
    ("AK",0,7),("TX",4,7),("FL",8,7),
    ("HI",0,8),
]


def _hex_corners(cx: float, cy: float, size: float):
    """
    Calculate the 6 corner (x, y) coordinates of a pointy-top hexagon.

    A hexagon has 6 corners evenly spaced at 60° intervals around a center point.
    'Pointy-top' means one vertex points straight up (vs. flat-top where a flat
    edge is on top). The -30° offset in angle_deg achieves this.

    We generate 7 points (not 6) because Plotly needs the first and last point
    to be the same to close the polygon shape.
    """
    coords_x, coords_y = [], []
    for i in range(7):  # 7 to close the polygon
        angle_deg = 60 * i - 30          # -30 rotates to pointy-top orientation
        angle_rad = math.pi / 180 * angle_deg
        coords_x.append(cx + size * math.cos(angle_rad))
        coords_y.append(cy + size * math.sin(angle_rad))
    return coords_x, coords_y


def build_hex_map_figure(
    state_data: dict,
    metric: str,
    max_val: float,
    highlighted: list[str],
):
    """
    Build and return a Plotly Figure object representing the US hex map.

    This function doesn't call any Streamlit functions — it's pure Plotly.
    The figure is passed to st.plotly_chart() in the main app.

    Keeping chart-building logic in separate functions (not inline in main())
    makes the code easier to read, test, and replace later.

    Parameters:
        state_data: dict mapping state abbreviation → dict of metric values
        metric: which metric to color by ("ctr" or "impressions")
        max_val: the maximum value of that metric (used to normalize colors)
        highlighted: list of state abbreviations to emphasize
    """
    HEX_SIZE = 1.0
    HEX_W = math.sqrt(3) * HEX_SIZE   # Width of a pointy-top hex
    HEX_H = 2 * HEX_SIZE               # Height

    # go.Figure() is an empty Plotly figure. We add traces (shapes, scatter
    # points, etc.) to it one by one with fig.add_trace().
    fig = go.Figure()

    has_highlights = len(highlighted) > 0

    def get_fill(val):
        """
        Linearly interpolate between Rose-200 (light pink) and Rose-600 (dark red)
        based on the metric value relative to max_val.
        Returns an RGB color string like "rgb(200, 100, 130)".
        """
        if val is None:
            return "rgb(226,232,240)"  # slate-200 — no data gray
        ratio = max(0.0, min(1.0, val / max_val)) if max_val > 0 else 0
        # Interpolate from FPG lightest orange tint (#FEF0E9) to FPG text orange (#C2521B)
        r = int(254 + (194 - 254) * ratio)
        g = int(240 + (82  - 240) * ratio)
        b = int(233 + (27  - 233) * ratio)
        return f"rgb({r},{g},{b})"

    # Draw one hexagon per state
    for state, col, row in US_HEX_MAP:
        # Calculate pixel-space center coordinates for this hex cell.
        # Odd rows are offset horizontally by half a hex width (staggered grid).
        cx = col * HEX_W + (HEX_W / 2 if row % 2 == 1 else 0)
        cy = -row * HEX_H * 0.75  # Negative because screen Y increases downward,
                                   # but we want north at the top

        sd = state_data.get(state)
        val = sd[metric] if sd else None

        fill = get_fill(val)
        opacity = 1.0
        line_color = "white"
        line_width = 1.5

        # When something is highlighted, dim all other states to 25% opacity
        if has_highlights:
            if state in highlighted:
                line_color = BRAND["neutral"]  # Dark border on highlighted state
                line_width = 3
            else:
                opacity = 0.25          # Dim non-highlighted states

        hx, hy = _hex_corners(cx, cy, HEX_SIZE)

        # Build the hover tooltip HTML for this hex
        if sd:
            hover_text = (
                f"<b>{state}</b><br>"
                f"HCPs: {sd['npiCount']}<br>"
                f"Avg Freq: {sd['impressions']:.1f}<br>"
                f"CTR: {sd['ctr']:.2f}%"
            )
        else:
            hover_text = f"<b>{state}</b><br>No data"

        # go.Scatter with fill="toself" draws a filled polygon.
        # This is how Plotly draws custom shapes — you give it x/y coordinates
        # for the outline and tell it to fill the enclosed area.
        fig.add_trace(
            go.Scatter(
                x=hx, y=hy,
                fill="toself",
                fillcolor=fill,
                opacity=opacity,
                line=dict(color=line_color, width=line_width),
                mode="lines",       # "lines" means no markers at the vertices
                hoverinfo="text",
                hovertext=hover_text,
                showlegend=False,   # Don't add this trace to the legend
            )
        )

        # Add the state abbreviation as a text label centered on the hex.
        # fig.add_annotation() places arbitrary text at any (x, y) position.
        text_color = "#ffffff" if (val is not None and val > max_val * 0.6) else "#64748b"
        fig.add_annotation(
            x=cx, y=cy,
            text=f"<b>{state}</b>",
            showarrow=False,        # No arrow pointing to the annotation
            font=dict(size=10, color=text_color),
        )

    # update_layout() sets figure-level properties (size, background, axes, etc.)
    # xaxis scaleanchor="y" with scaleratio=1 ensures hexagons aren't distorted
    # when the container resizes — x and y units stay equal.
    fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hoverlabel=dict(bgcolor="white", font_size=12, bordercolor="#e2e8f0"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: KPI Card
# ─────────────────────────────────────────────────────────────────────────────
def kpi_card(label: str, value: str, sub: str = ""):
    """
    Renders a styled KPI card using custom HTML.

    Streamlit doesn't have a built-in card component, so we compose one from
    raw HTML + the CSS classes defined above. st.markdown() with
    unsafe_allow_html=True renders it.

    This is a helper function — it calls st.markdown() internally and renders
    directly to whatever column or container is active when it's called.
    """
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS COMPUTATIONS
# ─────────────────────────────────────────────────────────────────────────────
# These are pure Python/pandas functions — no Streamlit calls inside them.
# Keeping business logic separate from rendering logic is good practice:
# - Easier to test
# - Easier to swap the data source later
# - Easier to understand what each piece does
#
# They're NOT decorated with @st.cache_data because they're fast pandas ops
# and their inputs change based on filter state. Caching would add complexity
# without meaningful performance benefit here.

def compute_partner_metrics(df: pd.DataFrame, vendor_filter: str):
    """
    Compute top-level KPIs and per-vendor bar chart data.

    Returns a dict (not a DataFrame) because we need multiple different
    values — a dict is more readable than a tuple of 5 things.
    """
    # Filter the DataFrame if a specific vendor is selected.
    # Otherwise use the full dataset. This pattern appears throughout.
    filt = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]

    total_imps = len(filt)
    total_clicks = int((filt["ACTIVITY_TYPE"] == "Click").sum())
    unique_npis = filt["NPI"].nunique()
    # Frequency = average impressions per HCP. Guard against division by zero.
    frequency = round(total_imps / unique_npis, 1) if unique_npis else 0

    # groupby().agg() computes multiple metrics at once per group.
    # The named aggregation syntax (col_name=("source_col", "agg_func"))
    # creates clean output column names directly.
    by_partner = (
        filt.groupby("VENDOR")
        .agg(
            Impressions=("ACTIVITY_ID", "count"),
            Clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
            Reach=("NPI", "nunique"),
        )
        .reset_index()  # Moves VENDOR from index back into a regular column
    )
    # np.where(condition, value_if_true, value_if_false) — a vectorized if/else.
    # Prevents division by zero when Impressions is 0.
    by_partner["CTR"] = np.where(
        by_partner["Impressions"] > 0,
        (by_partner["Clicks"] / by_partner["Impressions"]) * 100,
        0,
    )
    return {
        "total_imps": total_imps,
        "total_clicks": total_clicks,
        "unique_npis": unique_npis,
        "frequency": frequency,
        "chart": by_partner,  # DataFrame for the bar charts
    }


def compute_trend_data(df: pd.DataFrame, vendor_filter: str):
    """
    Compute monthly Reach and Frequency for the trend chart.

    ACTIVITY_DATE is a string ("YYYY-MM-DD"), so we extract the first 7
    characters ("YYYY-MM") to group by month without parsing to datetime.
    """
    filt = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]
    filt = filt.copy()  # .copy() prevents SettingWithCopyWarning when adding columns
    filt["MONTH"] = filt["ACTIVITY_DATE"].str[:7]  # "2025-08-15" → "2025-08"

    grouped = (
        filt.groupby("MONTH")
        .agg(
            Impressions=("ACTIVITY_ID", "count"),
            Clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
            Reach=("NPI", "nunique"),
        )
        .reset_index()
        .sort_values("MONTH")  # Ensures chronological order on the chart
    )
    grouped["Frequency"] = np.where(
        grouped["Reach"] > 0,
        (grouped["Impressions"] / grouped["Reach"]).round(1),
        0,
    )
    return grouped


def compute_hierarchy(df: pd.DataFrame, vendor_filter: str):
    """
    Build a flat DataFrame representing a 3-level hierarchy:
      Level 0: Vendor (partner)
      Level 1:   ↳ Channel
      Level 2:       ↳ Program

    The hierarchy is "faked" — it's a flat table where indentation in the
    "name" column creates the visual sense of nesting. The "level" column
    could be used for styling (e.g. bold level-0 rows) though it's not
    currently used in the display.

    A true collapsible tree isn't available in Streamlit without custom
    components, so this indented-flat-table approach is a common workaround.
    """
    filt = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]

    rows_out = []

    # Three nested groupby loops build the hierarchy from the outside in.
    for vendor, vg in filt.groupby("VENDOR"):
        v_imps = len(vg)
        v_clicks = int((vg["ACTIVITY_TYPE"] == "Click").sum())
        v_reach = vg["NPI"].nunique()
        v_ctr = (v_clicks / v_imps * 100) if v_imps else 0
        rows_out.append({
            "level": 0,
            "name": vendor,       # No indentation — top level
            "Impressions": v_imps,
            "Clicks": v_clicks,
            "CTR": round(v_ctr, 2),
            "Reach": v_reach,
        })

        for channel, cg in vg.groupby("CHANNEL"):
            c_imps = len(cg)
            c_clicks = int((cg["ACTIVITY_TYPE"] == "Click").sum())
            c_reach = cg["NPI"].nunique()
            c_ctr = (c_clicks / c_imps * 100) if c_imps else 0
            rows_out.append({
                "level": 1,
                "name": f"  ↳ {channel}",   # 2-space indent
                "Impressions": c_imps,
                "Clicks": c_clicks,
                "CTR": round(c_ctr, 2),
                "Reach": c_reach,
            })

            for program, pg in cg.groupby("PROGRAM"):
                p_imps = len(pg)
                p_clicks = int((pg["ACTIVITY_TYPE"] == "Click").sum())
                p_reach = pg["NPI"].nunique()
                p_ctr = (p_clicks / p_imps * 100) if p_imps else 0
                rows_out.append({
                    "level": 2,
                    "name": f"      ↳ {program}",  # 6-space indent
                    "Impressions": p_imps,
                    "Clicks": p_clicks,
                    "CTR": round(p_ctr, 2),
                    "Reach": p_reach,
                })

    return pd.DataFrame(rows_out)


def compute_geo_analysis(df: pd.DataFrame, level: str, filter_value: str):
    """
    Compute aggregated data for the Geographic Deep Dive view.

    'level' controls whether we group by STATE or SPECIALTY, and which
    dimension we expose as the filter. This dual-mode approach means one
    function handles both the hex map view and the scatter plot view.
    """
    if level == "state":
        filtered = df if filter_value == "All" else df[df["SPECIALTY"] == filter_value]
        group_col = "STATE"
        filter_options = sorted(df["SPECIALTY"].unique().tolist())
        entity_name = "State"
        filter_label = "Specialty"
    else:
        filtered = df if filter_value == "All" else df[df["STATE"] == filter_value]
        group_col = "SPECIALTY"
        filter_options = sorted(df["STATE"].unique().tolist())
        entity_name = "Specialty"
        filter_label = "State"

    agg = (
        filtered.groupby(group_col)
        .agg(
            total_imps=("ACTIVITY_ID", "count"),
            clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
            npiCount=("NPI", "nunique"),
        )
        .reset_index()
        .rename(columns={group_col: "name"})  # Normalize to "name" regardless of group
    )
    # "impressions" here = avg frequency (total impressions / unique HCPs)
    agg["impressions"] = np.where(agg["npiCount"] > 0, agg["total_imps"] / agg["npiCount"], 0)
    agg["ctr"] = np.where(agg["total_imps"] > 0, (agg["clicks"] / agg["total_imps"]) * 100, 0)

    max_imps = agg["impressions"].max() if len(agg) else 5
    max_ctr = agg["ctr"].max() if len(agg) else 2

    return {
        "data": agg,
        "filter_options": filter_options,
        "max_imps": max_imps,
        "max_ctr": max_ctr,
        "entity": entity_name,
        "filter_label": filter_label,
    }


def compute_creative_metrics(df: pd.DataFrame) -> dict:
    """
    Compute per-asset and per-format-family performance metrics.

    FP_ASSET_ID encodes the creative family:
      DM### → Programmatic Banner (DeepIntent)
      NA### → Native Display (EHS)
      AL### → DocNews Alert (Doximity)

    Returns both asset-level and format-family-level aggregations so the view
    can show two levels of granularity without re-computing.
    """
    filt = df[df["FP_ASSET_ID"].notna() & (df["FP_ASSET_ID"] != "Unknown")].copy()

    def _format_family(asset_id: str) -> str:
        if asset_id.startswith("DM"): return "Programmatic Banner"
        if asset_id.startswith("NA"): return "Native Display"
        if asset_id.startswith("AL"): return "DocNews Alert"
        return "Other"

    filt["Format"] = filt["FP_ASSET_ID"].apply(_format_family)

    # ── Per-asset aggregation ──────────────────────────────────────────────────
    by_asset = (
        filt.groupby("FP_ASSET_ID")
        .agg(
            Impressions=("ACTIVITY_ID",  "count"),
            Clicks=("ACTIVITY_TYPE",     lambda s: (s == "Click").sum()),
            Reach=("NPI",                "nunique"),
            Format=("Format",            "first"),
        )
        .reset_index()
        .rename(columns={"FP_ASSET_ID": "Asset"})
    )
    # Click-only assets (NA prefix = Native Display / EHS) have no impression rows.
    # CTR is undefined for these — set to NaN so the UI can display "N/A" clearly.
    click_only = by_asset["Asset"].str.startswith("NA")
    by_asset["CTR"] = np.where(
        click_only,
        np.nan,
        np.where(
            by_asset["Impressions"] > 0,
            (by_asset["Clicks"] / by_asset["Impressions"]) * 100,
            np.nan,
        ),
    )
    by_asset["AvgFreq"] = np.where(
        by_asset["Reach"] > 0,
        by_asset["Impressions"] / by_asset["Reach"],
        0,
    )
    # Sort: assets with valid CTR first (descending), click-only assets at bottom
    by_asset = pd.concat([
        by_asset[~click_only].sort_values("CTR", ascending=False),
        by_asset[click_only].sort_values("Clicks", ascending=False),
    ])

    # ── Per-format-family aggregation ─────────────────────────────────────────
    by_format = (
        filt.groupby("Format")
        .agg(
            Impressions=("ACTIVITY_ID", "count"),
            Clicks=("ACTIVITY_TYPE",    lambda s: (s == "Click").sum()),
            Reach=("NPI",               "nunique"),
        )
        .reset_index()
    )
    # Native Display row will have Impressions == Clicks (click-only) — mark as NaN
    by_format["CTR"] = np.where(
        by_format["Format"] == "Native Display",
        np.nan,
        np.where(
            by_format["Impressions"] > 0,
            (by_format["Clicks"] / by_format["Impressions"]) * 100,
            np.nan,
        ),
    )

    # Best asset = highest CTR among impression-trackable assets with sufficient volume
    significant = by_asset[by_asset["Impressions"] >= 50].dropna(subset=["CTR"])
    best = significant.iloc[0] if len(significant) else (by_asset.dropna(subset=["CTR"]).iloc[0] if len(by_asset.dropna(subset=["CTR"])) else None)

    return {
        "by_asset":     by_asset,
        "by_format":    by_format,
        "best_asset":   best,
        "total_assets": len(by_asset),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
# Wrapping everything in a main() function is optional in Streamlit, but it's
# good practice because:
#   1. It groups all rendering logic clearly
#   2. The if __name__ == "__main__" guard lets you import this file from other
#      scripts without immediately running the app
def main():

    # ── Sidebar ────────────────────────────────────────────────────────────────
    # Sidebar is declared first so widget values (data source, active tab) are
    # available before we decide which dataset to load below.
    with st.sidebar:
        # Branding header — raw HTML via st.markdown
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <span style="font-size:1.6rem;">🎨</span>
                <div>
                    <div style="font-weight:800;font-size:1.15rem;color:#050607;line-height:1.15;">fingerpaint</div>
                    <div style="font-weight:500;font-size:.95rem;color:#FC8549;line-height:1.15;">marketing</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # ── Navigation radio ──
        active_tab = st.radio(
            "Navigation",
            ["Partner Performance", "Creative Performance", "Geographic Deep Dive"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # ── Data source toggle ──
        # Allows switching between the seeded mock dataset and the real CSVs.
        # In SiS production the real data path uses Snowpark (see load_real_data).
        data_source = st.radio(
            "Data Source",
            ["Mock Data", "Real Data"],
            key="data_source",
        )

        # Dynamic status badge reflects the active data source
        if data_source == "Mock Data":
            badge_label = "MOCK DATA"
            badge_color = "#f59e0b"
        else:
            badge_label = "LIVE DATA"
            badge_color = "#22c55e"

        st.markdown(
            f'<div class="status-badge">'
            f'<div class="status-dot" style="background:{badge_color};"></div>'
            f'{badge_label}</div>',
            unsafe_allow_html=True,
        )

    # ── Load data ──────────────────────────────────────────────────────────────
    # Both functions are cached — the first call loads data, subsequent reruns
    # return instantly from cache.
    if data_source == "Real Data":
        with st.spinner("Loading real data…"):
            df = load_real_data()
    else:
        df = generate_mock_data()


    # ── Header ─────────────────────────────────────────────────────────────────
    # This renders in the main content area (not the sidebar).
    # We dynamically change the title based on which tab is active.
    # Because the whole script reruns when active_tab changes, this
    # automatically updates without any special event handling.
    header_titles = {
        "Partner Performance":   "Performance Overview",
        "Creative Performance":  "Creative Performance",
        "Geographic Deep Dive":  "Geographic Analysis",
    }
    header_title = header_titles.get(active_tab, active_tab)
    st.markdown(
        f"""
        <div style="margin-bottom:.25rem;">
            <h1 style="font-size:1.75rem;font-weight:800;color:#050607;margin:0;">{header_title}</h1>
            <p style="font-size:.75rem;font-weight:600;color:#FC8549;text-transform:uppercase;letter-spacing:.08em;margin:0;">
                Revealing the True Colors of Every Brand
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║  VIEW 1 — PARTNER PERFORMANCE                                        ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    if active_tab == "Partner Performance":

        # ── Vendor filter ──────────────────────────────────────────────────────
        # st.selectbox() renders a dropdown. Returns the selected value.
        # Building the options list dynamically from the data means new vendors
        # appear automatically without code changes.
        vendors = ["All"] + sorted(df["VENDOR"].unique().tolist())
        vendor_filter = st.selectbox("Filter Vendor", vendors, key="vendor_sel")

        # Compute metrics for the selected vendor. This runs on every rerun,
        # but it's fast pandas math so it doesn't need caching.
        metrics = compute_partner_metrics(df, vendor_filter)

        # ── KPI Row ────────────────────────────────────────────────────────────
        # st.columns(n) divides the available width into n equal columns and
        # returns a list of column objects. You then use `with col:` blocks to
        # render content inside each column.
        #
        # Columns are always laid out horizontally. You can nest columns inside
        # columns for more complex layouts.
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi_card("Total Impressions", f"{metrics['total_imps']:,}")
        with k2:
            kpi_card("Total Clicks", f"{metrics['total_clicks']:,}")
        with k3:
            kpi_card("Unique Reach", f"{metrics['unique_npis']:,}", "Physicians")
        with k4:
            kpi_card("Avg Frequency", str(metrics["frequency"]), "Imps per NPI")

        # st.markdown("") is a common way to add a small vertical gap.
        # There's no st.spacer() in base Streamlit.
        st.markdown("")

        # ── Monthly Trend Chart ────────────────────────────────────────────────
        trend = compute_trend_data(df, vendor_filter)

        st.markdown('<div class="section-title">📈  Monthly Reach & Frequency</div>', unsafe_allow_html=True)

        # make_subplots(specs=[[{"secondary_y": True}]]) creates a Plotly figure
        # with a secondary Y axis on the right side. This lets us plot Reach
        # (bar, left axis) and Frequency (line, right axis) on the same chart
        # with independent scales.
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

        # Add bars for Reach on the primary (left) Y axis
        fig_trend.add_trace(
            go.Bar(
                x=trend["MONTH"],
                y=trend["Reach"],
                name="Unique Reach (NPIs)",
                marker_color=BRAND["primary"],
                marker_cornerradius=4,  # Rounded bar tops (Plotly 5.12+)
            ),
            secondary_y=False,  # → left axis
        )

        # Add line for Frequency on the secondary (right) Y axis
        fig_trend.add_trace(
            go.Scatter(
                x=trend["MONTH"],
                y=trend["Frequency"],
                name="Avg Frequency",
                mode="lines+markers",  # Draw both line and dot markers
                line=dict(color=BRAND["accent"], width=3),
                marker=dict(size=7),
            ),
            secondary_y=True,   # → right axis
        )

        fig_trend.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            # Place the legend above the chart, left-aligned
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(gridcolor="#f1f5f9"),
            yaxis2=dict(gridcolor="#f1f5f9"),
        )

        # st.plotly_chart() renders the Plotly figure.
        # use_container_width=True makes it fill the available column width
        # rather than using Plotly's default fixed pixel width.
        st.plotly_chart(fig_trend, use_container_width=True)

        # ── Side-by-side Bar Charts ────────────────────────────────────────────
        # st.columns([1, 1]) creates two equal-width columns.
        # You can pass a list of relative weights: [1, 2] makes the second
        # column twice as wide as the first.
        c1, c2 = st.columns(2)
        chart_df = metrics["chart"]

        with c1:
            st.markdown('<div class="section-title">Reach by Partner</div>', unsafe_allow_html=True)
            fig_reach = go.Figure(
                go.Bar(
                    x=chart_df["VENDOR"],
                    y=chart_df["Reach"],
                    marker_color=BRAND["primary"],
                    marker_cornerradius=6,
                )
            )
            fig_reach.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9"),
            )
            st.plotly_chart(fig_reach, use_container_width=True)

        with c2:
            st.markdown('<div class="section-title">CTR % by Partner</div>', unsafe_allow_html=True)
            fig_ctr = go.Figure(
                go.Bar(
                    x=chart_df["VENDOR"],
                    y=chart_df["CTR"],
                    marker_color=BRAND["accent"],
                    marker_cornerradius=6,
                    # text= adds value labels on each bar
                    text=chart_df["CTR"].round(2).astype(str) + "%",
                    textposition="outside",  # Labels float above bar tops
                )
            )
            fig_ctr.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9", title="CTR %"),
            )
            st.plotly_chart(fig_ctr, use_container_width=True)

        # ── Drill-Down Table ───────────────────────────────────────────────────
        st.markdown(
            '<div class="section-title">📊  Detailed Performance  '
            '<span style="font-size:.65rem;font-weight:500;color:#94a3b8;text-transform:none;letter-spacing:normal;">'
            "Partner → Channel → Program</span></div>",
            unsafe_allow_html=True,
        )

        hier = compute_hierarchy(df, vendor_filter)
        if len(hier):
            display = hier[["name", "Impressions", "Clicks", "CTR", "Reach"]].copy()
            display.columns = ["Name", "Impressions", "Clicks", "CTR %", "Reach"]

            # st.dataframe() renders an interactive table.
            # .style.format() applies Python format strings to columns —
            # "{:,}" adds thousands commas, "{:.2f}%" formats as a percentage.
            # This is pandas Styler, not Streamlit-specific.
            #
            # hide_index=True removes the 0,1,2... row index column.
            # height= sets the table height in pixels; it will scroll if there
            # are more rows than fit.
            def _zebra(df):
                # Alternating lavender rows using FPG Legacy Purple at low opacity
                styles = pd.DataFrame("", index=df.index, columns=df.columns)
                for i in range(len(df)):
                    if i % 2 == 0:
                        styles.iloc[i] = "background-color: rgba(191, 168, 209, 0.18)"
                return styles

            st.dataframe(
                display.style.format({
                    "Impressions": "{:,}",
                    "Clicks": "{:,}",
                    "CTR %": "{:.2f}%",
                    "Reach": "{:,}",
                }).apply(_zebra, axis=None),
                use_container_width=True,
                hide_index=True,
                height=460,
            )
        else:
            # st.info() renders a blue info box. Other variants:
            # st.success() → green, st.warning() → yellow, st.error() → red
            st.info("No data available for this filter.")


    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║  VIEW 2 — CREATIVE PERFORMANCE                                       ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    elif active_tab == "Creative Performance":

        creative = compute_creative_metrics(df)
        by_asset  = creative["by_asset"]
        by_format = creative["by_format"]
        best      = creative["best_asset"]

        # ── KPI Row ────────────────────────────────────────────────────────────
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi_card("Assets in Flight", str(creative["total_assets"]))
        with k2:
            kpi_card(
                "Best Creative (CTR)",
                best["Asset"] if best is not None else "—",
                f"{best['CTR']:.2f}% CTR" if best is not None else "",
            )
        with k3:
            top_fmt = by_format.sort_values("CTR", ascending=False).iloc[0] if len(by_format) else None
            kpi_card(
                "Top Format",
                top_fmt["Format"] if top_fmt is not None else "—",
                f"{top_fmt['CTR']:.2f}% CTR" if top_fmt is not None else "",
            )
        with k4:
            avg_ctr = (by_asset["CTR"] * by_asset["Impressions"]).sum() / by_asset["Impressions"].sum() if len(by_asset) else 0
            kpi_card("Blended CTR", f"{avg_ctr:.2f}%", "Across all assets")

        st.markdown("")

        # ── CTR & Reach by Asset (paired, shared sort order) ───────────────────
        # Separate impression-trackable assets from click-only Native Display
        imp_assets    = by_asset.dropna(subset=["CTR"])
        native_assets = by_asset[by_asset["Format"] == "Native Display"]

        sort_by = st.radio(
            "Sort by",
            ["CTR", "Reach"],
            horizontal=True,
            key="asset_sort",
        )
        sort_col = "CTR" if sort_by == "CTR" else "Reach"
        asset_ordered = imp_assets.sort_values(sort_col, ascending=True)
        bar_h = max(300, len(asset_ordered) * 36)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="section-title">CTR % by Asset</div>', unsafe_allow_html=True)
            fig_ctr = go.Figure(go.Bar(
                x=asset_ordered["CTR"],
                y=asset_ordered["Asset"],
                orientation="h",
                marker_color=[
                    BRAND["primary"] if f == "Programmatic Banner"
                    else BRAND["plum"]
                    for f in asset_ordered["Format"]
                ],
                marker_cornerradius=4,
                text=asset_ordered["CTR"].round(2).astype(str) + "%",
                textposition="outside",
            ))
            fig_ctr.update_layout(
                height=bar_h,
                margin=dict(l=20, r=60, t=10, b=20),
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(gridcolor="#f1f5f9", title="CTR %"),
                yaxis=dict(tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_ctr, use_container_width=True, key="ctr_by_asset")

        with c2:
            st.markdown('<div class="section-title">Reach by Asset</div>', unsafe_allow_html=True)
            fig_reach = go.Figure(go.Bar(
                x=asset_ordered["Reach"],
                y=asset_ordered["Asset"],
                orientation="h",
                marker_color=BRAND["primary"],
                marker_opacity=0.75,
                marker_cornerradius=4,
            ))
            fig_reach.update_layout(
                height=bar_h,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(gridcolor="#f1f5f9", title="Unique HCPs"),
                yaxis=dict(tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_reach, use_container_width=True, key="reach_by_asset")

        # ── Native Display — clicks only ────────────────────────────────────────
        if len(native_assets):
            st.markdown('<div class="section-title">Native Display  <span style="font-size:.65rem;font-weight:500;color:#94a3b8;text-transform:none;letter-spacing:normal;">Clicks only — CTR not applicable</span></div>', unsafe_allow_html=True)
            nd_ordered = native_assets.sort_values("Clicks", ascending=True)
            nd_c1, nd_c2 = st.columns(2)
            with nd_c1:
                fig_nd_clicks = go.Figure(go.Bar(
                    x=nd_ordered["Clicks"],
                    y=nd_ordered["Asset"],
                    orientation="h",
                    marker_color=BRAND["secondary"],
                    marker_cornerradius=4,
                    text=nd_ordered["Clicks"].astype(str),
                    textposition="outside",
                ))
                fig_nd_clicks.update_layout(
                    height=max(200, len(nd_ordered) * 36),
                    margin=dict(l=20, r=40, t=10, b=20),
                    plot_bgcolor="white", paper_bgcolor="white",
                    xaxis=dict(gridcolor="#f1f5f9", title="Clicks"),
                    yaxis=dict(tickfont=dict(size=11)),
                )
                st.plotly_chart(fig_nd_clicks, use_container_width=True, key="nd_clicks")
            with nd_c2:
                fig_nd_reach = go.Figure(go.Bar(
                    x=nd_ordered["Reach"],
                    y=nd_ordered["Asset"],
                    orientation="h",
                    marker_color=BRAND["secondary"],
                    marker_opacity=0.75,
                    marker_cornerradius=4,
                ))
                fig_nd_reach.update_layout(
                    height=max(200, len(nd_ordered) * 36),
                    margin=dict(l=20, r=20, t=10, b=20),
                    plot_bgcolor="white", paper_bgcolor="white",
                    xaxis=dict(gridcolor="#f1f5f9", title="Unique HCPs"),
                    yaxis=dict(tickfont=dict(size=11)),
                )
                st.plotly_chart(fig_nd_reach, use_container_width=True, key="nd_reach")

        # ── Format Family Summary & Frequency vs CTR ───────────────────────────
        c3, c4 = st.columns(2)

        with c3:
            st.markdown('<div class="section-title">CTR % by Format Family  <span style="font-size:.65rem;font-weight:500;color:#94a3b8;text-transform:none;letter-spacing:normal;">Native Display excluded — clicks only</span></div>', unsafe_allow_html=True)
            fmt_colors = {
                "Programmatic Banner": BRAND["primary"],
                "DocNews Alert":       BRAND["plum"],
            }
            fmt_ctr = by_format.dropna(subset=["CTR"])
            fig_fmt = go.Figure(go.Bar(
                x=fmt_ctr["Format"],
                y=fmt_ctr["CTR"],
                marker_color=[fmt_colors.get(f, BRAND["secondary"]) for f in fmt_ctr["Format"]],
                marker_cornerradius=6,
                text=fmt_ctr["CTR"].round(2).astype(str) + "%",
                textposition="outside",
            ))
            fig_fmt.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9", title="CTR %"),
            )
            st.plotly_chart(fig_fmt, use_container_width=True, key="ctr_by_format")

        with c4:
            st.markdown('<div class="section-title">Frequency vs CTR</div>', unsafe_allow_html=True)
            # Click-only assets have no frequency/CTR relationship — exclude from scatter
            scatter_assets = by_asset.dropna(subset=["CTR"])
            fig_freq = go.Figure()
            fig_freq.add_trace(go.Scatter(
                x=scatter_assets["AvgFreq"],
                y=scatter_assets["CTR"],
                mode="markers+text",
                marker=dict(
                    size=scatter_assets["Reach"].clip(lower=5) / scatter_assets["Reach"].max() * 40 + 8,
                    color=BRAND["primary"],
                    opacity=0.75,
                    line=dict(width=1, color="white"),
                ),
                text=scatter_assets["Asset"],
                textposition="top center",
                textfont=dict(size=9, color="#64748b"),
                customdata=scatter_assets[["Asset", "Reach", "AvgFreq", "CTR"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Reach: %{customdata[1]}<br>"
                    "Avg Freq: %{customdata[2]:.1f}<br>"
                    "CTR: %{customdata[3]:.2f}%<extra></extra>"
                ),
            ))
            fig_freq.update_layout(
                height=300,
                margin=dict(l=40, r=20, t=10, b=40),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(gridcolor="#f1f5f9", title="Avg Frequency per HCP"),
                yaxis=dict(gridcolor="#f1f5f9", title="CTR %"),
            )
            st.plotly_chart(fig_freq, use_container_width=True, key="freq_vs_ctr")

        # ── Asset Detail Table ─────────────────────────────────────────────────
        st.markdown(
            '<div class="section-title">Asset Detail</div>',
            unsafe_allow_html=True,
        )
        detail = by_asset[["Asset", "Format", "Impressions", "Clicks", "CTR", "Reach", "AvgFreq"]].copy()
        detail.columns = ["Asset", "Format", "Impressions", "Clicks", "CTR %", "Reach", "Avg Freq"]
        detail["CTR %"] = detail["CTR %"].apply(
            lambda v: "" if pd.isna(v) else f"{v:.2f}%"
        )

        def _zebra_creative(df):
            styles = pd.DataFrame("", index=df.index, columns=df.columns)
            for i in range(len(df)):
                if i % 2 == 0:
                    styles.iloc[i] = "background-color: rgba(191, 168, 209, 0.18)"
            return styles

        st.dataframe(
            detail.style.format({
                "Impressions": "{:,}",
                "Clicks":      "{:,}",
                "Reach":       "{:,}",
                "Avg Freq":    "{:.1f}",
            }).apply(_zebra_creative, axis=None),
            use_container_width=True,
            hide_index=True,
        )

    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║  VIEW 3 — GEOGRAPHIC DEEP DIVE                                       ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    else:

        if data_source == "Real Data":
            st.info(
                "Geographic Deep Dive requires SPECIALTY and STATE data, which are not "
                "present in the current dataset. Switch to Mock Data to explore this view.",
                icon="ℹ️",
            )
            return

        # ── Session State ──────────────────────────────────────────────────────
        # st.session_state is a dictionary-like object that persists across
        # reruns for the duration of a browser session.
        #
        # Unlike regular Python variables (which reset on every rerun),
        # session_state values survive. This is how you maintain state between
        # interactions — e.g., a list of items the user has added.
        #
        # Always check if a key exists before reading it, because session_state
        # is empty on the first load.
        if "highlighted" not in st.session_state:
            st.session_state.highlighted = []  # List of highlighted entity names

        # ── Two-column layout: controls on left, visualization on right ────────
        # [1, 2.5] means the right column is 2.5x wider than the left.
        ctrl_col, viz_col = st.columns([1, 2.5])

        with ctrl_col:
            st.markdown('<div class="section-title">🔍  Analysis Controls</div>', unsafe_allow_html=True)

            # Toggle between State-level and Specialty-level analysis
            # format_func= lets you display custom labels while the returned
            # value is still the raw option ("state" / "specialty")
            analysis_level = st.radio(
                "Analysis Level",
                ["state", "specialty"],
                format_func=lambda x: "States" if x == "state" else "Specialties",
                horizontal=True,   # Renders options side-by-side instead of stacked
                key="analysis_level",
            )

            # First compute with "All" to get the full list of filter options
            geo = compute_geo_analysis(df, analysis_level, "All")

            # The filter options change depending on analysis_level:
            # - If viewing states, the filter is by Specialty
            # - If viewing specialties, the filter is by State
            analysis_filter = st.selectbox(
                f"Filter {geo['filter_label']}",
                ["All"] + geo["filter_options"],
                key="analysis_filter",
            )

            # Recompute with the actual selected filter value
            geo = compute_geo_analysis(df, analysis_level, analysis_filter)

            # ── Entity selector for comparison list ──
            entity_options = geo["data"]["name"].tolist()
            selected_entity = st.selectbox(
                f"Highlight {geo['entity']}",
                [""] + entity_options,
                format_func=lambda x: "Select to compare…" if x == "" else x,
                key="entity_sel",
            )

            # When an entity is selected, add it to the highlighted list in
            # session_state (if not already there), then call st.rerun() to
            # immediately re-render the page with the new highlight.
            #
            # st.rerun() triggers an immediate full script rerun from the top.
            # Use it when you've mutated session_state and want the UI to
            # reflect the change right away — without waiting for the next
            # natural user interaction.
            if selected_entity and selected_entity not in st.session_state.highlighted:
                st.session_state.highlighted.append(selected_entity)
                st.rerun()

            # Color-by metric selector (only relevant for the hex map)
            if analysis_level == "state":
                map_metric = st.radio(
                    "Color By",
                    ["ctr", "impressions"],
                    format_func=lambda x: "CTR %" if x == "ctr" else "Avg Frequency",
                    horizontal=True,
                    key="map_metric",
                )
            else:
                map_metric = "ctr"  # Scatter plot always colors by CTR (via BRAND palette)

            # ── Comparison List ────────────────────────────────────────────────
            # Only render this section if anything has been highlighted.
            if st.session_state.highlighted:
                st.markdown("---")
                st.markdown('<div class="section-title">Comparison List</div>', unsafe_allow_html=True)

                to_remove = None  # Track which entity to remove (can't modify list while iterating)

                for ent_name in st.session_state.highlighted:
                    # Look up this entity's metrics in the current aggregated data
                    ent_row = geo["data"][geo["data"]["name"] == ent_name]
                    if len(ent_row) == 0:
                        continue  # Entity might not exist under the current filter
                    ent = ent_row.iloc[0]  # .iloc[0] gets the first (only) matching row

                    # Custom HTML card for each highlighted entity
                    st.markdown(
                        f"""
                        <div class="entity-card">
                            <div class="entity-name">{ent['name']}</div>
                            <div class="entity-stat">{int(ent['npiCount'])} HCPs Reached</div>
                            <div style="margin-top:6px;">
                                <span class="entity-badge">{ent['impressions']:.1f} Avg Freq</span>
                                <span class="entity-badge">{ent['ctr']:.2f}% CTR</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # st.button() renders a clickable button. Returns True only
                    # on the rerun immediately after the user clicks it.
                    # This is how Streamlit handles button clicks — no callbacks,
                    # just a boolean that's True for exactly one rerun.
                    #
                    # key= is critical here: without it, multiple buttons in a
                    # loop would have duplicate keys and raise an error.
                    # type="tertiary" makes it a low-prominence ghost button.
                    if st.button(f"✕ Remove {ent_name}", key=f"rm_{ent_name}", type="tertiary"):
                        to_remove = ent_name

                # Remove after the loop to avoid mutating the list we're iterating
                if to_remove:
                    st.session_state.highlighted.remove(to_remove)
                    st.rerun()

                if st.button("Clear All", key="clear_all", type="secondary"):
                    st.session_state.highlighted = []
                    st.rerun()

        # ── Visualization Panel ────────────────────────────────────────────────
        with viz_col:
            highlighted_list = st.session_state.highlighted

            if analysis_level == "state":
                # ── Hex Map ────────────────────────────────────────────────────
                st.markdown(
                    '<div class="section-title">🗺️  Cohort Engagement Map'
                    f'<span style="font-size:.65rem;font-weight:500;color:#94a3b8;text-transform:none;letter-spacing:normal;margin-left:8px;">'
                    f'Comparing States by Impact</span></div>',
                    unsafe_allow_html=True,
                )

                # Convert the aggregated DataFrame into the dict format that
                # build_hex_map_figure() expects: { "CA": {metrics...}, ... }
                state_data = {}
                for _, row in geo["data"].iterrows():
                    state_data[row["name"]] = {
                        "ctr": row["ctr"],
                        "impressions": row["impressions"],
                        "npiCount": int(row["npiCount"]),
                    }

                max_val = geo["max_ctr"] if map_metric == "ctr" else geo["max_imps"]
                fig_map = build_hex_map_figure(state_data, map_metric, max_val, highlighted_list)

                # key= on st.plotly_chart() prevents flickering when the same
                # chart re-renders with new data. Without it, Streamlit may
                # re-create the chart element from scratch and cause a flash.
                st.plotly_chart(fig_map, use_container_width=True, key="hex_map")

                # Manual color scale legend (Plotly's built-in colorbar doesn't
                # work well with custom scatter-polygon hex maps)
                metric_label = f"{max_val:.1f}%" if map_metric == "ctr" else f"{max_val:.1f}"
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;justify-content:center;gap:8px;
                                font-size:.65rem;font-weight:700;color:#94a3b8;text-transform:uppercase;">
                        <span>Low</span>
                        <div style="width:120px;height:10px;border-radius:999px;
                                    background:linear-gradient(to right,#FEF0E9,#C2521B);"></div>
                        <span>High ({metric_label})</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:
                # ── Scatter / Bubble Plot ──────────────────────────────────────
                st.markdown(
                    '<div class="section-title">🔬  Cohort Engagement Matrix'
                    f'<span style="font-size:.65rem;font-weight:500;color:#94a3b8;text-transform:none;letter-spacing:normal;margin-left:8px;">'
                    f'Comparing Specialties by Impact</span></div>',
                    unsafe_allow_html=True,
                )

                scatter_df = geo["data"].copy()
                # Bubble size = HCP count. clip(lower=5) prevents invisible
                # tiny dots. Multiplying by 1.5 scales up for visibility.
                scatter_df["size_px"] = scatter_df["npiCount"].clip(lower=5) * 1.5

                # Build color and opacity arrays row-by-row.
                # When something is highlighted: highlighted items are bold/red,
                # everything else fades to near-transparent gray.
                # When nothing is highlighted: use the brand color palette.
                colors = []
                opacities = []
                has_hl = len(highlighted_list) > 0
                for _, row in scatter_df.iterrows():
                    if has_hl:
                        if row["name"] in highlighted_list:
                            colors.append(BRAND["primary"])
                            opacities.append(1.0)
                        else:
                            colors.append("#cbd5e1")  # slate-300 — muted
                            opacities.append(0.3)
                    else:
                        # Cycle through the brand palette using modulo
                        idx = _ % len(BRAND["palette"])
                        colors.append(BRAND["palette"][idx])
                        opacities.append(0.8)

                scatter_df["color"] = colors
                scatter_df["opacity"] = opacities

                fig_scatter = go.Figure()
                fig_scatter.add_trace(
                    go.Scatter(
                        x=scatter_df["impressions"],  # X axis: avg frequency
                        y=scatter_df["ctr"],           # Y axis: CTR %
                        mode="markers+text",           # Show both bubbles and labels
                        marker=dict(
                            size=scatter_df["size_px"],
                            color=scatter_df["color"],
                            opacity=scatter_df["opacity"],
                            line=dict(width=1, color="white"),  # White border on bubbles
                        ),
                        text=scatter_df["name"],
                        textposition="top center",
                        textfont=dict(size=9, color="#64748b"),
                        # customdata attaches extra data per point for use in tooltips.
                        # %{customdata[0]} in hovertemplate references the first column.
                        customdata=scatter_df[["name", "npiCount", "impressions", "ctr"]].values,
                        hovertemplate=(
                            "<b>%{customdata[0]}</b><br>"
                            "HCPs: %{customdata[1]}<br>"
                            "Avg Freq: %{customdata[2]:.1f}<br>"
                            "CTR: %{customdata[3]:.2f}%<extra></extra>"
                            # <extra></extra> suppresses Plotly's default
                            # trace name tooltip suffix
                        ),
                    )
                )
                fig_scatter.update_layout(
                    height=480,
                    margin=dict(l=40, r=20, t=20, b=50),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    xaxis=dict(title="Avg Frequency per HCP", gridcolor="#f1f5f9"),
                    yaxis=dict(title="CTR %", gridcolor="#f1f5f9"),
                )
                st.plotly_chart(fig_scatter, use_container_width=True, key="scatter")

                st.markdown(
                    """
                    <div style="text-align:center;font-size:.65rem;font-weight:700;
                                color:#94a3b8;text-transform:uppercase;">
                        Bubble size = Population (Reach)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
# `if __name__ == "__main__":` is standard Python. When you run this file
# directly (`streamlit run pld_app_annotated.py`), __name__ is "__main__"
# so main() gets called. If another script imports this file, __name__ is
# the module name and main() does NOT run automatically.
if __name__ == "__main__":
    main()
