"""
Risk Profiler — 12-question questionnaire, Indonesian OJK-standard profiles.
Profiles: Konservatif, Moderat, Agresif.
Maps to asset allocation ranges for Indonesian investment instruments.
"""

from dataclasses import dataclass, field
from typing import Optional

RISK_QUESTIONS = [
    {
        "id": "q1_horizon",
        "question": "When do you need to achieve this goal?",
        "dimension": "investment_horizon",
        "options": [
            {"text": "Less than 3 years", "score": 1},
            {"text": "3 – 5 years", "score": 2},
            {"text": "5 – 10 years", "score": 3},
            {"text": "10 – 20 years", "score": 4},
            {"text": "More than 20 years", "score": 5},
        ],
    },
    {
        "id": "q2_loss_reaction",
        "question": "Your portfolio drops 20% in a month. What do you do?",
        "dimension": "loss_tolerance",
        "options": [
            {"text": "Sell everything immediately", "score": 1},
            {"text": "Sell some, wait and see", "score": 2},
            {"text": "Hold and monitor closely", "score": 3},
            {"text": "Buy more at the lower price", "score": 4},
            {"text": "Buy significantly more", "score": 5},
        ],
    },
    {
        "id": "q3_income_stability",
        "question": "How stable is your primary income?",
        "dimension": "income_stability",
        "options": [
            {"text": "Very unstable / freelance / contract", "score": 1},
            {"text": "Somewhat stable, variable bonus", "score": 2},
            {"text": "Stable base, predictable bonus", "score": 3},
            {"text": "Very stable, multiple income streams", "score": 4},
            {"text": "Government / tenured / pension-backed", "score": 5},
        ],
    },
    {
        "id": "q4_dependents",
        "question": "How many dependents rely on your income?",
        "dimension": "financial_obligations",
        "options": [
            {"text": "None — I support only myself", "score": 5},
            {"text": "1 person (spouse / parent)", "score": 4},
            {"text": "2 people", "score": 3},
            {"text": "3 people", "score": 2},
            {"text": "4 or more people", "score": 1},
        ],
    },
    {
        "id": "q5_debt",
        "question": "What is your total monthly debt obligation vs. income?",
        "dimension": "debt_burden",
        "options": [
            {"text": "More than 50% of take-home", "score": 1},
            {"text": "30 – 50% of take-home", "score": 2},
            {"text": "15 – 30% of take-home", "score": 3},
            {"text": "Under 15% of take-home", "score": 4},
            {"text": "No debt at all", "score": 5},
        ],
    },
    {
        "id": "q6_investment_exp",
        "question": "How many years of investment experience do you have?",
        "dimension": "investment_experience",
        "options": [
            {"text": "None — this is my first time", "score": 1},
            {"text": "Less than 1 year", "score": 2},
            {"text": "1 – 3 years", "score": 3},
            {"text": "3 – 7 years", "score": 4},
            {"text": "More than 7 years", "score": 5},
        ],
    },
    {
        "id": "q7_volatility_comfort",
        "question": "Which statement best describes your view of market volatility?",
        "dimension": "volatility_tolerance",
        "options": [
            {"text": "I want guaranteed returns only — no volatility acceptable", "score": 1},
            {"text": "Small fluctuations are OK, but I prefer stability", "score": 2},
            {"text": "Moderate ups and downs are part of investing", "score": 3},
            {"text": "I am comfortable with significant volatility for higher returns", "score": 4},
            {"text": "I actively look for high-volatility assets for maximum growth", "score": 5},
        ],
    },
    {
        "id": "q8_liquidity",
        "question": "How important is it that your investment can be withdrawn quickly?",
        "dimension": "liquidity_need",
        "options": [
            {"text": "I may need to withdraw within 1 month", "score": 1},
            {"text": "I may need to withdraw within 6 months", "score": 2},
            {"text": "I may need to withdraw within 1–2 years", "score": 3},
            {"text": "I will not need to withdraw for 3–5 years", "score": 4},
            {"text": "I can lock in this investment for 5+ years", "score": 5},
        ],
    },
    {
        "id": "q9_emergency_fund",
        "question": "Do you have an emergency fund covering at least 6 months of expenses?",
        "dimension": "emergency_fund_status",
        "options": [
            {"text": "No emergency fund at all", "score": 1},
            {"text": "Yes, but less than 3 months", "score": 2},
            {"text": "3 – 6 months covered", "score": 3},
            {"text": "6 months or more covered", "score": 4},
            {"text": "Fully funded plus additional liquidity buffer", "score": 5},
        ],
    },
    {
        "id": "q10_goal_urgency",
        "question": "How would you describe the urgency of this goal?",
        "dimension": "goal_urgency",
        "options": [
            {"text": "Must achieve within 1–2 years — non-negotiable", "score": 1},
            {"text": "Important, 2–5 year window", "score": 2},
            {"text": "Moderate urgency, 5–10 years", "score": 3},
            {"text": "Long-term, 10–20 years", "score": 4},
            {"text": "Very long-term / flexible timeline", "score": 5},
        ],
    },
    {
        "id": "q11_knowledge",
        "question": "How well do you understand investment products like Reksa Dana, bonds, and REITs?",
        "dimension": "financial_knowledge",
        "options": [
            {"text": "I don't know what these are", "score": 1},
            {"text": "I've heard of them but never invested", "score": 2},
            {"text": "I understand the basics", "score": 3},
            {"text": "I understand and have invested in some", "score": 4},
            {"text": "I am very knowledgeable and actively invest", "score": 5},
        ],
    },
    {
        "id": "q12_recurring_invest",
        "question": "Can you commit to investing regularly every month without fail?",
        "dimension": "discipline",
        "options": [
            {"text": "No — my income is too irregular", "score": 1},
            {"text": "Probably not — some months will be missed", "score": 2},
            {"text": "Yes, most months I can invest", "score": 3},
            {"text": "Yes, consistently every month", "score": 4},
            {"text": "Yes — I have a standing instruction set up", "score": 5},
        ],
    },
]


