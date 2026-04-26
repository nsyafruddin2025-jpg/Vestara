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

# Income-bracket aware thresholds (green / yellow boundaries)
INCOME_THRESHOLDS = {
    "fresh_graduate": {"green": 0.25, "yellow": 0.45},   # < Rp 8M/mo disposable is tight
    "mid_career":     {"green": 0.30, "yellow": 0.50},   # standard thresholds
    "senior":         {"green": 0.35, "yellow": 0.55},   # higher disposable, more investable
}

# Goal-type modifiers — fixed-deadline goals (wedding, education) cannot extend timeline
# so their green threshold is stricter to reflect reduced lever flexibility
GOAL_TYPE_MODIFIERS = {
    "Wedding":          {"timeline_locked": True,  "green_boost": 0.02},  # can't delay
    "Education":        {"timeline_locked": True,  "green_boost": 0.02},  # academic intake
    "Higher Education": {"timeline_locked": True,  "green_boost": 0.03},  # abroad intake + visa
    "Property":         {"timeline_locked": False, "green_boost": 0.00},
    "Retirement":       {"timeline_locked": False, "green_boost": -0.02},  # more flexible
    "Emergency Fund":   {"timeline_locked": False, "green_boost": -0.03},  # already short
    "Custom":           {"timeline_locked": False, "green_boost": 0.00},
}

# Timeline extension limits by goal type (years); None = no limit
TIMELINE_MAX_YEARS = {
    "Wedding":          5,
    "Education":        4,
    "Higher Education": 3,  # student visa timelines are rigid
    "Property":         40,
    "Retirement":       40,
    "Emergency Fund":   2,
    "Custom":           40,
}


def get_thresholds(income_bracket: str, goal_type: str) -> tuple[float, float]:
    """Return (green_threshold, yellow_threshold) for given income bracket + goal type."""
    base = INCOME_THRESHOLDS.get(income_bracket, INCOME_THRESHOLDS["mid_career"])
    modifier = GOAL_TYPE_MODIFIERS.get(goal_type, GOAL_TYPE_MODIFIERS["Custom"])
    green = base["green"] + modifier["green_boost"]
    yellow = base["yellow"] + modifier["green_boost"]
    return (round(green, 4), round(yellow, 4))


def get_income_bracket(monthly_salary: float) -> str:
    if monthly_salary < 8_000_000:
        return "fresh_graduate"
    elif monthly_salary < 20_000_000:
        return "mid_career"
    else:
        return "senior"


def get_timeline_max(goal_type: str) -> int:
    return TIMELINE_MAX_YEARS.get(goal_type, 40)


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
    blocked_reason: Optional[str] = None


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
    green_threshold: float,
    max_years: int = 40,
) -> Optional[Scenario]:
    """Find minimum timeline extension to hit Green threshold."""
    for years in range(current_timeline, max_years + 1):
        monthly_req = compute_monthly_required(goal_cost, years)
        ratio = compute_ratio(monthly_salary, monthly_living_cost, monthly_req)
        if ratio < green_threshold:
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
    green_threshold: float,
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

    if best and best_ratio < green_threshold:
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
    green_threshold: float,
    min_reduction_pct: float = 0.05,
    max_reduction_pct: float = 0.60,
) -> Optional[Scenario]:
    """Find minimum goal reduction to hit Green threshold."""
    step = 0.01
    for reduction_pct in np.arange(min_reduction_pct, max_reduction_pct + step, step):
        new_cost = goal_cost * (1 - reduction_pct)
        monthly_req = compute_monthly_required(new_cost, current_timeline)
        ratio = compute_ratio(monthly_salary, monthly_living_cost, monthly_req)
        if ratio < green_threshold:
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
    green_threshold: float,
) -> Optional[Scenario]:
    """Find minimum contribution increase to hit Green threshold."""
    disposable = monthly_salary - monthly_living_cost
    if disposable <= 0:
        return None

    max_affordable = disposable * green_threshold
    for increase_pct in np.arange(0.05, 5.0, 0.05):
        new_contribution = current_contribution * (1 + increase_pct)
        if new_contribution >= max_affordable:
            ratio = green_threshold
            return Scenario(
                lever="monthly_contribution",
                adjustment=f"Increase from Rp {current_contribution:,.0f} to Rp {new_contribution:,.0f}/month",
                new_value=new_contribution,
                old_value=current_contribution,
                new_ratio=ratio,
                verdict="green",
                change_description=f"Contribution rise of {increase_pct*100:.0f}% — investment ratio hits {green_threshold*100:.0f}% of disposable income",
            )
    return None


