"""
Goal Builder — intelligent multi-step goal cost estimation.
Cost is always the OUTPUT after all criteria are collected.
All costs are projected to the target year using appropriate inflation rates.
"""

from dataclasses import dataclass, field
from typing import Optional
from vestara.data import cost_data as cd


# ══════════════════════════════════════════════════════════════
# STEP DEFINITIONS
# Each goal type has a fixed sequence of steps.
# The step index (0-based) drives the UI.
# ══════════════════════════════════════════════════════════════

PROPERTY_STEPS = [
    {"id": "property_type",    "label": "Property type",       "total": 5},
    {"id": "city",             "label": "City",               "total": 5},
    {"id": "area",             "label": "Area / Neighbourhood","total": 5},
    {"id": "size",             "label": "Size",              "total": 5},
    {"id": "target_year",      "label": "Target year",       "total": 5},
]

EDUCATION_STEPS = [
    {"id": "education_level",  "label": "Child's education level", "total": 5},
    {"id": "school_type",      "label": "School type",            "total": 5},
    {"id": "child_age",        "label": "Child's current age",    "total": 5},
    {"id": "city",             "label": "City",                   "total": 5},
]

RETIREMENT_STEPS = [
    {"id": "current_age",       "label": "Current age",        "total": 5},
    {"id": "retirement_age",   "label": "Retirement age",      "total": 5},
    {"id": "city",             "label": "City",               "total": 5},
    {"id": "lifestyle",        "label": "Lifestyle",           "total": 5},
    {"id": "life_expectancy",  "label": "Life expectancy",    "total": 5},
]

HIGHER_ED_STEPS = [
    {"id": "degree_level",    "label": "Degree level",         "total": 5},
    {"id": "location",        "label": "Study location",        "total": 5},
    {"id": "country",         "label": "Country",              "total": 5},
    {"id": "field",           "label": "Field of study",       "total": 5},
    {"id": "years_until",     "label": "Years until enrollment","total": 5},
]

WEDDING_STEPS = [
    {"id": "scale",           "label": "Wedding scale",        "total": 5},
    {"id": "city",            "label": "City",                "total": 5},
    {"id": "target_year",     "label": "Target year",         "total": 5},
    {"id": "venue",           "label": "Venue preference",    "total": 5},
    {"id": "entertainment",   "label": "Entertainment",        "total": 5},
]

EMERGENCY_FUND_STEPS = [
    {"id": "monthly_salary",  "label": "Monthly take-home salary", "total": 3},
    {"id": "monthly_expenses","label": "Monthly fixed expenses",     "total": 3},
    {"id": "coverage",         "label": "Coverage duration",          "total": 3},
]

CUSTOM_STEPS = [
    {"id": "goal_name",       "label": "Goal name",           "total": 3},
    {"id": "amount_mode",     "label": "Amount type",         "total": 3},
    {"id": "target_year",     "label": "Target year",         "total": 3},
]

STEPS_BY_GOAL = {
    "Property":        PROPERTY_STEPS,
    "Education":       EDUCATION_STEPS,
    "Retirement":      RETIREMENT_STEPS,
    "Higher Education": HIGHER_ED_STEPS,
    "Wedding":         WEDDING_STEPS,
    "Emergency Fund":   EMERGENCY_FUND_STEPS,
    "Custom":          CUSTOM_STEPS,
}


# ══════════════════════════════════════════════════════════════
# COST BREAKDOWN
# ══════════════════════════════════════════════════════════════

@dataclass
class CostBreakdownItem:
    label: str
    value: float
    detail: str = ""


@dataclass
class CostBreakdown:
    current_cost: float
    projected_cost: float
    years_to_goal: int
    inflation_rate: float
    items: list[CostBreakdownItem] = field(default_factory=list)


# ══════════════════════════════════════════════════════════════
# GOAL PROFILE
# ══════════════════════════════════════════════════════════════

@dataclass
class GoalProfile:
    goal_type: str
    city: str
    estimated_cost: float
    timeline_years: int
    description: str
    breakdown: Optional[CostBreakdown] = None

    def to_dict(self) -> dict:
        return {
            "goal_type": self.goal_type,
            "city": self.city,
            "estimated_cost": self.estimated_cost,
            "timeline_years": self.timeline_years,
            "description": self.description,
        }


