# Vestara — Product Brief

## What it is

Vestara is a goal-first investment planning platform for young Indonesian professionals (age 22-35, salary Rp 5-25M/month). It starts with the user's life goal, calculates the real cost in their specific Indonesian city, delivers an honest feasibility verdict (Green/Yellow/Red), and recommends an OJK-compliant investment portfolio.

## Goal types

- Property (home purchase)
- Education (school fees)
- Retirement
- Emergency Fund
- Wedding
- Higher Education (abroad)
- Custom (user-defined amount or guided description)

## Core ML components

1. **Feasibility Classifier** — GradientBoostingClassifier (XGBoost-family) trained on 5,000 synthetic samples. Features: monthly_salary, city_living_cost_index, goal_cost, timeline_years, income_growth_rate, monthly_living_cost, disposable_income, monthly_investment_required, investment_to_income_ratio. Verdicts: green/yellow/red.
2. **Scenario Optimizer** — Rule-based constrained optimizer for Yellow/Red flipping across 4 levers (timeline → location → goal size → contribution)
3. **Risk Profiler** — 12-question questionnaire → Konservatif/Moderat/Agresif profiles (OJK-aligned)
4. **Portfolio Optimizer** — Rule-based allocation across 6 Indonesian instruments

## Indonesian market scope

- Cities: Jakarta Selatan/Pusat/Utara, Bandung, Surabaya, Yogyakarta, Medan, Bali, Semarang, Makassar
- Cost data: 2025 property prices per sqm, school fees, living costs
- Portfolio instruments: Deposito, ORI/SBR, Reksa Dana (pasar uang, pendapatan tetap, equity), REITs (DIRE)
- Regulatory: OJK framework

## Key decisions to validate

1. Goal-first differentiation vs Bibit/Pluang/Bareksa
2. Threshold calibration (Green <30%, Yellow 30-50%, Red >50%)
3. Synthetic training data defensibility for course project
4. Scenario lever priority order
5. Rule-based portfolio allocation vs mean-variance optimization

## Threshold rationale (from product brief)

- Green <30%: Below 30% sustainable saving rate (OJK research cited)
- Yellow 30-50%: Challenging but achievable with conditions
- Red >50%: Not achievable as stated
- Priority for scenario adjustment: timeline → location → goal size → contribution
