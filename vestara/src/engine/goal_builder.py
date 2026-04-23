"""
Goal Builder — guides user through goal selection and cost estimation.
Supports 7 goal types with smart follow-up questions.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

from vestara.data.cost_data import (
    PROPERTY_PRICE_PER_SQM,
    SCHOOL_FEES_ANNUAL,
    LIVING_COST_MONTHLY,
    EDUCATION_ABROAD_ANNUAL,
    RETIREMENT_ANNUAL_EXPENSE,
    WEDDING_COST,
    EMERGENCY_FUND_MULTIPLE,
    GOAL_TYPES,
)

# Buffers applied to raw base costs
PROPERTY_BUFFER = 1.15   # 15% contingency: PPHTB + BPHTB + notary + price appreciation
IDR_DEPRECIATION_RATE = 0.04  # IDR weakens ~4%/yr vs major currencies (2019–2024 avg)
ABROAD_BUFFER = 1.10         # 10% buffer: application fees, living setup, exchange rate slippage


@dataclass
class GoalProfile:
    goal_type: str
    city: str
    estimated_cost: float
    timeline_years: int
    description: str

    def to_dict(self) -> dict:
        return {
            "goal_type": self.goal_type,
            "city": self.city,
            "estimated_cost": self.estimated_cost,
            "timeline_years": self.timeline_years,
            "description": self.description,
        }


class GoalBuilder:
    CITIES = list(PROPERTY_PRICE_PER_SQM.keys())

    # Property follow-up questions
    PROPERTY_QUESTIONS = [
        {"id": "property_size", "question": "What unit size are you targeting?", "type": "select", "options": ["Studio / 1BR (24-36 sqm)", "2BR Standard (45-54 sqm)", "2BR Large / 3BR (70-90 sqm)", "Large / Penthouse (90-150 sqm)"], "key": "size_sqm_range"},
        {"id": "property_location_detail", "question": "Which area/neighbourhood?", "type": "text", "placeholder": "e.g. Kemang, Senayan, Menteng"},
    ]

    # Education follow-up questions
    EDUCATION_QUESTIONS = [
        {"id": "education_level", "question": "Education level?", "type": "select", "options": ["TK / SD (Elementary)", "SMP (Junior High)", "SMA / SMK (Senior High)"], "key": "level"},
        {"id": "school_tier", "question": "School type?", "type": "select", "options": ["Local Private (J煲0-15M/yr)", "Mid-tier Private (15-30M/yr)", "Premium Private (30-60M/yr)", "International School (60-150M/yr)"], "key": "tier"},
    ]

    # Retirement follow-up questions
    RETIREMENT_QUESTIONS = [
        {"id": "retirement_age", "question": "At what age do you want to retire?", "type": "number", "min": 45, "max": 75},
        {"id": "lifestyle", "question": "Desired retirement lifestyle?", "type": "select", "options": ["Basic (2-3M/month)", "Comfortable (4-6M/month)", "Premium (7-10M/month)"], "key": "lifestyle"},
    ]

    # Higher Education follow-up questions
    HIGHER_ED_QUESTIONS = [
        {"id": "degree_type", "question": "Degree type?", "type": "select", "options": ["Bachelor's Degree", "Master's Degree", "PhD / Doctorate"]},
        {"id": "country", "question": "Country of study?", "type": "select", "options": ["Australia", "Europe", "Singapore", "US", "Other"], "key": "country"},
        {"id": "institution_tier", "question": "Institution tier?", "type": "select", "options": ["Public / State University", "Private University", "Top 50 Global (e.g. NTU, NUS, Melbourne)", "Ivy League / Oxbridge / Top 10"], "key": "tier"},
    ]

    # Wedding follow-up questions
    WEDDING_QUESTIONS = [
        {"id": "wedding_scale", "question": "Wedding style?", "type": "select", "options": ["Simple / Intimate (50-100 guests)", "Moderate / Traditional (200-400 guests)", "Grand / Bilingual (500+ guests)"], "key": "scale"},
    ]

    # Emergency Fund follow-up questions
    EMERGENCY_FUND_QUESTIONS = [
        {"id": "months_covered", "question": "How many months of expenses?", "type": "select", "options": ["3 months (minimum)", "6 months (standard)", "12 months (conservative)"], "key": "months"},
    ]

    def estimate_property_cost(self, city: str, size_label: str) -> float:
        size_map = {
            "Studio / 1BR (24-36 sqm)": 30,
            "2BR Standard (45-54 sqm)": 50,
            "2BR Large / 3BR (70-90 sqm)": 80,
            "Large / Penthouse (90-150 sqm)": 120,
        }
        sqm = size_map.get(size_label, 54)
        price_per_sqm = PROPERTY_PRICE_PER_SQM.get(city, PROPERTY_PRICE_PER_SQM["Jakarta Selatan"])
        base_cost = sqm * price_per_sqm
        return base_cost * PROPERTY_BUFFER

    def estimate_education_cost(self, level: str, tier_label: str) -> float:
        tier_map = {
            "Local Private (J煲0-15M/yr)": SCHOOL_FEES_ANNUAL["local_private_low"],
            "Mid-tier Private (15-30M/yr)": SCHOOL_FEES_ANNUAL["local_private_mid"],
            "Premium Private (30-60M/yr)": SCHOOL_FEES_ANNUAL["local_private_high"],
            "International School (60-150M/yr)": SCHOOL_FEES_ANNUAL["international_mid"],
        }
        annual = tier_map.get(tier_label, SCHOOL_FEES_ANNUAL["local_private_mid"])
        years_map = {"TK / SD (Elementary)": 6, "SMP (Junior High)": 3, "SMA / SMK (Senior High)": 3}
        years = years_map.get(level, 3)
        return annual * years

    def estimate_retirement_cost(self, current_age: int, retirement_age: int, lifestyle: str) -> float:
        monthly_map = {
            "Basic (2-3M/month)": RETIREMENT_ANNUAL_EXPENSE["basic"],
            "Comfortable (4-6M/month)": RETIREMENT_ANNUAL_EXPENSE["comfortable"],
            "Premium (7-10M/month)": RETIREMENT_ANNUAL_EXPENSE["premium"],
        }
        annual = monthly_map.get(lifestyle, RETIREMENT_ANNUAL_EXPENSE["comfortable"])
        years = max(retirement_age - current_age, 1)
        return annual * years

    def estimate_higher_education_cost(self, country: str, tier: str, degree: str) -> float:
        base_annual_map = {
            "Australia": (80_000_000, 150_000_000),
            "Europe": (100_000_000, 200_000_000),
            "Singapore": (120_000_000, 250_000_000),
            "US": (150_000_000, 350_000_000),
            "Other": (80_000_000, 180_000_000),
        }
        tier_multiplier = {
            "Public / State University": 0.8,
            "Private University": 1.0,
            "Top 50 Global (e.g. NTU, NUS, Melbourne)": 1.3,
            "Ivy League / Oxbridge / Top 10": 1.8,
        }
        degree_years = {"Bachelor's Degree": 4, "Master's Degree": 2, "PhD / Doctorate": 4}
        annual_range = base_annual_map.get(country, (100_000_000, 200_000_000))
        mid = (annual_range[0] + annual_range[1]) / 2
        years = degree_years.get(degree, 4)
        multiplier = tier_multiplier.get(tier, 1.0)
        base_cost = mid * years * multiplier
        # Currency depreciation: IDR weakens ~4%/yr + 10% buffer for fees/setup slippage
        depreciated = base_cost * ((1 + IDR_DEPRECIATION_RATE) ** years) * ABROAD_BUFFER
        return depreciated

    def estimate_wedding_cost(self, scale: str) -> float:
        scale_map = {
            "Simple / Intimate (50-100 guests)": WEDDING_COST["simple"],
            "Moderate / Traditional (200-400 guests)": WEDDING_COST["moderate"],
            "Grand / Bilingual (500+ guests)": WEDDING_COST["grand"],
        }
        return scale_map.get(scale, WEDDING_COST["moderate"])

    def estimate_emergency_fund_cost(self, city: str, months_label: str) -> float:
        monthly_living = LIVING_COST_MONTHLY.get(city, 6_000_000)
        months_map = {"3 months (minimum)": 3, "6 months (standard)": 6, "12 months (conservative)": 12}
        months = months_map.get(months_label, 6)
        return monthly_living * months

    def estimate_custom_cost(self, target_amount: Optional[float] = None) -> Optional[float]:
        return target_amount

    def build_goal(self, goal_type: str, city: str, answers: dict) -> GoalProfile:
        cost = 0.0
        description = ""

        if goal_type == "Property":
            size_label = answers.get("property_size", "2BR Standard (45-54 sqm)")
            cost = self.estimate_property_cost(city, size_label)
            description = f"{size_label} in {city}"

        elif goal_type == "Education":
            level = answers.get("education_level", "SMA / SMK (Senior High)")
            tier = answers.get("school_tier", "Mid-tier Private (15-30M/yr)")
            cost = self.estimate_education_cost(level, tier)
            description = f"{tier} {level} education"

        elif goal_type == "Retirement":
            lifestyle = answers.get("retirement", "Comfortable (4-6M/month)")
            current_age = answers.get("current_age", 25)
            retirement_age = answers.get("retirement_age", 55)
            cost = self.estimate_retirement_cost(current_age, retirement_age, lifestyle)
            description = f"{lifestyle} retirement from age {retirement_age}"

        elif goal_type == "Higher Education":
            country = answers.get("country", "Singapore")
            tier = answers.get("institution_tier", "Private University")
            degree = answers.get("degree_type", "Bachelor's Degree")
            cost = self.estimate_higher_education_cost(country, tier, degree)
            description = f"{degree} at {tier} in {country}"

        elif goal_type == "Wedding":
            scale = answers.get("wedding_scale", "Moderate / Traditional (200-400 guests)")
            cost = self.estimate_wedding_cost(scale)
            description = f"{scale} wedding"

        elif goal_type == "Emergency Fund":
            months_label = answers.get("months_covered", "6 months (standard)")
            cost = self.estimate_emergency_fund_cost(city, months_label)
            description = f"{months_label} emergency fund for {city}"

        elif goal_type == "Custom":
            custom_amount = answers.get("custom_amount")
            if custom_amount:
                cost = custom_amount
                description = answers.get("custom_description", f"Custom goal: Rp {custom_amount:,.0f}")
            else:
                description = answers.get("custom_description", "Custom financial goal")

        return GoalProfile(
            goal_type=goal_type,
            city=city,
            estimated_cost=cost,
            timeline_years=answers.get("timeline_years", 10),
            description=description,
        )


if __name__ == "__main__":
    gb = GoalBuilder()

    print("=== Property Goal ===")
    profile = gb.build_goal("Property", "Jakarta Selatan", {
        "property_size": "2BR Standard (45-54 sqm)",
        "timeline_years": 10,
    })
    print(f"  Cost: Rp {profile.estimated_cost:,.0f}")

    print("\n=== Education Goal ===")
    profile = gb.build_goal("Education", "Jakarta Selatan", {
        "education_level": "SMA / SMK (Senior High)",
        "school_tier": "International School (60-150M/yr)",
        "timeline_years": 5,
    })
    print(f"  Cost: Rp {profile.estimated_cost:,.0f}")

    print("\n=== Retirement Goal ===")
    profile = gb.build_goal("Retirement", "Bandung", {
        "current_age": 25,
        "retirement_age": 55,
        "retirement": "Comfortable (4-6M/month)",
        "timeline_years": 30,
    })
    print(f"  Cost: Rp {profile.estimated_cost:,.0f}")

    print("\n=== Higher Education (Abroad) ===")
    profile = gb.build_goal("Higher Education", "Singapore", {
        "degree_type": "Master's Degree",
        "country": "Singapore",
        "institution_tier": "Top 50 Global (e.g. NTU, NUS, Melbourne)",
        "timeline_years": 2,
    })
    print(f"  Cost: Rp {profile.estimated_cost:,.0f}")

    print("\n=== Wedding Goal ===")
    profile = gb.build_goal("Wedding", "Surabaya", {
        "wedding_scale": "Moderate / Traditional (200-400 guests)",
        "timeline_years": 3,
    })
    print(f"  Cost: Rp {profile.estimated_cost:,.0f}")

    print("\n=== Emergency Fund ===")
    profile = gb.build_goal("Emergency Fund", "Bandung", {
        "months_covered": "6 months (standard)",
        "timeline_years": 1,
    })
    print(f"  Cost: Rp {profile.estimated_cost:,.0f}")
