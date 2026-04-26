"""
Cost data seed for Indonesian cities — 2025 realistic figures.
All values in IDR unless otherwise noted.
"""

import datetime

# ══════════════════════════════════════════════════════════════
# INFLATION & ADJUSTMENT RATES
# ══════════════════════════════════════════════════════════════

PROPERTY_INFLATION_RATE = 0.06       # Annual property price inflation
PROPERTY_BUFFER = 1.15              # 15%: PPHTB + BPHTB + notary + agent fees

EDUCATION_INFLATION_RATE = {
    "Government": 0.08,      # Government schools: limited by state funding
    "Local Private": 0.08,   # Local private: similar to government inflation
    "National Plus": 0.10,   # National Plus: premium segment, higher inflation
    "International": 0.12,   # International: fastest-growing segment
}

HIGHER_ED_TUITION_INFLATION = 0.05  # Annual tuition inflation (local & abroad)
RETIREMENT_LIVING_INFLATION = 0.04  # Annual cost of living inflation in retirement
WEDDING_INFLATION_RATE = 0.05       # Annual wedding cost inflation
IDR_DEPRECIATION_RATE = 0.04         # IDR weakens vs major currencies annually
CURRENCY_RISK_BUFFER = 0.10         # 10% buffer for forex volatility

# ══════════════════════════════════════════════════════════════
# EDUCATION: CHILD'S SCHOOL
# ══════════════════════════════════════════════════════════════

EDUCATION_ENTRY_AGE = {
    "Primary": 6,      # SD: entry at 6
    "Secondary": 12,   # SMP: entry at 12
    "High School": 15, # SMA: entry at 15
}

EDUCATION_DURATION = {
    "Primary": 6,      # SD: 6 years
    "Secondary": 3,    # SMP: 3 years
    "High School": 3,  # SMA: 3 years
}

# Annual school fees by level × city (IDR)
# Level: Primary / Secondary / High School
SCHOOL_FEES_ANNUAL = {
    # ── Government schools (negligible tuition, some levies) ──
    "Government": {
        "Jakarta Selatan": 3_000_000, "Jakarta Pusat": 3_000_000, "Jakarta Utara": 2_500_000,
        "Jakarta Timur": 2_500_000, "Jakarta Barat": 2_800_000,
        "Bandung": 2_000_000, "Surabaya": 2_500_000, "Yogyakarta": 1_800_000,
        "Medan": 1_500_000, "Bali (Denpasar)": 2_000_000, "Semarang": 1_800_000, "Makassar": 2_000_000,
        "Depok": 2_200_000, "Bekasi": 2_300_000,
        "Tangerang": 2_400_000, "Tangerang Selatan": 2_500_000, "Bogor": 2_000_000,
    },
    # ── Local Private schools ──
    "Local Private": {
        "Jakarta Selatan": 12_000_000, "Jakarta Pusat": 10_000_000, "Jakarta Utara": 8_000_000,
        "Jakarta Timur": 7_500_000, "Jakarta Barat": 9_000_000,
        "Bandung": 8_000_000, "Surabaya": 9_000_000, "Yogyakarta": 7_000_000,
        "Medan": 6_000_000, "Bali (Denpasar)": 8_000_000, "Semarang": 6_500_000, "Makassar": 7_000_000,
        "Depok": 7_500_000, "Bekasi": 8_000_000,
        "Tangerang": 9_000_000, "Tangerang Selatan": 10_000_000, "Bogor": 7_000_000,
    },
    # ── National Plus schools ──
    "National Plus": {
        "Jakarta Selatan": 30_000_000, "Jakarta Pusat": 28_000_000, "Jakarta Utara": 25_000_000,
        "Jakarta Timur": 24_000_000, "Jakarta Barat": 27_000_000,
        "Bandung": 25_000_000, "Surabaya": 26_000_000, "Yogyakarta": 22_000_000,
        "Medan": 20_000_000, "Bali (Denpasar)": 25_000_000, "Semarang": 20_000_000, "Makassar": 22_000_000,
        "Depok": 24_000_000, "Bekasi": 25_000_000,
        "Tangerang": 26_000_000, "Tangerang Selatan": 28_000_000, "Bogor": 22_000_000,
    },
    # ── International schools (annual tuition, USD-denominated converted) ──
    # Using Rp 16,000/USD approximation; international schools charge USD
    "International": {
        "Jakarta Selatan": 180_000_000, "Jakarta Pusat": 170_000_000, "Jakarta Utara": 150_000_000,
        "Jakarta Timur": 145_000_000, "Jakarta Barat": 165_000_000,
        "Bandung": 150_000_000, "Surabaya": 160_000_000, "Yogyakarta": 140_000_000,
        "Medan": 130_000_000, "Bali (Denpasar)": 160_000_000, "Semarang": 130_000_000, "Makassar": 140_000_000,
        "Depok": 145_000_000, "Bekasi": 150_000_000,
        "Tangerang": 155_000_000, "Tangerang Selatan": 165_000_000, "Bogor": 140_000_000,
    },
}

