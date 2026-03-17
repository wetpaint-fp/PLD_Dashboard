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

| Constant | Heroicon Name | Used For |
|---|---|---|
| `_IC_CHART_BAR` | `chart-bar` | Monthly Reach & Frequency, Native Display |
| `_IC_ARROW_TRENDING_UP` | `arrow-trending-up` | CTR % sections, CTR % by Journey Stage |
| `_IC_VIEWFINDER` | `viewfinder-circle` | Heatmaps (Stage × Partner, Journey × Format) |
| `_IC_TABLE` | `table-cells` | Detailed Performance, Asset Detail, Comparison List, Specialty Engagement |
| `_IC_USERS` | `users` | Reach sections, Reach by Journey Stage |
| `_IC_ADJUSTMENTS` | `adjustments-horizontal` | Analysis Controls / filter panels |
| `_IC_MAP` | `map` | Cohort Engagement Map |
| `_IC_CHART_PIE` | `chart-pie` | Frequency vs CTR scatter, Specialty Reach |

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