# ══════════════════════════════════════════════════════════════
# CALCULATOR HELPERS
# ══════════════════════════════════════════════════════════════

def _project(value: float, rate: float, years: int) -> float:
    """Apply annual compounding to project a value to future."""
    return value * ((1 + rate) ** years)


def _format_year(year: int) -> str:
    return str(year)


# ══════════════════════════════════════════════════════════════
# EDUCATION (CHILD'S SCHOOL)
# ══════════════════════════════════════════════════════════════

def calculate_education(
    education_level: str,
    school_type: str,
    child_age: int,
    city: str,
) -> tuple[float, CostBreakdown]:
    """
    Project total education cost from now to child's school entry year,
    then for the full duration of that school level.
    """
    entry_age = cd.EDUCATION_ENTRY_AGE.get(education_level, 6)
    duration = cd.EDUCATION_DURATION.get(education_level, 6)
    years_until_entry = max(entry_age - child_age, 0)
    entry_year = cd.get_current_year() + years_until_entry

    # Current annual fee
    fee_table = cd.SCHOOL_FEES_ANNUAL.get(school_type, cd.SCHOOL_FEES_ANNUAL["Local Private"])
    current_annual_fee = fee_table.get(city, fee_table["Jakarta Selatan"])

    inflation_rate = cd.EDUCATION_INFLATION_RATE.get(school_type, 0.08)

    # Project annual fee at entry year
    projected_annual_fee = _project(current_annual_fee, inflation_rate, years_until_entry)

    # Total over full duration
    projected_total = projected_annual_fee * duration
    current_total = current_annual_fee * duration

    items = [
        CostBreakdownItem(
            "Current annual fee",
            current_annual_fee,
            f"{school_type} school in {city}",
        ),
        CostBreakdownItem(
            f"Years until entry",
            years_until_entry,
            f"Entry at age {entry_age} (year {entry_year})",
        ),
        CostBreakdownItem(
            "Annual inflation rate",
            inflation_rate * 100,
            f"{inflation_rate * 100:.0f}% per year ({school_type})",
        ),
        CostBreakdownItem(
            "Projected annual fee at entry",
            projected_annual_fee,
            f"Year {entry_year}",
        ),
        CostBreakdownItem(
            "Duration of this level",
            duration,
            f"{education_level}: {duration} years",
        ),
        CostBreakdownItem(
            "Total projected cost",
            projected_total,
            f"{current_total:,.0f} today → {projected_total:,.0f} in {years_until_entry} years",
        ),
    ]

    return projected_total, CostBreakdown(
        current_cost=current_total,
        projected_cost=projected_total,
        years_to_goal=years_until_entry,
        inflation_rate=inflation_rate,
        items=items,
    )


# ══════════════════════════════════════════════════════════════
# HIGHER EDUCATION
# ══════════════════════════════════════════════════════════════