EDUCATION_LEVELS = ["Primary", "Secondary", "High School"]
EDUCATION_SCHOOL_TYPES = ["Government", "Local Private", "National Plus", "International"]

# ══════════════════════════════════════════════════════════════
# HIGHER EDUCATION
# ══════════════════════════════════════════════════════════════

HIGHER_ED_DEGREE_DURATION = {
    "Bachelor": 4,
    "Master": 2,
    "PhD": 4,   # conservative: 4 years avg for PhD completion
}

# Tuition per year by country × field (IDR, converted from local currency)
# Field multipliers: Business/Economics=1.0, Engineering/Tech=1.2, Medicine/Health=1.8, Law=1.1, Arts/SocialScience=0.9, Other=1.0
HIGHER_ED_BASE_ANNUAL_TUITION = {
    "Indonesia": {
        "public": (15_000_000, 25_000_000),    # UI/UGM public university
        "private": (30_000_000, 80_000_000),    # Private university
        "top_private": (100_000_000, 200_000_000),  # President University, Binus
    },
    "Singapore": (150_000_000, 350_000_000),   # NUS/NTU/SMU
    "Australia": (120_000_000, 300_000_000),   # ANU/UniMelb/UNSW
    "UK": (150_000_000, 400_000_000),         # Russell Group
    "USA": (200_000_000, 600_000_000),        # Top 50 universities
    "Netherlands": (100_000_000, 250_000_000), # TU Delft, UvA
    "Germany": (5_000_000, 30_000_000),        # Public universities (minimal tuition)
    "Japan": (50_000_000, 150_000_000),        # Top Japanese universities
    "Other": (80_000_000, 200_000_000),
}

# Field cost multipliers applied to base tuition
HIGHER_ED_FIELD_MULTIPLIER = {
    "Business / Economics": 1.0,
    "Engineering / Technology": 1.2,
    "Medicine / Health": 1.8,
    "Law": 1.1,
    "Arts / Social Science": 0.9,
    "Other": 1.0,
}

# Annual living costs by country (IDR)
HIGHER_ED_ANNUAL_LIVING = {
    "Indonesia": 36_000_000,     # Rp 3M/month
    "Singapore": 120_000_000,    # SGD 3,500/month
    "Australia": 96_000_000,     # AUD 12,000/yr
    "UK": 108_000_000,          # GBP 7,000/yr
    "USA": 144_000_000,         # USD 9,000/yr
    "Netherlands": 84_000_000,  # EUR 7,000/yr
    "Germany": 72_000_000,       # EUR 6,000/yr
    "Japan": 96_000_000,         # JPY 900,000/yr
    "Other": 80_000_000,
}

HIGHER_ED_ABROAD_COUNTRIES = ["Singapore", "Australia", "UK", "USA", "Netherlands", "Germany", "Japan", "Other"]
HIGHER_ED_DEGREE_LEVELS = ["Bachelor", "Master", "PhD"]
HIGHER_ED_FIELDS = list(HIGHER_ED_FIELD_MULTIPLIER.keys())

