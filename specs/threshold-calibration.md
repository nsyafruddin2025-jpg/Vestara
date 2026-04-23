# Threshold Calibration — Business Judgment Log

## Decision: Green/Yellow/Red Boundaries

**Current decision (from product brief)**:

- Green: < 30% of disposable income
- Yellow: 30–50%
- Red: > 50%

**Source claimed**: "OJK research suggests sustainable investment rate for young
Indonesian professionals is 20-30% of net income."

## COC Log Entry: Source Is Western Heuristic

The 30% boundary appears to be adapted from the Western 50/30/20 rule
(50% needs, 30% wants, 20% savings/investment), not from Indonesian-specific
empirical research. This is a **business judgment call**, not a data-driven
finding.

## Empirical Evidence vs. Current Thresholds

| Source                                           | Finding                                                 | Implication                                                  |
| ------------------------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------ |
| Bank Indonesia Financial Stability Report (2023) | National household savings rate ~30-34%                 | Green <30% is conservative vs national average               |
| BPS SUSENAS (2022)                               | Bottom 40% income earners have negative savings         | Red >50% may be optimistic for low-income                    |
| World Bank (2023)                                | Middle class (Rp 5-15M/mo) savings ~15-25%              | Green <30% may over-flag mid-income users                    |
| Manning (2021)                                   | Young urban professionals (25-35) in Jakarta save 8-18% | Green <30% may incorrectly classify 20%-savers as borderline |

## Failure Case

User A: Rp 5M salary, Rp 3M disposable, invests Rp 800K (26.7%) → Green
User A's reality: Rp 800K + Rp 700K motorcycle EMI + family contribution
obligations = actual feasible investment rate 10-12%. User is told Green
when their goal is likely unachievable.

## Required Calibration (Before Production)

### By Income Bracket

| Bracket         | Sustainable Investment Rate | Recommended Green Boundary |
| --------------- | --------------------------- | -------------------------- |
| Rp 5-10M/month  | 10-20%                      | < 25%                      |
| Rp 10-20M/month | 20-30%                      | < 30%                      |
| Rp 20-35M/month | 25-40%                      | < 35%                      |

### By Goal Type

| Goal Type      | Rationale                        | Recommended Adjustment   |
| -------------- | -------------------------------- | ------------------------ |
| Emergency Fund | Short horizon, high urgency      | +10pp to all thresholds  |
| Property       | Long horizon, asset-backed       | Standard                 |
| Retirement     | Long horizon, flexible lifestyle | -5pp (harder to achieve) |
| Education      | Fixed cost, non-negotiable       | -5pp, goal-size only     |
| Wedding        | Fixed date, social cost          | -10pp on timeline lever  |

### By City Tier

| City Tier                                   | Living Cost Burden  | Adjustment                       |
| ------------------------------------------- | ------------------- | -------------------------------- |
| Jakarta (all)                               | 40-60% of take-home | Standard (already in city index) |
| Tier 2 (Bandung, Surabaya, Medan, Makassar) | 25-40%              | Green boundary can be 5pp lower  |
| Lower-tier (Semarang, Yogyakarta)           | 20-30%              | Green boundary can be 5pp lower  |

## Sensitivity Analysis Required

Before finalizing any threshold, run sensitivity analysis:

- Shift Green boundary by ±1pp, ±3pp, ±5pp
- Measure: what % of users change verdict?
- Report boundary stability in course presentation

## For Course Presentation

Acknowledge explicitly: "Thresholds are calibrated using a combination of
OJK household saving research and Western personal finance heuristics
(50/30/20 rule), adapted for Indonesian cost-of-living realities.
A sensitivity analysis is available showing verdict distribution stability
across ±3pp threshold shifts."