def calculate_higher_education(
    degree_level: str,
    study_location: str,   # "In Indonesia" or "Abroad"
    country: str,
    field: str,
    years_until_enrollment: int,
) -> tuple[float, CostBreakdown]:
    """
    Project total higher education cost (tuition + living) to enrollment year.
    Abroad costs include IDR depreciation and currency risk buffer.
    """
    duration = cd.HIGHER_ED_DEGREE_DURATION.get(degree_level, 4)
    enrollment_year = cd.get_current_year() + years_until_enrollment
    field_mult = cd.HIGHER_ED_FIELD_MULTIPLIER.get(field, 1.0)
    inflation_rate = cd.HIGHER_ED_TUITION_INFLATION

    items = [
        CostBreakdownItem("Degree level", duration, f"{degree_level}: {duration} years"),
        CostBreakdownItem("Years until enrollment", years_until_enrollment, f"Starting {enrollment_year}"),
        CostBreakdownItem("Field of study", field_mult, f"{field} (×{field_mult:.1f} multiplier)"),
    ]

    if study_location == "In Indonesia":
        # Indonesia: public or private university
        pub_lo, pub_hi = cd.HIGHER_ED_BASE_ANNUAL_TUITION["Indonesia"]["public"]
        priv_lo, priv_hi = cd.HIGHER_ED_BASE_ANNUAL_TUITION["Indonesia"]["private"]
        # Use private mid-range
        annual_tuition_current = (priv_lo + priv_hi) / 2 * field_mult
        annual_living = cd.HIGHER_ED_ANNUAL_LIVING["Indonesia"]
        country_label = "Indonesia (Private University)"
    else:
        country_key = country if country in cd.HIGHER_ED_ANNUAL_LIVING else "Other"
        lo, hi = cd.HIGHER_ED_BASE_ANNUAL_TUITION.get(country, cd.HIGHER_ED_BASE_ANNUAL_TUITION["Other"])
        annual_tuition_current = (lo + hi) / 2 * field_mult
        annual_living = cd.HIGHER_ED_ANNUAL_LIVING.get(country_key, cd.HIGHER_ED_ANNUAL_LIVING["Other"])
        country_label = country

    # Project tuition to enrollment year
    projected_tuition = _project(annual_tuition_current, inflation_rate, years_until_enrollment)

    # Living cost inflation (domestic: lower; abroad: higher)
    living_inflation = inflation_rate if study_location == "In Indonesia" else inflation_rate + 0.02
    projected_living = _project(annual_living, living_inflation, years_until_enrollment)

    # Abroad: IDR depreciation + currency risk
    abroad_adjustment = 1.0
    if study_location == "Abroad":
        idr_depreciation = _project(1.0, cd.IDR_DEPRECIATION_RATE, years_until_enrollment)
        abroad_adjustment = idr_depreciation * (1 + cd.CURRENCY_RISK_BUFFER)
        items.append(CostBreakdownItem(
            "IDR depreciation",
            (idr_depreciation - 1) * 100,
            f"×{idr_depreciation:.2f} over {years_until_enrollment} years",
        ))
        items.append(CostBreakdownItem(
            "Currency risk buffer",
            cd.CURRENCY_RISK_BUFFER * 100,
            f"+{cd.CURRENCY_RISK_BUFFER * 100:.0f}% for forex volatility",
        ))

    # Totals
    current_annual = annual_tuition_current + annual_living
    projected_annual = (projected_tuition + projected_living) * abroad_adjustment
    projected_total = projected_annual * duration
    current_total = current_annual * duration

    items.extend([
        CostBreakdownItem(
            "Current annual tuition",
            annual_tuition_current,
            f"{country_label} — {field}",
        ),
        CostBreakdownItem(
            "Current annual living costs",
            annual_living,
            f"{study_location}",
        ),
        CostBreakdownItem(
            f"Projected costs at enrollment ({enrollment_year})",
            projected_annual,
            f"Tuition × {projected_tuition/annual_tuition_current:.1f} + living × {projected_living/annual_living:.1f}" +
            (f" + IDR depreciation" if study_location == "Abroad" else ""),
        ),
        CostBreakdownItem(
            "Total projected cost",
            projected_total,
            f"{duration} years × Rp {projected_annual:,.0f}/yr",
        ),
    ])

    return projected_total, CostBreakdown(
        current_cost=current_total,
        projected_cost=projected_total,
        years_to_goal=years_until_enrollment,
        inflation_rate=inflation_rate,
        items=items,
    )


# ══════════════════════════════════════════════════════════════
# PROPERTY
# ══════════════════════════════════════════════════════════════