# ══════════════════════════════════════════════════════════════
# PROPERTY
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════
# ⚠️  BASELINE_FALLBACK DATA
# All values below are FALLBACK estimates — used only when live data
# sources (BI, BPS, Numbeo) are unavailable. The primary data source
# is vestara/data/fetcher.py which pulls from live public APIs.
# These values should never be shown as "current prices" — only as
# "last verified fallback" when the fetcher has no cached data.
# ══════════════════════════════════════════════════════════════════════

BASELINE_FALLBACK_APARTMENT_PRICE_PER_SQM: dict[str, int] = {
    # Core 10 cities
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
    # Jakarta missing districts (added from Numbeo directional data)
    "Jakarta Timur": 25_000_000,
    "Jakarta Barat": 30_000_000,
    # Jabodetabek areas
    "Depok": 18_000_000,
    "Bekasi": 20_000_000,
    "Tangerang": 22_000_000,
    "Tangerang Selatan": 26_000_000,
    "Bogor": 15_000_000,
}

# Legacy alias — DEPRECATED, use BASELINE_FALLBACK_APARTMENT_PRICE_PER_SQM
APARTMENT_PRICE_PER_SQM = BASELINE_FALLBACK_APARTMENT_PRICE_PER_SQM

# Landed houses command ~30% premium (land ownership, garden, parking)
LANDED_HOUSE_PREMIUM = 1.30

# Apartment sizes (building sqm, no land component)
APARTMENT_SIZES = {
    "Studio / 1BR": 30,
    "2BR": 55,
    "3BR": 85,
    "4BR+": 120,
}

# Landed house sizes (building sqm, with land)
LANDED_HOUSE_SIZES = {
    "Tipe 36": {"building_sqm": 36,  "total_sqm": 60},
    "Tipe 45": {"building_sqm": 45,  "total_sqm": 72},
    "Tipe 54": {"building_sqm": 54,  "total_sqm": 90},
    "Tipe 70": {"building_sqm": 70,  "total_sqm": 120},
    "Tipe 120": {"building_sqm": 120, "total_sqm": 200},
    "Custom": None,  # user enters building_sqm and total_sqm manually
}

PROPERTY_TYPES = ["Apartment", "Landed House", "Land Only", "Shophouse / Ruko"]

PROPERTY_SIZES_BY_TYPE = {
    "Apartment": list(APARTMENT_SIZES.keys()),
    "Landed House": list(LANDED_HOUSE_SIZES.keys()),
    "Land Only": ["Per sqm — enter total land size below"],
    "Shophouse / Ruko": ["Custom (enter sqm below)"],
}

PROPERTY_PRICE_PER_SQM = APARTMENT_PRICE_PER_SQM  # backward compatibility alias

# ══════════════════════════════════════════════════════════════
# RETIREMENT
# ══════════════════════════════════════════════════════════════

RETIREMENT_ANNUAL_EXPENSE = {
    "basic": 60_000_000,         # Rp 5M/month
    "comfortable": 120_000_000,  # Rp 10M/month
    "premium": 240_000_000,     # Rp 20M/month
}

RETIREMENT_LIFESTYLE_OPTIONS = [
    "Basic (Rp 5-8M/month)",
    "Comfortable (Rp 8-15M/month)",
    "Premium (Rp 15-30M/month)",
    "Custom — enter my own amount",
]

LIFE_EXPECTANCY_OPTIONS = [75, 80, 85, "Custom — enter my own assumption"]

# ══════════════════════════════════════════════════════════════
# EMERGENCY FUND
# ══════════════════════════════════════════════════════════════

EMERGENCY_FUND_COVERAGE_OPTIONS = [
    "3 months",
    "6 months",
    "9 months",
    "12 months",
]

EMERGENCY_FUND_MULTIPLE = 6

# ══════════════════════════════════════════════════════════════
# WEDDING
# ══════════════════════════════════════════════════════════════

