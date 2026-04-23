# Goal Builder — Spec

## Goal Types and Flows

### Property

**Trigger question**: "What unit size are you targeting?"
Options: Studio/1BR, 2BR Standard, 2BR Large/3BR, Large/Penthouse
**Optional**: neighbourhood text input
**Cost calculation**: size_sqm × city_price_per_sqm × 1.15 (contingency buffer)

### Education

**Trigger questions**: education level + school tier
**Cost calculation**: annual_fee × years_until_completion
**Note**: Only for school fees, not university

### Retirement

**Trigger questions**: current age, retirement age, desired lifestyle
**Cost calculation**: annual_expense × years_in_retirement
**Lifestyle tiers**: Basic (2-3M/mo), Comfortable (4-6M/mo), Premium (7-10M/mo)

### Emergency Fund

**Trigger question**: months of coverage
Options: 3 months (minimum), 6 months (standard), 12 months (conservative)
**Cost calculation**: monthly_living_cost × months

### Wedding

**Trigger question**: wedding scale
Options: Simple (50-100 guests), Moderate (200-400), Grand (500+)
**Cost calculation**: fixed per tier

### Higher Education (Abroad)

**Trigger questions**: degree type, country, institution tier
**Cost calculation**: base_annual_cost × degree_years × tier_multiplier
**Currency buffer**: +3-5% annual IDR depreciation + 10% contingency

### Custom

**Path A**: User enters target amount directly (IDR)
**Path B**: User describes goal + estimated amount (optional)
**Note**: Both paths available simultaneously — user chooses

## Session State Contract

```
st.session_state["goal_profile"]: dict
  goal_type: str
  city: str
  estimated_cost: float
  timeline_years: int
  description: str
st.session_state["goal_set"]: bool
```

## Cost Estimation Accuracy Requirements

| Goal Type        | Accuracy Required | Source Standard                                       |
| ---------------- | ----------------- | ----------------------------------------------------- |
| Property         | ±15%              | Property price per sqm ± 10%, contingency buffer ± 5% |
| Education        | ±20%              | School fee tiers are wide ranges                      |
| Retirement       | ±30%              | Lifestyle tiers are broad estimates                   |
| Emergency Fund   | ±5%               | Direct calculation from living cost                   |
| Wedding          | ±20%              | Tier pricing varies widely                            |
| Higher Education | ±25%              | Country/tier ranges wide + currency risk              |
| Custom           | N/A               | User-provided or not estimable                        |

## Required Outputs

Every goal profile must include:

1. `goal_type`: string
2. `city`: string
3. `estimated_cost`: float (IDR)
4. `timeline_years`: int
5. `description`: string (human-readable description)

## Navigation

Goal Builder → Feasibility Analysis → Risk Profiler → Portfolio Recommendation
Each step requires the previous to be complete (session state gates).

## Cost Data Dependency

Goal Builder depends on `vestara.data.cost_data` for:

- PROPERTY_PRICE_PER_SQM
- SCHOOL_FEES_ANNUAL
- LIVING_COST_MONTHLY
- EDUCATION_ABROAD_ANNUAL
- RETIREMENT_ANNUAL_EXPENSE
- WEDDING_COST
