# Forecast Structure and HTML Parsing Reference

This document outlines the layout and HTML structure of the Mountain Weather Information Service (MWIS) text forecasts (e.g., `https://mwis.org.uk/forecasts/scottish/the-northwest-highlands/text`). Use this guide to parse the live HTML forecasts deterministically.

---

## Forecast Page Layout

- **Region Title**: Defined in the `<h1>` tag at the top of the page.
- **Tabs/Days**: The forecast has 3 days of forecasts mapped to tab panes with IDs:
  - `Forecast0` (Day 1 / Today or Tomorrow)
  - `Forecast1` (Day 2 / Tomorrow or Day After)
  - `Forecast2` (Day 3 / Day After)
- **Metadata**: Each tab contains a `Viewing Forecast For` metadata block including the target date and a `Last updated` timestamp (e.g., `Sat 4th Jul 26 at 4:17PM`).
- **Outlook**: A `Planning Outlook` section is located near the end of the page.

---

## Field Descriptions & HTML Headings Mapping

Every row inside a forecast day is formatted as:
```html
<div class="row">
    <div class="col-xs-12 col-lg-5 col-xl-4"><h4>[Heading]</h4></div>
    <div class="col">[Content]</div>
</div>
```

### Day 1 Only Fields
- `Summary for all mountain areas` (UK Summary)
- `Headline for [Region Name]` (Region Headline)

### Day 1, 2, and 3 Shared Fields (in sequence)
- `How windy? (On the Munros)` (or corresponding summit level name)
- `Effect of the wind on you?`
- `How Wet?`
- `Cloud on the hills?`
- `Chance of cloud free Munros?` (or summits)
- `Sunshine and air clarity?`
- `How Cold? (at [RefHeight])` (uses `RefHeight` from CSV)
- `Freezing Level`

### Outlook Field (Outside Tab Panes)
- Heading: `<h3>Planning Outlook</h3>`
- Container: `<div class="forecast-area--planning-outlook">`

---

## Update Frequency & Date Interpretation

- **Issue Times**: New forecasts are typically issued daily between **16:00 and 17:00 British Time**.
- **Day 1 Context**:
  - Prior to the 16:00–17:00 issue: Day 1 refers to **Today**.
  - After the 16:00–17:00 issue: Day 1 refers to **Tomorrow**.
