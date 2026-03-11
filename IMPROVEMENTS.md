# PLD Dashboard — Improvements Backlog

## KPI / Metric Gaps

### Reach Quality
- [ ] Coverage % — unique HCPs reached vs. target list size
- [ ] Reach breakdown by targeting type (Claims-Based vs. HCP-Target-List vs. Site-Retargeting)
- [ ] Reach by specialty (are we hitting the right prescribers?)
- [ ] Reach overlap between channels (same HCPs across Programmatic + Native + DocNews?)

### Creative Performance
- [ ] CTR by asset / creative (`FP_ASSET_ID`: DM003-A through DM009-A, NA001-A–NA007-A, AL010-A)
- [ ] CTR by ad format/size (banner vs. native vs. DocNews Alert)
- [ ] Frequency vs. CTR curve (at what impression threshold do HCPs tune out?)

### Channel Efficiency
- [ ] Per-vendor CTR (must be calculated within-vendor only — never blended across vendors)
- [ ] Doximity engagement rate: `content_view / headline_view` (did they read, or just see?)

### Conversion Funnel
- [ ] Surface conversion events (11 conversions exist in data, currently invisible)
- [ ] CVR (clicks → conversions, currently 0.80%)
- [ ] Funnel view: Impressions → Clicks → Conversions by channel/creative

### Pacing & Frequency
- [ ] Daily impression volume trend with anomaly callouts (Jan 1 low-volume, Jan 22 dropoff)
- [ ] Frequency distribution (% of HCPs at 1x, 2–3x, 4–5x, 6x+ impressions)

### Audience Segments
- [ ] Performance by `Segment` from BRI_LOOKUP (23 unique audience segments, currently unused)
- [ ] Performance by `TARGETING DETAILS` (32 unique values, currently unused)
