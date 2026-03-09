"""
Fingerpaint Marketing — HCP Campaign Analytics Dashboard
=========================================================
Streamlit in Snowflake (SiS) application.
Converted from React prototype. Uses mock data generation.

Features:
  • Partner Performance: KPIs, monthly trends, bar charts, drill-down table
  • Geographic Deep Dive: US hex map, scatter/bubble analysis, comparison list
"""

import streamlit as st
import pandas as pd
import numpy as np
import random
import math
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Fingerpaint Marketing — HCP Analytics",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# BRAND / DESIGN TOKENS
# ─────────────────────────────────────────────
BRAND = {
    "primary": "#e11d48",
    "secondary": "#be123c",
    "accent": "#fbbf24",
    "neutral": "#1e293b",
    "light": "#f1f5f9",
    "palette": ["#e11d48", "#8b5cf6", "#f59e0b", "#10b981", "#06b6d4", "#ec4899"],
}

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown(
    """
<style>
    /* ── Global ── */
    .block-container { padding-top: 1.5rem; }
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] .stMarkdown h1 { font-size: 1.25rem; }

    /* ── KPI cards ── */
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
        color: #0f172a;
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
        color: #1e293b;
        margin-bottom: 1rem;
    }

    /* ── Comparison entity cards ── */
    .entity-card {
        background: #fff1f2;
        border: 1px solid #fecdd3;
        border-radius: 10px;
        padding: .85rem 1rem;
        margin-bottom: .5rem;
    }
    .entity-name { font-weight: 700; color: #0f172a; font-size: .85rem; }
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
        border: 1px solid #fecdd3;
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

    /* Hide Streamlit's default elements for cleaner look */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# MOCK DATA GENERATION  (cached per session)
# ─────────────────────────────────────────────
@st.cache_data
def generate_mock_data() -> pd.DataFrame:
    """Generate realistic HCP campaign activity data (mirrors JS generateMockData)."""
    random.seed(42)
    np.random.seed(42)

    partners = ["PulsePoint", "Medscape", "Doximity", "Sermo"]
    channels = ["Programmatic Display", "Email", "EHR", "Social"]
    programs = ["Retargeting", "High Value HCPs", "Conquesting", "Newsletter"]
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

    # Pre-generate NPIs
    npis = []
    for i in range(500):
        npis.append({
            "id": f"1{random.randint(100000000, 999999999)}",
            "specialty": random.choice(specialties),
            "state": random.choice(states),
        })

    # Pre-generate placement lookup
    placements = {}
    for i in range(50):
        pname = f"placement_{i}"
        placements[pname] = {
            "PARTNER_NAME": random.choice(partners),
            "CHANNEL_CATEGORY": random.choice(channels),
            "PROGRAM_FRIENDLY_NAME": random.choice(programs),
        }

    rows = []
    base_date = pd.Timestamp("2025-08-01")
    for i in range(4000):
        npi_obj = random.choice(npis)
        pname = f"placement_{random.randint(0, 49)}"
        pd_detail = placements[pname]
        date = base_date + pd.Timedelta(days=random.randint(0, 179))

        # Build specialty / state bias into CTR
        base_click_prob = 0.05
        if npi_obj["specialty"] == "Oncology":
            base_click_prob += 0.08
        if npi_obj["state"] in ("NY", "CA", "TX", "FL"):
            base_click_prob += 0.03
        if npi_obj["specialty"] == "PCP":
            base_click_prob -= 0.02

        is_click = random.random() < base_click_prob

        rows.append({
            "ACTIVITY_ID": f"act_{i}",
            "NPI": npi_obj["id"],
            "PLACEMENT_NAME": pname,
            "VENDOR": pd_detail["PARTNER_NAME"],
            "CHANNEL": pd_detail["CHANNEL_CATEGORY"],
            "PROGRAM": pd_detail["PROGRAM_FRIENDLY_NAME"],
            "ACTIVITY_TYPE": "Click" if is_click else "Impression",
            "ACTIVITY_DATE": date.strftime("%Y-%m-%d"),
            "SPECIALTY": npi_obj["specialty"],
            "STATE": npi_obj["state"],
        })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# US HEX MAP COORDINATES  (pointy‑top hex grid)
# ─────────────────────────────────────────────
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
    """Return the 6 corner coordinates of a pointy-top hexagon."""
    coords_x, coords_y = [], []
    for i in range(7):  # 7 to close the polygon
        angle_deg = 60 * i - 30
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
    Build a Plotly figure of the US hex-bin choropleth.
    state_data = { "CA": {"ctr": 5.2, "impressions": 8.1, "npiCount": 42, ...}, … }
    """
    HEX_SIZE = 1.0
    HEX_W = math.sqrt(3) * HEX_SIZE
    HEX_H = 2 * HEX_SIZE

    fig = go.Figure()

    has_highlights = len(highlighted) > 0

    # Color interpolation: Rose-200 → Rose-600
    def get_fill(val):
        if val is None:
            return "rgb(226,232,240)"  # slate-200
        ratio = max(0.0, min(1.0, val / max_val)) if max_val > 0 else 0
        r = int(254 + (225 - 254) * ratio)
        g = int(205 + (29 - 205) * ratio)
        b = int(211 + (72 - 211) * ratio)
        return f"rgb({r},{g},{b})"

    for state, col, row in US_HEX_MAP:
        cx = col * HEX_W + (HEX_W / 2 if row % 2 == 1 else 0)
        cy = -row * HEX_H * 0.75  # negative so north is up

        sd = state_data.get(state)
        val = sd[metric] if sd else None

        fill = get_fill(val)
        opacity = 1.0
        line_color = "white"
        line_width = 1.5

        if has_highlights:
            if state in highlighted:
                line_color = "#1e293b"
                line_width = 3
            else:
                opacity = 0.25

        hx, hy = _hex_corners(cx, cy, HEX_SIZE)

        hover_text = ""
        if sd:
            hover_text = (
                f"<b>{state}</b><br>"
                f"HCPs: {sd['npiCount']}<br>"
                f"Avg Freq: {sd['impressions']:.1f}<br>"
                f"CTR: {sd['ctr']:.2f}%"
            )
        else:
            hover_text = f"<b>{state}</b><br>No data"

        fig.add_trace(
            go.Scatter(
                x=hx, y=hy,
                fill="toself",
                fillcolor=fill,
                opacity=opacity,
                line=dict(color=line_color, width=line_width),
                mode="lines",
                hoverinfo="text",
                hovertext=hover_text,
                showlegend=False,
            )
        )
        # State label
        text_color = "#ffffff" if (val is not None and val > max_val * 0.6) else "#64748b"
        fig.add_annotation(
            x=cx, y=cy,
            text=f"<b>{state}</b>",
            showarrow=False,
            font=dict(size=10, color=text_color),
        )

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


# ─────────────────────────────────────────────
# HELPER: KPI Card
# ─────────────────────────────────────────────
def kpi_card(label: str, value: str, sub: str = ""):
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


# ─────────────────────────────────────────────
# ANALYTICS COMPUTATIONS
# ─────────────────────────────────────────────
def compute_partner_metrics(df: pd.DataFrame, vendor_filter: str):
    """Compute KPIs and per-partner bar chart data."""
    filt = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]
    total_imps = len(filt)
    total_clicks = int((filt["ACTIVITY_TYPE"] == "Click").sum())
    unique_npis = filt["NPI"].nunique()
    frequency = round(total_imps / unique_npis, 1) if unique_npis else 0

    by_partner = (
        filt.groupby("VENDOR")
        .agg(
            Impressions=("ACTIVITY_ID", "count"),
            Clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
            Reach=("NPI", "nunique"),
        )
        .reset_index()
    )
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
        "chart": by_partner,
    }


