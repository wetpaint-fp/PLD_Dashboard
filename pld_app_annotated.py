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

# Shared Plotly tooltip style — applied to every figure via fig.update_traces().
PLOTLY_HOVERLABEL = dict(
    bgcolor="rgba(255,255,255,0.8)",
    bordercolor="#e2e8f0",
    font=dict(color=BRAND["neutral"], size=12),
    align="left",
)

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

# ─────────────────────────────────────────────────────────────────────────────
# HEROICONS — inline SVG icon system
# ─────────────────────────────────────────────────────────────────────────────
# All icons are Heroicons v2 solid (24×24). Inner path content only — the
# outer <svg> wrapper is added by _icon() which injects BRAND["primary"] fill.

_IC_CHART_BAR = (
    '<path d="M18.375 2.25C17.3395 2.25 16.5 3.08947 16.5 4.125V19.875C16.5 20.9105'
    ' 17.3395 21.75 18.375 21.75H19.125C20.1605 21.75 21 20.9105 21 19.875V4.125C21'
    ' 3.08947 20.1605 2.25 19.125 2.25H18.375Z"/>'
    '<path d="M9.75 8.625C9.75 7.58947 10.5895 6.75 11.625 6.75H12.375C13.4105 6.75'
    ' 14.25 7.58947 14.25 8.625V19.875C14.25 20.9105 13.4105 21.75 12.375 21.75H11.625'
    'C10.5895 21.75 9.75 20.9105 9.75 19.875V8.625Z"/>'
    '<path d="M3 13.125C3 12.0895 3.83947 11.25 4.875 11.25H5.625C6.66053 11.25 7.5'
    ' 12.0895 7.5 13.125V19.875C7.5 20.9105 6.66053 21.75 5.625 21.75H4.875C3.83947'
    ' 21.75 3 20.9105 3 19.875V13.125Z"/>'
)
_IC_ARROW_TRENDING_UP = (
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M15.2194 6.26793C15.3679 5.88122'
    ' 15.8017 5.68808 16.1884 5.83652L22.1297 8.11716C22.3154 8.18844 22.4651 8.33057'
    ' 22.546 8.51229C22.627 8.694 22.6324 8.90042 22.5611 9.08612L20.2804 15.0274'
    'C20.132 15.4141 19.6982 15.6072 19.3115 15.4588C18.9248 15.3104 18.7316 14.8765'
    ' 18.8801 14.4898L20.5118 10.239L19.4253 10.7227C16.9721 11.815 15.1036 13.6758'
    ' 13.975 15.8962C13.8662 16.1104 13.6614 16.2594 13.4241 16.2971C13.1869 16.3348'
    ' 12.946 16.2566 12.7761 16.0868L9 12.3107L2.78033 18.5303C2.48744 18.8232 2.01256'
    ' 18.8232 1.71967 18.5303C1.42678 18.2374 1.42678 17.7626 1.71967 17.4697L8.46967'
    ' 10.7197C8.61032 10.579 8.80109 10.5 9 10.5C9.19891 10.5 9.38968 10.579 9.53033'
    ' 10.7197L13.1363 14.3257C14.4369 12.2046 16.3711 10.4406 18.8152 9.35239L19.9017'
    ' 8.86864L15.6508 7.23689C15.2641 7.08845 15.071 6.65463 15.2194 6.26793Z"/>'
)
_IC_VIEWFINDER = (
    '<path d="M6 3C4.34315 3 3 4.34315 3 6V7.5C3 7.91421 3.33579 8.25 3.75 8.25'
    'C4.16421 8.25 4.5 7.91421 4.5 7.5V6C4.5 5.17157 5.17157 4.5 6 4.5H7.5C7.91421'
    ' 4.5 8.25 4.16421 8.25 3.75C8.25 3.33579 7.91421 3 7.5 3H6Z"/>'
    '<path d="M16.5 3C16.0858 3 15.75 3.33579 15.75 3.75C15.75 4.16421 16.0858 4.5'
    ' 16.5 4.5H18C18.8284 4.5 19.5 5.17157 19.5 6V7.5C19.5 7.91421 19.8358 8.25'
    ' 20.25 8.25C20.6642 8.25 21 7.91421 21 7.5V6C21 4.34315 19.6569 3 18 3H16.5Z"/>'
    '<path d="M12 8.25C9.92893 8.25 8.25 9.92893 8.25 12C8.25 14.0711 9.92893 15.75'
    ' 12 15.75C14.0711 15.75 15.75 14.0711 15.75 12C15.75 9.92893 14.0711 8.25 12 8.25Z"/>'
    '<path d="M4.5 16.5C4.5 16.0858 4.16421 15.75 3.75 15.75C3.33579 15.75 3 16.0858'
    ' 3 16.5V18C3 19.6569 4.34315 21 6 21H7.5C7.91421 21 8.25 20.6642 8.25 20.25'
    'C8.25 19.8358 7.91421 19.5 7.5 19.5H6C5.17157 19.5 4.5 18.8284 4.5 18V16.5Z"/>'
    '<path d="M21 16.5C21 16.0858 20.6642 15.75 20.25 15.75C19.8358 15.75 19.5 16.0858'
    ' 19.5 16.5V18C19.5 18.8284 18.8284 19.5 18 19.5H16.5C16.0858 19.5 15.75 19.8358'
    ' 15.75 20.25C15.75 20.6642 16.0858 21 16.5 21H18C19.6569 21 21 19.6569 21 18V16.5Z"/>'
)
_IC_TABLE = (
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M1.5 5.625C1.5 4.58947 2.33947'
    ' 3.75 3.375 3.75H20.625C21.6605 3.75 22.5 4.58947 22.5 5.625V18.375C22.5 19.4105'
    ' 21.6605 20.25 20.625 20.25H3.375C2.33947 20.25 1.5 19.4105 1.5 18.375V5.625ZM21'
    ' 9.375C21 9.16789 20.8321 9 20.625 9H13.125C12.9179 9 12.75 9.16789 12.75 9.375'
    'V10.875C12.75 11.0821 12.9179 11.25 13.125 11.25H20.625C20.8321 11.25 21 11.0821'
    ' 21 10.875V9.375ZM21 13.125C21 12.9179 20.8321 12.75 20.625 12.75H13.125C12.9179'
    ' 12.75 12.75 12.9179 12.75 13.125V14.625C12.75 14.8321 12.9179 15 13.125 15'
    'H20.625C20.8321 15 21 14.8321 21 14.625V13.125ZM21 16.875C21 16.6679 20.8321'
    ' 16.5 20.625 16.5H13.125C12.9179 16.5 12.75 16.6679 12.75 16.875V18.375C12.75'
    ' 18.5821 12.9179 18.75 13.125 18.75H20.625C20.8321 18.75 21 18.5821 21 18.375'
    'V16.875ZM10.875 18.75C11.0821 18.75 11.25 18.5821 11.25 18.375V16.875C11.25'
    ' 16.6679 11.0821 16.5 10.875 16.5H3.375C3.16789 16.5 3 16.6679 3 16.875V18.375'
    'C3 18.5821 3.16789 18.75 3.375 18.75H10.875ZM3.375 15H10.875C11.0821 15 11.25'
    ' 14.8321 11.25 14.625V13.125C11.25 12.9179 11.0821 12.75 10.875 12.75H3.375'
    'C3.16789 12.75 3 12.9179 3 13.125V14.625C3 14.8321 3.16789 15 3.375 15ZM3.375'
    ' 11.25H10.875C11.0821 11.25 11.25 11.0821 11.25 10.875V9.375C11.25 9.16789'
    ' 11.0821 9 10.875 9H3.375C3.16789 9 3 9.16789 3 9.375V10.875C3 11.0821 3.16789'
    ' 11.25 3.375 11.25Z"/>'
)
_IC_USERS = (
    '<path d="M4.5 6.375C4.5 4.09683 6.34683 2.25 8.625 2.25C10.9032 2.25 12.75 4.09683'
    ' 12.75 6.375C12.75 8.65317 10.9032 10.5 8.625 10.5C6.34683 10.5 4.5 8.65317 4.5 6.375Z"/>'
    '<path d="M14.25 8.625C14.25 6.76104 15.761 5.25 17.625 5.25C19.489 5.25 21 6.76104'
    ' 21 8.625C21 10.489 19.489 12 17.625 12C15.761 12 14.25 10.489 14.25 8.625Z"/>'
    '<path d="M1.5 19.125C1.5 15.19 4.68997 12 8.625 12C12.56 12 15.75 15.19 15.75'
    ' 19.125V19.1276C15.75 19.1674 15.7496 19.2074 15.749 19.2469C15.7446 19.5054'
    ' 15.6074 19.7435 15.3859 19.8768C13.4107 21.0661 11.0966 21.75 8.625 21.75'
    'C6.15343 21.75 3.8393 21.0661 1.86406 19.8768C1.64256 19.7435 1.50537 19.5054'
    ' 1.50103 19.2469C1.50034 19.2064 1.5 19.1657 1.5 19.125Z"/>'
    '<path d="M17.2498 19.1281C17.2498 19.1762 17.2494 19.2244 17.2486 19.2722'
    'C17.2429 19.6108 17.1612 19.9378 17.0157 20.232C17.2172 20.2439 17.4203 20.25'
    ' 17.6248 20.25C19.2206 20.25 20.732 19.8803 22.0764 19.2213C22.3234 19.1002'
    ' 22.4843 18.8536 22.4957 18.5787C22.4984 18.5111 22.4998 18.4432 22.4998 18.375'
    'C22.4998 15.6826 20.3172 13.5 17.6248 13.5C16.8784 13.5 16.1711 13.6678 15.5387'
    ' 13.9676C16.6135 15.4061 17.2498 17.1912 17.2498 19.125V19.1281Z"/>'
)
_IC_ADJUSTMENTS = (
    '<path d="M18.75 12.75L20.25 12.75C20.6642 12.75 21 12.4142 21 12C21 11.5858'
    ' 20.6642 11.25 20.25 11.25L18.75 11.25C18.3358 11.25 18 11.5858 18 12C18'
    ' 12.4142 18.3358 12.75 18.75 12.75Z"/>'
    '<path d="M12 6C12 5.58579 12.3358 5.25 12.75 5.25L20.25 5.25002C20.6642 5.25002'
    ' 21 5.5858 21 6.00002C21 6.41423 20.6642 6.75002 20.25 6.75002L12.75 6.75'
    'C12.3358 6.75 12 6.41421 12 6Z"/>'
    '<path d="M12 18C12 17.5858 12.3358 17.25 12.75 17.25L20.25 17.25C20.6642 17.25'
    ' 21 17.5858 21 18C21 18.4142 20.6642 18.75 20.25 18.75L12.75 18.75C12.3358 18.75'
    ' 12 18.4142 12 18Z"/>'
    '<path d="M3.75001 6.75001L5.25001 6.75C5.66422 6.75 6 6.41421 6 5.99999C6 5.58578'
    ' 5.66421 5.25 5.24999 5.25L3.74999 5.25001C3.33578 5.25002 3 5.58581 3 6.00002'
    'C3 6.41424 3.33579 6.75002 3.75001 6.75001Z"/>'
    '<path d="M5.25001 18.75L3.75001 18.75C3.33579 18.75 3 18.4142 3 18C3 17.5858'
    ' 3.33578 17.25 3.74999 17.25L5.24999 17.25C5.66421 17.25 6 17.5858 6 18C6'
    ' 18.4142 5.66422 18.75 5.25001 18.75Z"/>'
    '<path d="M3 12C3 11.5858 3.33579 11.25 3.75 11.25H11.25C11.6642 11.25 12 11.5858'
    ' 12 12C12 12.4142 11.6642 12.75 11.25 12.75H3.75C3.33579 12.75 3 12.4142 3 12Z"/>'
    '<path d="M9 3.75C7.75736 3.75 6.75 4.75736 6.75 6C6.75 7.24264 7.75736 8.25'
    ' 9 8.25C10.2426 8.25 11.25 7.24264 11.25 6C11.25 4.75736 10.2426 3.75 9 3.75Z"/>'
    '<path d="M12.75 12C12.75 10.7574 13.7574 9.75 15 9.75C16.2426 9.75 17.25 10.7574'
    ' 17.25 12C17.25 13.2426 16.2426 14.25 15 14.25C13.7574 14.25 12.75 13.2426'
    ' 12.75 12Z"/>'
    '<path d="M9 15.75C7.75736 15.75 6.75 16.7574 6.75 18C6.75 19.2426 7.75736 20.25'
    ' 9 20.25C10.2426 20.25 11.25 19.2426 11.25 18C11.25 16.7574 10.2426 15.75 9 15.75Z"/>'
)
_IC_MAP = (
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M8.16147 2.58076C8.68934 2.31683'
    ' 9.31066 2.31683 9.83853 2.58076L14.8323 5.07765C14.9379 5.13043 15.0621 5.13043'
    ' 15.1677 5.07765L19.0365 3.14326C20.2832 2.51992 21.75 3.42647 21.75 4.82031'
    'V17.3047C21.75 18.0149 21.3487 18.6642 20.7135 18.9818L15.8385 21.4193C15.3107'
    ' 21.6832 14.6893 21.6832 14.1615 21.4193L9.16771 18.9224C9.06213 18.8696 8.93787'
    ' 18.8696 8.8323 18.9224L4.96353 20.8568C3.71683 21.4801 2.25 20.5736 2.25 19.1797'
    'V6.69531C2.25 5.98512 2.65125 5.33587 3.28647 5.01826L8.16147 2.58076ZM9 6.00002'
    'C9.41421 6.00002 9.75 6.3358 9.75 6.75002V15C9.75 15.4142 9.41421 15.75 9 15.75'
    'C8.58579 15.75 8.25 15.4142 8.25 15V6.75002C8.25 6.3358 8.58579 6.00002 9 6.00002'
    'ZM15.75 9.00002C15.75 8.5858 15.4142 8.25002 15 8.25002C14.5858 8.25002 14.25'
    ' 8.5858 14.25 9.00002V17.25C14.25 17.6642 14.5858 18 15 18C15.4142 18 15.75'
    ' 17.6642 15.75 17.25V9.00002Z"/>'
)
_IC_CHART_PIE = (
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M2.25 13.5C2.25 8.94365 5.94365'
    ' 5.25 10.5 5.25C10.9142 5.25 11.25 5.58579 11.25 6V12.75H18C18.4142 12.75 18.75'
    ' 13.0858 18.75 13.5C18.75 18.0563 15.0563 21.75 10.5 21.75C5.94365 21.75 2.25'
    ' 18.0563 2.25 13.5Z"/>'
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M12.75 3C12.75 2.58579 13.0858'
    ' 2.25 13.5 2.25C18.0563 2.25 21.75 5.94365 21.75 10.5C21.75 10.9142 21.4142 11.25'
    ' 21 11.25H13.5C13.0858 11.25 12.75 10.9142 12.75 10.5V3Z"/>'
)