WEDDING_BASE_COST = {
    # (city: base_cost) — mid-range estimates
    "Jakarta Selatan": 150_000_000, "Jakarta Pusat": 140_000_000, "Jakarta Utara": 120_000_000,
    "Jakarta Timur": 115_000_000, "Jakarta Barat": 135_000_000,
    "Bandung": 100_000_000, "Surabaya": 110_000_000, "Yogyakarta": 80_000_000,
    "Medan": 70_000_000, "Bali (Denpasar)": 130_000_000, "Semarang": 70_000_000, "Makassar": 90_000_000,
    # Jabodetabek
    "Depok": 95_000_000, "Bekasi": 100_000_000,
    "Tangerang": 115_000_000, "Tangerang Selatan": 125_000_000, "Bogor": 85_000_000,
}

WEDDING_SCALE_MULTIPLIER = {
    "Intimate (up to 50 guests)": 0.5,
    "Standard (50-200 guests)": 1.0,
    "Grand (200+ guests)": 1.8,
}

WEDDING_VENUE_MULTIPLIER = {
    "Home / Family House": 0.5,
    "Restaurant": 0.8,
    "Garden / Outdoor Venue": 1.0,
    "Hotel Ballroom": 1.5,
}

WEDDING_CATERING_MULTIPLIER = {
    "Standard": 1.0,
    "Premium": 1.4,
}

WEDDING_ENTERTAINMENT_MULTIPLIER = {
    "Basic (MC + Sound)": 1.0,
    "Band / DJ": 1.3,
    "Full Production (Band + MC + Decoration)": 1.8,
}

WEDDING_SCALES = list(WEDDING_SCALE_MULTIPLIER.keys())
WEDDING_VENUES = list(WEDDING_VENUE_MULTIPLIER.keys())
WEDDING_CATERING = list(WEDDING_CATERING_MULTIPLIER.keys())
WEDDING_ENTERTAINMENT = list(WEDDING_ENTERTAINMENT_MULTIPLIER.keys())

# Legacy alias
WEDDING_COST = WEDDING_BASE_COST  # for backward compat in old code paths

# ══════════════════════════════════════════════════════════════
# LIVING COSTS & COMMON DATA
# ══════════════════════════════════════════════════════════════

# BASELINE_FALLBACK — same caveat as property prices above
BASELINE_FALLBACK_LIVING_COST_MONTHLY: dict[str, int] = {
    # Core 10 cities
    "Jakarta Selatan": 8_500_000, "Jakarta Pusat": 7_500_000, "Jakarta Utara": 6_000_000,
    "Bandung": 5_000_000, "Surabaya": 5_500_000, "Yogyakarta": 4_000_000,
    "Medan": 3_500_000, "Bali (Denpasar)": 6_500_000, "Semarang": 3_800_000, "Makassar": 4_200_000,
    # Jakarta missing districts
    "Jakarta Timur": 5_500_000, "Jakarta Barat": 6_500_000,
    # Jabodetabek areas
    "Depok": 4_500_000, "Bekasi": 4_800_000,
    "Tangerang": 5_000_000, "Tangerang Selatan": 5_500_000, "Bogor": 4_200_000,
}

# Legacy alias — DEPRECATED, use BASELINE_FALLBACK_LIVING_COST_MONTHLY
LIVING_COST_MONTHLY = BASELINE_FALLBACK_LIVING_COST_MONTHLY

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

GOAL_TYPES = ["Property", "Education", "Retirement", "Emergency Fund", "Wedding", "Higher Education", "Custom"]

# ══════════════════════════════════════════════════════════════
# UTILITY
# ══════════════════════════════════════════════════════════════

def get_current_year() -> int:
    return datetime.datetime.now().year

INSTRUMENT_RISK_LABELS = {
    "Reksa Dana Saham": "High Risk — value may drop significantly",
    "Reksa Dana Campuran": "Medium Risk — moderate fluctuation",
    "Reksa Dana Pasar Uang": "Low Risk — stable, liquid",
    "ORI": "Low Risk — government guaranteed, fixed return",
    "SBR": "Low Risk — government guaranteed, fixed return",
    "ORI/SBR": "Low Risk — government guaranteed, fixed return",
    "Deposito": "Very Low Risk — LPS guaranteed up to Rp 2B",
    "DIRE": "Medium-High Risk — affected by property market",
    "DIRE/REITs": "Medium-High Risk — affected by property market",
}
