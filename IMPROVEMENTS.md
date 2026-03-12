# PLD Dashboard — Improvements Backlog

## KPI / Metric Gaps

### Reach Quality
- [ ] Coverage % — unique HCPs reached vs. target list size
- [ ] Reach breakdown by targeting type (Claims-Based vs. HCP-Target-List vs. Site-Retargeting)
- [ ] Reach by specialty (are we hitting the right prescribers?)
- [ ] Reach overlap between channels (same HCPs across Programmatic + Native + DocNews?)

### Creative Performance
- [x] CTR by asset / creative (`FP_ASSET_ID`: DM003-A through DM009-A, NA001-A–NA007-A, AL010-A)
- [x] CTR by ad format/size (banner vs. native vs. DocNews Alert)
- [x] Frequency vs. CTR curve (at what impression threshold do HCPs tune out?)

### Channel Efficiency
- [x] Per-vendor CTR (must be calculated within-vendor only — never blended across vendors)
- [ ] Doximity engagement rate: `content_view / headline_view` (did they read, or just see?)

### Conversion Funnel
- [ ] ⭐ Surface conversion events (11 conversions exist in data, currently invisible)
- [ ] ⭐ CVR (clicks → conversions, currently 0.80%)
- [ ] ⭐ Funnel view: Impressions → Clicks → Conversions by channel/creative

### Pacing & Frequency
- [ ] Daily impression volume trend with anomaly callouts (Jan 1 low-volume, Jan 22 dropoff)
- [ ] ⭐ Frequency distribution (% of HCPs at 1x, 2–3x, 4–5x, 6x+ impressions)

### Audience Segments
- [x] Performance by `Segment` from BRI_LOOKUP (23 unique audience segments)
- [x] Stacked reach by segment × format family (Creative page only — answers "which formats reach which segments?")
- [ ] Performance by `TARGETING DETAILS` (32 unique values, currently unused)

### UI Polish
- [ ] Global hover tooltip styling — branded bgcolor, border color, font (deferred; apply via Plotly template at top of app)

---

## Priority for Next Sprint

**⭐ Most impactful unenacted improvements:**

1. **Conversion funnel** — 11 conversions exist in the data and are completely invisible in the current UI. CVR and a funnel view (Impressions → Clicks → Conversions) are the highest-value additions for a client conversation.
2. **Doximity engagement rate** (`content_view / headline_view`) — Doximity has no impressions, so CTR is undefined for that vendor. This ratio is the correct engagement metric and is currently absent.
3. **Frequency distribution** — Showing % of HCPs at 1x / 2–3x / 4–5x / 6x+ lets the client spot overexposure and act on it. The raw data to compute this already exists.
4. **Coverage %** — Reach vs. target list size is a fundamental campaign KPI. Without it, "2,847 HCPs reached" has no denominator.
5. **Reach by specialty** — Confirms whether spend is landing on the right prescriber types (e.g., Pain Management vs. Anesthesiology for Brixadi).
