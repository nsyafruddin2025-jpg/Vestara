"""
Synthetic training data generator for the Feasibility Classifier.
Produces labelled examples: salary, goal_cost, timeline_years, city_living_cost_index,
income_growth_rate, disposable_income_pct, investment_to_income_ratio → verdict.
"""

import numpy as np
import pandas as pd
from vestara.data.cost_data import (
    PROPERTY_PRICE_PER_SQM,
    LIVING_COST_MONTHLY,
    SALARY_DISTRIBUTION,
    INCOME_GROWTH_RATE_ANNUAL,
    GOAL_TYPES,
)

np.random.seed(42)

CITIES = list(PROPERTY_PRICE_PER_SQM.keys())
SALARY_BUCKETS = ["fresh_graduate", "mid_career", "senior"]


def compute_investment_to_income_ratio(
    monthly_salary: float,
    monthly_living_cost: float,
    monthly_investment: float,
) -> float:
    disposable = monthly_salary - monthly_living_cost
    if disposable <= 0:
        return 1.0
    return monthly_investment / disposable


def compute_disposable_income(monthly_salary: float, monthly_living_cost: float) -> float:
    return max(0.0, monthly_salary - monthly_living_cost)


def project_goal_cost_at_year(
    goal_cost: float,
    annual_expense: float,
    years: int,
    goal_type: str,
) -> float:
    if goal_type == "Property":
        return goal_cost
    if goal_type == "Education":
        return goal_cost
    if goal_type == "Higher Education":
        return goal_cost
    inflation = 0.05
    return goal_cost * (1 + inflation) ** years


def label_verdict(investment_to_income_ratio: float, years_to_goal: int) -> str:
    """
    Label based on investment-to-disposable-income ratio thresholds
    calibrated to OJK saving behaviour research.
    Green  < 30% sustainable
    Yellow 30–50% challenging but possible
    Red    > 50% not achievable as stated
    """
    if investment_to_income_ratio < 0.30:
        return "green"
    elif investment_to_income_ratio < 0.50:
        return "yellow"
    else:
        return "red"


def generate_goal_cost(goal_type: str, city: str) -> float:
    """Return realistic goal cost in IDR."""
    if goal_type == "Property":
        size_sqm = np.random.choice([36, 45, 54, 70, 90, 120], p=[0.25, 0.25, 0.2, 0.15, 0.1, 0.05])
        price_per_sqm = PROPERTY_PRICE_PER_SQM[city]
        return size_sqm * price_per_sqm
    elif goal_type == "Education":
        return np.random.uniform(50_000_000, 300_000_000)
    elif goal_type == "Retirement":
        years = np.random.randint(15, 35)
        expense = np.random.choice([36_000_000, 72_000_000, 120_000_000])
        return expense * years
    elif goal_type == "Emergency Fund":
        living_cost = LIVING_COST_MONTHLY[city]
        return living_cost * 6
    elif goal_type == "Wedding":
        return np.random.choice([30_000_000, 80_000_000, 200_000_000], p=[0.4, 0.4, 0.2])
    elif goal_type == "Higher Education":
        abroad_costs = [80_000_000, 120_000_000, 150_000_000, 200_000_000]
        return np.random.choice(abroad_costs)
    else:
        return np.random.uniform(50_000_000, 500_000_000)


def generate_synthetic_dataset(n_samples: int = 5000) -> pd.DataFrame:
    rows = []

    for _ in range(n_samples):
        bucket = np.random.choice(SALARY_BUCKETS, p=[0.40, 0.45, 0.15])
        monthly_salary = np.random.uniform(*SALARY_DISTRIBUTION[bucket])
        city = np.random.choice(CITIES)
        monthly_living_cost = LIVING_COST_MONTHLY[city]

        income_growth_rate = np.random.uniform(*INCOME_GROWTH_RATE_ANNUAL[bucket])

        goal_type = np.random.choice(GOAL_TYPES)
        goal_cost = generate_goal_cost(goal_type, city)
        timeline_years = np.random.randint(3, 31)

        living_cost_index = list(LIVING_COST_MONTHLY.keys()).index(city) + 1

        future_goal_cost = project_goal_cost_at_year(goal_cost, 0, timeline_years, goal_type)

        monthly_required = future_goal_cost / (timeline_years * 12)

        iti_ratio = compute_investment_to_income_ratio(
            monthly_salary, monthly_living_cost, monthly_required
        )
        iti_ratio = min(iti_ratio, 2.0)

        disposable = compute_disposable_income(monthly_salary, monthly_living_cost)

        rows.append(
            {
                "monthly_salary": round(monthly_salary),
                "city": city,
                "city_living_cost_index": living_cost_index,
                "goal_type": goal_type,
                "goal_cost": round(goal_cost),
                "timeline_years": timeline_years,
                "income_growth_rate": round(income_growth_rate, 4),
                "monthly_living_cost": round(monthly_living_cost),
                "disposable_income": round(disposable),
                "monthly_investment_required": round(monthly_required),
                "investment_to_income_ratio": round(iti_ratio, 4),
                "verdict": label_verdict(iti_ratio, timeline_years),
            }
        )

    return pd.DataFrame(rows)


TRAINING_FEATURES = [
    "monthly_salary",
    "city_living_cost_index",
    "goal_cost",
    "timeline_years",
    "income_growth_rate",
    "monthly_living_cost",
    "disposable_income",
    "monthly_investment_required",
    "investment_to_income_ratio",
]


if __name__ == "__main__":
    df = generate_synthetic_dataset(5000)
    print(f"Generated {len(df)} samples")
    print(f"\nVerdict distribution:\n{df['verdict'].value_counts()}")
    print(f"\nSample:\n{df.head(3).T}")
    df.to_csv("vestara/data/synthetic_training_data.csv", index=False)
