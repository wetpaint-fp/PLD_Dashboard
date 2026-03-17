# Icon Reference

All icons are [Heroicons v2](https://heroicons.com) solid (24×24), rendered inline as SVG via the `_icon()` helper in `pld_app_annotated.py`. No external HTTP — fully SiS-compatible.

## Usage

```python
st.markdown(
    f'<div class="section-title">{_icon(_IC_CHART_BAR)}My Section</div>',
    unsafe_allow_html=True,
)
```

Optional size override (default 14px):

```python
_icon(_IC_USERS, size=16)
```

Color is always `BRAND["primary"]` (`#47254A`). To use a different color, call `_icon()` directly and pass a custom fill — or add a second parameter to the helper.

---

## Available Icons

| Constant | Heroicon Name | Suggested Use |
|---|---|---|
| `_IC_ADJUSTMENTS` | `adjustments-horizontal` | Filters / analysis controls |
| `_IC_ARROW_TRENDING_UP` | `arrow-trending-up` | CTR, performance metrics |
| `_IC_BEAKER` | `beaker` | Specialties, science, lab data |
| `_IC_CALENDAR` | `calendar-days` | Date ranges, time filters |
| `_IC_CHART_BAR` | `chart-bar` | Reach, volume, bar charts |
| `_IC_CHART_PIE` | `chart-pie` | Scatter, mix, share of voice |
| `_IC_CURSOR_RIPPLE` | `cursor-arrow-ripple` | Clicks, engagement events |
| `_IC_FUNNEL` | `funnel` | Filters, pipeline, journey stages |
| `_IC_GLOBE` | `globe-americas` | Geography, map views |
| `_IC_MAP` | `map` | Hex map, geographic drill-down |
| `_IC_MEGAPHONE` | `megaphone` | Campaigns, reach, awareness |
| `_IC_SIGNAL` | `signal` | Campaign activity, live metrics |
| `_IC_TABLE` | `table-cells` | Tables, detail views, grids |
| `_IC_TV` | `tv` | Creative formats, display ads |
| `_IC_USERS` | `users` | HCP reach, audience segments |
| `_IC_VIEWFINDER` | `viewfinder-circle` | Targeting, precision, heatmaps |
| `_IC_VIEW_COLUMNS` | `view-columns` | Column layouts, side-by-side views |

---

## Adding a New Icon

1. Find the icon at [heroicons.com](https://heroicons.com) — select **Solid**, copy the SVG
2. Strip the outer `<svg>` tag, keep only the inner `<path>` element(s)
3. Add a constant near the others in `pld_app_annotated.py`:

```python
_IC_MY_ICON = (
    '<path d="M..." />'
)
```

4. Use it: `_icon(_IC_MY_ICON)`
