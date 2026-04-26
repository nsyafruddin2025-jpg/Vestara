"""
Cost data seed for Indonesian cities — 2025 realistic figures.
All values in IDR unless otherwise noted.
"""

# ── Apartment prices per sqm (building footprint, IDR) ────────────────────────
APARTMENT_PRICE_PER_SQM = {
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

# ── Landed house configuration ────────────────────────────────────────────────
# landedness = building_sqm / total_sqm (rest is land)
# e.g. Tipe 36: building=36 sqm, land=60 sqm → landedness=0.60
LANDED_HOUSE_TYPES = {
    # Apartment types (landedness=1.0, pure building sqm)
    "Studio / 1BR Apartment (24-36 sqm)":   {"building_sqm": 30,  "landedness": 1.0},
    "2BR Apartment (45-65 sqm)":            {"building_sqm": 55,  "landedness": 1.0},
    "3BR Apartment (75-100 sqm)":           {"building_sqm": 85,  "landedness": 1.0},
    # Landed house types (building < total, premium applies)
    "Small Landed House / Tipe 36 (36 sqm building, 60 sqm land)":  {"building_sqm": 36,  "landedness": 0.60},
    "Medium Landed House / Tipe 45-54 (45-54 sqm building)":         {"building_sqm": 50,  "landedness": 0.70},
    "Large Landed House / Tipe 70-120 (70-120 sqm building)":        {"building_sqm": 95,  "landedness": 0.75},
    "Villa / Premium Landed (120 sqm+)":     {"building_sqm": 140, "landedness": 0.80},
    "Shophouse / Ruko":                     {"building_sqm": 80,  "landedness": 0.90},
    "Land Only (per sqm)":                  {"building_sqm": 0,   "landedness": 0.00},
}

# Landed houses in Jakarta command ~30% premium over equivalent apartment sqm
# (land ownership, larger floor plates, garden, parking)
LANDED_HOUSE_PREMIUM = 1.30

# Backward-compatibility alias
PROPERTY_PRICE_PER_SQM = APARTMENT_PRICE_PER_SQM

# ── School fees ────────────────────────────────────────────────────────────────
SCHOOL_FEES_ANNUAL = {
    "local_private_low": 3_000_000,
    "local_private_mid": 8_000_000,
    "local_private_high": 18_000_000,
    "international_mid": 60_000_000,
    "international_top": 150_000_000,
}

# ── Living costs ──────────────────────────────────────────────────────────────
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

# ── Salary brackets ───────────────────────────────────────────────────────────
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

# ── Goal types ────────────────────────────────────────────────────────────────
GOAL_TYPES = [
    "Property",
    "Education",
    "Retirement",
    "Emergency Fund",
    "Wedding",
    "Higher Education",
    "Custom",
]

# ── Education abroad ─────────────────────────────────────────────────────────
EDUCATION_ABROAD_ANNUAL = {
    "Australia": (80_000_000, 200_000_000),
    "Europe": (100_000_000, 250_000_000),
    "Singapore": (120_000_000, 300_000_000),
    "US": (150_000_000, 400_000_000),
}

# ── Retirement ───────────────────────────────────────────────────────────────
# Annual expense estimates per lifestyle tier
RETIREMENT_ANNUAL_EXPENSE = {
    "basic": 60_000_000,      # Rp 5M/month
    "comfortable": 120_000_000,  # Rp 10M/month
    "premium": 240_000_000,     # Rp 20M/month
}

RETIREMENT_LIFESTYLE_OPTIONS = [
    "Basic (Rp 5-8M/month estimated spend)",
    "Comfortable (Rp 8-15M/month)",
    "Premium (Rp 15-30M/month)",
    "Custom — enter my own monthly target",
]

# ── Wedding ───────────────────────────────────────────────────────────────────
WEDDING_COST = {
    "simple": 30_000_000,
    "moderate": 80_000_000,
    "grand": 200_000_000,
}

# ── Emergency fund ───────────────────────────────────────────────────────────
EMERGENCY_FUND_OPTIONS = [
    "3 months (minimum)",
    "6 months (standard)",
    "12 months (conservative)",
    "Custom — enter my own monthly expenses",
]

EMERGENCY_FUND_MULTIPLE = 6
