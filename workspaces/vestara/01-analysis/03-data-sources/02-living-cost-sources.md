# Living Cost Data Sources — Architecture Decision

## Sources Evaluated

### 1. BPS Household Expenditure Survey (SUSENAS) — Primary
- **URL**: https://www.bps.go.id — "Pengeluaran Konsumen" publications
- **Data**: Monthly per-capita expenditure by province and city
- **Update frequency**: Annual (released ~March for previous year)
- **Reliability**: HIGH — official government expenditure data
- **What we use**: Monthly living cost by city (derived: expenditure × 1.1 for savings buffer)
- **Limitation**: City-level data limited; many cities only have provincial averages

### 2. Numbeo Indonesia — Primary for City Granularity
- **URL**: https://www.numbeo.com/cost-of-living/country_result.jsp?country=Indonesia
- **Data**: Consumer price index, cost of living index, restaurant prices, groceries, transport
- **Update frequency**: Continuous crowdsourced + periodic verification
- **Reliability**: MEDIUM — user-contributed but actively moderated
- **What we use**: Monthly cost of living per city; rent index for each city
- **Limitation**: Sample-based; methodology not always transparent

### 3. Bank Indonesia Regional Economic Data — Supplementary
- **URL**: https://www.bi.go.id — regional economic statistics
- **Data**: Provincial CPI, regional economic growth, consumption indicators
- **Update frequency**: Monthly (provincial CPI)
- **Reliability**: HIGH — official source
- **What we use**: Inflation trend adjustment factor applied to all living cost estimates
- **Limitation**: Provincial level only, not city-level

## Fetch Strategy

### Primary Pipeline: Numbeo (city-level) + BPS (anchor)
1. **Numbeo** — monthly check for living cost updates per city
2. **BPS** — annual anchor to verify Numbeo direction is not wildly off
3. **BI CPI** — apply regional inflation factor to project forward

### Cache Policy
- **TTL**: 7 days
- **Storage**: `data/cache/living_costs.json`
- **On cache miss**: Numbeo primary, BPS fallback, BI CPI as trend check
- **On all sources fail**: Fall back to `BASELINE_FALLBACK` in cost_data.py

## Data Structure Per City
```json
{
  "city": "Jakarta Selatan",
  "monthly_cost": 8500000,
  "currency": "IDR",
  "sources": ["numbeo", "bps"],
  "numbeo_url": "https://www.numbeo.com/cost-of-living/in/Jakarta...",
  "last_updated_numbeo": "2026-04-15",
  "last_updated_bps": "2026-03-01",
  "reliability": "MEDIUM",
  "notes": "Composite of Numbeo rent+groceries+transport+utilities"
}
```

## Cities Currently Supported (with sources)
| City | Primary | Secondary | Notes |
|------|---------|-----------|-------|
| Jakarta Selatan | Numbeo | BPS anchor | High reliability |
| Jakarta Pusat | Numbeo | BPS anchor | High reliability |
| Jakarta Utara | Numbeo | BPS estimate | New district, MEDIUM |
| Jakarta Timur | Numbeo | 99.co | New district, MEDIUM |
| Bandung | Numbeo | BPS | Good coverage |
| Surabaya | Numbeo | BPS | Good coverage |
| Yogyakarta | BPS | Numbeo | Lower Numbeo sample |
| Medan | BPS primary | Numbeo secondary | Limited Numbeo data |
| Bali (Denpasar) | Numbeo | BPS | Tourism premium captured |
| Semarang | BPS primary | Numbeo | Limited Numbeo |
| Makassar | BPS primary | Numbeo | Limited Numbeo |
| Depok | Numbeo | Extrapolate | New, lower reliability |
| Bekasi | Numbeo | Extrapolate | New, lower reliability |
| Tangerang | Numbeo | BPS | New, MEDIUM |
| Tangerang Selatan | Numbeo | BPS | New, MEDIUM |
| Bogor | BPS primary | Numbeo | New, lower reliability |

## Living Cost Components
Numbeo provides: restaurants, groceries, transport, utilities, rent, healthcare, entertainment
For our purposes we use: **all-in monthly estimate** (rent + groceries + transport + utilities)

## Anti-Patterns to Avoid
- Never use Numbeo's "cost of living index" without converting to absolute IDR amounts
- Never apply a single national inflation rate — Indonesian regional inflation varies significantly (Papua can be 2x Java)
- Never treat living cost as static — it compounds at RETIREMENT_LIVING_INFLATION annually
