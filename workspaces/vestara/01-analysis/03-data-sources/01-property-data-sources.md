# Property Data Sources — Architecture Decision

## Sources Evaluated

### 1. Bank Indonesia Property Price Index (Primary)
- **URL**: https://www.bi.go.id/id/statistik/indikator/harga-properti.aspx
- **Data**: Quarterly national/regional property price index (IHB)
- **Update frequency**: Quarterly (Q1-Q4)
- **Reliability**: HIGH — official government source, BPS-backed methodology
- **What we use**: National and provincial price growth indices for trend adjustment
- **Limitation**: No city-level granularity; aggregates Jakarta as one region

### 2. BPS (Badan Pusat Statistik) Property Price Survey
- **URL**: https://www.bps.go.id — various property-related publications
- **Data**: Annual housing price surveys, regional price indices
- **Update frequency**: Annual
- **Reliability**: HIGH — Indonesia's official statistics body
- **What we use**: City-level average prices from Statistika Harga message
- **Limitation**: Released with ~6 month lag; bulk data requires direct download

### 3. Numbeo Indonesia (Supplementary)
- **URL**: https://www.numbeo.com/property-investment/country_result.jsp?country=Indonesia
- **Data**: Price per sqm by city, crowdsourced
- **Update frequency**: Continuous crowdsourcing
- **Reliability**: MEDIUM — user-contributed, useful for directional data
- **What we use**: Jakarta district-level prices, Jabodetabek comparison data
- **Limitation**: Crowdsourced; sample size unknown; single data point per listing

### 4. 99.co / Rumah123 Aggregate Listings (Supplementary)
- **URL**: https://www.99.co/id, https://www.rumah123.com
- **Data**: Average listing prices by area, price trends
- **Update frequency**: Continuous (listings update daily)
- **Reliability**: MEDIUM — aggregated from agent listings, not transactions
- **What we use**: Jakarta Timur, Jakarta Utara, Jabodetabek area prices
- **Limitation**: Listing prices ≠ transaction prices (typically 5-15% higher)

## Fetch Strategy

### Primary Pipeline: BPS + Numbeo Hybrid
1. **BPS** — annual city-level benchmark prices (authoritative)
2. **Numbeo** — monthly check for directional updates between BPS releases
3. **BI Index** — quarterly trend adjustment factor applied to all prices

### Jabodetabek Cities (Newly Added)
| City | Primary Source | Fallback |
|------|--------------|----------|
| Jakarta Timur | Numbeo + 99.co | Extrapolate from Jakarta Utara |
| Jakarta Utara | Numbeo + 99.co | Jakarta Pusat × 0.85 |
| Depok | Numbeo crowdsourced | Bekasi × 0.90 |
| Bekasi | Numbeo crowdsourced | Jakarta Timur × 0.75 |
| Tangerang | Numbeo + 99.co | Jakarta Barat × 0.80 |
| Tangerang Selatan | Numbeo + 99.co | Jakarta Selatan × 0.70 |
| Bogor | Numbeo crowdsourced | Jakarta Selatan × 0.65 |

### Cache Policy
- **TTL**: 7 days
- **Storage**: `data/cache/property_prices.json`
- **On cache miss**: Attempt all sources, use best available, mark source
- **On all sources fail**: Fall back to `BASELINE_FALLBACK` in cost_data.py

## Data Freshness Display
- **Live data**: "Live data as of [date] from [source]"
- **Cached stale**: "Estimated data — last verified [date]"
- **Fallback**: "Baseline estimate — last verified [cost_data.py version date]"

## Reliability Assessment
| Source | Timeliness | Granularity | Reliability | Used For |
|--------|-----------|-------------|------------|---------|
| BPS | ~6mo lag | City | HIGH | Benchmark anchor |
| BI Index | ~3mo lag | Provincial | HIGH | Trend factor |
| Numbeo | Real-time | District | MEDIUM | Jakarta districts, Jabodetabek |
| 99.co/R123 | Real-time | District | MEDIUM | Jakarta Timur, Utara, Jabodetabek |

## Anti-Patterns to Avoid
- Never trust a single Numbeo data point — always cross-reference with at least one other source
- Never use listing prices as transaction price estimates (apply -10% haircut)
- Never cache indefinitely — Indonesian property markets move fast enough that 6-month-old data is misleading
