"""
Vestara — Goal-First Investment Platform
Streamlit UI — wraps Goal Builder, Feasibility Engine, and Portfolio Optimizer.
Dark mode fintech redesign.
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os

from vestara.src.engine.goal_builder import GoalBuilder
from vestara.src.engine.risk_profiler import RiskProfiler, RISK_QUESTIONS
from vestara.src.portfolio.optimizer import build_portfolio, INSTRUMENT_LABELS as PORT_LABELS
from vestara.data.cost_data import LIVING_COST_MONTHLY, GOAL_TYPES, LANDED_HOUSE_TYPES, SALARY_DISTRIBUTION

# Page config
st.set_page_config(
    page_title="Vestara — Plan Your Life, Then Your Investment",
    page_icon="🏠",
    layout="wide",
)

# ── Global Dark Mode CSS ─────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

.block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
.main .block-container { padding-left: 2rem !important; padding-right: 2rem !important; }

[data-testid="stApp"] { background-color: #0A0A0F !important; }
[data-testid="stSidebar"] { background-color: #0D0D14 !important; border-right: 1px solid #1E1E2E !important; }
.st-ca { background-color: #13131A !important; }

h1, h2, h3, h4, h5, h6 { color: #F8FAFC !important; font-weight: 700 !important; }
p, span, div { color: #94A3B8 !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0A0A0F; }
::-webkit-scrollbar-thumb { background: #1E1E2E; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #7C3AED; }

.vestara-card {
    background-color: #13131A;
    border: 1px solid #1E1E2E;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}

.vestara-metric {
    text-align: center;
    padding: 1rem;
}
.vestara-metric .metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #7C3AED !important;
    font-family: 'Inter', monospace;
}
.vestara-metric .metric-label {
    font-size: 0.85rem;
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.verdict-green { border: 2px solid #10B981; box-shadow: 0 0 30px rgba(16,185,129,0.15); }
.verdict-yellow { border: 2px solid #F59E0B; box-shadow: 0 0 30px rgba(245,158,11,0.15); }
.verdict-red { border: 2px solid #EF4444; box-shadow: 0 0 30px rgba(239,68,68,0.15); }

.st-dg > div > button:first-child {
    background: linear-gradient(135deg, #7C3AED, #6D28D9) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
}
.st-dg > div > button:first-child:hover {
    background: linear-gradient(135deg, #8B5CF6, #7C3AED) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextArea"] textarea {
    background-color: #13131A !important;
    border: 1px solid #1E1E2E !important;
    color: #F8FAFC !important;
    border-radius: 10px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stSelectbox"] > div > div:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
}

[data-testid="stRadio"] label { color: #F8FAFC !important; }
[data-testid="stRadio"] label:hover { color: #7C3AED !important; }

.st-abq .css-1aehpvj { background-color: #7C3AED !important; }
.st-abq .css-1632mt { background-color: #1E1E2E !important; }

.st-cj .css-1v0mbg9 { background-color: #7C3AED !important; }

[data-testid="stSidebarNav"] span { color: #F8FAFC !important; }
[data-testid="stSidebarNav"] span:hover { color: #7C3AED !important; }

.st-em { border-radius: 12px !important; }

[data-testid="stDataFrame"] { background-color: #13131A !important; }

details { background-color: #13131A !important; border: 1px solid #1E1E2E !important; border-radius: 12px !important; }
summary { color: #F8FAFC !important; }

.hero-title {
    position: relative;
    display: inline-block;
}
.hero-title::after {
    content: '';
    position: absolute;
    bottom: -4px;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #7C3AED, #06B6D4);
    border-radius: 2px;
}

.goal-card {
    background: #13131A;
    border: 2px solid #1E1E2E;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
}
.goal-card:hover { border-color: #7C3AED; transform: translateY(-2px); }
.goal-card.selected { border-color: #7C3AED; box-shadow: 0 0 20px rgba(124,58,237,0.3); }
.goal-card-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.goal-card-title { font-weight: 600; color: #F8FAFC; font-size: 1rem; }
.goal-card-desc { font-size: 0.8rem; color: #94A3B8; margin-top: 0.25rem; }

.cost-display {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7C3AED, #06B6D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Inter', monospace;
}

.risk-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.risk-high { background: rgba(239,68,68,0.15); color: #EF4444; }
.risk-medium { background: rgba(245,158,11,0.15); color: #F59E0B; }
.risk-low { background: rgba(16,185,129,0.15); color: #10B981; }

.summary-card {
    background: #13131A;
    border: 1px solid #1E1E2E;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

element.style { margin-bottom: 0rem; }

.verdict-text {
    font-size: 1.75rem;
    font-weight: 800;
    text-align: center;
    padding: 1.5rem;
}

.scenario-card {
    background: #13131A;
    border: 1px solid #1E1E2E;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.75rem;
}
.scenario-lever {
    display: inline-block;
    background: linear-gradient(135deg, #7C3AED, #06B6D4);
    color: white;
    font-weight: 700;
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    margin-right: 0.5rem;
}

.question-card {
    background: #13131A;
    border: 1px solid #1E1E2E;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.question-number {
    display: inline-block;
    background: linear-gradient(135deg, #7C3AED, #6D28D9);
    color: white;
    font-weight: 700;
    font-size: 0.75rem;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    margin-right: 0.75rem;
}

.score-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    font-size: 2rem;
    font-weight: 800;
}
.score-circle.green { background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.1)); border: 3px solid #10B981; color: #10B981; }
.score-circle.yellow { background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.1)); border: 3px solid #F59E0B; color: #F59E0B; }
.score-circle.red { background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.1)); border: 3px solid #EF4444; color: #EF4444; }

.profile-card {
    background: #13131A;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
}
.profile-card.konservatif { border: 2px solid #06B6D4; box-shadow: 0 0 30px rgba(6,182,212,0.15); }
.profile-card.moderat { border: 2px solid #7C3AED; box-shadow: 0 0 30px rgba(124,58,237,0.15); }
.profile-card.agresif { border: 2px solid #F59E0B; box-shadow: 0 0 30px rgba(245,158,11,0.15); }

.allocation-table {
    width: 100%;
    border-collapse: collapse;
}
.allocation-table th {
    color: #F8FAFC;
    font-weight: 600;
    text-align: left;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #1E1E2E;
}
.allocation-table td {
    color: #94A3B8;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #1E1E2E;
}
.allocation-table tr:hover td { background-color: rgba(124,58,237,0.05); }

.metric-col {
    background: #13131A;
    border: 1px solid #1E1E2E;
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
}
.metric-col .metric-val {
    font-size: 1.5rem;
    font-weight: 700;
    color: #7C3AED;
    font-family: 'Inter', monospace;
}
.metric-col .metric-lbl {
    font-size: 0.75rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}

.health-score {
    font-size: 4rem;
    font-weight: 800;
    text-align: center;
}
.health-score.excellent { color: #10B981; }
.health-score.good { color: #06B6D4; }
.health-score.needs_work { color: #F59E0B; }

.disclaimer-banner {
    background: rgba(245,158,11,0.1);
    border: 1px solid #F59E0B;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
}

.goal-progress-card {
    background: #13131A;
    border: 1px solid #1E1E2E;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.goal-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 0.5rem;
}
.goal-meta {
    font-size: 0.8rem;
    color: #94A3B8;
}

.progress-bar-bg {
    background: #1E1E2E;
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin-top: 0.75rem;
}
.progress-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.3s ease;
}
.progress-bar-fill.green { background: linear-gradient(90deg, #10B981, #059669); }
.progress-bar-fill.yellow { background: linear-gradient(90deg, #F59E0B, #D97706); }
.progress-bar-fill.red { background: linear-gradient(90deg, #EF4444, #DC2626); }

.verdict-pill {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
}
.verdict-pill.green { background: rgba(16,185,129,0.15); color: #10B981; }
.verdict-pill.yellow { background: rgba(245,158,11,0.15); color: #F59E0B; }
.verdict-pill.red { background: rgba(239,68,68,0.15); color: #EF4444; }

.sidebar-brand {
    font-size: 1.5rem;
    font-weight: 800;
    color: #F8FAFC !important;
    margin-bottom: 0.25rem;
}
.sidebar-tagline {
    font-size: 0.8rem;
    color: #94A3B8 !important;
    margin-bottom: 1.5rem;
}

.salary-bracket {
    font-size: 0.8rem;
    color: #94A3B8;
    margin-top: 0.25rem;
}
.salary-bracket .bracket-label {
    color: #7C3AED;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ── Model loader ────────────────────────────────────────────────────────────────

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../../models")
SYNTHETIC_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/synthetic_training_data.csv")

# Instrument risk labels (English)
INSTRUMENT_RISK_LABELS = {
    "reksa_dana_equity":           "High Risk — value may drop significantly",
    "reksa_dana_pendapatan_tetap": "Medium Risk — moderate fluctuation",
    "reksa_dana_pasar_uang":       "Very Low Risk — LPS guaranteed up to Rp 2B",
    "reits":                       "Medium-High Risk — affected by property market",
    "obligasi_ori_sbr":            "Low Risk — government guaranteed, fixed return",
    "deposito":                    "Very Low Risk — LPS guaranteed up to Rp 2B",
}


@st.cache_resource
def load_classifier():
    path = os.path.join(MODELS_DIR, "feasibility_classifier.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


def compute_feasibility(monthly_salary: float, city: str, goal_cost: float, timeline_years: int, income_growth_rate: float):
    """Compute feasibility verdict using rule-based threshold (classifier unavailable in this env)."""
    monthly_living = LIVING_COST_MONTHLY.get(city, 6_000_000)
    monthly_required = goal_cost / (timeline_years * 12)
    disposable = max(monthly_salary - monthly_living, 1)
    ratio = min(monthly_required / disposable, 2.0)

    if ratio < 0.30:
        verdict = "green"
    elif ratio < 0.50:
        verdict = "yellow"
    else:
        verdict = "red"

    return {
        "verdict": verdict,
        "ratio": ratio,
        "monthly_required": monthly_required,
        "monthly_living": monthly_living,
        "disposable": disposable,
        "investment_pct_of_salary": monthly_required / monthly_salary,
    }


# ── Salary formatting helpers ────────────────────────────────────────────────────

def get_salary_bracket(amount: float) -> str:
    """Return career bracket label based on monthly salary."""
    if amount < 8_000_000:
        return "Fresh Graduate"
    elif amount < 25_000_000:
        return "Mid Career"
    else:
        return "Senior Professional"


def format_idr(amount: float) -> str:
    """Format IDR with thousand separators: Rp 2.415.000.000"""
    return f"Rp {amount:,.0f}".replace(",", ".")


def format_salary_input(value: float) -> str:
    """Format salary for display with Rp prefix and dot separators."""
    if value == 0:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


# ── Verdict display helpers ────────────────────────────────────────────────────

def verdict_badge(verdict: str) -> str:
    colors = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
    labels = {"green": "Achievable", "yellow": "Achievable With Conditions", "red": "Not Achievable As Stated"}
    return f"{colors.get(verdict, '⚪')} **{labels.get(verdict, verdict)}**"


def render_verdict(verdict: str, ratio: float, monthly_required: float, monthly_salary: float):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Verdict", verdict.replace("green", "🟢 Achievable").replace("yellow", "🟡 Achievable With Conditions").replace("red", "🔴 Not Achievable As Stated"))
    with col2:
        st.metric("Monthly Investment Needed", f"Rp {monthly_required:,.0f}")
    with col3:
        st.metric("Investment-to-Salary Ratio", f"{ratio:.1%}")


# ── Sidebar navigation ─────────────────────────────────────────────────────────

st.sidebar.markdown('<div class="sidebar-brand">🏠 Vestara</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-tagline">Goal-first investment planning for Indonesia</div>', unsafe_allow_html=True)
page = st.sidebar.radio("Go to", [
    "🏗️ Goal Builder",
    "📊 Feasibility Analysis",
    "📋 Risk Profiler",
    "💼 Portfolio Recommendation",
    "📈 Dashboard",
])


# ── Page 1: Goal Builder ──────────────────────────────────────────────────────

if page == "🏗️ Goal Builder":
    st.markdown('<div class="hero-title" style="font-size:2rem;font-weight:800;color:#F8FAFC;">What\'s your financial goal?</div>', unsafe_allow_html=True)
    st.markdown("#### Tell us about your life goal")
    st.markdown("")

    # Goal type card grid
    goal_types_with_icons = [
        ("🏠", "Property", "Buy a home or land"),
        ("🎓", "Education", "Fund schooling or university"),
        ("🌴", "Retirement", "Build a comfortable retirement fund"),
        ("🎓", "Higher Education", "Study abroad (Master's / PhD)"),
        ("💍", "Wedding", "Plan your wedding"),
        ("🛡️", "Emergency Fund", "Build a safety net"),
        ("✨", "Custom", "Set any custom financial goal"),
    ]

    if "selected_goal" not in st.session_state:
        st.session_state["selected_goal"] = None

    st.markdown("##### Choose your goal type")
    row1 = goal_types_with_icons[:4]
    cols = st.columns(4)
    for idx, (icon, name, desc) in enumerate(row1):
        with cols[idx]:
            selected = st.session_state["selected_goal"] == name
            card_class = "goal-card selected" if selected else "goal-card"
            st.markdown(f"""
            <div class="{card_class}" onclick="
                const els = document.querySelectorAll('.goal-card');
                els.forEach(e => e.classList.remove('selected'));
                this.classList.add('selected');
            ">
                <div class="goal-card-icon">{icon}</div>
                <div class="goal-card-title">{name}</div>
                <div class="goal-card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    row2 = goal_types_with_icons[4:]
    cols2 = st.columns(3)
    for idx, (icon, name, desc) in enumerate(row2):
        with cols2[idx]:
            selected = st.session_state["selected_goal"] == name
            card_class = "goal-card selected" if selected else "goal-card"
            st.markdown(f"""
            <div class="{card_class}" onclick="
                const els = document.querySelectorAll('.goal-card');
                els.forEach(e => e.classList.remove('selected'));
                this.classList.add('selected');
            ">
                <div class="goal-card-icon">{icon}</div>
                <div class="goal-card-title">{name}</div>
                <div class="goal-card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    goal_type = st.selectbox("Goal Type", GOAL_TYPES, index=None, placeholder="Select a goal type above")
    city = st.selectbox("City", list(LIVING_COST_MONTHLY.keys()))

    st.markdown("")
    st.markdown("---")
    st.markdown("#### Goal Details")

    answers = {}

    if goal_type == "Property":
        property_options = list(LANDED_HOUSE_TYPES.keys())
        selected_property = st.selectbox("Property Type", property_options, index=0)
        answers["property_size"] = selected_property
        location_detail = st.text_input("Neighbourhood (optional)", placeholder="e.g. Kemang, Senayan, Menteng")
        answers["location_detail"] = location_detail

    elif goal_type == "Education":
        answers["education_level"] = st.selectbox("Education Level", [
            "TK / SD (Elementary)", "SMP (Junior High)", "SMA / SMK (Senior High)"
        ])
        answers["school_tier"] = st.selectbox("School Type", [
            "Local Private (Rp 0-15M/yr)", "Mid-tier Private (Rp 15-30M/yr)",
            "Premium Private (Rp 30-60M/yr)", "International School (Rp 60-150M/yr)"
        ])

    elif goal_type == "Retirement":
        answers["current_age"] = st.number_input("Your Current Age", min_value=18, max_value=65, value=25)
        answers["retirement_age"] = st.number_input("Target Retirement Age", min_value=45, max_value=75, value=55)
        lifestyle_options = [
            "Basic (Rp 5-8M/month estimated spend)",
            "Comfortable (Rp 8-15M/month)",
            "Premium (Rp 15-30M/month)",
            "Custom — enter my own monthly target",
        ]
        selected_lifestyle = st.selectbox("Desired Lifestyle", lifestyle_options)
        answers["retirement"] = selected_lifestyle
        if "Custom" in selected_lifestyle:
            custom_monthly = st.number_input(
                "Your Target Monthly Retirement Spend (IDR)",
                min_value=1_000_000,
                max_value=500_000_000,
                value=10_000_000,
                step=500_000,
                help="Enter how much you plan to spend per month in retirement"
            )
            answers["custom_retirement_monthly"] = custom_monthly

    elif goal_type == "Higher Education":
        answers["degree_type"] = st.selectbox("Degree", ["Bachelor's Degree", "Master's Degree", "PhD / Doctorate"])
        answers["country"] = st.selectbox("Country of Study", ["Australia", "Europe", "Singapore", "US", "Other"])
        answers["institution_tier"] = st.selectbox("Institution Tier", [
            "Public / State University", "Private University",
            "Top 50 Global (e.g. NTU, NUS, Melbourne)", "Ivy League / Oxbridge / Top 10"
        ])

    elif goal_type == "Wedding":
        answers["wedding_scale"] = st.selectbox("Wedding Style", [
            "Simple / Intimate (50-100 guests)", "Moderate / Traditional (200-400 guests)", "Grand / Bilingual (500+ guests)"
        ])

    elif goal_type == "Emergency Fund":
        emergency_options = [
            "3 months (minimum)",
            "6 months (standard)",
            "12 months (conservative)",
            "Custom — enter my own monthly expenses",
        ]
        selected_emergency = st.selectbox("Coverage", emergency_options)
        answers["months_covered"] = selected_emergency
        if "Custom" in selected_emergency:
            custom_expenses = st.number_input(
                "Your Monthly Expenses (IDR)",
                min_value=1_000_000,
                max_value=500_000_000,
                value=5_000_000,
                step=500_000,
                help="Enter your estimated monthly living expenses"
            )
            answers["custom_emergency_monthly"] = custom_expenses

    elif goal_type == "Custom":
        custom_choice = st.radio("How would you like to set your custom goal?", [
            "Enter a target amount directly",
            "Describe your goal and I'll help estimate the cost",
        ])
        if custom_choice == "Enter a target amount directly":
            answers["custom_amount"] = st.number_input(
                "Target Amount (IDR)", min_value=0, value=100_000_000, step=5_000_000,
                help="Enter the total amount you want to save"
            )
        else:
            answers["custom_description"] = st.text_area(
                "Describe your goal", placeholder="e.g. I want to start a business..."
            )
            answers["custom_amount"] = st.number_input(
                "Estimated amount if known (IDR, optional)", min_value=0, value=0, step=5_000_000
            )

    answers["timeline_years"] = st.slider("Investment Timeline (years)", 1, 40, 10)

    st.markdown("---")

    if st.button("Estimate Goal Cost", type="primary"):
        gb = GoalBuilder()
        profile = gb.build_goal(goal_type, city, answers)

        st.markdown(f"""
        <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #7C3AED, #06B6D4) 1;">
            <div style="text-align:center;">
                <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Estimated Cost</div>
                <div class="cost-display">{format_idr(profile.estimated_cost)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**{profile.description}** | {profile.timeline_years} years")

        # Data freshness warning
        st.markdown("""
        <div style="background:rgba(245,158,11,0.1);border:1px solid #F59E0B;border-radius:12px;padding:1rem;margin-top:1rem;">
            <span style="color:#F59E0B;font-weight:600;">&#9888; </span>
            <span style="color:#94A3B8;">Cost estimates are based on 2025 data.
            Actual prices may vary by &#177;15-20%.
            Please verify with a property agent or relevant institution before making decisions.</span>
        </div>
        """, unsafe_allow_html=True)

        st.session_state["goal_profile"] = profile.to_dict()
        st.session_state["goal_set"] = True

        st.info("&#8592; Proceed to **Feasibility Analysis** to check if this goal is achievable with your income.")


# ── Page 2: Feasibility Analysis ────────────────────────────────────────────────

elif page == "📊 Feasibility Analysis":
    st.title("Feasibility Analysis")
    st.markdown("### How achievable is your goal?")

    if "goal_set" not in st.session_state:
        st.warning("&#9888; Please complete the **Goal Builder** first.")
        st.stop()

    goal = st.session_state["goal_profile"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Your Income")
        monthly_salary = st.number_input(
            "Monthly Take-Home Salary (IDR)",
            min_value=1_000_000,
            max_value=500_000_000,
            value=15_000_000,
            step=500_000,
            help="Your net monthly income after taxes and deductions",
            format="%d",
        )
        bracket = get_salary_bracket(monthly_salary)
        st.markdown(f'<div class="salary-bracket">Career bracket: <span class="bracket-label">{bracket}</span></div>', unsafe_allow_html=True)

        income_growth = st.slider(
            "Expected Annual Income Growth Rate",
            min_value=0.0, max_value=0.30, value=0.08, step=0.005,
            format="%.1f%%", help="Average annual salary increase you expect over the investment horizon"
        )
    with col2:
        st.markdown("#### Goal Summary")
        st.markdown(f"""
        <div class="metric-col">
            <div class="metric-val">{format_idr(goal['estimated_cost'])}</div>
            <div class="metric-lbl">Goal Amount</div>
        </div>
        <div style="height:0.75rem;"></div>
        <div class="metric-col">
            <div class="metric-val" style="font-size:1.25rem;">{goal['timeline_years']} years</div>
            <div class="metric-lbl">Timeline</div>
        </div>
        <div style="height:0.75rem;"></div>
        <div class="metric-col">
            <div class="metric-val" style="font-size:1rem;">{goal['goal_type']}</div>
            <div class="metric-lbl">Goal Type</div>
        </div>
        <div style="height:0.75rem;"></div>
        <div class="metric-col">
            <div class="metric-val" style="font-size:1rem;">{goal['city']}</div>
            <div class="metric-lbl">City</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("Analyse Feasibility", type="primary"):
        result = compute_feasibility(
            monthly_salary=monthly_salary,
            city=goal["city"],
            goal_cost=goal["estimated_cost"],
            timeline_years=goal["timeline_years"],
            income_growth_rate=income_growth,
        )

        # Large verdict display
        verdict_class_map = {"green": "verdict-green", "yellow": "verdict-yellow", "red": "verdict-red"}
        verdict_text_map = {
            "green": "ACHIEVABLE",
            "yellow": "ACHIEVABLE WITH CONDITIONS",
            "red": "NOT ACHIEVABLE AS STATED",
        }
        verdict_icon_map = {"green": "&#9989;", "yellow": "&#9888;", "red": "&#10060;"}

        vc = verdict_class_map.get(result["verdict"], "verdict-green")
        vt = verdict_text_map.get(result["verdict"], "ACHIEVABLE")
        vi = verdict_icon_map.get(result["verdict"], "&#9989;")

        st.markdown(f"""
        <div class="vestara-card {vc}">
            <div class="verdict-text">
                <div style="font-size:3rem;margin-bottom:0.5rem;">{vi}</div>
                <div style="font-size:2rem;font-weight:800;color:#F8FAFC;">{vt}</div>
                <div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">with ratio {result['ratio']:.1%}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3-column metric cards
        st.markdown("")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f"""
            <div class="metric-col">
                <div class="metric-val">{format_idr(result['monthly_living'])}</div>
                <div class="metric-lbl">Monthly Living Cost</div>
            </div>
            """, unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""
            <div class="metric-col">
                <div class="metric-val">{format_idr(result['disposable'])}</div>
                <div class="metric-lbl">Disposable Income</div>
            </div>
            """, unsafe_allow_html=True)
        with mc3:
            st.markdown(f"""
            <div class="metric-col">
                <div class="metric-val">{format_idr(result['monthly_required'])}</div>
                <div class="metric-lbl">Required Monthly Investment</div>
            </div>
            """, unsafe_allow_html=True)

        st.session_state["feasibility_result"] = result
        st.session_state["monthly_contribution"] = result["monthly_required"]
        st.session_state["salary"] = monthly_salary
        st.session_state["income_growth"] = income_growth

        if result["verdict"] in ("yellow", "red"):
            st.markdown("")
            st.markdown("---")
            st.markdown("#### Scenario Analysis — How to flip to Green?")
            st.markdown("""
            <div style="background:rgba(124,58,237,0.1);border:1px solid #7C3AED;border-radius:12px;padding:1rem;margin-bottom:1.5rem;">
                <div style="color:#F8FAFC;font-weight:600;margin-bottom:0.5rem;">Priority adjustments (easiest to hardest):</div>
                <div style="color:#94A3B8;font-size:0.9rem;">
                    <div>1. <strong>Extend timeline</strong> — giving your money more time to compound</div>
                    <div>2. <strong>Adjust location</strong> — choosing a lower-cost city or neighbourhood</div>
                    <div>3. <strong>Reduce goal size</strong> — a smaller target with the same timeline</div>
                    <div>4. <strong>Increase monthly contribution</strong> — investing more each month</div>
                </div>
                <div style="color:#94A3B8;font-size:0.85rem;margin-top:0.75rem;font-style:italic;">
                    Below are the minimum viable changes calculated for your profile.
                </div>
            </div>
            """, unsafe_allow_html=True)

            from vestara.src.engine.scenario_optimizer import run_scenario_analysis

            monthly_living = LIVING_COST_MONTHLY.get(goal["city"], 6_000_000)
            scenarios = run_scenario_analysis(
                goal_cost=goal["estimated_cost"],
                monthly_salary=monthly_salary,
                monthly_living_cost=monthly_living,
                current_timeline=goal["timeline_years"],
                current_contribution=result["monthly_required"],
                goal_type=goal["goal_type"],
            )

            if scenarios.blocked_reason:
                st.error("&#9888; Scenario Optimizer Blocked")
                st.write(scenarios.blocked_reason)
                st.stop()

            if scenarios.scenarios:
                for i, s in enumerate(scenarios.scenarios):
                    verdict_pill_class = "green" if s.verdict == "green" else ("yellow" if s.verdict == "yellow" else "red")
                    with st.expander(f"&#128279; {s.lever.upper()}: {s.adjustment}", expanded=(i == 0)):
                        st.write(s.change_description)
                        st.write(f"New investment ratio: **{s.new_ratio:.1%}**")
                        st.markdown(f"Verdict: <span class='verdict-pill {verdict_pill_class}'>{s.verdict.upper()}</span>", unsafe_allow_html=True)
                        if i == 0:
                            st.session_state["recommended_scenario"] = s
            else:
                st.warning("No viable scenario found within reasonable parameters.")


# ── Page 3: Risk Profiler ─────────────────────────────────────────────────────--

elif page == "📋 Risk Profiler":
    st.title("Risk Profiler")
    st.markdown("### 12 questions to find your Indonesian investment profile")

    if "risk_answers" not in st.session_state:
        st.session_state["risk_answers"] = {}
    if "risk_page" not in st.session_state:
        st.session_state["risk_page"] = 0

    answers = st.session_state["risk_answers"]
    page_idx = st.session_state["risk_page"]

    QUESTIONS_PER_PAGE = 3
    start = page_idx * QUESTIONS_PER_PAGE
    end = min(start + QUESTIONS_PER_PAGE, len(RISK_QUESTIONS))
    page_questions = RISK_QUESTIONS[start:end]

    progress_val = min(end / len(RISK_QUESTIONS), 1.0)
    st.markdown(f"""
    <div style="background:#1E1E2E;border-radius:999px;height:8px;margin-bottom:0.5rem;">
        <div style="background:linear-gradient(90deg,#7C3AED,#06B6D4);height:100%;border-radius:999px;width:{int(progress_val*100)}%;transition:width 0.3s ease;"></div>
    </div>
    <div style="color:#94A3B8;font-size:0.8rem;">Questions {start + 1}–{end} of {len(RISK_QUESTIONS)}</div>
    """, unsafe_allow_html=True)

    for q in page_questions:
        q_num = q['id'].replace('q', '').replace('_', ' ')
        st.markdown(f"""
        <div class="question-card">
            <div style="margin-bottom:0.75rem;">
                <span class="question-number">{q_num}</span>
                <span style="color:#F8FAFC;font-weight:600;">{q['question']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        selected = st.radio(
            label=q["id"],
            options=[f"{i+1}. {opt['text']}" for i, opt in enumerate(q["options"])],
            key=f"radio_{q['id']}",
            index=None,
        )
        if selected:
            chosen_idx = int(selected.split(".")[0]) - 1
            answers[q["id"]] = q["options"][chosen_idx]["score"]
        st.markdown("")

    col_prev, col_next = st.columns(2)
    with col_prev:
        if page_idx > 0:
            if st.button("&#8592; Previous"):
                st.session_state["risk_page"] -= 1
                st.rerun()
    with col_next:
        if end < len(RISK_QUESTIONS):
            if st.button("Next &#8594;"):
                st.session_state["risk_page"] += 1
                st.rerun()

    if len(answers) == 12:
        st.markdown("")
        st.markdown("---")
        st.success("&#127881; All questions answered!")
        rp = RiskProfiler()
        for qid, score in answers.items():
            rp.submit_answer(qid, score)
        profile = rp.get_profile()

        score_class = "green" if profile.percentage >= 70 else ("yellow" if profile.percentage >= 40 else "red")
        st.markdown(f"""
        <div class="profile-card" style="margin-bottom:1.5rem;">
            <div class="score-circle {score_class}">{profile.score}/{profile.max_score}</div>
            <div style="text-align:center;margin-top:0.75rem;">
                <span class="verdict-pill {score_class}" style="font-size:0.85rem;">{profile.percentage}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        profile_class = profile.profile.lower()
        profile_border_class = "konservatif" if profile.profile == "Konservatif" else ("moderat" if profile.profile == "Moderat" else "agresif")
        st.markdown(f"""
        <div class="profile-card {profile_border_class}" style="margin-bottom:1.5rem;">
            <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Your Risk Profile</div>
            <div style="font-size:1.75rem;font-weight:800;color:#F8FAFC;margin-bottom:0.5rem;">{profile.profile}</div>
            <div style="color:#94A3B8;font-size:0.9rem;">{profile.description}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Recommended Asset Allocation")
        alloc_data = []
        for instrument, pct in profile.allocation.items():
            label = PORT_LABELS.get(instrument, instrument)
            alloc_data.append({"Instrument": label, "Allocation": f"{pct}%", "%": pct})

        df = pd.DataFrame(alloc_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.session_state["risk_profile"] = profile.to_dict()
        st.session_state["risk_profile_set"] = True


# ── Page 4: Portfolio Recommendation ──────────────────────────────────────────

elif page == "💼 Portfolio Recommendation":
    st.title("Portfolio Recommendation")

    if "goal_set" not in st.session_state:
        st.warning("&#9888; Please complete **Goal Builder** first.")
        st.stop()
    if "risk_profile_set" not in st.session_state:
        st.warning("&#9888; Please complete the **Risk Profiler** first.")
        st.stop()

    goal = st.session_state["goal_profile"]
    risk = st.session_state["risk_profile"]

    monthly_contribution = st.session_state.get("monthly_contribution", goal["estimated_cost"] / (goal["timeline_years"] * 12))

    # Regulatory disclaimer
    st.markdown("""
    <div class="disclaimer-banner">
        <div style="color:#F59E0B;font-weight:700;font-size:1rem;margin-bottom:0.25rem;">&#9888; Disclaimer</div>
        <div style="color:#94A3B8;font-size:0.9rem;">
            <strong>Vestara provides educational goal planning tools only.</strong>
            This illustrative portfolio is not personalised investment advice.
            Consult a licensed <strong>OJK financial advisor</strong> before making any investment decision.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initial Disclosure Document expander
    with st.expander("&#128279; Initial Disclosure / Penyingkapan Informasi Awal (POJK 21/2011)"):
        st.markdown("#### What Vestara does and does not do")
        st.markdown("""
        **Vestara DOES:**
        - Estimate financial goal costs based on synthetic data
        - Provide illustrative investment instrument allocation based on risk profile
        - Show projected growth based on historical return assumptions

        **Vestara DOES NOT:**
        - Provide personalised investment advice
        - Process investment transactions on behalf of users
        - Guarantee accuracy of cost estimates or projected returns
        """)
        st.markdown("---")
        st.markdown("#### Model Limitations")
        st.markdown("""
        - **Training data:** This model is trained on **synthetic data**, not real Indonesian market data.
          Allocation results are illustrative, not guaranteed recommendations.
        - **Cost estimates:** All cost estimates are **approximations with &#177;15-20% uncertainty**.
          Actual prices may differ significantly based on location, timing, and market conditions.
        - **Past performance does not guarantee future returns:** Investment instrument performance
          in the past is not an indication of future performance.
        """)
        st.markdown("---")
        st.markdown("#### Reference Sources")
        st.markdown(
            "- &#128220; **OJK Investor Education:** [sifikasiuangmu.ojk.go.id](https://sifikasiuangmu.ojk.go.id) "
            "— Financial education portal of Otoritas Jasa Keuangan Indonesia"
        )

    st.markdown("")
    st.markdown(f"#### Illustrative Allocation — **{goal['goal_type']}** goal in **{goal['city']}**")
    st.markdown(f"**Risk Profile: {risk['profile']}** | Monthly investment: **{format_idr(monthly_contribution)}**")

    result = build_portfolio(
        risk_profile=risk["profile"],
        monthly_contribution=monthly_contribution,
        goal_amount=goal["estimated_cost"],
        timeline_years=goal["timeline_years"],
    )

    # Lumpy goal equity warning
    equity_pct = next((a.percentage for a in result.allocations if a.instrument == "reksa_dana_equity"), 0)
    is_property_short = (goal["goal_type"] == "Property" and goal["timeline_years"] < 5)
    if is_property_short and equity_pct > 20:
        st.warning(
            "&#9888; **Property Goal Warning:** "
            "Property goals require funds at a specific date. "
            "Equity funds can drop significantly before the target date. "
            "Consider a more conservative allocation to reduce timing risk."
        )

    st.markdown("")
    st.markdown("#### Monthly Allocation")

    alloc_rows = []
    for a in result.allocations:
        risk_label = INSTRUMENT_RISK_LABELS.get(a.instrument, "")
        risk_badge_class = "risk-high" if "High" in risk_label else ("risk-medium" if "Medium" in risk_label else "risk-low")
        alloc_rows.append({
            "Instrument": PORT_LABELS.get(a.instrument, a.instrument),
            "%": f"{a.percentage:.1f}%",
            "Monthly (IDR)": format_idr(a.monthly_amount),
            "Expected Return": f"{a.expected_return:.1%}",
            "Risk": risk_label,
        })
    st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True, hide_index=True)

    col_summary1, col_summary2, col_summary3 = st.columns(3)
    with col_summary1:
        st.markdown(f"""
        <div class="metric-col">
            <div class="metric-val" style="font-size:1.1rem;">{result.blended_return:.2%}</div>
            <div class="metric-lbl">Blended Expected Return</div>
        </div>
        """, unsafe_allow_html=True)
    with col_summary2:
        st.markdown(f"""
        <div class="metric-col">
            <div class="metric-val" style="font-size:1.1rem;">{result.blended_volatility:.2%}</div>
            <div class="metric-lbl">Blended Volatility</div>
        </div>
        """, unsafe_allow_html=True)
    with col_summary3:
        st.markdown(f"""
        <div class="metric-col">
            <div class="metric-val" style="font-size:1rem;">{format_idr(result.projected_value_at_goal_year)}</div>
            <div class="metric-lbl">Projected Value at Goal Year</div>
        </div>
        """, unsafe_allow_html=True)

    shortfall = result.goal_amount - result.projected_value_at_goal_year
    if shortfall > 0:
        st.error(f"&#9888; Projected shortfall of **{format_idr(shortfall)}** — consider increasing monthly contribution or extending timeline.")
    else:
        st.success(f"&#9989; On track — projected value exceeds goal by **{format_idr(abs(shortfall))}**")

    st.markdown("")
    st.markdown("#### Growth Trajectory — Illustrative")

    trajectory_df = pd.DataFrame(
        [{"Year": year, "Projected Value (IDR)": value} for year, value in result.yearly_trajectory],
    )
    trajectory_df = trajectory_df.set_index("Year")

    goal_amount = result.goal_amount

    st.line_chart(
        trajectory_df,
        y="Projected Value (IDR)",
        height=320,
    )
    st.caption(
        f"Goal target: **{format_idr(goal_amount)}** at year {result.timeline_years} | "
        f"Projected: **{format_idr(result.projected_value_at_goal_year)}** "
        f"(illustrative only, not a guarantee)"
    )


# ── Page 5: Dashboard ──────────────────────────────────────────────────────────

elif page == "📈 Dashboard":
    st.title("Dashboard")

    has_goal = st.session_state.get("goal_set", False)
    has_feasibility = st.session_state.get("feasibility_result") is not None
    has_risk = st.session_state.get("risk_profile_set", False)

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Goal Set</div>
            <div style="font-size:1.25rem;font-weight:700;color:{'#10B981' if has_goal else '#EF4444'};">{'&#9989; Yes' if has_goal else '&#10060; Not yet'}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Feasibility Analysed</div>
            <div style="font-size:1.25rem;font-weight:700;color:{'#10B981' if has_feasibility else '#EF4444'};">{'&#9989; Yes' if has_feasibility else '&#10060; Not yet'}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Risk Profiled</div>
            <div style="font-size:1.25rem;font-weight:700;color:{'#10B981' if has_risk else '#EF4444'};">{'&#9989; Yes' if has_risk else '&#10060; Not yet'}</div>
        </div>
        """, unsafe_allow_html=True)
    with sc4:
        overall = [has_goal, has_feasibility, has_risk].count(True)
        health_class = "excellent" if overall == 3 else ("good" if overall == 2 else "needs_work")
        health_label = "Excellent" if overall == 3 else ("Good" if overall == 2 else "Needs Work")
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Overall Health</div>
            <div class="health-score {health_class}" style="font-size:1.5rem;">{health_label}</div>
        </div>
        """, unsafe_allow_html=True)

    if has_goal:
        goal = st.session_state["goal_profile"]
        st.markdown("")
        st.markdown("---")
        st.markdown("#### Your Goal Summary")

        verdict_pill_class = "green"
        if has_feasibility:
            fr = st.session_state.get("feasibility_result", {})
            vf = fr.get("verdict", "green")
            verdict_pill_class = vf

        st.markdown(f"""
        <div class="goal-progress-card">
            <div class="goal-name">&#127968; {goal['goal_type']} in {goal['city']}</div>
            <div class="goal-meta">
                <span>Timeline: {goal['timeline_years']} years</span> &middot;
                <span>Amount: {format_idr(goal['estimated_cost'])}</span>
            </div>
            <div style="margin-top:0.75rem;">
                <span class="verdict-pill {verdict_pill_class}">
                    {f"Investment ratio: {st.session_state.get('feasibility_result', {}).get('ratio', 0):.1%}" if has_feasibility else "Pending analysis"}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if has_feasibility:
        result = st.session_state["feasibility_result"]
        st.markdown("")
        st.markdown("---")
        st.markdown("#### Feasibility Summary")
        st.json(result)

    if has_risk:
        risk = st.session_state["risk_profile"]
        st.markdown("")
        st.markdown("---")
        st.markdown("#### Risk Profile")
        st.json(risk)

    if all([has_goal, has_feasibility, has_risk]):
        st.balloons()
        st.success("&#127881; Your complete financial plan is ready! Head to **Portfolio Recommendation** to see your investment allocation.")
