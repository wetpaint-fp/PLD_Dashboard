# PLD Dashboard — Improvements Backlog

## Completed (v2)

- ~~Coverage % — unique HCPs reached vs. target list size~~ ✅ KPI card on Partner Performance (manual input in prototype; Snowpark query in production)
- ~~CTR by asset / creative~~ ✅ Creative Performance page
- ~~CTR by ad format/size~~ ✅ Segment × Format heatmap on Creative page
- ~~Frequency vs. CTR curve~~ ✅ Scatter plot on Creative page
- ~~Per-vendor CTR~~ ✅ CTR by Partner bar chart (excludes null/0/100% vendors)
- ~~Doximity engagement rate~~ ✅ Applied across all views: bar charts, heatmaps, creative metrics
- ~~Surface conversion events~~ ✅ Conversion funnel (Impressions → Clicks → Conversions)
- ~~CVR~~ ✅ Shown in KPI card subtext and funnel hover
- ~~Funnel view~~ ✅ `go.Funnel` on Partner Performance page
- ~~Frequency distribution~~ ✅ Bar chart (1×, 2–3×, 4–5×, 6×+) on Partner Performance
- ~~Performance by Segment~~ ✅ Journey stage bars on HCP Audience; heatmaps on both PP and CP
- ~~Stacked reach by segment × format family~~ ✅ Segment × Format heatmap on Creative page
- ~~Global hover tooltip styling~~ ✅ `PLOTLY_HOVERLABEL` constant applied to all Plotly figures
- ~~Heroicon section headers~~ ✅ Inline SVG Heroicons on all section titles (SiS-compatible)
- ~~HCP Audience KPI cards~~ ✅ Unique HCPs, Lower Funnel %, Most Active Stage, Top Specialty
- ~~Journey stage filter for specialty views~~ ✅ Selectbox filter on HCP Audience

---

## Remaining Backlog

### Reach Quality

- Reach breakdown by targeting type (Claims-Based vs. HCP-Target-List vs. Site-Retargeting)
- Reach overlap between channels (same HCPs across Programmatic + Native + DocNews?)

### Pacing

- Daily impression volume trend with anomaly callouts (Jan 1 low-volume, Jan 22 dropoff)

### Audience Segments

- Performance by `TARGETING DETAILS` (32 unique values, currently unused)

### Data / Production

- Wire Snowpark `load_data()` to live Snowflake tables (see [`SNOWFLAKE_DEPLOYMENT.md`](SNOWFLAKE_DEPLOYMENT.md))
- `HCP_DIM` table needed for specialty/state geo views in production
- `TARGET_LIST` table needed for automatic Coverage % in production