_IC_BEAKER = (
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M10.5 3.79758V8.81802C10.5 9.61367'
    ' 10.1839 10.3767 9.62131 10.9393L7.24427 13.3164C8.99161 13.192 10.7578 13.5404'
    ' 12.3354 14.3292C14.0988 15.2109 16.1395 15.442 18.048 14.9649L18.333 14.8937'
    'L14.3787 10.9393C13.8161 10.3767 13.5 9.61367 13.5 8.81802V3.79758C13.0041 3.76602'
    ' 12.504 3.75 12 3.75C11.496 3.75 10.9958 3.76602 10.5 3.79758ZM15 3.93576'
    'C15.3732 3.93623 15.6969 3.65833 15.7442 3.27849C15.7955 2.86746 15.5038 2.4927'
    ' 15.0928 2.44144C14.8362 2.40945 14.5784 2.38138 14.3194 2.3573C13.5556 2.28628'
    ' 12.7819 2.25 12 2.25C11.218 2.25 10.4444 2.28628 9.68055 2.3573C9.4216 2.38138'
    ' 9.16378 2.40945 8.90718 2.44144C8.49615 2.4927 8.2045 2.86746 8.25575 3.27849'
    'C8.30312 3.65833 8.62676 3.93623 8.99999 3.93576V8.81802C8.99999 9.21584 8.84195'
    ' 9.59737 8.56065 9.87868L2.26745 16.1719C0.646313 17.793 1.36446 20.6474 3.73836'
    ' 21.0527C6.42419 21.5112 9.1845 21.75 12 21.75C14.8155 21.75 17.5758 21.5112'
    ' 20.2616 21.0527C22.6355 20.6474 23.3537 17.793 21.7325 16.1719L15.4393 9.87868'
    'C15.158 9.59737 15 9.21584 15 8.81802V3.93576Z"/>'
)
_IC_CALENDAR = (
    '<path d="M12.75 12.75C12.75 13.1642 12.4142 13.5 12 13.5C11.5858 13.5 11.25 13.1642'
    ' 11.25 12.75C11.25 12.3358 11.5858 12 12 12C12.4142 12 12.75 12.3358 12.75 12.75Z"/>'
    '<path d="M7.5 15.75C7.91421 15.75 8.25 15.4142 8.25 15C8.25 14.5858 7.91421 14.25'
    ' 7.5 14.25C7.08579 14.25 6.75 14.5858 6.75 15C6.75 15.4142 7.08579 15.75 7.5 15.75Z"/>'
    '<path d="M8.25 17.25C8.25 17.6642 7.91421 18 7.5 18C7.08579 18 6.75 17.6642 6.75'
    ' 17.25C6.75 16.8358 7.08579 16.5 7.5 16.5C7.91421 16.5 8.25 16.8358 8.25 17.25Z"/>'
    '<path d="M9.75 15.75C10.1642 15.75 10.5 15.4142 10.5 15C10.5 14.5858 10.1642 14.25'
    ' 9.75 14.25C9.33579 14.25 9 14.5858 9 15C9 15.4142 9.33579 15.75 9.75 15.75Z"/>'
    '<path d="M10.5 17.25C10.5 17.6642 10.1642 18 9.75 18C9.33579 18 9 17.6642 9 17.25'
    'C9 16.8358 9.33579 16.5 9.75 16.5C10.1642 16.5 10.5 16.8358 10.5 17.25Z"/>'
    '<path d="M12 15.75C12.4142 15.75 12.75 15.4142 12.75 15C12.75 14.5858 12.4142 14.25'
    ' 12 14.25C11.5858 14.25 11.25 14.5858 11.25 15C11.25 15.4142 11.5858 15.75 12 15.75Z"/>'
    '<path d="M12.75 17.25C12.75 17.6642 12.4142 18 12 18C11.5858 18 11.25 17.6642 11.25'
    ' 17.25C11.25 16.8358 11.5858 16.5 12 16.5C12.4142 16.5 12.75 16.8358 12.75 17.25Z"/>'
    '<path d="M14.25 15.75C14.6642 15.75 15 15.4142 15 15C15 14.5858 14.6642 14.25 14.25'
    ' 14.25C13.8358 14.25 13.5 14.5858 13.5 15C13.5 15.4142 13.8358 15.75 14.25 15.75Z"/>'
    '<path d="M15 17.25C15 17.6642 14.6642 18 14.25 18C13.8358 18 13.5 17.6642 13.5 17.25'
    'C13.5 16.8358 13.8358 16.5 14.25 16.5C14.6642 16.5 15 16.8358 15 17.25Z"/>'
    '<path d="M16.5 15.75C16.9142 15.75 17.25 15.4142 17.25 15C17.25 14.5858 16.9142 14.25'
    ' 16.5 14.25C16.0858 14.25 15.75 14.5858 15.75 15C15.75 15.4142 16.0858 15.75 16.5 15.75Z"/>'
    '<path d="M15 12.75C15 13.1642 14.6642 13.5 14.25 13.5C13.8358 13.5 13.5 13.1642 13.5'
    ' 12.75C13.5 12.3358 13.8358 12 14.25 12C14.6642 12 15 12.3358 15 12.75Z"/>'
    '<path d="M16.5 13.5C16.9142 13.5 17.25 13.1642 17.25 12.75C17.25 12.3358 16.9142 12'
    ' 16.5 12C16.0858 12 15.75 12.3358 15.75 12.75C15.75 13.1642 16.0858 13.5 16.5 13.5Z"/>'
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M6.75 2.25C7.16421 2.25 7.5 2.58579'
    ' 7.5 3V4.5H16.5V3C16.5 2.58579 16.8358 2.25 17.25 2.25C17.6642 2.25 18 2.58579 18 3'
    'V4.5H18.75C20.4069 4.5 21.75 5.84315 21.75 7.5V18.75C21.75 20.4069 20.4069 21.75'
    ' 18.75 21.75H5.25C3.59315 21.75 2.25 20.4069 2.25 18.75V7.5C2.25 5.84315 3.59315'
    ' 4.5 5.25 4.5H6V3C6 2.58579 6.33579 2.25 6.75 2.25ZM20.25 11.25C20.25 10.4216'
    ' 19.5784 9.75 18.75 9.75H5.25C4.42157 9.75 3.75 10.4216 3.75 11.25V18.75C3.75'
    ' 19.5784 4.42157 20.25 5.25 20.25H18.75C19.5784 20.25 20.25 19.5784 20.25 18.75V11.25Z"/>'
)
_IC_CURSOR_RIPPLE = (
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M5.63604 4.57538C5.92893 4.86828'
    ' 5.92893 5.34315 5.63604 5.63604C2.12132 9.15076 2.12132 14.8492 5.63604 18.364'
    'C5.92893 18.6569 5.92893 19.1317 5.63604 19.4246C5.34315 19.7175 4.86827 19.7175'
    ' 4.57538 19.4246C0.474874 15.3241 0.474873 8.67589 4.57538 4.57538C4.86827 4.28249'
    ' 5.34315 4.28249 5.63604 4.57538ZM18.364 4.57538C18.6569 4.28249 19.1317 4.28249'
    ' 19.4246 4.57538C23.5251 8.67589 23.5251 15.3241 19.4246 19.4246C19.1317 19.7175'
    ' 18.6569 19.7175 18.364 19.4246C18.0711 19.1317 18.0711 18.6569 18.364 18.364'
    'C21.8787 14.8492 21.8787 9.15076 18.364 5.63604C18.0711 5.34315 18.0711 4.86828'
    ' 18.364 4.57538ZM7.75736 6.6967C8.05025 6.9896 8.05025 7.46447 7.75736 7.75736'
    'C5.41421 10.1005 5.41421 13.8995 7.75736 16.2426C8.05025 16.5355 8.05025 17.0104'
    ' 7.75736 17.3033C7.46447 17.5962 6.98959 17.5962 6.6967 17.3033C3.76777 14.3744'
    ' 3.76777 9.62564 6.6967 6.6967C6.98959 6.40381 7.46447 6.40381 7.75736 6.6967Z'
    'M16.2426 6.6967C16.5355 6.40381 17.0104 6.40381 17.3033 6.6967C20.2322 9.62564'
    ' 20.2322 14.3744 17.3033 17.3033C17.0104 17.5962 16.5355 17.5962 16.2426 17.3033'
    'C15.9497 17.0104 15.9497 16.5355 16.2426 16.2426C18.5858 13.8995 18.5858 10.1005'
    ' 16.2426 7.75736C15.9497 7.46447 15.9497 6.9896 16.2426 6.6967ZM9.87868 8.81802'
    'C10.1716 9.11092 10.1716 9.58579 9.87868 9.87868C8.70711 11.0503 8.70711 12.9498'
    ' 9.87868 14.1213C10.1716 14.4142 10.1716 14.8891 9.87868 15.182C9.58579 15.4749'
    ' 9.11091 15.4749 8.81802 15.182C7.06066 13.4246 7.06066 10.5754 8.81802 8.81802'
    'C9.11091 8.52513 9.58579 8.52513 9.87868 8.81802ZM14.1213 8.81802C14.4142 8.52513'
    ' 14.8891 8.52513 15.182 8.81802C16.9393 10.5754 16.9393 13.4246 15.182 15.182'
    'C14.8891 15.4749 14.4142 15.4749 14.1213 15.182C13.8284 14.8891 13.8284 14.4142'
    ' 14.1213 14.1213C15.2929 12.9498 15.2929 11.0503 14.1213 9.87868C13.8284 9.58579'
    ' 13.8284 9.11092 14.1213 8.81802ZM10.875 12C10.875 11.3787 11.3787 10.875 12 10.875'
    'C12.6213 10.875 13.125 11.3787 13.125 12C13.125 12.6213 12.6213 13.125 12 13.125'
    'C11.3787 13.125 10.875 12.6213 10.875 12Z"/>'
)
_IC_GLOBE = (
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M12 2.25C6.61522 2.25 2.25 6.61522'
    ' 2.25 12C2.25 17.3848 6.61522 21.75 12 21.75C17.3848 21.75 21.75 17.3848 21.75 12'
    'C21.75 6.61522 17.3848 2.25 12 2.25ZM6.26197 6.0723C4.71293 7.57208 3.75 9.67359'
    ' 3.75 12C3.75 16.5563 7.44365 20.25 12 20.25C16.5563 20.25 20.25 16.5563 20.25 12'
    'C20.25 9.24461 18.8992 6.80472 16.8237 5.3064C16.4863 5.84545 16.0374 6.30831'
    ' 15.5056 6.66289L14.2499 7.5L14.4145 7.82918C14.6835 8.3671 14.2923 9 13.6909 9'
    'C13.5653 9 13.4414 8.97076 13.3291 8.91459L12.7252 8.61262C12.2921 8.39607 11.769'
    ' 8.48095 11.4266 8.82336L11.2954 8.9545C10.8561 9.39384 10.8561 10.1062 11.2954'
    ' 10.5455L11.5905 10.8406C11.8474 11.0975 12.2126 11.2146 12.571 11.1548L13.7411'
    ' 10.9598C14.0641 10.906 14.3946 10.9956 14.6462 11.2053L15.9755 12.313C16.2962'
    ' 12.5802 16.4356 13.0073 16.3344 13.4122C15.9519 14.9419 15.1609 16.339 14.046'
    ' 17.4539L13.3233 18.1766C12.9809 18.519 12.4578 18.6039 12.0247 18.3874L11.8718'
    ' 18.3109C11.4907 18.1204 11.2499 17.7308 11.2499 17.3047V16.216C11.2499 15.9176'
    ' 11.1314 15.6315 10.9204 15.4205L9.57328 14.0734C9.23087 13.731 9.14599 13.2079'
    ' 9.36254 12.7747L9.74992 12L8.10954 10.3596C7.22527 9.47535 6.6394 8.33689 6.43381'
    ' 7.10337L6.26197 6.0723Z"/>'
)
_IC_MEGAPHONE = (
    '<path d="M16.8812 4.34543C14.81 5.17401 12.5917 5.7132 10.276 5.91302C9.60847 5.97061'
    ' 8.93276 6.00002 8.25 6.00002H7.5C4.60051 6.00002 2.25 8.35052 2.25 11.25C2.25'
    ' 13.8496 4.13945 16.0079 6.61997 16.4266C6.95424 17.7956 7.41805 19.1138 7.99764'
    ' 20.3674C8.46171 21.3712 9.67181 21.6875 10.5803 21.163L11.2366 20.784C12.1167'
    ' 20.2759 12.4023 19.1913 12.0087 18.3159C11.7738 17.7935 11.5642 17.2574 11.3814'
    ' 16.709C13.2988 16.9671 15.1419 17.4588 16.8812 18.1546C17.6069 15.9852 18 13.6635'
    ' 18 11.25C18 8.83648 17.6069 6.51478 16.8812 4.34543Z"/>'
    '<path d="M18.2606 3.74072C19.0641 6.09642 19.5 8.6223 19.5 11.25C19.5 13.8777 19.0641'
    ' 16.4036 18.2606 18.7593C18.2054 18.9211 18.1487 19.0821 18.0901 19.2422C17.9477'
    ' 19.6312 18.1476 20.0619 18.5366 20.2043C18.9256 20.3467 19.3563 20.1468 19.4987'
    ' 19.7578C19.6387 19.3753 19.7696 18.9884 19.891 18.5973C20.4147 16.9106 20.7627'
    ' 15.1469 20.914 13.3278C21.431 12.7893 21.75 12.0567 21.75 11.25C21.75 10.4434'
    ' 21.431 9.71073 20.914 9.17228C20.7627 7.35319 20.4147 5.58948 19.891 3.90274'
    'C19.7696 3.51165 19.6387 3.12472 19.4987 2.74221C19.3563 2.35324 18.9256 2.15334'
    ' 18.5366 2.29572C18.1476 2.43811 17.9477 2.86885 18.0901 3.25783C18.1487 3.41795'
    ' 18.2055 3.57898 18.2606 3.74072Z"/>'
)
_IC_SIGNAL = (
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M17.3033 5.1967C14.3744 2.26777'
    ' 9.62563 2.26777 6.6967 5.1967C3.76777 8.12563 3.76777 12.8744 6.6967 15.8033'
    'C6.98959 16.0962 6.98959 16.5711 6.6967 16.864C6.40381 17.1569 5.92893 17.1569'
    ' 5.63604 16.864C2.12132 13.3492 2.12132 7.65076 5.63604 4.13604C9.15076 0.62132'
    ' 14.8492 0.62132 18.364 4.13604C20.1211 5.89321 21 8.19775 21 10.4998C21 10.9141'
    ' 20.6642 11.2498 20.25 11.2499C19.8358 11.2499 19.5 10.9141 19.5 10.4999C19.5'
    ' 8.57933 18.7679 6.66128 17.3033 5.1967ZM15.182 7.31802C13.4246 5.56066 10.5754'
    ' 5.56066 8.81802 7.31802C7.06066 9.07538 7.06066 11.9246 8.81802 13.682C9.11091'
    ' 13.9749 9.11091 14.4497 8.81802 14.7426C8.52513 15.0355 8.05025 15.0355 7.75736'
    ' 14.7426C5.41421 12.3995 5.41421 8.60051 7.75736 6.25736C10.1005 3.91421 13.8995'
    ' 3.91421 16.2426 6.25736C17.414 7.42877 18 8.96558 18 10.4999C18 10.9141 17.6642'
    ' 11.2499 17.25 11.2499C16.8358 11.2499 16.5 10.9142 16.5 10.4999C16.5 9.34715'
    ' 16.0608 8.19683 15.182 7.31802ZM11.5484 8.63179C11.8602 8.54824 12.1905 8.67359'
    ' 12.3684 8.94299L17.5955 16.8599C17.7627 17.113 17.7609 17.4419 17.591 17.6932'
    'C17.421 17.9445 17.1165 18.0687 16.8193 18.0079L14.722 17.5787L15.7668 21.4777'
    'C15.874 21.8778 15.6365 22.289 15.2364 22.3963C14.8363 22.5035 14.4251 22.266'
    ' 14.3179 21.8659L13.2732 17.967L11.6717 19.3872C11.4447 19.5884 11.1189 19.6332'
    ' 10.8461 19.5005C10.5733 19.3678 10.4073 19.0839 10.4254 18.7811L10.9939 9.3113'
    'C11.0132 8.98905 11.2366 8.71534 11.5484 8.63179Z"/>'
)
_IC_TV = (
    '<path d="M19.5 6H4.5V15H19.5V6Z"/>'
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M3.375 3C2.33947 3 1.5 3.83947 1.5'
    ' 4.875V16.125C1.5 17.1605 2.33947 18 3.375 18H9.75V19.5H6C5.58579 19.5 5.25 19.8358'
    ' 5.25 20.25C5.25 20.6642 5.58579 21 6 21H18C18.4142 21 18.75 20.6642 18.75 20.25'
    'C18.75 19.8358 18.4142 19.5 18 19.5H14.25V18H20.625C21.6605 18 22.5 17.1605 22.5'
    ' 16.125V4.875C22.5 3.83947 21.6605 3 20.625 3H3.375ZM3.375 16.5H20.625C20.8321 16.5'
    ' 21 16.3321 21 16.125V4.875C21 4.66789 20.8321 4.5 20.625 4.5H3.375C3.16789 4.5 3'
    ' 4.66789 3 4.875V16.125C3 16.3321 3.16789 16.5 3.375 16.5Z"/>'
)
_IC_VIEW_COLUMNS = (
    '<path d="M15 3.75H9V20.25H15V3.75Z"/>'
    '<path d="M16.5 20.25H19.875C20.9105 20.25 21.75 19.4105 21.75 18.375V5.625C21.75'
    ' 4.58947 20.9105 3.75 19.875 3.75H16.5V20.25Z"/>'
    '<path d="M4.125 3.75H7.5V20.25H4.125C3.08947 20.25 2.25 19.4105 2.25 18.375V5.625'
    'C2.25 4.58947 3.08947 3.75 4.125 3.75Z"/>'
)
_IC_FUNNEL = (
    '<path fill-rule="evenodd" clip-rule="evenodd" d="M3.79154 2.93825C6.46066 2.48562'
    ' 9.20314 2.25 12.0001 2.25C14.7969 2.25 17.5394 2.48561 20.2085 2.93822C21.1108'
    ' 3.09125 21.75 3.87676 21.75 4.77402V5.81802C21.75 6.61367 21.4339 7.37673 20.8713'
    ' 7.93934L14.6893 14.1213C14.408 14.4026 14.25 14.7842 14.25 15.182V18.1094C14.25'
    ' 19.2457 13.608 20.2845 12.5916 20.7927L10.8354 21.6708C10.6029 21.7871 10.3268'
    ' 21.7746 10.1057 21.638C9.88459 21.5013 9.75 21.2599 9.75 21V15.182C9.75 14.7842'
    ' 9.59196 14.4026 9.31066 14.1213L3.12868 7.93934C2.56607 7.37673 2.25 6.61367 2.25'
    ' 5.81802V4.77404C2.25 3.87678 2.88917 3.09127 3.79154 2.93825Z"/>'
)

