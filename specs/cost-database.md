# Cost Database — Spec

## Scope

City-specific cost data for 10 Indonesian cities, covering:

- Property prices (per sqm, IDR)
- School fees (annual, by tier)
- Living costs (monthly, young professional estimate)

## Cities Covered

Jakarta Selatan, Jakarta Pusat, Jakarta Utara, Bandung, Surabaya,
Yogyakarta, Medan, Bali (Denpasar), Semarang, Makassar.

## Property Price Data

### Schema

```
city: string
price_per_sqm: int (IDR)
last_updated: date
source: string
volatility_tier: enum [low, medium, high]
```

### Volatility Tiers

- **High**: Jakarta Selatan, Surabaya CBD — prone to 20-40% swings in 3-year windows
- **Medium**: Bandung, Jakarta Pusat, Bali
- **Low**: Medan, Semarang, Makassar, Yogyakarta

### Maintenance Requirement

Property prices must be updated at minimum annually. High-volatility cities
should be updated every 6 months. Price changes >10% since last update
should trigger a user-facing notice: "Property prices in {city} have
shifted by X% since your goal was set. Your feasibility verdict may
have changed."

### Contingency Buffer

Property goals must include a 15% contingency buffer in cost estimates:

```
estimated_cost = size_sqm × price_per_sqm × 1.15
```

This accounts for transaction costs (PBB, notary, BPHTB ~10-12% of value)
and price appreciation during the investment horizon.

## School Fee Data

### Schema

```
city: string
level: enum [tk, sd, smp, sma]
tier: enum [local_private_low, local_private_mid, local_private_high, international_mid, international_top]
annual_fee_idr: int
currency_adjustable: boolean
```

## Living Cost Data

### Schema

```
city: string
monthly_cost_idr: int
profile: enum [young_professional_single, young_professional_couple, with_dependents]
last_updated: date
source: string
```

### Living Cost Purpose

Used to compute disposable income: `disposable = monthly_salary - monthly_living_cost`
This drives the feasibility verdict calculation.

### What Is Included

- Rent (1BR apartment, city average)
- Transport (motorcycle EMI + fuel or public transport)
- Food (home cooking + occasional eating out)
- Utilities (electricity, water, internet, phone)
- Clothing and personal care

### What Is NOT Included

- Debt repayments (car EMI, personal loans) — user-reported separately
- Family contribution obligations — user-reported separately
- Savings for other goals — modeled separately
- Entertainment and lifestyle discretionary — modeled as a lumpen buffer

## Currency Buffer for Abroad Education

Higher Education goals involving overseas institutions require a currency buffer:

```
annual_cost = base_cost_idr × (1 + annual_idr_depreciation_rate)^years × 1.10
```

Where:

- annual_idr_depreciation_rate: 3-5% (based on 10-year IDR/AUD, IDR/EUR historical rates)
- 1.10: 10% currency contingency buffer

This prevents systematic underestimation of abroad education costs due to
IDR weakening over a 4-year degree program.

## Data Quality Standards

1. **Source documentation**: Every data point must cite a source (real estate portal,
   school website, government statistics, or survey)
2. **Staleness dating**: Every value has a `last_updated` field
3. **Volatility flagging**: High-volatility cities flagged in UI when displaying estimates
4. **Known gaps**: Where data is estimated, clearly label "estimated based on..."
   not "actual"
