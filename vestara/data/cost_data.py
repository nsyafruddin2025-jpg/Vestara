"""
Cost data seed for Indonesian cities — 2025 realistic figures.
All values in IDR unless otherwise noted.
"""

PROPERTY_PRICE_PER_SQM = {
    "Jakarta Selatan": 42_000_000,
    "Jakarta Pusat": 38_000_000,
    "Jakarta Utara": 28_000_000,
    "Bandung": 14_000_000,
    "Surabaya": 16_000_000,
    "Yogyakarta": 10_000_000,
    "Medan": 9_000_000,
    "Bali (Denpasar)": 22_000_000,
    "Semarang": 8_500_000,
    "Makassar": 11_000_000,
}

SCHOOL_FEES_ANNUAL = {
    "local_private_low": 3_000_000,
    "local_private_mid": 8_000_000,
    "local_private_high": 18_000_000,
    "international_mid": 60_000_000,
    "international_top": 150_000_000,
}

LIVING_COST_MONTHLY = {
    "Jakarta Selatan": 8_500_000,
    "Jakarta Pusat": 7_500_000,
    "Jakarta Utara": 6_000_000,
    "Bandung": 5_000_000,
    "Surabaya": 5_500_000,
    "Yogyakarta": 4_000_000,
    "Medan": 3_500_000,
    "Bali (Denpasar)": 6_500_000,
    "Semarang": 3_800_000,
    "Makassar": 4_200_000,
}

CITY_LIVING_COST_INDEX = {city: idx for idx, (_, city) in enumerate(sorted(LIVING_COST_MONTHLY.items()), 1)}

SALARY_DISTRIBUTION = {
    "fresh_graduate": (5_000_000, 8_000_000),
    "mid_career": (10_000_000, 25_000_000),
    "senior": (25_000_000, 60_000_000),
}

INCOME_GROWTH_RATE_ANNUAL = {
    "fresh_graduate": (0.08, 0.15),
    "mid_career": (0.05, 0.12),
    "senior": (0.03, 0.08),
}

GOAL_TYPES = [
    "Property",
    "Education",
    "Retirement",
    "Emergency Fund",
    "Wedding",
    "Higher Education",
    "Custom",
]

EDUCATION_ABROAD_ANNUAL = {
    "Australia": (80_000_000, 200_000_000),
    "Europe": (100_000_000, 250_000_000),
    "Singapore": (120_000_000, 300_000_000),
    "US": (150_000_000, 400_000_000),
}

RETIREMENT_ANNUAL_EXPENSE = {
    "basic": 36_000_000,
    "comfortable": 72_000_000,
    "premium": 120_000_000,
}

WEDDING_COST = {
    "simple": 30_000_000,
    "moderate": 80_000_000,
    "grand": 200_000_000,
}

EMERGENCY_FUND_MULTIPLE = 6