def _icon(inner: str, size: int = 14) -> str:
    """Wrap Heroicon inner SVG paths in a sized, brand-coloured <svg> tag."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
        f' fill="{BRAND["primary"]}" width="{size}" height="{size}"'
        f' style="vertical-align:-2px;margin-right:6px;">'
        f'{inner}</svg>'
    )


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

    /* Top bar */
    [data-testid="stHeader"] {
        background: #ffffff;
    }

    /* Sidebar collapse button — always visible */
    [data-testid="stSidebarCollapseButton"] {
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* Styles the sidebar panel itself */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ede8f0 0%, #ffffff 100%);
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] .stMarkdown h1 { font-size: 1.25rem; }

    /* Sidebar section label style */
    .sidebar-section-label {
        font-size: .7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .1em;
        color: #64748b;
        margin: .75rem 0 .25rem 0;
    }

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

        # AL assets (DocNews Alert / Doximity) report headline_view / content_view,
        # not Impression / Click. This mirrors real Doximity data behaviour.
        if asset_id.startswith("AL"):
            activity_type = "content_view" if is_click else "headline_view"
        elif asset_id.startswith("NA"):
            activity_type = "Click"   # NA = click-only (EHS Native Display)
        else:
            activity_type = "Click" if is_click else "Impression"

        rows.append({
            "ACTIVITY_ID": f"act_{i}",
            "NPI": npi_obj["id"],
            "PLACEMENT_NAME": pname,
            "VENDOR": pd_detail["PARTNER_NAME"],
            "CHANNEL": pd_detail["CHANNEL_CATEGORY"],
            "PROGRAM": pd_detail["PROGRAM_FRIENDLY_NAME"],
            "FP_ASSET_ID": asset_id,
            "ACTIVITY_TYPE": activity_type,
            "ACTIVITY_DATE": date.strftime("%Y-%m-%d"),
            "SPECIALTY": npi_obj["specialty"],
            "STATE": npi_obj["state"],
            "Segment": segment,
        })

    # Add Conversion events — DeepIntent (DM assets) only, mirroring real data.
    # CVR ≈ 5% of clicks → ~20 conversion events for a 4000-row dataset.
    dm_clicks = [r for r in rows if r["FP_ASSET_ID"].startswith("DM") and r["ACTIVITY_TYPE"] == "Click"]
    conversion_sample = random.sample(dm_clicks, min(20, len(dm_clicks)))
    for src in conversion_sample:
        rows.append({
            **src,
            "ACTIVITY_ID": f"conv_{src['ACTIVITY_ID']}",
            "ACTIVITY_TYPE": "Conversion",
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

    Doximity (AL assets) reports headline_view / content_view rather than
    Impression / Click, so we compute an EngRate column for that vendor
    instead of a traditional CTR.
    """
    filt = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]

    # Count only true delivery events (not conversions) for impression total
    total_imps   = int((filt["ACTIVITY_TYPE"].isin(["Impression", "headline_view", "content_view"])).sum())
    total_clicks = int((filt["ACTIVITY_TYPE"] == "Click").sum())
    total_conversions = int((filt["ACTIVITY_TYPE"] == "Conversion").sum())
    cvr = round(total_conversions / total_clicks * 100, 2) if total_clicks else 0.0

    unique_npis = filt["NPI"].nunique()
    frequency   = round(total_imps / unique_npis, 1) if unique_npis else 0

    # Per-vendor aggregation — include Doximity engagement counts.
    by_partner = (
        filt.groupby("VENDOR")
        .agg(
            Impressions=("ACTIVITY_ID", "count"),
            Clicks=("ACTIVITY_TYPE",          lambda s: (s == "Click").sum()),
            HeadlineViews=("ACTIVITY_TYPE",   lambda s: (s == "headline_view").sum()),
            ContentViews=("ACTIVITY_TYPE",    lambda s: (s == "content_view").sum()),
            Reach=("NPI", "nunique"),
        )
        .reset_index()
    )
    # Traditional CTR for non-Doximity vendors (exclude Doximity's headline/content rows
    # from the denominator to avoid artificially low CTR).
    non_dox_imps = by_partner["Impressions"] - by_partner["HeadlineViews"] - by_partner["ContentViews"]
    by_partner["CTR"] = np.where(
        non_dox_imps > 0,
        (by_partner["Clicks"] / non_dox_imps) * 100,
        np.nan,
    )
    # Engagement rate (content_view / headline_view) for Doximity rows only.
    by_partner["EngRate"] = np.where(
        by_partner["HeadlineViews"] > 0,
        (by_partner["ContentViews"] / by_partner["HeadlineViews"]) * 100,
        np.nan,
    )

    return {
        "total_imps":         total_imps,
        "total_clicks":       total_clicks,
        "total_conversions":  total_conversions,
        "cvr":                cvr,
        "unique_npis":        unique_npis,
        "frequency":          frequency,
        "chart":              by_partner,
    }


