"""
Portfolio Optimizer — mean-variance inspired allocation for Indonesian instruments.
Given risk profile + timeline + goal amount, produces monthly split across instruments
and projected growth curve.
"""

from dataclasses import dataclass
import numpy as np

INSTRUMENTS = [
    "deposito",
    "obligasi_ori_sbr",
    "reksa_dana_pasar_uang",
    "reksa_dana_pendapatan_tetap",
    "reksa_dana_equity",
    "reits",
]

INSTRUMENT_LABELS = {
    "deposito": "Deposito",
    "obligasi_ori_sbr": "ORI / SBR (Government Bonds)",
    "reksa_dana_pasar_uang": "Reksa Dana Pasar Uang",
    "reksa_dana_pendapatan_tetap": "Reksa Dana Pendapatan Tetap",
    "reksa_dana_equity": "Reksa Dana Equity",
    "reits": "REITs (DIRE)",
}

# Annual return assumptions (conservative long-term estimates)
EXPECTED_RETURNS = {
    "deposito": 0.045,
    "obligasi_ori_sbr": 0.065,
    "reksa_dana_pasar_uang": 0.055,
    "reksa_dana_pendapatan_tetap": 0.075,
    "reksa_dana_equity": 0.12,
    "reits": 0.10,
}

# Annual volatility (std dev)
VOLATILITY = {
    "deposito": 0.01,
    "obligasi_ori_sbr": 0.04,
    "reksa_dana_pasar_uang": 0.02,
    "reksa_dana_pendapatan_tetap": 0.06,
    "reksa_dana_equity": 0.20,
    "reits": 0.15,
}


@dataclass
class PortfolioAllocation:
    instrument: str
    percentage: float
    monthly_amount: float
    expected_return: float
    expected_growth_10yr: float


@dataclass
class PortfolioProjection:
    allocations: list[PortfolioAllocation]
    blended_return: float
    blended_volatility: float
    projected_value_at_goal_year: float
    goal_amount: float
    timeline_years: int
    yearly_trajectory: list[tuple[int, float]]


def compute_blended_return(allocations: list[PortfolioAllocation]) -> float:
    return sum(a.percentage * a.expected_return for a in allocations)


def compute_blended_volatility(allocations: list[PortfolioAllocation]) -> float:
    # Simplified: weighted average volatility (ignores correlation for MVP)
    return sum(a.percentage * VOLATILITY.get(a.instrument, 0.05) for a in allocations)


def project_growth(
    monthly_contribution: float,
    allocations: list[PortfolioAllocation],
    years: int,
) -> list[tuple[int, float]]:
    """
    Project portfolio value year by year using blended return rate.
    Returns list of (year, portfolio_value).
    """
    blended = compute_blended_return(allocations)
    monthly_rate = blended / 12

    values = []
    current = 0.0
    for year in range(years + 1):
        values.append((year, current))
        for month in range(12):
            current = current * (1 + monthly_rate) + monthly_contribution
    values.append((years, current))
    return values


def build_portfolio(
    risk_profile: str,
    monthly_contribution: float,
    goal_amount: float,
    timeline_years: int,
) -> PortfolioProjection:
    """
    Build portfolio allocation given risk profile, contribution, and goal.
    Uses rule-based allocation anchored to risk profile ranges.
    """
    if risk_profile == "Konservatif":
        raw = {
            "deposito": 30,
            "obligasi_ori_sbr": 40,
            "reksa_dana_pasar_uang": 15,
            "reksa_dana_pendapatan_tetap": 10,
            "reksa_dana_equity": 5,
            "reits": 0,
        }
    elif risk_profile == "Moderat":
        raw = {
            "deposito": 15,
            "obligasi_ori_sbr": 25,
            "reksa_dana_pasar_uang": 10,
            "reksa_dana_pendapatan_tetap": 20,
            "reksa_dana_equity": 22,
            "reits": 8,
        }
    else:  # Agresif
        raw = {
            "deposito": 0,
            "obligasi_ori_sbr": 5,
            "reksa_dana_pasar_uang": 0,
            "reksa_dana_pendapatan_tetap": 5,
            "reksa_dana_equity": 65,
            "reits": 25,
        }

    total = sum(raw.values())
    raw = {k: v / total * 100 for k, v in raw.items()}

    allocations = []
    for instrument, pct in raw.items():
        if pct < 1:
            continue
        monthly_amount = monthly_contribution * (pct / 100)
        expected = EXPECTED_RETURNS[instrument]
        growth_10yr = (1 + expected) ** 10 - 1
        allocations.append(
            PortfolioAllocation(
                instrument=instrument,
                percentage=round(pct, 1),
                monthly_amount=round(monthly_amount),
                expected_return=expected,
                expected_growth_10yr=growth_10yr,
            )
        )

    blended_return = compute_blended_return(allocations)
    blended_volatility = compute_blended_volatility(allocations)
    yearly_trajectory = project_growth(monthly_contribution, allocations, timeline_years)
    projected_value = yearly_trajectory[-1][1]

    return PortfolioProjection(
        allocations=allocations,
        blended_return=blended_return,
        blended_volatility=blended_volatility,
        projected_value_at_goal_year=projected_value,
        goal_amount=goal_amount,
        timeline_years=timeline_years,
        yearly_trajectory=yearly_trajectory,
    )


if __name__ == "__main__":
    for profile in ["Konservatif", "Moderat", "Agresif"]:
        result = build_portfolio(profile, 2_000_000, 1_000_000_000, 10)
        print(f"\n=== {profile} Portfolio ===")
        print(f"Monthly contribution: Rp {2_000_000:,.0f}")
        print(f"Goal: Rp {result.goal_amount:,.0f} in {result.timeline_years} years")
        print(f"Blended return: {result.blended_return:.2%} | Volatility: {result.blended_volatility:.2%}")
        print(f"Projected value: Rp {result.projected_value_at_goal_year:,.0f}")
        print("Allocation:")
        for a in result.allocations:
            label = INSTRUMENT_LABELS[a.instrument]
            print(f"  {label:35s} {a.percentage:5.1f}%  (Rp {a.monthly_amount:>12,.0f}/mo)")
