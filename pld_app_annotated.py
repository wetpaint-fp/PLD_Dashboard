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

# Prescriber journey funnel order, derived from the BRI_LOOKUP "Segment" column.
# Segments are sub-groups of the HCP Target List, ordered from coldest audience
# (never heard of Brixadi) to hottest (active champion / brand advocate).
# Deciles Ai is a separate ML-scored priority tier; Site Visitors is a
# retargeting pool independent of the journey stages.
SEGMENT_FUNNEL_ORDER = [
    "Unaware",
    "Educate",
    "Aware",
    "Trialing",
    "Adopting",
    "Advocating",
    "Deciles Ai",
    "Site Visitors",
]


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

    # Audience segments match the BRI_LOOKUP "Segment" column from the real data.
    # In BRI_LOOKUP, all active segments are sub-groups of HCP-Target-List targeting
    # except "Site Visitors" (Site-Retargeting). The journey stages reflect where
    # each HCP sits in their prescribing adoption of Brixadi.
    #
    # Weights mirror the real campaign: Aware/Trialing/Adopting get the most budget;
    # Advocating is a small but high-value group; Site Visitors is a small retargeting pool.
    seg_weights = {
        "Unaware":       0.06,
        "Educate":       0.10,
        "Aware":         0.22,
        "Trialing":      0.20,
        "Adopting":      0.16,
        "Advocating":    0.08,
        "Deciles Ai":    0.13,
        "Site Visitors": 0.05,
    }
    segments    = list(seg_weights.keys())
    seg_probs   = list(seg_weights.values())

    # CTR biases reflect real-world HCP engagement: HCPs further down the prescribing
    # journey (Adopting, Advocating) are more likely to engage; cold audiences (Unaware)
    # click less. Site Visitors are high-intent retargeting targets.
    segment_ctr_bias = {
        "Unaware":       -0.03,
        "Educate":       -0.01,
        "Aware":          0.00,
        "Trialing":       0.03,
        "Adopting":       0.05,
        "Advocating":     0.07,
        "Deciles Ai":     0.04,
        "Site Visitors":  0.06,
    }

    # Build 50 fake placement definitions (maps placement name → partner/channel/program/asset/segment)
    placements = {}
    for i in range(50):
        pname = f"placement_{i}"
        partner = random.choice(partners)
        placements[pname] = {
            "PARTNER_NAME": partner,
            "CHANNEL_CATEGORY": random.choice(channels),
            "PROGRAM_FRIENDLY_NAME": random.choice(programs),
            "FP_ASSET_ID": random.choice(asset_map[partner]),
            "Segment": np.random.choice(segments, p=seg_probs),
        }

    # Generate 4000 activity events (one row = one ad served to one HCP)
    rows = []
    base_date = pd.Timestamp("2025-08-01")
    for i in range(4000):
        npi_obj = random.choice(npis)
        pname = f"placement_{random.randint(0, 49)}"
        pd_detail = placements[pname]
        date = base_date + pd.Timedelta(days=random.randint(0, 179))

        # Bias click probability by specialty, state, asset, and segment
        asset_id = pd_detail["FP_ASSET_ID"]
        segment  = pd_detail["Segment"]
        base_click_prob = 0.05
        if npi_obj["specialty"] == "Oncology":
            base_click_prob += 0.08  # Oncologists click more
        if npi_obj["state"] in ("NY", "CA", "TX", "FL"):
            base_click_prob += 0.03  # High-population states click more
        if npi_obj["specialty"] == "PCP":
            base_click_prob -= 0.02  # PCPs click less
        base_click_prob += asset_ctr_bias.get(asset_id, 0.0)     # Per-creative bias
        base_click_prob += segment_ctr_bias.get(segment, 0.0)    # Per-segment bias

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
            "Segment": segment,
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


def compute_segment_metrics(df: pd.DataFrame, vendor_filter: str) -> pd.DataFrame:
    """
    Compute CTR, reach, and impressions per audience segment.

    Segments come from BRI_LOOKUP in real data (via the "Segment" column) or
    from placement metadata in mock data. One row per segment, ordered by
    SEGMENT_FUNNEL_ORDER (prescriber journey stage) so charts always read
    Unaware → Educate → Aware → Trialing → Adopting → Advocating.

    Note: click-only vendors (NA assets) inflate impression counts here.
    For a production view, filter to impression-trackable vendors first.
    """
    filt = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]
    filt = filt[filt["Segment"].notna() & (filt["Segment"] != "Unknown")]

    agg = (
        filt.groupby("Segment")
        .agg(
            Impressions=("ACTIVITY_ID", "count"),
            Clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
            Reach=("NPI", "nunique"),
        )
        .reset_index()
    )
    agg["CTR"] = np.where(
        agg["Impressions"] > 0,
        (agg["Clicks"] / agg["Impressions"]) * 100,
        0,
    )
    # Sort by prescriber journey stage; any unrecognised segment goes at the end
    funnel_pos = {s: i for i, s in enumerate(SEGMENT_FUNNEL_ORDER)}
    agg["_order"] = agg["Segment"].map(funnel_pos).fillna(999)
    return agg.sort_values("_order").drop(columns="_order").reset_index(drop=True)