def calculate_property(
    property_type: str,
    city: str,
    area: str,
    size_label: str,
    target_year: int,
    custom_building_sqm: Optional[float] = None,
    custom_total_sqm: Optional[float] = None,
) -> tuple[float, CostBreakdown]:
    """
    Project property cost to target year with property inflation + transaction buffer.
    """
    current_year = cd.get_current_year()
    years_to_purchase = max(target_year - current_year, 0)
    inflation_rate = cd.PROPERTY_INFLATION_RATE

    price_per_sqm = cd.APARTMENT_PRICE_PER_SQM.get(city, cd.APARTMENT_PRICE_PER_SQM["Jakarta Selatan"])

    if property_type == "Apartment":
        building_sqm = cd.APARTMENT_SIZES.get(size_label, 55)
        total_sqm = building_sqm  # no land component
        landedness = 1.0
    elif property_type == "Landed House":
        if size_label == "Custom" and custom_building_sqm and custom_total_sqm:
            building_sqm = custom_building_sqm
            total_sqm = custom_total_sqm
        else:
            config = cd.LANDED_HOUSE_SIZES.get(size_label, cd.LANDED_HOUSE_SIZES["Tipe 45"])
            building_sqm = config["building_sqm"]
            total_sqm = config["total_sqm"]
        landedness = building_sqm / total_sqm if total_sqm else 1.0
    elif property_type == "Land Only":
        sqm = custom_total_sqm or 150
        building_sqm = 0
        total_sqm = sqm
        landedness = 0.0
    else:  # Shophouse
        building_sqm = custom_building_sqm or 80
        total_sqm = custom_total_sqm or 100
        landedness = building_sqm / total_sqm if total_sqm else 1.0

    # Current base cost
    if landedness >= 1.0:
        # Pure building (apartment / land only)
        base_cost = building_sqm * price_per_sqm
    else:
        # Landed house: building_sqm * price * premium + land_sqm * price
        land_sqm = total_sqm - building_sqm
        building_cost = building_sqm * price_per_sqm * cd.LANDED_HOUSE_PREMIUM
        land_cost = land_sqm * price_per_sqm
        base_cost = building_cost + land_cost

    # Project to target year
    projected_base = _project(base_cost, inflation_rate, years_to_purchase)
    transaction_cost = projected_base * (cd.PROPERTY_BUFFER - 1)
    projected_total = projected_base + transaction_cost

    items = [
        CostBreakdownItem(
            "Current price per sqm",
            price_per_sqm,
            f"{city}",
        ),
        CostBreakdownItem(
            "Property type",
            0,
            f"{property_type}, {size_label}" +
            (f" ({building_sqm:.0f} sqm building + {total_sqm - building_sqm:.0f} sqm land)"
             if landedness < 1.0 else f" ({building_sqm:.0f} sqm)"),
        ),
        CostBreakdownItem(
            "Current estimated price",
            base_cost,
            "Today's price (excludes transaction costs)",
        ),
        CostBreakdownItem(
            "Annual property inflation",
            inflation_rate * 100,
            f"{inflation_rate * 100:.0f}% per year",
        ),
        CostBreakdownItem(
            "Years to purchase",
            years_to_purchase,
            f"Target: {target_year}",
        ),
        CostBreakdownItem(
            "Projected price at target year",
            projected_base,
            f"{base_cost:,.0f} × {(1 + inflation_rate) ** years_to_purchase:.2f}",
        ),
        CostBreakdownItem(
            "Transaction costs",
            transaction_cost,
            f"+{(cd.PROPERTY_BUFFER - 1) * 100:.0f}% (PPHTB, notary, agent)",
        ),
        CostBreakdownItem(
            "Total projected cost",
            projected_total,
            f"Includes purchase price + transaction buffer",
        ),
    ]

    return projected_total, CostBreakdown(
        current_cost=base_cost,
        projected_cost=projected_total,
        years_to_goal=years_to_purchase,
        inflation_rate=inflation_rate,
        items=items,
    )


# ══════════════════════════════════════════════════════════════
# RETIREMENT
# ══════════════════════════════════════════════════════════════