def compute_freq_distribution(df: pd.DataFrame, vendor_filter: str) -> pd.DataFrame:
    """
    Bucket HCPs by impression frequency into cohorts: 1×, 2–3×, 4–5×, 6×+.

    Only counts Impression rows (not clicks, conversions, or Doximity
    headline/content views) so the distribution reflects true ad exposure.

    Returns a DataFrame with columns: Bucket, HCPs, Pct.
    """
    filt = df if vendor_filter == "All" else df[df["VENDOR"] == vendor_filter]
    imp_filt = filt[filt["ACTIVITY_TYPE"] == "Impression"]
    npi_counts = imp_filt.groupby("NPI").size()

    buckets = {
        "1×":   int((npi_counts == 1).sum()),
        "2–3×": int(((npi_counts >= 2) & (npi_counts <= 3)).sum()),
        "4–5×": int(((npi_counts >= 4) & (npi_counts <= 5)).sum()),
        "6×+":  int((npi_counts >= 6).sum()),
    }
    total = sum(buckets.values()) or 1
    return pd.DataFrame({
        "Bucket": list(buckets.keys()),
        "HCPs":   list(buckets.values()),
        "Pct":    [v / total * 100 for v in buckets.values()],
    })


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
            <p style="font-size:.9rem;font-weight:600;color:#FC8549;text-transform:uppercase;letter-spacing:.08em;margin:6px 0 0 2px;">
                Revealing the True Colors of Every Brand
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # ── Navigation radio ──
        st.markdown('<div class="sidebar-section-label">Pages</div>', unsafe_allow_html=True)
        active_tab = st.radio(
            "Navigation",
            ["Partner Performance", "Creative Performance", "HCP Audience"],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # ── Data source toggle ──
        # Allows switching between the seeded mock dataset and the real CSVs.
        # In SiS production the real data path uses Snowpark (see load_real_data).
        st.markdown('<div class="sidebar-section-label">Data Source</div>', unsafe_allow_html=True)
        data_source = st.radio(
            "Data Source",
            ["Mock Data", "Real Data"],
            key="data_source",
            label_visibility="collapsed",
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

        st.markdown("---")
        st.markdown(
            '<div style="font-size:.65rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:.08em;color:#64748b;margin-bottom:.35rem;">'
            'Campaign Settings</div>',
            unsafe_allow_html=True,
        )
        # Target universe drives Coverage % on the Partner Performance page.
        # Set this to the total HCPs in your target NPI list.
        target_universe = st.number_input(
            "Target Universe (HCPs)",
            min_value=100,
            max_value=100_000,
            value=5_000,
            step=100,
            key="target_universe",
            help="Total HCPs in your target NPI list. Used to calculate Coverage %.",
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
        "Partner Performance":   "Partner Performance",
        "Creative Performance":  "Creative Performance",
        "HCP Audience":          "HCP Audience",
    }
    header_title = header_titles.get(active_tab, active_tab)
    st.markdown(
        f"""
        <div style="margin-bottom:.25rem;">
            <h1 style="font-size:1.75rem;font-weight:800;color:#050607;margin:0 0 .35rem 0;">{header_title}</h1>
            <hr style="border:none;border-top:1px solid #e2e8f0;margin:0;">
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
        # Coverage % = unique HCPs reached / target universe (set in sidebar).
        coverage_pct = (metrics["unique_npis"] / target_universe * 100) if target_universe else 0
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            kpi_card("Total Impressions", f"{metrics['total_imps']:,}")
        with k2:
            kpi_card("Total Clicks", f"{metrics['total_clicks']:,}")
        with k3:
            kpi_card(
                "Conversions",
                str(metrics["total_conversions"]),
                f"CVR {metrics['cvr']:.2f}% of clicks",
            )
        with k4:
            kpi_card(
                "Unique Reach",
                f"{metrics['unique_npis']:,}",
                f"{coverage_pct:.0f}% of {target_universe:,} target HCPs",
            )
        with k5:
            kpi_card("Avg Frequency", str(metrics["frequency"]), "Imps per NPI")

        st.markdown("")

        # ── Conversion Funnel ──────────────────────────────────────────────────
        # Three-step funnel: Impressions → Clicks → Conversions.
        # go.Funnel shows % of initial at each stage so CTR and CVR are
        # visible at a glance without needing separate labels.
        st.markdown(
            f'<div class="section-title">{_icon(_IC_FUNNEL)}Conversion Funnel</div>',
            unsafe_allow_html=True,
        )
        fig_funnel = go.Figure(go.Funnel(
            y=["Impressions", "Clicks", "Conversions"],
            x=[metrics["total_imps"], metrics["total_clicks"], metrics["total_conversions"]],
            textinfo="value+percent initial",
            textfont=dict(size=13),
            marker=dict(color=[BRAND["primary"], BRAND["accent"], BRAND["plum"]]),
            connector=dict(line=dict(color="#e2e8f0", width=1)),
            hovertemplate=(
                "<b>%{label}</b><br>Count:<br>%{value:,}<br>"
                "% of Impressions:<br>%{percentInitial:.2%}<extra></extra>"
            ),
        ))
        fig_funnel.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=10, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
        fig_funnel.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
        st.plotly_chart(fig_funnel, use_container_width=True, key="pp_funnel")

        # ── Monthly Trend Chart ────────────────────────────────────────────────
        trend = compute_trend_data(df, vendor_filter)

        st.markdown(f'<div class="section-title">{_icon(_IC_CHART_BAR)}Monthly Reach & Frequency</div>', unsafe_allow_html=True)

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
                hovertemplate="<b>%{x}</b><br>Reach:<br>%{y:,}<extra></extra>",
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
                hovertemplate="<b>%{x}</b><br>Avg Frequency:<br>%{y:.1f}<extra></extra>",
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
        fig_trend.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
        st.plotly_chart(fig_trend, use_container_width=True)

        # ── Three-column bar section: CTR | Reach | Frequency Distribution ───────
        c1, c2, c3 = st.columns(3)
        chart_df = metrics["chart"]

        with c1:
            # Doximity reports engagement rate (content_view / headline_view)
            # rather than CTR (click / impression). We use whichever metric is
            # valid per vendor so no vendor appears blank or misleading.
            display_metric = chart_df["CTR"].where(
                chart_df["CTR"].notna(), chart_df["EngRate"]
            )
            has_eng_rate = chart_df["EngRate"].notna().any()
            ctr_title_note = (
                '<span style="font-size:.6rem;font-weight:500;color:#94a3b8;'
                'text-transform:none;letter-spacing:normal;margin-left:6px;">'
                '* Doximity = Engagement Rate</span>'
                if has_eng_rate else ""
            )
            st.markdown(
                f'<div class="section-title">{_icon(_IC_CURSOR_RIPPLE)}CTR % by Partner{ctr_title_note}</div>',
                unsafe_allow_html=True,
            )
            bar_colors = [
                BRAND["plum"] if not pd.isna(row["EngRate"]) else BRAND["accent"]
                for _, row in chart_df.iterrows()
            ]
            fig_ctr = go.Figure(go.Bar(
                x=chart_df["VENDOR"],
                y=display_metric,
                marker_color=bar_colors,
                marker_cornerradius=6,
                text=display_metric.round(2).astype(str) + "%",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
            ))
            fig_ctr.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9", title="CTR / Eng Rate %"),
            )
            fig_ctr.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_ctr, use_container_width=True, key="pp_ctr_partner")

        with c2:
            st.markdown(f'<div class="section-title">{_icon(_IC_MEGAPHONE)}Reach by Partner</div>', unsafe_allow_html=True)
            fig_reach = go.Figure(go.Bar(
                x=chart_df["VENDOR"],
                y=chart_df["Reach"],
                marker_color=BRAND["primary"],
                marker_cornerradius=6,
                hovertemplate="<b>%{x}</b><br>Reach:<br>%{y:,}<extra></extra>",
            ))
            fig_reach.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9"),
            )
            fig_reach.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_reach, use_container_width=True, key="pp_reach_partner")

        with c3:
            st.markdown(
                f'<div class="section-title">{_icon(_IC_SIGNAL)}Frequency Distribution'
                '<span style="font-size:.6rem;font-weight:500;color:#94a3b8;'
                'text-transform:none;letter-spacing:normal;margin-left:6px;">'
                '% of HCPs by exposure</span></div>',
                unsafe_allow_html=True,
            )
            freq_dist = compute_freq_distribution(df, vendor_filter)
            bucket_colors = [BRAND["secondary"], BRAND["primary"], BRAND["accent"], BRAND["plum"]]
            fig_freq_dist = go.Figure(go.Bar(
                x=freq_dist["Bucket"],
                y=freq_dist["Pct"],
                marker_color=bucket_colors,
                marker_cornerradius=6,
                text=freq_dist["Pct"].round(0).astype(int).astype(str) + "%",
                textposition="outside",
                customdata=freq_dist["HCPs"].values,
                hovertemplate=(
                    "<b>%{x}</b><br>HCPs:<br>%{customdata:,}<br>"
                    "Share:<br>%{y:.1f}%<extra></extra>"
                ),
            ))
            fig_freq_dist.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9", title="% of HCPs"),
                xaxis=dict(categoryorder="array", categoryarray=["1×", "2–3×", "4–5×", "6×+"]),
            )
            fig_freq_dist.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_freq_dist, use_container_width=True, key="pp_freq_dist")

        # ── CTR by Stage × Partner Heatmap ────────────────────────────────────
        st.markdown(
            f'<div class="section-title">{_icon(_IC_VIEWFINDER)}CTR % by Stage × Partner'
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
        # Compute global CTR range from unfiltered data so the color scale
        # stays anchored when a vendor filter is applied.
        _global_seg = df[df["Segment"].notna() & (df["Segment"] != "Unknown")]
        _global_seg = _global_seg[~_global_seg["FP_ASSET_ID"].str.startswith("NA", na=False)]
        _global_sv_agg = (
            _global_seg.groupby(["Segment", "VENDOR"])
            .agg(
                Impressions=("ACTIVITY_ID", "count"),
                Clicks=("ACTIVITY_TYPE", lambda s: (s == "Click").sum()),
            )
            .reset_index()
        )
        _global_sv_agg["CTR"] = np.where(
            _global_sv_agg["Impressions"] > 0,
            _global_sv_agg["Clicks"] / _global_sv_agg["Impressions"] * 100,
            np.nan,
        )
        _sv_zmin = float(_global_sv_agg["CTR"].min(skipna=True))
        _sv_zmax = float(_global_sv_agg["CTR"].max(skipna=True))
        if len(sv_agg):
            pivot_sv  = sv_agg.pivot(index="Segment", columns="VENDOR", values="CTR")
            # Reindex rows to always show all known segments (gaps become NaN → "—").
            all_known_segs = [s for s in SEGMENT_FUNNEL_ORDER if s in
                              df["Segment"].dropna().unique().tolist()]
            pivot_sv  = pivot_sv.reindex(all_known_segs)
            funnel_pos = {s: i for i, s in enumerate(SEGMENT_FUNNEL_ORDER)}
            row_order  = sorted(pivot_sv.index, key=lambda s: funnel_pos.get(s, 999))
            z_vals     = pivot_sv.values.tolist()
            text_vals  = [[f"{v:.1f}%" if v == v else "—" for v in row] for row in z_vals]
            fig_sv = go.Figure(go.Heatmap(
                z=z_vals,
                x=pivot_sv.columns.tolist(),
                y=pivot_sv.index.tolist(),
                colorscale=[[0, "#E8DEEE"], [0.5, "#8A5CA8"], [1, "#47254A"]],
                zmin=_sv_zmin,
                zmax=_sv_zmax,
                text=text_vals,
                texttemplate="%{text}",
                textfont=dict(size=11),
                hovertemplate="<b>%{y}</b><br>Partner:<br>%{x}<br>CTR:<br>%{text}<extra></extra>",
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
            fig_sv.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_sv, use_container_width=True, key="pp_seg_vendor_heatmap")
        else:
            st.info("No segment data available.")

        # ── Drill-Down Table ───────────────────────────────────────────────────
        st.markdown(
            f'<div class="section-title">{_icon(_IC_TABLE)}Detailed Performance  '
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
            st.markdown(f'<div class="section-title">{_icon(_IC_CURSOR_RIPPLE)}CTR % by Asset</div>', unsafe_allow_html=True)
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
                hovertemplate="<b>%{y}</b><br>CTR:<br>%{x:.2f}%<extra></extra>",
            ))
            fig_ctr.update_layout(
                height=bar_h,
                margin=dict(l=20, r=60, t=10, b=20),
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(gridcolor="#f1f5f9", title="CTR %"),
                yaxis=dict(tickfont=dict(size=11)),
            )
            fig_ctr.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_ctr, use_container_width=True, key="ctr_by_asset")

        with c2:
            st.markdown(f'<div class="section-title">{_icon(_IC_MEGAPHONE)}Reach by Asset</div>', unsafe_allow_html=True)
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
                hovertemplate="<b>%{y}</b><br>Reach:<br>%{x:,}<extra></extra>",
            ))
            fig_reach.update_layout(
                height=bar_h,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(gridcolor="#f1f5f9", title="Unique HCPs"),
                yaxis=dict(tickfont=dict(size=11)),
            )
            fig_reach.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_reach, use_container_width=True, key="reach_by_asset")

        # ── Native Display — clicks only ────────────────────────────────────────
        if len(native_assets):
            st.markdown(f'<div class="section-title">{_icon(_IC_TV)}Native Display  <span style="font-size:.65rem;font-weight:500;color:#94a3b8;text-transform:none;letter-spacing:normal;">Clicks only — CTR not applicable</span></div>', unsafe_allow_html=True)
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
                    hovertemplate="<b>%{y}</b><br>Clicks:<br>%{x:,}<extra></extra>",
                ))
                fig_nd_clicks.update_layout(
                    height=max(200, len(nd_ordered) * 36),
                    margin=dict(l=20, r=40, t=10, b=20),
                    plot_bgcolor="white", paper_bgcolor="white",
                    xaxis=dict(gridcolor="#f1f5f9", title="Clicks"),
                    yaxis=dict(tickfont=dict(size=11)),
                )
                fig_nd_clicks.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
                st.plotly_chart(fig_nd_clicks, use_container_width=True, key="nd_clicks")
            with nd_c2:
                fig_nd_reach = go.Figure(go.Bar(
                    x=nd_ordered["Reach"],
                    y=nd_ordered["Asset"],
                    orientation="h",
                    marker_color=BRAND["secondary"],
                    marker_opacity=0.75,
                    marker_cornerradius=4,
                    hovertemplate="<b>%{y}</b><br>Reach:<br>%{x:,}<extra></extra>",
                ))
                fig_nd_reach.update_layout(
                    height=max(200, len(nd_ordered) * 36),
                    margin=dict(l=20, r=20, t=10, b=20),
                    plot_bgcolor="white", paper_bgcolor="white",
                    xaxis=dict(gridcolor="#f1f5f9", title="Unique HCPs"),
                    yaxis=dict(tickfont=dict(size=11)),
                )
                fig_nd_reach.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
                st.plotly_chart(fig_nd_reach, use_container_width=True, key="nd_reach")

        # ── Format Family Summary & Frequency vs CTR ───────────────────────────
        c3, c4 = st.columns(2)

        with c3:
            st.markdown(f'<div class="section-title">{_icon(_IC_TV)}CTR % by Format Family  <span style="font-size:.65rem;font-weight:500;color:#94a3b8;text-transform:none;letter-spacing:normal;">Native Display excluded — clicks only</span></div>', unsafe_allow_html=True)
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
                hovertemplate="<b>%{x}</b><br>CTR:<br>%{y:.2f}%<extra></extra>",
            ))
            fig_fmt.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis=dict(gridcolor="#f1f5f9", title="CTR %"),
            )
            fig_fmt.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_fmt, use_container_width=True, key="ctr_by_format")

        with c4:
            st.markdown(f'<div class="section-title">{_icon(_IC_SIGNAL)}Frequency vs CTR</div>', unsafe_allow_html=True)
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
                    "Reach:<br>%{customdata[1]}<br>"
                    "Avg Freq:<br>%{customdata[2]:.1f}<br>"
                    "CTR:<br>%{customdata[3]:.2f}%<extra></extra>"
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
            fig_freq.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_freq, use_container_width=True, key="freq_vs_ctr")

        # ── Audience Segment × Format CTR Heatmap ─────────────────────────────
        # The unique creative-page question: which creative format engages each
        # journey stage most effectively? The previous stacked reach chart showed
        # who we're reaching but not how well — the heatmap crosses both dimensions.
        # Native Display (click-only) and DocNews Alert (engagement-only) have no
        # valid CTR, so only Programmatic Banner cells are coloured.
        st.markdown(
            f'<div class="section-title">{_icon(_IC_VIEWFINDER)}Prescriber Journey × Creative Format'
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
                hovertemplate="<b>%{y}</b><br>Format:<br>%{x}<br>%{text}<extra></extra>",
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
            fig_cp_heat.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_cp_heat, use_container_width=True, key="cp_seg_format_heatmap")
        else:
            st.info("No segment data available.")

        # ── Asset Detail Table ─────────────────────────────────────────────────
        st.markdown(
            f'<div class="section-title">{_icon(_IC_TABLE)}Asset Detail</div>',
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
                    f'<div class="section-title">{_icon(_IC_MEGAPHONE)}Reach by Journey Stage'
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
                    hovertemplate="<b>%{y}</b><br>HCPs reached:<br>%{x:,}<extra></extra>",
                ))
                fig_seg_bar.update_layout(
                    height=360,
                    margin=dict(l=20, r=60, t=10, b=20),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    xaxis=dict(gridcolor="#f1f5f9", title="Unique HCPs"),
                    yaxis=dict(tickfont=dict(size=11)),
                )
                fig_seg_bar.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
                st.plotly_chart(fig_seg_bar, use_container_width=True, key="ha_seg_bar")

            with jc2:
                st.markdown(
                    f'<div class="section-title">{_icon(_IC_CURSOR_RIPPLE)}CTR % by Journey Stage'
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
                    hovertemplate="<b>%{y}</b><br>CTR:<br>%{x:.2f}%<extra></extra>",
                ))
                fig_ctr_stage.update_layout(
                    height=360,
                    margin=dict(l=20, r=60, t=10, b=20),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    xaxis=dict(gridcolor="#f1f5f9", title="CTR %"),
                    yaxis=dict(tickfont=dict(size=11), autorange="reversed"),
                )
                fig_ctr_stage.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
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

        # ── Journey Stage filter for specialty views ───────────────────────────
        # "Of my [Stage] HCPs, what's the specialty mix?"
        # Filters only the specialty charts below; journey bars above are
        # always brand-level and unaffected.
        st.markdown(
            f'<div class="section-title">{_icon(_IC_USERS)}Specialty Composition</div>',
            unsafe_allow_html=True,
        )
        stage_options = ["All Stages"] + journey_stages
        selected_stage = st.selectbox(
            "Filter by Journey Stage",
            stage_options,
            key="spec_stage_filter",
            help="Filter the specialty views to HCPs in a specific prescriber journey stage.",
        )
        spec_df_src = (
            df if selected_stage == "All Stages"
            else df[df["Segment"] == selected_stage]
        )
        stage_label = "" if selected_stage == "All Stages" else f" — {selected_stage}"

        # ── Specialties: Treemap + Bubble Chart ───────────────────────────────
        # Treemap: area = reach (who we touched); pure volume overview.
        # Bubble: x = avg frequency, y = CTR %, size = reach.
        # Both filtered by the selected stage when one is chosen.
        spec_geo = compute_geo_analysis(spec_df_src, "specialty", "All")
        spec_df = spec_geo["data"].copy()

        # Assign each specialty a consistent brand palette color by index
        spec_colors = [
            BRAND["palette"][i % len(BRAND["palette"])]
            for i in range(len(spec_df))
        ]
        spec_df["color"] = spec_colors

        tree_col, bubble_col = st.columns(2)

        with tree_col:
            st.markdown(
                f'<div class="section-title">{_icon(_IC_BEAKER)}Specialty Reach'
                f'<span style="font-size:.65rem;font-weight:500;color:#94a3b8;'
                f'text-transform:none;letter-spacing:normal;margin-left:8px;">'
                f'HCPs by Specialty{stage_label}</span></div>',
                unsafe_allow_html=True,
            )
            fig_spec_tree = go.Figure(
                go.Treemap(
                    labels=spec_df["name"],
                    parents=[""] * len(spec_df),
                    values=spec_df["npiCount"],
                    customdata=spec_df[["name", "npiCount"]].values,
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "HCPs Reached:<br>%{customdata[1]}<extra></extra>"
                    ),
                    texttemplate="<b>%{label}</b><br>%{value} HCPs",
                    textfont=dict(size=13),
                    marker=dict(colors=spec_colors, pad=dict(t=2, l=2, r=2, b=2)),
                )
            )
            fig_spec_tree.update_layout(
                height=340,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="white",
            )
            fig_spec_tree.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_spec_tree, use_container_width=True, key="spec_treemap")

        with bubble_col:
            st.markdown(
                f'<div class="section-title">{_icon(_IC_BEAKER)}Specialty Engagement'
                f'<span style="font-size:.65rem;font-weight:500;color:#94a3b8;'
                f'text-transform:none;letter-spacing:normal;margin-left:8px;">'
                f'Frequency vs. CTR %{stage_label}</span></div>',
                unsafe_allow_html=True,
            )
            # Square-root scale: perceptually correct for bubble area encoding.
            # Scaled so the largest specialty lands around 60px diameter.
            max_count = spec_df["npiCount"].max() or 1
            spec_df["size_px"] = (spec_df["npiCount"] / max_count).pow(0.5) * 60

            fig_spec_bubble = go.Figure()
            fig_spec_bubble.add_trace(
                go.Scatter(
                    x=spec_df["impressions"],
                    y=spec_df["ctr"],
                    mode="markers+text",
                    marker=dict(
                        size=spec_df["size_px"],
                        color=spec_df["color"],
                        opacity=0.85,
                        line=dict(width=1, color="white"),
                    ),
                    text=spec_df["name"],
                    textposition="top center",
                    textfont=dict(size=9, color="#64748b"),
                    customdata=spec_df[["name", "npiCount", "impressions", "ctr"]].values,
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "HCPs:<br>%{customdata[1]}<br>"
                        "Avg Freq:<br>%{customdata[2]:.1f}<br>"
                        "CTR:<br>%{customdata[3]:.2f}%<extra></extra>"
                    ),
                )
            )
            fig_spec_bubble.update_layout(
                height=340,
                margin=dict(l=40, r=20, t=20, b=50),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(title="Avg Frequency per HCP", gridcolor="#f1f5f9"),
                yaxis=dict(title="CTR %", gridcolor="#f1f5f9"),
            )
            fig_spec_bubble.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
            st.plotly_chart(fig_spec_bubble, use_container_width=True, key="spec_bubble")

            st.markdown(
                """
                <div style="text-align:center;font-size:.65rem;font-weight:700;
                            color:#94a3b8;text-transform:uppercase;">
                    Bubble size = Population (Reach)
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

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
            st.markdown(f'<div class="section-title">{_icon(_IC_ADJUSTMENTS)}Analysis Controls</div>', unsafe_allow_html=True)

            analysis_level = "state"

            # First compute with "All" to get the full list of filter options
            geo = compute_geo_analysis(df, analysis_level, "All")

            # Filter by Specialty to narrow the state hex map
            analysis_filter = st.selectbox(
                "Filter Specialty",
                ["All"] + geo["filter_options"],
                key="analysis_filter",
            )

            # Recompute with the actual selected filter value
            geo = compute_geo_analysis(df, analysis_level, analysis_filter)

            # ── Entity selector for comparison list ──
            entity_options = geo["data"]["name"].tolist()
            selected_entity = st.selectbox(
                "Highlight State",
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

            # Color-by metric selector for the hex map
            map_metric = st.radio(
                "Color By",
                ["ctr", "impressions"],
                format_func=lambda x: "CTR %" if x == "ctr" else "Avg Frequency",
                horizontal=True,
                key="map_metric",
            )

            # ── Comparison List ────────────────────────────────────────────────
            # Only render this section if anything has been highlighted.
            if st.session_state.highlighted:
                st.markdown("---")
                st.markdown(f'<div class="section-title">{_icon(_IC_TABLE)}Comparison List</div>', unsafe_allow_html=True)

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

            # ── Hex Map ────────────────────────────────────────────────────────
            st.markdown(
                f'<div class="section-title">{_icon(_IC_MAP)}Cohort Engagement Map'
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
            fig_map.update_traces(hoverlabel=PLOTLY_HOVERLABEL)
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



# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
# `if __name__ == "__main__":` is standard Python. When you run this file
# directly (`streamlit run pld_app_annotated.py`), __name__ is "__main__"
# so main() gets called. If another script imports this file, __name__ is
# the module name and main() does NOT run automatically.
if __name__ == "__main__":
    main()