def compute_segment_by_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute CTR (or engagement rate) and reach per Segment × Format family for
    the Creative Performance heatmap.

    Format is derived from FP_ASSET_ID prefix:
      DM### → Programmatic Banner  (impressions + clicks  → CTR = clicks / impressions)
      AL### → DocNews Alert        (mock: click/impression → CTR = clicks / impressions)
                                   (real: headline_view / content_view → engagement rate)
      NA### → Native Display       (click-only, no impressions → CTR = NaN)

    In production the DocNews Alert column label should read "Engagement Rate"
    since Doximity reports content_view ÷ headline_view, not a traditional CTR.

    Sorted by SEGMENT_FUNNEL_ORDER so heatmap rows always read journey-stage order.
    """
    filt = df[df["Segment"].notna() & (df["Segment"] != "Unknown")].copy()
    # Exclude NA (Native Display) rows from CTR computation — they are click-only
    # and have no impressions, so any CTR would be artificially 100%.
    filt_ctr = filt[~filt["FP_ASSET_ID"].str.startswith("NA", na=False)].copy()

    def _fmt(asset_id):
        if pd.isna(asset_id):
            return "Other"
        a = str(asset_id).upper()
        if a.startswith("DM"):
            return "Programmatic Banner"
        if a.startswith("NA"):
            return "Native Display"
        if a.startswith("AL"):
            return "DocNews Alert"
        return "Other"

    filt["Format"]     = filt["FP_ASSET_ID"].apply(_fmt)
    filt_ctr["Format"] = filt_ctr["FP_ASSET_ID"].apply(_fmt)

    # Reach from all rows (including Native Display)
    reach_agg = (
        filt.groupby(["Segment", "Format"])
        .agg(Reach=("NPI", "nunique"))
        .reset_index()
    )
    # CTR from impression-trackable rows only (DM + AL)
    ctr_agg = (
        filt_ctr.groupby(["Segment", "Format"])
        .agg(
            Impressions=("ACTIVITY_ID", "count"),
            Clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
        )
        .reset_index()
    )
    ctr_agg["CTR"] = np.where(
        ctr_agg["Impressions"] > 0,
        ctr_agg["Clicks"] / ctr_agg["Impressions"] * 100,
        np.nan,
    )
    agg = reach_agg.merge(ctr_agg[["Segment", "Format", "Impressions", "Clicks", "CTR"]],
                          on=["Segment", "Format"], how="left")
    funnel_pos = {s: i for i, s in enumerate(SEGMENT_FUNNEL_ORDER)}
    agg["_order"] = agg["Segment"].map(funnel_pos).fillna(999)
    return agg.sort_values("_order").drop(columns="_order").reset_index(drop=True)


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
        # Branding header — inline SVG logo (no external HTTP; required for SiS)
        st.markdown(
            """
            <div style="background:#050607;border-radius:8px;padding:10px 14px;margin-bottom:4px;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 211.14 52.08" style="width:100%;max-width:180px;display:block;">
                  <defs><style>.st0{fill:#fff}.st1{fill:#ba6af0}</style></defs>
                  <g>
                    <path class="st0" d="M12.881,50.705c-4.083-1-5.18-5.781-5.406-9.375-.357-5.803.294-11.624,1.925-17.205-.335.172-.679.324-1.032.456-.526.208-1.222.528-1.729.779-1.029.525-2.01,1.138-2.932,1.833-.703.589-1.647.801-2.534.569-1.729-.751-1.227-2.669-.513-3.823,1.059-1.522,2.51-2.728,4.2-3.491,1.929-.898,3.953-1.576,6.033-2.021C11.627,16.896,19.654.752,30.2.011l.026.023c1.209-.143,2.427.173,3.414.885.954.629,1.409,1.79,1.136,2.9-.299.941-1.246,1.516-2.219,1.349-.8-.147-1.349-.833-2.022-1.23-.086-.052-.175-.099-.267-.139-.043-.008-.091.006-.126-.022-.673-.514-2.657-.109-4.061,1.368-2.589,2.727-5.495,7.642-7.415,12.26,2.536-.271,7.305.45,6.36,3.174-.45,1.3-2.091,1.348-2.9,1.356-1.929.028-3.852.234-5.744.614-2.396,7.485-2.809,15.463-1.2,23.156.356,1.837.965,5.117-1.437,5.116-.292-.005-.582-.043-.864-.116ZM65.993,49.077c-1.769-.566.079-3.082.627-3.916,3.081-4.55,5.063-9.753,5.791-15.2-.167.3-.323.613-.475.9-.278.538-.598,1.054-.958,1.541-1.181,1.439-2.963,2.248-4.824,2.189-2.069-.007-3.447-1.453-4.245-3.2-.429.66-.947,1.259-1.538,1.779-2.156,1.869-5.953,2.626-8.4.879-1.152-.912-1.879-2.258-2.01-3.722-.274-2.486.769-4.637,1.584-6.9.34-.946,1.165-2.472.084-3.014-1.044-.523-3,.2-3.769,1-2.441,2.532-3.362,5.84-4.263,9.148-1.436,5.277-5.913,4.454-5.308.6.215-1.191.568-2.352,1.052-3.461.752-1.843,1.543-3.91,2.413-5.7.112-.23,1.334-2.554.457-2.409-.419.07-.981.99-1.225,1.293-2.415,3.019-4.122,6.52-6.373,9.654-.089.123-.184.244-.277.364v.024c-1.255,1.606-2.824,3.2-4.967,3.278-4.074.152-4.537-3.883-4.124-6.974.156-1.14.413-2.263.769-3.357.657-1.949,1.431-3.856,2.316-5.712.27-.737.64-1.432,1.1-2.068,1.006-1.161,3.088-.821,3.023.9-.084.926-.339,1.829-.751,2.663-.253.582-.485,1.169-.709,1.763-.368.978-2.957,7.331-1.008,7.681.9.161,2.357-1.532,2.875-2.063,1.193-1.482,2.289-3.039,3.281-4.662,1.45-1.989,6.949-10.879,9.989-6.1.3.47.529,1.222,1.058,1.481.648.316,1.364-.1,1.925-.412.683-.392,1.39-.741,2.116-1.045,1.518-.625,4.018-1.3,5.072.462.785,1.319.549,2.964.3,4.4-.35,1.761-.826,3.494-1.422,5.187-.432,1.338-1.216,3-.432,4.36.51.558,1.298.768,2.018.54l.138-.058c2.489-1,3.676-3.654,4.218-5.51.449-4.081,2.68-8.566,6.444-9.689,1.282-.348,2.636-.325,3.906.064,1.186.426,2.208,1.216,2.919,2.256.477.652.89,1.348,1.232,2.08,2.031,4.247,1.482,9.52.981,14.05-.183,1.725-.515,3.431-.99,5.1-.502,1.764-1.154,3.483-1.949,5.136-1.21,2.471-3.281,4.683-6,4.683-.568-.006-1.132-.101-1.671-.28v-.003h0ZM66.764,20.564c-.893,1.162-1.509,2.513-1.8,3.949-.263,1.347-.241,4.473,1.368,5,2.076.673,3.873-1.623,4.765-3.952.979-2.55.903-5.642-1.028-6.55-.195-.092-.407-.138-.622-.137-1.084.182-2.051.791-2.683,1.691h0ZM112.114,43.718c-.596-1.898-1.008-3.849-1.231-5.826-.343-3.487-.253-7.003.269-10.467.102-.741.248-1.476.436-2.2-.177.1-.352.2-.52.288-1.166.6-3.87,1.512-4.484-.292-.512-1.51,1.58-6.743-1.824-5.678-1.255.48-2.322,1.353-3.04,2.489-2.486,3.754-2.171,8.362-3.662,12.473-.4.897-1.451,1.3-2.348.9-.213-.095-.406-.231-.566-.4-.489-.704-.685-1.572-.544-2.418-2.796,1.96-6.139,2.991-9.554,2.944-2.894.094-5.446-1.884-6.077-4.71-.955-3.656-.144-8.556,2.584-11.529,1.7-1.889,3.977-3.164,6.476-3.625.134-.027.27-.056.4-.081,2.094-.39,4.757.2,5.624,2.4,1.328,3.375-1.166,6.155-4.086,7.819-.839.478-1.725.867-2.644,1.161-.904.212-1.786.508-2.635.884-2.071,1.161-1.871,3.952.342,4.361,2.053.376,4.6-.466,6.47-1.26.118-.049.233-.1.35-.159l.068-.047c1.881-1.296,3.229-3.229,3.795-5.442.537-2.377,1.154-4.743,1.594-7.113.175-.941.3-2.294,1.261-2.776.807-.36,1.753.002,2.113.809.052.116.09.238.113.363.312,1.935,1.171,1.269,2.615.388,1.614-.984,3.513-2.442,5.491-1.6,3.406,1.449-.425,5.03,1.046,7.119.919,1.3,2.956-1.076,3.43-1.741.4-.564.78-1.145,1.191-1.7.509-.665,1.087-1.274,1.725-1.817,1.09-1.016,2.506-1.611,3.995-1.678,1.472.013,2.896.519,4.047,1.437,3.99,3.218,3.394,10.746.87,14.625-1.4,2.168-3.922,4.221-6.621,3.127-1.246-.49-2.306-1.359-3.031-2.485.344,4.503,1.516,8.904,3.456,12.982.421.9,1.869,3.6.049,3.966-.359.075-.726.114-1.093.115-3.034-.006-4.954-2.793-5.851-5.605h.001ZM120.867,18.835c-2.129.11-3.373,2.936-3.434,5.671-.058,2.493.733,5.3,2.912,5.464,1.685.126,2.89-2.759,3.158-4.106.276-1.439.219-2.921-.165-4.335-.29-1.018-1.138-2.7-2.4-2.7l-.071.006ZM87.291,18.545c-1.289.567-2.409,1.46-3.25,2.59-.544.681-1.032,2.192-.3,2.882,1.129,1.058,3.187.151,4.494-.6.215-.124.41-.244.578-.35,1.268-.806,2.96-2.341,1.931-3.962-.429-.59-1.135-.914-1.862-.852-.543.007-1.081.106-1.591.293h0ZM186.044,33.378c-.176-.302-.316-.622-.418-.956-.235.266-.488.516-.755.749-2.156,1.87-5.952,2.627-8.4.879-1.152-.912-1.879-2.258-2.01-3.722-.275-2.485.769-4.637,1.585-6.9.34-.946,1.165-2.472.084-3.014-1.045-.523-3,.2-3.77,1-2.442,2.532-3.361,5.841-4.262,9.148-1.437,5.277-5.914,4.454-5.309.6.214-1.191.568-2.352,1.053-3.461.751-1.843,1.543-3.91,2.412-5.7.111-.23,1.333-2.554.456-2.409-.419.07-.981.991-1.224,1.293-2.416,3.019-4.122,6.52-6.373,9.654-.088.123-.184.243-.277.364v.023c-1.256,1.606-2.824,3.2-4.967,3.277-2.661.1-3.776-1.59-4.118-3.632-1.43,1.9-3.981,4.151-6.5,3.41-1.986-.585-3.183-3.45-2.076-5.174-1.096,1.82-2.607,3.355-4.409,4.48-2.679,1.512-6.716,1.353-8.186-1.472-1.193-2.289-.14-5.392.838-7.626,4.891-11.178,12.962-8.923,12.962-8.923,5.2,1.458,4.732,6.753,2.884,10.235s.257,4.3.257,4.3c1.917.638,4.206-3,4.331-3.2.567-3.287,2.053-6.339,3.383-9.371.343-.783.978-1.87,1.92-1.851,2.707.049,1.613,2.964,1.044,4.273-.254.581-.487,1.169-.711,1.763-.368.978-2.957,7.331-1.008,7.681.9.161,2.358-1.532,2.876-2.064,1.192-1.482,2.288-3.04,3.281-4.662,1.449-1.988,6.948-10.879,9.988-6.1.3.47.529,1.223,1.059,1.481.647.316,1.364-.1,1.924-.412.683-.391,1.39-.74,2.116-1.045,1.518-.625,4.018-1.3,5.073.462.784,1.318.548,2.963.3,4.4-.35,1.761-.826,3.494-1.423,5.187-.432,1.339-1.216,3-.432,4.36.51.558,1.297.769,2.018.541l.139-.059c2.737-1.1,3.9-4.258,4.358-6.134.081-.415.162-.825.244-1.23.021-.142.031-.224.031-.224l.013.017c.544-2.745,1.25-5.456,2.113-8.118-.239-.018-.476-.035-.707-.043-1.4.023-2.793-.193-4.12-.638-1.132-.365-1.9-1.419-1.9-2.609.094-.891,1.06-.808,1.739-.783,1.1.042,2.182.228,3.275.313,1.017.079,2.036.11,3.055.128.122-.3.237-.589.366-.889.631-1.463,1.26-3.087,2.625-4.03.621-.529,1.553-.456,2.082.165.213.249.336.562.352.889-.024,1.337-.423,2.64-1.152,3.761-.027.055-.053.111-.08.166,1.3.02,2.6.024,3.912-.032.108,0,.226-.012.348-.022.582-.108,1.183-.042,1.729.188.263.266.373.648.291,1.014-.331,1.128-1.247,1.989-2.394,2.249-.857.22-1.74.321-2.624.3-.27,0-1.8.062-3,.074-.008.021-.019.041-.028.062-1.129,2.523-1.94,5.177-2.415,7.9-.237,1.558-.681,4.131.449,5.464.434.59,1.265.715,1.854.281.007-.005.014-.01.021-.016,1.514-.889,2.647-2.8,3.588-4.193.433-.643.713-1.506,1.422-1.913.642-.363,1.455-.184,1.885.416,1.253,1.953-.833,5.131-1.973,6.6-1.531,1.964-3.532,3.512-5.818,4.5-.56.239-1.161.364-1.77.369-1.288.017-2.485-.665-3.126-1.783v-.006h0ZM133.4,28.822c2.067.926,5.7-2,7.036-3.993,1.46-2.174,2.2-5.246.329-6.377-.335-.204-.721-.31-1.113-.307-3.842,0-9.297,9.31-6.252,10.677h0ZM31.062,13.426c-.144-.108-.218-.332-.349-.5-.162-.169-.314-.346-.455-.532-.369-.694-.341-1.532.073-2.2.42-.513.987-.886,1.625-1.066.023-.009.062-.106.086-.13.142-.088.31-.124.475-.1.187,0,.374.021.557.063.373.089.726.245,1.043.461.293-.1.548.168.925.291.074.023.159,0,.22.033.163.083.932.379,1.1.168.046.071-.053.224-.064.326.096.1.171.219.219.35,0,.006.2.069.226.088.057.039.1.091.158.135s.126.069.18.113c.105.137.159.306.153.479.006.075-.01.15-.048.215-.028.043-.136.151-.193.141-.2-.035-.234-.148-.355-.272-.227.008-.363.181-.617.143-.178.202-.272.463-.263.732-.49-.128-1.012-.033-1.425.26-.31.182-.648.311-1,.381-.432.367-.958.605-1.519.689-.273-.004-.538-.098-.752-.268Z"/>
                    <path class="st1" d="M155.88,13.626c-.9-.144-1.64-.786-1.909-1.657-.022-.065-.039-.132-.05-.2-.113-1.091.488-2.132,1.49-2.579.308-.141.635-.236.971-.283.557-.07,1.122.017,1.632.251.213-.016.428.016.627.094.229.104.487.124.729.056h.278c.217.015.436.005.651-.03.154-.031.271-.135.427-.125.231.013.412.213.628.2.328-.019.485-.269.8-.327.33.11.814.414,1-.025.187-.07.394-.057.571.034.146.086.324.101.483.041.074-.065-.043-.166.025-.226.331-.15.5.215.7.352.289.062.584.095.88.1.112-.063.134-.217.174-.351.239-.132.5.061.729.1.16-.042.25-.152.4-.2.207.135.454.197.7.176.181.186.452.255.7.176.148.096.33.124.5.075.021-.372.183-.735.578-.653.119.111,0,.241.025.351.04.168.252.284.2.527.105.124.278.165.427.1.072-.143-.017-.331.226-.327.057.215.268.248.528.2.1-.015-.012.074.024.151.117.06.22.146.3.251.3-.172.464.112.629.226.016.184-.157.179-.227.276-.203-.024-.404-.066-.6-.126-.032-.266-.539-.467-.679-.175.066.244.272.347.352.577-.044.11-.137.194-.251.227-.159-.199-.38-.34-.627-.4-.116.253-.1.831-.527.678,0-.455-.373-.71-.779-.4-.076.057-.1.2-.176.276-.058.057-.2.087-.276.151-.128.1-.121.2-.226.2-.14.007-.231-.213-.377-.226s-.17.113-.326.2c-.111.063-.263.058-.326.1s-.1.166-.177.151c-.145-.073-.187-.248-.4-.251-.298.141-.609.25-.93.326-.12.045-.221.167-.351.176-.09.002-.18-.01-.267-.034-.141-.049-.296-.046-.435.009-.081.062-.1.186-.176.251-.338-.115-.704-.117-1.043-.006-.225.058-.457.085-.69.08-.093.033-.15.157-.277.176-.1.017-.266-.072-.351-.075-.3-.011-.722.2-1.106.2-.378.023-.755.064-1.129.125-1.2.152-2,1.069-3.259,1.069-.146.002-.292-.008-.436-.03v-.003h-.001Z"/>
                    <path class="st1" d="M128.912,42.526v9.416h1.931v-6.152h.078l2.437,6.106h1.315l2.437-6.084h.078v6.129h1.931v-9.416h-2.455l-2.595,6.329h-.109l-2.59-6.327-2.459-.002h0ZM143.027,51.942l.697-2.147h3.398l.7,2.147h2.133l-3.246-9.416h-2.566l-3.251,9.416h2.133ZM144.229,48.241l1.158-3.564h.074l1.158,3.564h-2.39ZM151.735,51.942h1.992v-3.339h1.453l1.783,3.339h2.198l-2.001-3.66c1.07-.446,1.739-1.523,1.664-2.68,0-1.871-1.237-3.076-3.374-3.076h-3.715v9.416ZM153.727,47.004v-2.851h1.343c1.149,0,1.706.51,1.706,1.448s-.557,1.402-1.693,1.402h-1.356ZM160.879,51.942h1.992v-2.676l.979-1.195,2.579,3.871h2.381l-3.536-5.2,3.494-4.216h-2.39l-3.386,4.152h-.124v-4.152h-1.992l.004,9.416h0ZM170.455,51.942h6.363v-1.641h-4.372v-2.248h4.028v-1.642h-4.028v-2.243h4.352v-1.641h-6.342v9.416h0ZM178.675,44.167h2.883v7.775h1.968v-7.775h2.882v-1.641h-7.733v1.641h-.001ZM190.329,42.526h-1.992v9.416h1.992v-9.416ZM200.494,42.526h-1.983v5.922h-.083l-4.066-5.922h-1.747v9.416h1.992v-5.927h.069l4.097,5.927h1.72v-9.416h0ZM209.025,45.567h2.023c-.333-1.933-2.071-3.302-4.028-3.172-2.49,0-4.405,1.793-4.405,4.847,0,2.979,1.793,4.828,4.446,4.828,2.09.157,3.91-1.408,4.069-3.498.012-.161.014-.324.005-.486v-1.183h-3.939v1.494h2.023c.008,1.054-.84,1.915-1.893,1.923-.085,0-.17-.004-.254-.015-1.494,0-2.437-1.118-2.437-3.088s.979-3.067,2.418-3.067c.914-.068,1.745.529,1.973,1.417Z"/>
                  </g>
                </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # ── Navigation radio ──
        active_tab = st.radio(
            "Navigation",
            ["Partner Performance", "Creative Performance", "HCP Audience"],
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
        "HCP Audience":          "HCP Audience",
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

        with c2:
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

        # ── CTR by Stage × Partner Heatmap ────────────────────────────────────
        st.markdown(
            '<div class="section-title">🎯  CTR % by Stage × Partner'
            '<span style="font-size:.65rem;font-weight:500;color:#94a3b8;'
            'text-transform:none;letter-spacing:normal;margin-left:8px;">'
            'Darker = higher CTR</span></div>',
            unsafe_allow_html=True,
        )
        filt_seg = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]
        filt_seg = filt_seg[filt_seg["Segment"].notna() & (filt_seg["Segment"] != "Unknown")]
        # Exclude click-only (NA) assets — no impressions means CTR would be 100%.
        filt_seg = filt_seg[~filt_seg["FP_ASSET_ID"].str.startswith("NA", na=False)]
        sv_agg = (
            filt_seg.groupby(["Segment", "VENDOR"])
            .agg(
                Impressions=("ACTIVITY_ID", "count"),
                Clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
            )
            .reset_index()
        )
        sv_agg["CTR"] = np.where(
            sv_agg["Impressions"] > 0,
            sv_agg["Clicks"] / sv_agg["Impressions"] * 100,
            np.nan,
        )
        if len(sv_agg):
            pivot_sv  = sv_agg.pivot(index="Segment", columns="VENDOR", values="CTR")
            funnel_pos = {s: i for i, s in enumerate(SEGMENT_FUNNEL_ORDER)}
            row_order  = sorted(pivot_sv.index, key=lambda s: funnel_pos.get(s, 999))
            pivot_sv   = pivot_sv.loc[row_order]
            z_vals     = pivot_sv.values.tolist()
            text_vals  = [[f"{v:.1f}%" if v == v else "—" for v in row] for row in z_vals]
            fig_sv = go.Figure(go.Heatmap(
                z=z_vals,
                x=pivot_sv.columns.tolist(),
                y=pivot_sv.index.tolist(),
                colorscale=[[0, "#E8DEEE"], [0.5, "#8A5CA8"], [1, "#47254A"]],
                text=text_vals,
                texttemplate="%{text}",
                textfont=dict(size=11),
                hovertemplate="<b>%{y}</b><br>Partner: %{x}<br>CTR: %{text}<extra></extra>",
                showscale=True,
                colorbar=dict(title="CTR %", thickness=12, len=0.7),
            ))
            fig_sv.update_layout(
                height=max(300, len(row_order) * 48 + 60),
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(side="bottom", tickfont=dict(size=11)),
                yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
            )
            st.plotly_chart(fig_sv, use_container_width=True, key="pp_seg_vendor_heatmap")
        else:
            st.info("No segment data available.")

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
                marker_color=[
                    BRAND["primary"] if f == "Programmatic Banner"
                    else BRAND["plum"]
                    for f in asset_ordered["Format"]
                ],
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

        # ── Audience Segment × Format CTR Heatmap ─────────────────────────────
        # The unique creative-page question: which creative format engages each
        # journey stage most effectively? The previous stacked reach chart showed
        # who we're reaching but not how well — the heatmap crosses both dimensions.
        # Native Display (click-only) and DocNews Alert (engagement-only) have no
        # valid CTR, so only Programmatic Banner cells are coloured.
        st.markdown(
            '<div class="section-title">🎯  Prescriber Journey × Creative Format'
            '<span style="font-size:.65rem;font-weight:500;color:#94a3b8;'
            'text-transform:none;letter-spacing:normal;margin-left:8px;">'
            'CTR % — Native Display excluded (click-only, no impressions)'
            '</span></div>',
            unsafe_allow_html=True,
        )
        cp_seg_fmt = compute_segment_by_format(df)
        if len(cp_seg_fmt):
            # Build two pivots: CTR (for heatmap colour) and Reach (for annotation)
            ctr_pivot   = cp_seg_fmt.pivot(index="Segment", columns="Format", values="CTR")
            reach_pivot = cp_seg_fmt.pivot(index="Segment", columns="Format", values="Reach")

            # Enforce funnel order on rows
            funnel_pos = {s: i for i, s in enumerate(SEGMENT_FUNNEL_ORDER)}
            row_order  = sorted(ctr_pivot.index, key=lambda s: funnel_pos.get(s, 999))
            ctr_pivot   = ctr_pivot.loc[row_order]
            reach_pivot = reach_pivot.loc[row_order]

            # Column order: impression-trackable formats only — Native Display is
            # excluded because it's click-only and has no CTR to show.
            col_order = [c for c in ["DocNews Alert", "Programmatic Banner", "Other"]
                         if c in ctr_pivot.columns]
            ctr_pivot   = ctr_pivot[col_order]
            reach_pivot = reach_pivot[col_order]

            # Cell text: CTR% for Programmatic Banner, reach count for others
            text_vals = []
            for seg in ctr_pivot.index:
                row_texts = []
                for fmt in ctr_pivot.columns:
                    ctr_v   = ctr_pivot.loc[seg, fmt]
                    reach_v = reach_pivot.loc[seg, fmt]
                    if fmt == "Programmatic Banner" and ctr_v == ctr_v:
                        row_texts.append(f"{ctr_v:.1f}%")
                    elif reach_v == reach_v and reach_v > 0:
                        row_texts.append(f"{int(reach_v)} HCPs")
                    else:
                        row_texts.append("—")
                text_vals.append(row_texts)

            fig_cp_heat = go.Figure(go.Heatmap(
                z=ctr_pivot.values.tolist(),
                x=ctr_pivot.columns.tolist(),
                y=ctr_pivot.index.tolist(),
                colorscale=[[0, "#E8DEEE"], [0.5, "#8A5CA8"], [1, "#47254A"]],
                text=text_vals,
                texttemplate="%{text}",
                textfont=dict(size=11),
                hovertemplate="<b>%{y}</b><br>Format: %{x}<br>%{text}<extra></extra>",
                showscale=True,
                colorbar=dict(title="CTR %", thickness=12, len=0.7),
            ))
            fig_cp_heat.update_layout(
                height=max(300, len(row_order) * 48 + 60),
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(side="bottom", tickfont=dict(size=11)),
                yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
            )
            st.plotly_chart(fig_cp_heat, use_container_width=True, key="cp_seg_format_heatmap")
        else:
            st.info("No segment data available.")

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
    # ║  VIEW 3 — HCP AUDIENCE                                               ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    else:

        # ── Prescriber Journey Distribution ───────────────────────────────────
        journey_stages = ["Unaware", "Educate", "Aware", "Trialing", "Adopting", "Advocating"]
        journey_colors = ["#D9C9E0", "#C5AED4", "#A882BE", "#8A5CA8", "#6B3590", "#47254A"]
        other_color    = "#BFA8D1"
        seg_color_map  = {**dict(zip(journey_stages, journey_colors)),
                           "Deciles Ai": other_color, "Site Visitors": other_color}

        seg_df_all = compute_segment_metrics(df, "All")
        if len(seg_df_all):
            journey_df = seg_df_all[seg_df_all["Segment"].isin(journey_stages)].copy()
            journey_df["_order"] = journey_df["Segment"].map(
                {s: i for i, s in enumerate(journey_stages)}
            )
            journey_df = journey_df.sort_values("_order")

            jc1, jc2 = st.columns([1, 1])

            with jc1:
                st.markdown(
                    '<div class="section-title">🎯  Reach by Journey Stage'
                    '<span style="font-size:.65rem;font-weight:500;color:#94a3b8;'
                    'text-transform:none;letter-spacing:normal;margin-left:8px;">'
                    'Unique HCPs reached</span></div>',
                    unsafe_allow_html=True,
                )
                all_segs = journey_df.sort_values("_order", ascending=False)

                fig_seg_bar = go.Figure(go.Bar(
                    x=all_segs["Reach"],
                    y=all_segs["Segment"],
                    orientation="h",
                    marker_color=[seg_color_map.get(s, other_color) for s in all_segs["Segment"]],
                    marker_cornerradius=4,
                    text=all_segs["Reach"].apply(lambda v: f"{v:,}"),
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>HCPs reached: %{x:,}<extra></extra>",
                ))
                fig_seg_bar.update_layout(
                    height=360,
                    margin=dict(l=20, r=60, t=10, b=20),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    xaxis=dict(gridcolor="#f1f5f9", title="Unique HCPs"),
                    yaxis=dict(tickfont=dict(size=11)),
                )
                st.plotly_chart(fig_seg_bar, use_container_width=True, key="ha_seg_bar")

            with jc2:
                st.markdown(
                    '<div class="section-title">📈  CTR % by Journey Stage'
                    '<span style="font-size:.65rem;font-weight:500;color:#94a3b8;'
                    'text-transform:none;letter-spacing:normal;margin-left:8px;">'
                    'Engagement rises as HCPs advance along the journey</span></div>',
                    unsafe_allow_html=True,
                )
                # journey_df already filtered to the 6 stages, ordered Unaware → Advocating.
                # Exclude click-only NA rows before computing CTR (same rule as heatmap).
                ctr_filt = df[
                    df["Segment"].isin(journey_stages) &
                    ~df["FP_ASSET_ID"].str.startswith("NA", na=False)
                ]
                ctr_by_stage = (
                    ctr_filt.groupby("Segment")
                    .agg(
                        Impressions=("ACTIVITY_ID", "count"),
                        Clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
                    )
                    .reset_index()
                )
                ctr_by_stage["CTR"] = np.where(
                    ctr_by_stage["Impressions"] > 0,
                    ctr_by_stage["Clicks"] / ctr_by_stage["Impressions"] * 100,
                    np.nan,
                )
                ctr_by_stage["_order"] = ctr_by_stage["Segment"].map(
                    {s: i for i, s in enumerate(journey_stages)}
                )
                ctr_by_stage = ctr_by_stage.sort_values("_order")

                fig_ctr_stage = go.Figure(go.Bar(
                    x=ctr_by_stage["CTR"],
                    y=ctr_by_stage["Segment"],
                    orientation="h",
                    marker_color=[seg_color_map.get(s, other_color) for s in ctr_by_stage["Segment"]],
                    marker_cornerradius=4,
                    text=ctr_by_stage["CTR"].round(2).astype(str) + "%",
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>CTR: %{x:.2f}%<extra></extra>",
                ))
                fig_ctr_stage.update_layout(
                    height=360,
                    margin=dict(l=20, r=60, t=10, b=20),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    xaxis=dict(gridcolor="#f1f5f9", title="CTR %"),
                    yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
                )
                st.plotly_chart(fig_ctr_stage, use_container_width=True, key="ha_journey")
        else:
            st.info("No segment data available.")

        st.markdown("---")

        if data_source == "Real Data":
            st.info(
                "Geographic analysis requires SPECIALTY and STATE data, which are not "
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