@dataclass
class RiskProfile:
    profile: str  # "Konservatif" | "Moderat" | "Agresif"
    score: int
    max_score: int
    percentage: float
    allocation: dict
    description: str

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "allocation": self.allocation,
            "description": self.description,
        }


PROFILE_BOUNDARIES = {
    "Konservatif": (12, 30),
    "Moderat": (31, 45),
    "Agresif": (46, 60),
}

ALLOCATION_RANGES = {
    "Konservatif": {
        "deposito": (25, 35),
        "obligasi_ori_sbr": (35, 45),
        "reksa_dana_pasar_uang": (15, 25),
        "reksa_dana_pendapatan_tetap": (10, 20),
        "reksa_dana_equity": (0, 5),
        "reits": (0, 5),
    },
    "Moderat": {
        "deposito": (10, 20),
        "obligasi_ori_sbr": (20, 30),
        "reksa_dana_pasar_uang": (10, 15),
        "reksa_dana_pendapatan_tetap": (20, 30),
        "reksa_dana_equity": (15, 25),
        "reits": (5, 10),
    },
    "Agresif": {
        "deposito": (0, 5),
        "obligasi_ori_sbr": (5, 10),
        "reksa_dana_pasar_uang": (0, 5),
        "reksa_dana_pendapatan_tetap": (5, 10),
        "reksa_dana_equity": (50, 65),
        "reits": (15, 25),
    },
}

PROFILE_DESCRIPTIONS = {
    "Konservatif": "You prefer stability and capital preservation. Your portfolio prioritises low-risk, liquid instruments like deposito and government bonds (ORI/SBR). Growth potential is modest but your money is well-protected.",
    "Moderat": "You balance growth and safety. You invest primarily in bonds and mixed Reksa Dana, with a meaningful equity and REIT component for long-term growth. You can tolerate some volatility.",
    "Agresif": "You prioritise long-term growth and can withstand significant market swings. Your portfolio is heavily weighted toward equity Reksa Dana and REITs. Short-term losses don't动摇 your conviction.",
}


def score_to_profile(score: int, max_score: int = 60) -> RiskProfile:
    pct = score / max_score
    if score <= 30:
        profile = "Konservatif"
        mid_alloc = {k: (v[0] + v[1]) / 2 for k, v in ALLOCATION_RANGES["Konservatif"].items()}
    elif score <= 45:
        profile = "Moderat"
        mid_alloc = {k: (v[0] + v[1]) / 2 for k, v in ALLOCATION_RANGES["Moderat"].items()}
    else:
        profile = "Agresif"
        mid_alloc = {k: (v[0] + v[1]) / 2 for k, v in ALLOCATION_RANGES["Agresif"].items()}

    rounded_alloc = {k: round(v / 5) * 5 for k, v in mid_alloc.items()}
    total = sum(rounded_alloc.values())
    if total != 100:
        diff = 100 - total
        rounded_alloc["reksa_dana_equity"] += diff

    return RiskProfile(
        profile=profile,
        score=score,
        max_score=max_score,
        percentage=round(pct * 100, 1),
        allocation=rounded_alloc,
        description=PROFILE_DESCRIPTIONS[profile],
    )


class RiskProfiler:
    def __init__(self):
        self._responses: dict[str, int] = {}

    def submit_answer(self, question_id: str, score: int) -> None:
        self._responses[question_id] = score

    def get_score(self) -> int:
        return sum(self._responses.values())

    def get_profile(self) -> Optional[RiskProfile]:
        if len(self._responses) < 12:
            return None
        return score_to_profile(self.get_score())

    def is_complete(self) -> bool:
        return len(self._responses) == 12

    def reset(self) -> None:
        self._responses = {}

    @property
    def answered_ids(self) -> list[str]:
        return list(self._responses.keys())


if __name__ == "__main__":
    rp = RiskProfiler()
    # Simulate a Moderat profile
    scores = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    for q, s in zip(RISK_QUESTIONS, scores):
        rp.submit_answer(q["id"], s)

    profile = rp.get_profile()
    print(f"Profile: {profile.profile}")
    print(f"Score: {profile.score}/{profile.max_score} ({profile.percentage}%)")
    print(f"Allocation:")
    for instrument, pct in profile.allocation.items():
        print(f"  {instrument:30s}  {pct:5d}%")
    print(f"\nDescription: {profile.description}")