def run_scenario_analysis(
    goal_cost: float,
    monthly_salary: float,
    monthly_living_cost: float,
    current_timeline: int,
    current_contribution: float,
    goal_type: str = "Custom",
    current_city: str = "Jakarta Selatan",
) -> ScenarioResult:
    """
    Run full scenario analysis across all four levers.
    Returns scenarios sorted by ease of adjustment (timeline easiest, contribution hardest).

    Thresholds are income-bracket and goal-type aware:
    - fresh_graduate (<8M): green < 25%, yellow < 45%
    - mid_career (8-20M): green < 30%, yellow < 50%
    - senior (>20M): green < 35%, yellow < 55%
    - Fixed-deadline goals (Wedding, Education, Higher Education) have stricter green
      thresholds and cannot use timeline extension as a lever.
    """
    income_bracket = get_income_bracket(monthly_salary)
    green_threshold, yellow_threshold = get_thresholds(income_bracket, goal_type)
    goal_modifier = GOAL_TYPE_MODIFIERS.get(goal_type, GOAL_TYPE_MODIFIERS["Custom"])

    current_ratio = compute_ratio(
        monthly_salary, monthly_living_cost, compute_monthly_required(goal_cost, current_timeline)
    )
    current_verdict = (
        "green" if current_ratio < green_threshold
        else ("yellow" if current_ratio < yellow_threshold else "red")
    )

    # HARD GATE: block when ratio >= 100%
    if current_ratio >= 1.0:
        return ScenarioResult(
            current_ratio=current_ratio,
            current_verdict="red",
            scenarios=[],
            recommended=None,
            projection_years=list(range(current_timeline + 1)),
            projection_monthly=compound_projection(monthly_salary, 0.08, current_timeline),
            blocked_reason=(
                "Your required monthly investment exceeds your entire disposable income. "
                "Please consider: (1) reducing your goal size, or "
                "(2) exploring a lower-cost city or neighbourhood. "
                "Increasing your monthly contribution is not structurally available "
                "when disposable income is fully consumed."
            ),
        )

    scenarios = []

    # Priority 1: timeline (SKIP for fixed-deadline goals)
    if not goal_modifier["timeline_locked"]:
        timeline_max = get_timeline_max(goal_type)
        t_scenario = optimize_timeline(
            goal_cost, monthly_salary, monthly_living_cost, current_timeline,
            green_threshold, max_years=timeline_max,
        )
        if t_scenario:
            scenarios.append(t_scenario)
    else:
        # Fixed-deadline goal: warn that timeline extension is unavailable
        pass  # scenarios list unchanged; location/goal_size/contribution remain available

    # Priority 2: location
    l_scenario = optimize_location(
        goal_cost, monthly_salary, current_city, current_timeline, green_threshold,
    )
    if l_scenario:
        scenarios.append(l_scenario)

    # Priority 3: goal size
    g_scenario = optimize_goal_size(
        goal_cost, monthly_salary, monthly_living_cost, current_timeline, green_threshold,
    )
    if g_scenario:
        scenarios.append(g_scenario)

    # Priority 4: contribution
    c_scenario = optimize_monthly_contribution(
        goal_cost, monthly_salary, monthly_living_cost, current_timeline,
        current_contribution, green_threshold,
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