def calculate_retirement(
    current_age: int,
    retirement_age: int,
    city: str,
    lifestyle: str,
    life_expectancy: int,
    custom_monthly: Optional[float] = None,
) -> tuple[float, CostBreakdown]:
    """
    Project total retirement fund needed: monthly spend × 12 × years in retirement,
    all inflated to retirement year.
    """
    years_to_retirement = max(retirement_age - current_age, 0)
    years_in_retirement = max(life_expectancy - retirement_age, 0)

    if "Custom" in lifestyle and custom_monthly is not None:
        monthly_current = custom_monthly
    elif "Basic" in lifestyle:
        monthly_current = 6_500_000  # midpoint Rp 5-8M
    elif "Premium" in lifestyle:
        monthly_current = 22_500_000  # midpoint Rp 15-30M
    else:
        monthly_current = 11_500_000  # midpoint Rp 8-15M

    inflation_rate = cd.RETIREMENT_LIVING_INFLATION

    # Project monthly cost at retirement
    monthly_at_retirement = _project(monthly_current, inflation_rate, years_to_retirement)
    annual_at_retirement = monthly_at_retirement * 12
    total_needed = annual_at_retirement * years_in_retirement

    current_total = monthly_current * 12 * years_in_retirement

    lifestyle_label = lifestyle.replace("Custom — enter my own amount", "Custom lifestyle")
    items = [
        CostBreakdownItem(
            "Current estimated monthly spend",
            monthly_current,
            f"{city} — {lifestyle_label}",
        ),
        CostBreakdownItem(
            "Years to retirement",
            years_to_retirement,
            f"Age {current_age} → {retirement_age}",
        ),
        CostBreakdownItem(
            "Years in retirement",
            years_in_retirement,
            f"Age {retirement_age} → {life_expectancy}",
        ),
        CostBreakdownItem(
            "Annual inflation in retirement",
            inflation_rate * 100,
            f"{inflation_rate * 100:.0f}% per year",
        ),
        CostBreakdownItem(
            "Monthly cost at retirement",
            monthly_at_retirement,
            f"Year {cd.get_current_year() + years_to_retirement}",
        ),
        CostBreakdownItem(
            "Annual cost at retirement",
            annual_at_retirement,
            f"12 × monthly",
        ),
        CostBreakdownItem(
            "Total projected retirement fund",
            total_needed,
            f"{annual_at_retirement:,.0f}/yr × {years_in_retirement} years",
        ),
    ]

    return total_needed, CostBreakdown(
        current_cost=current_total,
        projected_cost=total_needed,
        years_to_goal=years_to_retirement,
        inflation_rate=inflation_rate,
        items=items,
    )


# ══════════════════════════════════════════════════════════════
# EMERGENCY FUND
# ══════════════════════════════════════════════════════════════

def calculate_emergency_fund(
    monthly_salary: float,
    monthly_expenses: float,
    coverage_months: int,
) -> tuple[float, CostBreakdown]:
    """
    Emergency fund = monthly expenses × coverage months.
    No inflation — near-term goal, typically < 2 years to accumulate.
    """
    total = monthly_expenses * coverage_months

    items = [
        CostBreakdownItem(
            "Monthly take-home salary",
            monthly_salary,
            "Total monthly income after tax",
        ),
        CostBreakdownItem(
            "Monthly fixed expenses",
            monthly_expenses,
            "Rent, utilities, food, transport",
        ),
        CostBreakdownItem(
            "Coverage duration",
            coverage_months,
            "Months of expenses covered",
        ),
        CostBreakdownItem(
            "Total emergency fund needed",
            total,
            "No inflation applied — near-term goal",
        ),
    ]

    return total, CostBreakdown(
        current_cost=total,
        projected_cost=total,
        years_to_goal=1,  # assume ~1 year to build
        inflation_rate=0.0,
        items=items,
    )


# ══════════════════════════════════════════════════════════════
# WEDDING
# ══════════════════════════════════════════════════════════════

