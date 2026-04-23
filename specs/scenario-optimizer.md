# Scenario Optimizer — Spec

## Current Implementation

Four-lever priority order: timeline → location → goal_size → contribution.
Applied uniformly to all goal types.

## CRITICAL FINDING: Hard Gate Missing

For users with ratio >100% (disposable income is negative or zero),
the scenario optimizer presents contribution increase as a lever when it is
**structurally impossible**. This is a Critical severity failure.

## Required: Hard Gate

```
IF monthly_investment_required / disposable_income >= 1.0:
    BLOCK contribution_increase lever
    BLOCK scenario_optimizer
    DISPLAY: "Your goal requires more than your entire disposable income.
              Please consider: (1) reducing goal size, (2) extending timeline,
              or (3) exploring a higher-income city for cost purposes."
    RETURN immediately
```

## Goal-Type-Aware Lever Weights

The priority order must vary by goal type:

| Goal Type      | #1 Lever     | #2 Lever     | #3 Lever    | #4 Lever  | Flag                      |
| -------------- | ------------ | ------------ | ----------- | --------- | ------------------------- |
| Property       | contribution | goal_size    | timeline    | location  | timeline is soft          |
| Education      | contribution | goal_size    | scholarship | timeline  | timeline is FIXED         |
| Retirement     | timeline     | contribution | goal_size   | lifestyle | contribution is hard      |
| Emergency Fund | contribution | reduce_scope | timeline    | —         | timeline is N/A           |
| Wedding        | goal_size    | contribution | timeline    | —         | timeline is FIXED         |
| Higher Ed      | contribution | scholarship  | goal_size   | timeline  | location is country-level |
| Custom         | goal_size    | contribution | timeline    | location  | depends on goal           |

## Lever Definitions

### 1. Contribution Increase

- Validate: only available if disposable_income > monthly_required × 0.5
- Show: exact additional monthly amount needed
- Show: what sacrifice that represents (% of lifestyle spending cut)

### 2. Goal Size Reduction

- Show: what specific reduction (e.g., "reduce apartment from 70sqm to 54sqm")
- Show: new monthly required
- Psychologically hard — frame as "what you'd give up" not "reduce ambition"

### 3. Timeline Extension

- For Fixed-deadline goals (wedding, education): **DO NOT recommend first**
- Flag: "This goal has a natural deadline — extending timeline means delaying
  the goal itself. This may not be acceptable for your situation."
- For Property: culturally acceptable (rental phase normalized)

### 4. Location Change

- Property only: show same-size apartment in lower-cost neighbourhood/city
- For non-property goals: treat as "what if" exploration only, not recommendation
- Show: what changes in the goal (school quality, wedding venue tier)

## Scenario Output Format

Each scenario must display:

1. Lever name and adjustment
2. New investment-to-income ratio
3. New verdict (must be Green for recommended scenarios)
4. Change description in plain language
5. What the user gives up / gains
6. Confidence: HIGH/MEDIUM/LOW based on input certainty
