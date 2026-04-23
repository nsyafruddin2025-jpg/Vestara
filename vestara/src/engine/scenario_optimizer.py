"""
Scenario Optimizer — finds minimum viable adjustment to flip Yellow/Red to Green.
Priority order: (1) extend timeline, (2) adjust location, (3) reduce goal size,
(4) increase monthly contribution.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

from vestara.data.cost_data import PROPERTY_PRICE_PER_SQM, LIVING_COST_MONTHLY

GREEN_THRESHOLD = 0.30  # investment-to-disposable-income ratio


@dataclass
class Scenario:
    lever: str
    adjustment: str
    new_value: float
    old_value: float
    new_ratio: float
    verdict: str
    change_description: str


@dataclass
class ScenarioResult:
    current_ratio: float
    current_verdict: str
    scenarios: list[Scenario]
    recommended: Optional[Scenario]
    projection_years: list[float]
    projection_monthly: list[float]


def compound_projection(monthly_salary: float, annual_growth: float, years: int) -> list[float]:
    """Return monthly salary trajectory over N years."""
    trajectory = []
    for y in range(years + 1):
        inflated = monthly_salary * ((1 + annual_growth) ** y)
        trajectory.append(inflated)
    return trajectory


def compute_monthly_required(goal_cost: float, timeline_years: int) -> float:
    return goal_cost / (timeline_years * 12)


def compute_ratio(monthly_salary: float, monthly_living_cost: float, monthly_required: float) -> float:
    disposable = monthly_salary - monthly_living_cost
    if disposable <= 0:
        return 1.0
    return min(monthly_required / disposable, 2.0)


def optimize_timeline(
    goal_cost: float,
    monthly_salary: float,
    monthly_living_cost: float,
    current_timeline: int,
    max_years: int = 40,
) -> Optional[Scenario]:
    """Find minimum timeline extension to hit Green threshold."""
    for years in range(current_timeline, max_years + 1):
        monthly_req = compute_monthly_required(goal_cost, years)
        ratio = compute_ratio(monthly_salary, monthly_living_cost, monthly_req)
        if ratio < GREEN_THRESHOLD:
            return Scenario(
                lever="timeline",
                adjustment=f"Extend from {current_timeline} to {years} years",
                new_value=years,
                old_value=current_timeline,
                new_ratio=ratio,
                verdict="green",
                change_description=f"Adding {years - current_timeline} more years reduces monthly required from Rp {compute_monthly_required(goal_cost, current_timeline):,.0f} to Rp {monthly_req:,.0f}",
            )
    return None


def optimize_location(
    goal_cost: float,
    monthly_salary: float,
    current_city: str,
    current_timeline: int,
) -> Optional[Scenario]:
    """Find lowest-cost city that makes goal achievable."""
    current_living = LIVING_COST_MONTHLY.get(current_city, 6_000_000)

    monthly_req = compute_monthly_required(goal_cost, current_timeline)
    best = None
    best_ratio = compute_ratio(monthly_salary, current_living, monthly_req)

    for city, living_cost in sorted(LIVING_COST_MONTHLY.items(), key=lambda x: x[1]):
        if city == current_city:
            continue
        ratio = compute_ratio(monthly_salary, living_cost, monthly_req)
        if ratio < best_ratio:
            best_ratio = ratio
            best = city

    if best and best_ratio < GREEN_THRESHOLD:
        old_living = current_living
        new_living = LIVING_COST_MONTHLY[best]
        return Scenario(
            lever="location",
            adjustment=f"Move from {current_city} to {best}",
            new_value=LIVING_COST_MONTHLY[best],
            old_value=old_living,
            new_ratio=best_ratio,
            verdict="green",
            change_description=f"Lower living cost (Rp {old_living:,.0f} → Rp {new_living:,.0f}/month) increases disposable income",
        )
    return None


def optimize_goal_size(
    goal_cost: float,
    monthly_salary: float,
    monthly_living_cost: float,
    current_timeline: int,
    min_reduction_pct: float = 0.05,
    max_reduction_pct: float = 0.60,
) -> Optional[Scenario]:
    """Find minimum goal reduction to hit Green threshold."""
    step = 0.01
    for reduction_pct in np.arange(min_reduction_pct, max_reduction_pct + step, step):
        new_cost = goal_cost * (1 - reduction_pct)
        monthly_req = compute_monthly_required(new_cost, current_timeline)
        ratio = compute_ratio(monthly_salary, monthly_living_cost, monthly_req)
        if ratio < GREEN_THRESHOLD:
            return Scenario(
                lever="goal_size",
                adjustment=f"Reduce goal by {reduction_pct*100:.0f}%",
                new_value=new_cost,
                old_value=goal_cost,
                new_ratio=ratio,
                verdict="green",
                change_description=f"Target drops from Rp {goal_cost:,.0f} to Rp {new_cost:,.0f} — monthly needed drops to Rp {monthly_req:,.0f}",
            )
    return None


def optimize_monthly_contribution(
    goal_cost: float,
    monthly_salary: float,
    monthly_living_cost: float,
    current_timeline: int,
    current_contribution: float,
) -> Optional[Scenario]:
    """Find minimum contribution increase to hit Green threshold."""
    disposable = monthly_salary - monthly_living_cost
    if disposable <= 0:
        return None

    max_affordable = disposable * GREEN_THRESHOLD
    for increase_pct in np.arange(0.05, 5.0, 0.05):
        new_contribution = current_contribution * (1 + increase_pct)
        if new_contribution >= max_affordable:
            ratio = GREEN_THRESHOLD
            return Scenario(
                lever="monthly_contribution",
                adjustment=f"Increase from Rp {current_contribution:,.0f} to Rp {new_contribution:,.0f}/month",
                new_value=new_contribution,
                old_value=current_contribution,
                new_ratio=ratio,
                verdict="green",
                change_description=f"Contribution rise of {increase_pct*100:.0f}% — investment ratio hits {GREEN_THRESHOLD*100:.0f}% of disposable income",
            )
    return None


def run_scenario_analysis(
    goal_cost: float,
    monthly_salary: float,
    monthly_living_cost: float,
    current_timeline: int,
    current_contribution: float,
) -> ScenarioResult:
    """
    Run full scenario analysis across all four levers.
    Returns scenarios sorted by ease of adjustment (timeline easiest, contribution hardest).
    """
    current_ratio = compute_ratio(
        monthly_salary, monthly_living_cost, compute_monthly_required(goal_cost, current_timeline)
    )
    current_verdict = "green" if current_ratio < GREEN_THRESHOLD else ("yellow" if current_ratio < 0.50 else "red")

    scenarios = []

    # Priority 1: timeline
    t_scenario = optimize_timeline(goal_cost, monthly_salary, monthly_living_cost, current_timeline)
    if t_scenario:
        scenarios.append(t_scenario)

    # Priority 2: location
    l_scenario = optimize_location(goal_cost, monthly_salary, "", current_timeline)
    if l_scenario:
        scenarios.append(l_scenario)

    # Priority 3: goal size
    g_scenario = optimize_goal_size(goal_cost, monthly_salary, monthly_living_cost, current_timeline)
    if g_scenario:
        scenarios.append(g_scenario)

    # Priority 4: contribution
    c_scenario = optimize_monthly_contribution(
        goal_cost, monthly_salary, monthly_living_cost, current_timeline, current_contribution
    )
    if c_scenario:
        scenarios.append(c_scenario)

    # First achievable scenario is the recommendation
    recommended = scenarios[0] if scenarios else None

    return ScenarioResult(
        current_ratio=current_ratio,
        current_verdict=current_verdict,
        scenarios=scenarios,
        recommended=recommended,
        projection_years=list(range(current_timeline + 1)),
        projection_monthly=compound_projection(monthly_salary, 0.08, current_timeline),
    )


if __name__ == "__main__":
    # Test: Yellow scenario
    result = run_scenario_analysis(
        goal_cost=2_100_000_000,
        monthly_salary=15_000_000,
        monthly_living_cost=8_500_000,
        current_timeline=5,
        current_contribution=1_500_000,
    )
    print(f"Current ratio: {result.current_ratio:.2%} | Verdict: {result.current_verdict}")
    print(f"Found {len(result.scenarios)} scenario(s):")
    for s in result.scenarios:
        print(f"  [{s.lever.upper()}] {s.adjustment}")
        print(f"    New ratio: {s.new_ratio:.2%} | {s.change_description}")
    if result.recommended:
        print(f"\nRecommended: {result.recommended.lever.upper()} — {result.recommended.adjustment}")