def calculate_wedding(
    scale: str,
    city: str,
    target_year: int,
    venue: str,
    catering: str,
    entertainment: str,
) -> tuple[float, CostBreakdown]:
    """
    Project wedding cost to target year with inflation.
    Base × scale × venue × catering × entertainment multipliers.
    """
    current_year = cd.get_current_year()
    years_to_wedding = max(target_year - current_year, 0)
    inflation_rate = cd.WEDDING_INFLATION_RATE

    base = cd.WEDDING_BASE_COST.get(city, cd.WEDDING_BASE_COST["Jakarta Selatan"])
    scale_mult = cd.WEDDING_SCALE_MULTIPLIER.get(scale, 1.0)
    venue_mult = cd.WEDDING_VENUE_MULTIPLIER.get(venue, 1.0)
    catering_mult = cd.WEDDING_CATERING_MULTIPLIER.get(catering, 1.0)
    entertainment_mult = cd.WEDDING_ENTERTAINMENT_MULTIPLIER.get(entertainment, 1.0)

    current_total = base * scale_mult * venue_mult * catering_mult * entertainment_mult
    projected_total = _project(current_total, inflation_rate, years_to_wedding)

    items = [
        CostBreakdownItem("Base cost", base, f"{city} at today's prices"),
        CostBreakdownItem("Scale multiplier", scale_mult, f"{scale}"),
        CostBreakdownItem("Venue multiplier", venue_mult, f"{venue}"),
        CostBreakdownItem("Catering multiplier", catering_mult, f"{catering}"),
        CostBreakdownItem("Entertainment multiplier", entertainment_mult, f"{entertainment}"),
        CostBreakdownItem(
            "Current estimated cost",
            current_total,
            "Today's price",
        ),
        CostBreakdownItem(
            "Annual inflation",
            inflation_rate * 100,
            f"{inflation_rate * 100:.0f}% per year",
        ),
        CostBreakdownItem(
            "Years to wedding",
            years_to_wedding,
            f"Target: {target_year}",
        ),
        CostBreakdownItem(
            "Total projected cost",
            projected_total,
            f"{current_total:,.0f} × {(1 + inflation_rate) ** years_to_wedding:.2f}",
        ),
    ]

    return projected_total, CostBreakdown(
        current_cost=current_total,
        projected_cost=projected_total,
        years_to_goal=years_to_wedding,
        inflation_rate=inflation_rate,
        items=items,
    )


# ══════════════════════════════════════════════════════════════
# CUSTOM GOAL
# ══════════════════════════════════════════════════════════════

def calculate_custom(
    goal_name: str,
    target_amount: Optional[float],
    target_year: int,
) -> tuple[float, CostBreakdown]:
    """Custom goal — user-supplied amount, projected to target year at 6%."""
    if target_amount is None or target_amount <= 0:
        return 0.0, CostBreakdown(0.0, 0.0, 0, 0.0)

    current_year = cd.get_current_year()
    years = max(target_year - current_year, 0)
    inflation_rate = 0.06  # generic asset inflation assumption

    projected = _project(target_amount, inflation_rate, years)

    items = [
        CostBreakdownItem("Target amount (today)", target_amount, goal_name),
        CostBreakdownItem("Years to goal", years, f"Target: {target_year}"),
        CostBreakdownItem(
            "Annual inflation",
            inflation_rate * 100,
            "Generic 6% assumption",
        ),
        CostBreakdownItem(
            "Projected total needed",
            projected,
            f"Amount in {target_year} rupees",
        ),
    ]

    return projected, CostBreakdown(
        current_cost=target_amount,
        projected_cost=projected,
        years_to_goal=years,
        inflation_rate=inflation_rate,
        items=items,
    )


# ══════════════════════════════════════════════════════════════
# GOAL BUILDER CLASS
# ══════════════════════════════════════════════════════════════