def compute_trend_data(df: pd.DataFrame, vendor_filter: str):
    """Monthly trend: Reach & Frequency."""
    filt = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]
    filt = filt.copy()
    filt["MONTH"] = filt["ACTIVITY_DATE"].str[:7]

    grouped = (
        filt.groupby("MONTH")
        .agg(
            Impressions=("ACTIVITY_ID", "count"),
            Clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
            Reach=("NPI", "nunique"),
        )
        .reset_index()
        .sort_values("MONTH")
    )
    grouped["Frequency"] = np.where(
        grouped["Reach"] > 0,
        (grouped["Impressions"] / grouped["Reach"]).round(1),
        0,
    )
    return grouped


def compute_hierarchy(df: pd.DataFrame, vendor_filter: str):
    """Build hierarchical table data: Partner → Channel → Program."""
    filt = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]

    levels = ["VENDOR", "CHANNEL", "PROGRAM"]
    rows_out = []

    for vendor, vg in filt.groupby("VENDOR"):
        v_imps = len(vg)
        v_clicks = int((vg["ACTIVITY_TYPE"] == "Click").sum())
        v_reach = vg["NPI"].nunique()
        v_ctr = (v_clicks / v_imps * 100) if v_imps else 0
        rows_out.append({
            "level": 0, "name": vendor,
            "Impressions": v_imps, "Clicks": v_clicks,
            "CTR": round(v_ctr, 2), "Reach": v_reach,
        })
        for channel, cg in vg.groupby("CHANNEL"):
            c_imps = len(cg)
            c_clicks = int((cg["ACTIVITY_TYPE"] == "Click").sum())
            c_reach = cg["NPI"].nunique()
            c_ctr = (c_clicks / c_imps * 100) if c_imps else 0
            rows_out.append({
                "level": 1, "name": f"  ↳ {channel}",
                "Impressions": c_imps, "Clicks": c_clicks,
                "CTR": round(c_ctr, 2), "Reach": c_reach,
            })
            for program, pg in cg.groupby("PROGRAM"):
                p_imps = len(pg)
                p_clicks = int((pg["ACTIVITY_TYPE"] == "Click").sum())
                p_reach = pg["NPI"].nunique()
                p_ctr = (p_clicks / p_imps * 100) if p_imps else 0
                rows_out.append({
                    "level": 2, "name": f"      ↳ {program}",
                    "Impressions": p_imps, "Clicks": p_clicks,
                    "CTR": round(p_ctr, 2), "Reach": p_reach,
                })

    return pd.DataFrame(rows_out)