class GoalBuilder:
    """Orchestrates the multi-step goal building process."""

    CITIES = list(cd.APARTMENT_PRICE_PER_SQM.keys())

    @staticmethod
    def get_steps(goal_type: str) -> list[dict]:
        return STEPS_BY_GOAL.get(goal_type, [])

    @staticmethod
    def get_current_year() -> int:
        return cd.get_current_year()

    def build_goal(self, goal_type: str, step_answers: dict) -> GoalProfile:
        """
        Build a complete GoalProfile from all step answers.
        step_answers keys vary by goal_type — see calculate_* functions above.
        """
        gtype = goal_type

        if gtype == "Education":
            cost, breakdown = calculate_education(
                education_level=step_answers.get("education_level", "Primary"),
                school_type=step_answers.get("school_type", "Local Private"),
                child_age=int(step_answers.get("child_age", 6)),
                city=step_answers.get("city", "Jakarta Selatan"),
            )
            level = step_answers.get("education_level", "Primary")
            stype = step_answers.get("school_type", "Local Private")
            city = step_answers.get("city", "Jakarta Selatan")
            description = f"{stype} {level} school in {city}"

        elif gtype == "Higher Education":
            cost, breakdown = calculate_higher_education(
                degree_level=step_answers.get("degree_level", "Bachelor"),
                study_location=step_answers.get("study_location", "In Indonesia"),
                country=step_answers.get("country", "Singapore"),
                field=step_answers.get("field", "Business / Economics"),
                years_until_enrollment=int(step_answers.get("years_until_enrollment", 4)),
            )
            deg = step_answers.get("degree_level", "Bachelor")
            loc = step_answers.get("study_location", "In Indonesia")
            country = step_answers.get("country", "Singapore")
            description = f"{deg} — {country if loc == 'Abroad' else 'Indonesia'}"

        elif gtype == "Property":
            custom_b = step_answers.get("custom_building_sqm")
            custom_t = step_answers.get("custom_total_sqm")
            cost, breakdown = calculate_property(
                property_type=step_answers.get("property_type", "Apartment"),
                city=step_answers.get("city", "Jakarta Selatan"),
                area=step_answers.get("area", ""),
                size_label=step_answers.get("size", "2BR"),
                target_year=int(step_answers.get("target_year", cd.get_current_year() + 10)),
                custom_building_sqm=float(custom_b) if custom_b else None,
                custom_total_sqm=float(custom_t) if custom_t else None,
            )
            ptype = step_answers.get("property_type", "Apartment")
            city = step_answers.get("city", "Jakarta Selatan")
            size = step_answers.get("size", "2BR")
            description = f"{size} {ptype} in {city}"

        elif gtype == "Retirement":
            life_exp = step_answers.get("life_expectancy", 80)
            if life_exp == "Custom — enter my own assumption":
                life_exp = int(step_answers.get("custom_life_expectancy", 80))
            cost, breakdown = calculate_retirement(
                current_age=int(step_answers.get("current_age", 25)),
                retirement_age=int(step_answers.get("retirement_age", 55)),
                city=step_answers.get("city", "Jakarta Selatan"),
                lifestyle=step_answers.get("lifestyle", "Comfortable (Rp 8-15M/month)"),
                life_expectancy=int(life_exp) if isinstance(life_exp, int) else 80,
                custom_monthly=float(step_answers.get("custom_monthly")) if "Custom" in step_answers.get("lifestyle", "") else None,
            )
            ret_age = step_answers.get("retirement_age", 55)
            city = step_answers.get("city", "Jakarta Selatan")
            description = f"Retirement at age {ret_age} in {city}"

        elif gtype == "Emergency Fund":
            coverage_str = step_answers.get("coverage", "6 months")
            coverage_months = int(coverage_str.split()[0]) if coverage_str[0].isdigit() else 6
            cost, breakdown = calculate_emergency_fund(
                monthly_salary=float(step_answers.get("monthly_salary", 0)),
                monthly_expenses=float(step_answers.get("monthly_expenses", 0)),
                coverage_months=coverage_months,
            )
            description = f"Emergency fund — {coverage_str} coverage"

        elif gtype == "Wedding":
            cost, breakdown = calculate_wedding(
                scale=step_answers.get("scale", "Standard (50-200 guests)"),
                city=step_answers.get("city", "Jakarta Selatan"),
                target_year=int(step_answers.get("target_year", cd.get_current_year() + 3)),
                venue=step_answers.get("venue", "Garden / Outdoor Venue"),
                catering=step_answers.get("catering", "Standard"),
                entertainment=step_answers.get("entertainment", "Basic (MC + Sound)"),
            )
            scale = step_answers.get("scale", "Standard (50-200 guests)")
            city = step_answers.get("city", "Jakarta Selatan")
            year = step_answers.get("target_year", cd.get_current_year() + 3)
            description = f"{scale} wedding in {city} ({year})"

        elif gtype == "Custom":
            amount = step_answers.get("target_amount")
            year = step_answers.get("target_year", cd.get_current_year() + 5)
            cost, breakdown = calculate_custom(
                goal_name=step_answers.get("goal_name", "Custom goal"),
                target_amount=float(amount) if amount else None,
                target_year=int(year),
            )
            description = step_answers.get("goal_name", "Custom goal")

        else:
            cost, breakdown = 0.0, CostBreakdown(0.0, 0.0, 0, 0.0)
            description = gtype

        timeline_years = breakdown.years_to_goal if breakdown else 0

        return GoalProfile(
            goal_type=gtype,
            city=step_answers.get("city", ""),
            estimated_cost=cost,
            timeline_years=timeline_years,
            description=description,
            breakdown=breakdown,
        )