def compute_geo_analysis(df: pd.DataFrame, level: str, filter_value: str):
    """
    Compute scatter / hex map data.
    level: 'state' or 'specialty'
    filter_value: 'All' or a specific specialty/state name
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
        .rename(columns={group_col: "name"})
    )
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


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    # Load data
    df = generate_mock_data()

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <span style="font-size:1.6rem;">🎨</span>
                <div>
                    <div style="font-weight:800;font-size:1.15rem;color:#0f172a;line-height:1.15;">fingerpaint</div>
                    <div style="font-weight:500;font-size:.95rem;color:#e11d48;line-height:1.15;">marketing</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        active_tab = st.radio(
            "Navigation",
            ["Partner Performance", "Geographic Deep Dive"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown(
            '<div class="status-badge"><div class="status-dot"></div>MOCK DATA</div>',
            unsafe_allow_html=True,
        )

    # ── Header ──
    header_title = "Performance Overview" if active_tab == "Partner Performance" else "Geographic Analysis"
    st.markdown(
        f"""
        <div style="margin-bottom:.25rem;">
            <h1 style="font-size:1.75rem;font-weight:800;color:#0f172a;margin:0;">{header_title}</h1>
            <p style="font-size:.75rem;font-weight:600;color:#e11d48;text-transform:uppercase;letter-spacing:.08em;margin:0;">
                Revealing the True Colors of Every Brand
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ╔═══════════════════════════════════════════╗
    # ║  TAB 1 — PARTNER PERFORMANCE              ║
    # ╚═══════════════════════════════════════════╝
    if active_tab == "Partner Performance":
        vendors = ["All"] + sorted(df["VENDOR"].unique().tolist())
        vendor_filter = st.selectbox("Filter Vendor", vendors, key="vendor_sel")

        metrics = compute_partner_metrics(df, vendor_filter)

        # ── KPIs ──
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            kpi_card("Total Impressions", f"{metrics['total_imps']:,}")
        with k2:
            kpi_card("Total Clicks", f"{metrics['total_clicks']:,}")
        with k3:
            kpi_card("Unique Reach", f"{metrics['unique_npis']:,}", "Physicians")
        with k4:
            kpi_card("Avg Frequency", str(metrics["frequency"]), "Imps per NPI")

        st.markdown("")

        # ── Monthly Trends ──
        trend = compute_trend_data(df, vendor_filter)

        st.markdown('<div class="section-title">📈  Monthly Reach & Frequency</div>', unsafe_allow_html=True)
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
            go.Bar(
                x=trend["MONTH"], y=trend["Reach"],
                name="Unique Reach (NPIs)",
                marker_color="#f59e0b",
                marker_cornerradius=4,
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=trend["MONTH"], y=trend["Frequency"],
                name="Avg Frequency",
                mode="lines+markers",
                line=dict(color="#10b981", width=3),
                marker=dict(size=7),
            ),
            secondary_y=True,
        )
        fig_trend.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(gridcolor="#f1f5f9"),
            yaxis2=dict(gridcolor="#f1f5f9"),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # ── Bar Charts ──
        c1, c2 = st.columns(2)
        chart_df = metrics["chart"]

        with c1:
            st.markdown('<div class="section-title">Reach by Partner</div>', unsafe_allow_html=True)
            fig_reach = go.Figure(
                go.Bar(
                    x=chart_df["VENDOR"], y=chart_df["Reach"],
                    marker_color=BRAND["primary"],
                    marker_cornerradius=6,
                )
            )
            fig_reach.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9"),
            )
            st.plotly_chart(fig_reach, use_container_width=True)

        with c2:
            st.markdown('<div class="section-title">CTR % by Partner</div>', unsafe_allow_html=True)
            fig_ctr = go.Figure(
                go.Bar(
                    x=chart_df["VENDOR"], y=chart_df["CTR"],
                    marker_color="#8b5cf6",
                    marker_cornerradius=6,
                    text=chart_df["CTR"].round(2).astype(str) + "%",
                    textposition="outside",
                )
            )
            fig_ctr.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9", title="CTR %"),
            )
            st.plotly_chart(fig_ctr, use_container_width=True)

        # ── Drill-Down Table ──
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

            st.dataframe(
                display.style.format({
                    "Impressions": "{:,}",
                    "Clicks": "{:,}",
                    "CTR %": "{:.2f}%",
                    "Reach": "{:,}",
                }),
                use_container_width=True,
                hide_index=True,
                height=460,
            )
        else:
            st.info("No data available for this filter.")

    # ╔═══════════════════════════════════════════╗
    # ║  TAB 2 — GEOGRAPHIC DEEP DIVE              ║
    # ╚═══════════════════════════════════════════╝
    else:
        # Initialize session state for highlighted entities
        if "highlighted" not in st.session_state:
            st.session_state.highlighted = []

        ctrl_col, viz_col = st.columns([1, 2.5])

        with ctrl_col:
            st.markdown('<div class="section-title">🔍  Analysis Controls</div>', unsafe_allow_html=True)

            analysis_level = st.radio(
                "Analysis Level",
                ["state", "specialty"],
                format_func=lambda x: "States" if x == "state" else "Specialties",
                horizontal=True,
                key="analysis_level",
            )

            geo = compute_geo_analysis(df, analysis_level, "All")

            analysis_filter = st.selectbox(
                f"Filter {geo['filter_label']}",
                ["All"] + geo["filter_options"],
                key="analysis_filter",
            )

            # Recompute with actual filter
            geo = compute_geo_analysis(df, analysis_level, analysis_filter)

            # Entity selector for comparison
            entity_options = geo["data"]["name"].tolist()
            selected_entity = st.selectbox(
                f"Highlight {geo['entity']}",
                [""] + entity_options,
                format_func=lambda x: "Select to compare…" if x == "" else x,
                key="entity_sel",
            )
            if selected_entity and selected_entity not in st.session_state.highlighted:
                st.session_state.highlighted.append(selected_entity)
                st.rerun()

            # Color-by metric (for hex map)
            if analysis_level == "state":
                map_metric = st.radio(
                    "Color By", ["ctr", "impressions"],
                    format_func=lambda x: "CTR %" if x == "ctr" else "Avg Frequency",
                    horizontal=True,
                    key="map_metric",
                )
            else:
                map_metric = "ctr"

            # ── Comparison List ──
            if st.session_state.highlighted:
                st.markdown("---")
                st.markdown('<div class="section-title">Comparison List</div>', unsafe_allow_html=True)

                to_remove = None
                for ent_name in st.session_state.highlighted:
                    ent_row = geo["data"][geo["data"]["name"] == ent_name]
                    if len(ent_row) == 0:
                        continue
                    ent = ent_row.iloc[0]
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
                    if st.button(f"✕ Remove {ent_name}", key=f"rm_{ent_name}", type="tertiary"):
                        to_remove = ent_name

                if to_remove:
                    st.session_state.highlighted.remove(to_remove)
                    st.rerun()

                if st.button("Clear All", key="clear_all", type="secondary"):
                    st.session_state.highlighted = []
                    st.rerun()

        with viz_col:
            highlighted_list = st.session_state.highlighted

            if analysis_level == "state":
                # ── HEX MAP ──
                st.markdown(
                    '<div class="section-title">🗺️  Cohort Engagement Map'
                    f'<span style="font-size:.65rem;font-weight:500;color:#94a3b8;text-transform:none;letter-spacing:normal;margin-left:8px;">'
                    f'Comparing States by Impact</span></div>',
                    unsafe_allow_html=True,
                )

                state_data = {}
                for _, row in geo["data"].iterrows():
                    state_data[row["name"]] = {
                        "ctr": row["ctr"],
                        "impressions": row["impressions"],
                        "npiCount": int(row["npiCount"]),
                    }

                max_val = geo["max_ctr"] if map_metric == "ctr" else geo["max_imps"]
                fig_map = build_hex_map_figure(state_data, map_metric, max_val, highlighted_list)
                st.plotly_chart(fig_map, use_container_width=True, key="hex_map")

                # Color scale legend
                metric_label = f"{max_val:.1f}%" if map_metric == "ctr" else f"{max_val:.1f}"
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;justify-content:center;gap:8px;
                                font-size:.65rem;font-weight:700;color:#94a3b8;text-transform:uppercase;">
                        <span>Low</span>
                        <div style="width:120px;height:10px;border-radius:999px;
                                    background:linear-gradient(to right,#fecdd3,#e11d48);"></div>
                        <span>High ({metric_label})</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:
                # ── SCATTER PLOT ──
                st.markdown(
                    '<div class="section-title">🔬  Cohort Engagement Matrix'
                    f'<span style="font-size:.65rem;font-weight:500;color:#94a3b8;text-transform:none;letter-spacing:normal;margin-left:8px;">'
                    f'Comparing Specialties by Impact</span></div>',
                    unsafe_allow_html=True,
                )

                scatter_df = geo["data"].copy()
                scatter_df["size_px"] = scatter_df["npiCount"].clip(lower=5) * 1.5

                # Color logic: highlighted vs dimmed
                colors = []
                opacities = []
                has_hl = len(highlighted_list) > 0
                for _, row in scatter_df.iterrows():
                    if has_hl:
                        if row["name"] in highlighted_list:
                            colors.append(BRAND["primary"])
                            opacities.append(1.0)
                        else:
                            colors.append("#cbd5e1")
                            opacities.append(0.3)
                    else:
                        idx = _ % len(BRAND["palette"])
                        colors.append(BRAND["palette"][idx])
                        opacities.append(0.8)

                scatter_df["color"] = colors
                scatter_df["opacity"] = opacities

                fig_scatter = go.Figure()
                fig_scatter.add_trace(
                    go.Scatter(
                        x=scatter_df["impressions"],
                        y=scatter_df["ctr"],
                        mode="markers+text",
                        marker=dict(
                            size=scatter_df["size_px"],
                            color=scatter_df["color"],
                            opacity=scatter_df["opacity"],
                            line=dict(width=1, color="white"),
                        ),
                        text=scatter_df["name"],
                        textposition="top center",
                        textfont=dict(size=9, color="#64748b"),
                        customdata=scatter_df[["name", "npiCount", "impressions", "ctr"]].values,
                        hovertemplate=(
                            "<b>%{customdata[0]}</b><br>"
                            "HCPs: %{customdata[1]}<br>"
                            "Avg Freq: %{customdata[2]:.1f}<br>"
                            "CTR: %{customdata[3]:.2f}%<extra></extra>"
                        ),
                    )
                )
                fig_scatter.update_layout(
                    height=480,
                    margin=dict(l=40, r=20, t=20, b=50),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    xaxis=dict(
                        title="Avg Frequency per HCP",
                        gridcolor="#f1f5f9",
                    ),
                    yaxis=dict(
                        title="CTR %",
                        gridcolor="#f1f5f9",
                    ),
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


# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()