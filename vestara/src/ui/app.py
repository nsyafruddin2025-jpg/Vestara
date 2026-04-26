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

from vestara.src.engine.goal_builder import GoalBuilder, STEPS_BY_GOAL
from vestara.src.engine.risk_profiler import RiskProfiler, RISK_QUESTIONS
from vestara.src.engine.peer_clustering import get_clusterer
from vestara.src.portfolio.optimizer import build_portfolio
from vestara.data import cost_data as cd
from vestara.data.cost_data import LIVING_COST_MONTHLY, INSTRUMENT_RISK_LABELS
from vestara.data.fetcher import (
    fetch_property_prices,
    fetch_living_costs,
    get_all_price_data,
    get_city_property_price,
    get_city_living_cost,
    BASELINE_FALLBACK_PROPERTY,
    BASELINE_FALLBACK_LIVING,
)

st.set_page_config(
    page_title="Vestara — Plan Your Life, Then Your Investment",
    page_icon="🏠",
    layout="wide",
)

# ── Global Dark Mode CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
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
.vestara-card { background-color: #13131A; border: 1px solid #1E1E2E; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 24px rgba(0,0,0,0.4); }
.verdict-green { border: 2px solid #10B981; box-shadow: 0 0 30px rgba(16,185,129,0.15); }
.verdict-yellow { border: 2px solid #F59E0B; box-shadow: 0 0 30px rgba(245,158,11,0.15); }
.verdict-red { border: 2px solid #EF4444; box-shadow: 0 0 30px rgba(239,68,68,0.15); }
.st-dg > div > button:first-child { background: linear-gradient(135deg, #7C3AED, #6D28D9) !important; color: white !important; border: none !important; border-radius: 12px !important; font-weight: 600 !important; padding: 0.5rem 1.5rem !important; transition: all 0.2s ease !important; }
.st-dg > div > button:first-child:hover { background: linear-gradient(135deg, #8B5CF6, #7C3AED) !important; box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] > div > div, [data-testid="stTextArea"] textarea { background-color: #13131A !important; border: 1px solid #1E1E2E !important; color: #F8FAFC !important; border-radius: 10px !important; }
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus, [data-testid="stSelectbox"] > div > div:focus, [data-testid="stTextArea"] textarea:focus { border-color: #7C3AED !important; box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important; }
[data-testid="stRadio"] label { color: #F8FAFC !important; }
[data-testid="stRadio"] label:hover { color: #7C3AED !important; }
.st-abq .css-1aehpvj { background-color: #7C3AED !important; }
.st-abq .css-1632mt { background-color: #1E1E2E !important; }
.st-cj .css-1v0mbg9 { background-color: #7C3AED !important; }
[data-testid="stSidebarNav"] span { color: #F8FAFC !important; }
[data-testid="stSidebarNav"] span:hover { color: #7C3AED !important; }
.st-em { border-radius: 12px !important; }
details { background-color: #13131A !important; border: 1px solid #1E1E2E !important; border-radius: 12px !important; }
summary { color: #F8FAFC !important; }
.hero-title { position: relative; display: inline-block; }
.hero-title::after { content: ''; position: absolute; bottom: -4px; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, #7C3AED, #06B6D4); border-radius: 2px; }
.goal-card { background: #13131A; border: 2px solid #1E1E2E; border-radius: 16px; padding: 1.5rem; text-align: center; cursor: pointer; transition: all 0.2s ease; }
.goal-card:hover { border-color: #7C3AED; transform: translateY(-2px); }
.goal-card.selected { border-color: #7C3AED; box-shadow: 0 0 20px rgba(124,58,237,0.3); }
.goal-card-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.goal-card-title { font-weight: 600; color: #F8FAFC; font-size: 1rem; }
.goal-card-desc { font-size: 0.8rem; color: #94A3B8; margin-top: 0.25rem; }
.cost-display { font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #7C3AED, #06B6D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: 'Inter', monospace; }
.risk-high { background: rgba(239,68,68,0.15); color: #EF4444; }
.risk-medium { background: rgba(245,158,11,0.15); color: #F59E0B; }
.risk-low { background: rgba(16,185,129,0.15); color: #10B981; }
.summary-card { background: #13131A; border: 1px solid #1E1E2E; border-radius: 12px; padding: 1rem; text-align: center; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.verdict-text { font-size: 1.75rem; font-weight: 800; text-align: center; padding: 1.5rem; }
.scenario-card { background: #13131A; border: 1px solid #1E1E2E; border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem; }
.question-card { background: #13131A; border: 1px solid #1E1E2E; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; }
.question-number { display: inline-block; background: linear-gradient(135deg, #7C3AED, #6D28D9); color: white; font-weight: 700; font-size: 0.75rem; width: 28px; height: 28px; border-radius: 50%; text-align: center; line-height: 28px; margin-right: 0.75rem; }
.score-circle { width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-size: 2rem; font-weight: 800; }
.score-circle.green { background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.1)); border: 3px solid #10B981; color: #10B981; }
.score-circle.yellow { background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.1)); border: 3px solid #F59E0B; color: #F59E0B; }
.score-circle.red { background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(239,68,68,0.1)); border: 3px solid #EF4444; color: #EF4444; }
.profile-card { background: #13131A; border-radius: 16px; padding: 2rem; text-align: center; }
.profile-card.konservatif { border: 2px solid #06B6D4; box-shadow: 0 0 30px rgba(6,182,212,0.15); }
.profile-card.moderat { border: 2px solid #7C3AED; box-shadow: 0 0 30px rgba(124,58,237,0.15); }
.profile-card.agresif { border: 2px solid #F59E0B; box-shadow: 0 0 30px rgba(245,158,11,0.15); }
.metric-col { background: #13131A; border: 1px solid #1E1E2E; border-radius: 12px; padding: 1.25rem; text-align: center; }
.metric-col .metric-val { font-size: 1.5rem; font-weight: 700; color: #7C3AED; font-family: 'Inter', monospace; }
.metric-col .metric-lbl { font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }
.health-score { font-size: 4rem; font-weight: 800; text-align: center; }
.health-score.excellent { color: #10B981; }
.health-score.good { color: #06B6D4; }
.health-score.needs_work { color: #F59E0B; }
.disclaimer-banner { background: rgba(245,158,11,0.1); border: 1px solid #F59E0B; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; }
.goal-progress-card { background: #13131A; border: 1px solid #1E1E2E; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; }
.goal-name { font-size: 1.1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.5rem; }
.goal-meta { font-size: 0.8rem; color: #94A3B8; }
.verdict-pill { display: inline-block; padding: 0.35rem 0.85rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; }
.verdict-pill.green { background: rgba(16,185,129,0.15); color: #10B981; }
.verdict-pill.yellow { background: rgba(245,158,11,0.15); color: #F59E0B; }
.verdict-pill.red { background: rgba(239,68,68,0.15); color: #EF4444; }
.sidebar-brand { font-size: 1.5rem; font-weight: 800; color: #F8FAFC !important; margin-bottom: 0.25rem; }
.sidebar-tagline { font-size: 0.8rem; color: #94A3B8 !important; margin-bottom: 1.5rem; }
.step-card { background: #13131A; border: 1px solid #1E1E2E; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; }
.step-header { display: flex; align-items: center; margin-bottom: 1.5rem; }
.step-label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: #7C3AED; font-weight: 600; }
.step-title { font-size: 1.25rem; font-weight: 700; color: #F8FAFC; margin: 0.25rem 0 0 0; }
.progress-track { background: #1E1E2E; border-radius: 999px; height: 6px; margin-bottom: 2rem; overflow: hidden; }
.progress-fill { background: linear-gradient(90deg, #7C3AED, #06B6D4); height: 100%; border-radius: 999px; transition: width 0.4s ease; }
.breakdown-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #1E1E2E; }
.breakdown-row:last-child { border-bottom: none; }
.breakdown-label { color: #94A3B8; font-size: 0.9rem; }
.breakdown-value { color: #F8FAFC; font-weight: 600; font-size: 0.9rem; font-family: 'Inter', monospace; }
.breakdown-total-row { display: flex; justify-content: space-between; padding: 0.75rem 0; background: rgba(124,58,237,0.1); border-radius: 8px; margin-top: 0.5rem; padding: 0.75rem 1rem; }
.breakdown-total-label { color: #F8FAFC; font-weight: 700; font-size: 1rem; }
.breakdown-total-value { color: #7C3AED; font-weight: 800; font-size: 1.1rem; font-family: 'Inter', monospace; }
.nav-buttons { display: flex; justify-content: space-between; margin-top: 2rem; }
.current-year-badge { display: inline-block; background: rgba(124,58,237,0.15); color: #7C3AED; font-weight: 600; font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 6px; margin-left: 0.5rem; }
.entry-info { background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.3); border-radius: 10px; padding: 0.75rem 1rem; margin-top: 0.75rem; font-size: 0.9rem; }
.entry-info strong { color: #7C3AED; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────────

def format_idr(amount: float) -> str:
    if amount == 0:
        return "Rp 0"
    return f"Rp {amount:,.0f}".replace(",", ".")


def get_salary_bracket(amount: float) -> str:
    if amount < 8_000_000:
        return "Fresh Graduate"
    elif amount < 25_000_000:
        return "Mid Career"
    return "Senior Professional"


def render_cost_breakdown(breakdown):
    """Render a CostBreakdown object as a styled table."""
    if breakdown is None:
        return

    with st.expander("📊 View cost breakdown"):
        st.markdown(f"""
        <div style="margin-bottom:0.5rem;">
            <span style="color:#94A3B8;font-size:0.85rem;">
                Current cost: <strong style="color:#F8FAFC;">{format_idr(breakdown.current_cost)}</strong>
                &nbsp;&middot;&nbsp;
                Inflation: <strong style="color:#7C3AED;">{breakdown.inflation_rate * 100:.0f}%/yr</strong>
                &nbsp;&middot;&nbsp;
                Years: <strong style="color:#F8FAFC;">{breakdown.years_to_goal}</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)

        for item in breakdown.items:
            if item.value == 0:
                st.markdown(f"""
                <div class="breakdown-row">
                    <span class="breakdown-label">{item.label}</span>
                    <span class="breakdown-value">{item.detail}</span>
                </div>
                """, unsafe_allow_html=True)
            elif item.label == "Annual inflation rate" or item.label == "Annual cost of living inflation" or item.label == "Annual inflation":
                st.markdown(f"""
                <div class="breakdown-row">
                    <span class="breakdown-label">{item.label}</span>
                    <span class="breakdown-value">{item.value:.0f}% — {item.detail}</span>
                </div>
                """, unsafe_allow_html=True)
            elif item.label == "Field of study":
                st.markdown(f"""
                <div class="breakdown-row">
                    <span class="breakdown-label">{item.label}</span>
                    <span class="breakdown-value">{item.detail}</span>
                </div>
                """, unsafe_allow_html=True)
            elif isinstance(item.value, (int, float)) and item.value > 1000:
                st.markdown(f"""
                <div class="breakdown-row">
                    <span class="breakdown-label">{item.label}</span>
                    <span class="breakdown-value">{format_idr(item.value)} — {item.detail}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="breakdown-row">
                    <span class="breakdown-label">{item.label}</span>
                    <span class="breakdown-value">{item.value} — {item.detail}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="breakdown-total-row">
            <span class="breakdown-total-label">Projected Total ({cd.get_current_year() + breakdown.years_to_goal})</span>
            <span class="breakdown-total-value">{format_idr(breakdown.projected_cost)}</span>
        </div>
        """, unsafe_allow_html=True)


def render_progress_bar(current: int, total: int) -> None:
    pct = min(current / total, 1.0)
    st.markdown(f"""
    <div style="margin-bottom:0.25rem;">
        <span style="color:#7C3AED;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;">
            Step {current} of {total}
        </span>
    </div>
    <div class="progress-track">
        <div class="progress-fill" style="width:{int(pct * 100)}%;"></div>
    </div>
    """, unsafe_allow_html=True)


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

# ── Data Sources & Freshness ─────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("**📡 Data Sources**")

if "data_freshness" not in st.session_state:
    st.session_state["data_freshness"] = None

refresh_clicked = st.sidebar.button("🔄 Refresh Data")

if refresh_clicked:
    with st.spinner("Fetching latest prices..."):
        prop_result, living_result = get_all_price_data(force_refresh=True)
        st.session_state["data_freshness"] = {
            "property": prop_result.freshness,
            "living": living_result.freshness,
        }
    st.rerun()

# Show current freshness status
if st.session_state.get("data_freshness") is None:
    prop_result, living_result = get_all_price_data()
    st.session_state["data_freshness"] = {
        "property": prop_result.freshness,
        "living": living_result.freshness,
    }

pf = st.session_state["data_freshness"]["property"]
lf = st.session_state["data_freshness"]["living"]

def _freshness_badge(freshness) -> str:
    if freshness.status == "live":
        return f"🟢 Live · {freshness.last_updated}"
    elif freshness.status == "cached":
        return f"🟡 Cached · {freshness.last_updated} ({freshness.days_old}d ago)"
    else:
        return f"🔴 Baseline · {freshness.last_updated}"

st.sidebar.caption(f"**Property:** {pf.source or 'unknown'}")
st.sidebar.caption(_freshness_badge(pf))
st.sidebar.caption(f"**Living costs:** {lf.source or 'unknown'}")
st.sidebar.caption(_freshness_badge(lf))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: GOAL BUILDER
# ══════════════════════════════════════════════════════════════════════════════

if page == "🏗️ Goal Builder":
    st.markdown('<div class="hero-title" style="font-size:2rem;font-weight:800;color:#F8FAFC;">What\'s your financial goal?</div>', unsafe_allow_html=True)
    st.markdown("#### Choose your life goal")

    # ── Goal type card grid ──────────────────────────────────────────
    goal_types_with_icons = [
        ("🏠", "Property",        "Buy a home or land"),
        ("🎓", "Education",       "Child's school education"),
        ("🎓", "Higher Education", "University — Indonesia or abroad"),
        ("🌴", "Retirement",       "Build your retirement fund"),
        ("💍", "Wedding",          "Plan your wedding"),
        ("🛡️", "Emergency Fund",  "Build a safety net"),
        ("✨", "Custom",           "Any other financial goal"),
    ]

    if "selected_goal" not in st.session_state:
        st.session_state["selected_goal"] = None
    if "goal_step" not in st.session_state:
        st.session_state["goal_step"] = 0
    if "goal_step_answers" not in st.session_state:
        st.session_state["goal_step_answers"] = {}

    # Card grid
    cols = st.columns(4)
    for idx, (icon, name, desc) in enumerate(goal_types_with_icons[:4]):
        with cols[idx]:
            sel = st.session_state["selected_goal"] == name
            cls = "goal-card selected" if sel else "goal-card"
            st.markdown(f"""
            <div class="{cls}" onclick="
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
    cols2 = st.columns(3)
    for idx, (icon, name, desc) in enumerate(goal_types_with_icons[4:]):
        with cols2[idx]:
            sel = st.session_state["selected_goal"] == name
            cls = "goal-card selected" if sel else "goal-card"
            st.markdown(f"""
            <div class="{cls}" onclick="
                const els = document.querySelectorAll('.goal-card');
                els.forEach(e => e.classList.remove('selected'));
                this.classList.add('selected');
            ">
                <div class="goal-card-icon">{icon}</div>
                <div class="goal-card-title">{name}</div>
                <div class="goal-card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Goal type selector ──────────────────────────────────────────
    goal_type = st.selectbox(
        "Goal Type",
        ["Property", "Education", "Retirement", "Emergency Fund", "Wedding", "Higher Education", "Custom"],
        index=None,
        placeholder="Select a goal type above",
    )
    if goal_type:
        st.session_state["selected_goal"] = goal_type
        st.session_state["goal_type"] = goal_type
    else:
        goal_type = st.session_state.get("selected_goal")

    if goal_type:
        steps = STEPS_BY_GOAL.get(goal_type, [])
        total_steps = len(steps)
        current_step = st.session_state.get("goal_step", 0)
        answers = st.session_state.get("goal_step_answers", {})
        step_id = steps[current_step]["id"] if current_step < total_steps else None

        st.markdown("---")

        # ── Step-based question flow ─────────────────────────────────
        # EDUCATION
        if goal_type == "Education":
            render_progress_bar(current_step + 1, total_steps)

            if current_step == 0:  # Education level
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What level is your child starting?</div>', unsafe_allow_html=True)
                education_level = st.radio(
                    "Education level",
                    cd.EDUCATION_LEVELS,
                    index=None,
                    label_visibility="collapsed",
                )
                if st.button("Next →", type="primary"):
                    if education_level:
                        answers["education_level"] = education_level
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # School type
                render_progress_bar(2, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What type of school?</div>', unsafe_allow_html=True)
                school_type = st.radio(
                    "School type",
                    cd.EDUCATION_SCHOOL_TYPES,
                    index=None,
                )
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if school_type:
                            answers["school_type"] = school_type
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 2
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # Child's age
                render_progress_bar(3, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">How old is your child now?</div>', unsafe_allow_html=True)
                child_age = st.number_input(
                    "Child's current age",
                    min_value=0, max_value=20, value=6, step=1,
                )
                education_level = answers.get("education_level", "Primary")
                entry_age = cd.EDUCATION_ENTRY_AGE.get(education_level, 6)
                years_until = max(entry_age - child_age, 0)
                entry_year = cd.get_current_year() + years_until
                if years_until > 0:
                    st.markdown(f"""
                    <div class="entry-info">
                        <strong>Entry year:</strong> {years_until} years from now (year {entry_year})
                        — your child will enter <strong>{education_level}</strong> at age {entry_age}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="entry-info" style="border-color:#EF4444;">
                        <strong>Note:</strong> Your child is already past the entry age for {education_level}.
                        Cost is calculated from today.
                    </div>
                    """, unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["child_age"] = child_age
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:  # City → Calculate
                render_progress_bar(4, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which city will your child attend school in?</div>', unsafe_allow_html=True)
                city = st.selectbox("City", GoalBuilder.CITIES, index=GoalBuilder.CITIES.index("Jakarta Selatan") if "Jakarta Selatan" in GoalBuilder.CITIES else 0)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 2
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 4
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 4:  # Calculate
                render_progress_bar(5, total_steps)
                answers["city"] = answers.get("city", "Jakarta Selatan")
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Review your selections</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Level:** {answers.get('education_level', '-')}")
                    st.markdown(f"**School type:** {answers.get('school_type', '-')}")
                    st.markdown(f"**Child's age:** {answers.get('child_age', '-')}")
                with col2:
                    st.markdown(f"**City:** {answers.get('city', '-')}")
                    education_level = answers.get("education_level", "Primary")
                    child_age = answers.get("child_age", 6)
                    entry_age = cd.EDUCATION_ENTRY_AGE.get(education_level, 6)
                    years_until = max(entry_age - child_age, 0)
                    entry_year = cd.get_current_year() + years_until
                    school_type = answers.get("school_type", "Local Private")
                    inflation_rate = cd.EDUCATION_INFLATION_RATE.get(school_type, 0.08)
                    st.markdown(f"**Entry year:** {entry_year} ({years_until} years)")
                    st.markdown(f"**Inflation rate:** {inflation_rate * 100:.0f}%/yr")
                st.markdown("")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Education", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    # Show result immediately
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #7C3AED, #06B6D4) 1;">
                        <div style="text-align:center;">
                            <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div>
                            <div class="cost-display">{format_idr(profile.estimated_cost)}</div>
                            <div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">
                                {profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("&#8592; Proceed to **Feasibility Analysis** to check if this goal is achievable with your income.")
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── HIGHER EDUCATION ──────────────────────────────────────────
        elif goal_type == "Higher Education":
            render_progress_bar(current_step + 1, total_steps)

            if current_step == 0:  # Degree level
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What degree is your child aiming for?</div>', unsafe_allow_html=True)
                degree_level = st.radio(
                    "Degree level",
                    cd.HIGHER_ED_DEGREE_LEVELS,
                    index=None,
                    label_visibility="collapsed",
                )
                if st.button("Next →", type="primary"):
                    if degree_level:
                        answers["degree_level"] = degree_level
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # Location
                render_progress_bar(2, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Will they study in Indonesia or abroad?</div>', unsafe_allow_html=True)
                location = st.radio(
                    "Study location",
                    ["In Indonesia", "Abroad"],
                    index=None,
                    label_visibility="collapsed",
                )
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if location:
                            answers["study_location"] = location
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 2
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # Country (only if abroad)
                render_progress_bar(3, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                location = answers.get("study_location", "In Indonesia")
                if location == "Abroad":
                    st.markdown('<div class="step-title">Which country will they study in?</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="step-title">Study location confirmed: Indonesia</div>', unsafe_allow_html=True)
                country = st.selectbox(
                    "Country",
                    ["Indonesia"] + cd.HIGHER_ED_ABROAD_COUNTRIES,
                    index=None,
                    placeholder="Select country" if location == "Abroad" else None,
                )
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if country:
                            answers["country"] = country
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 3
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:  # Field of study
                render_progress_bar(4, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What field of study?</div>', unsafe_allow_html=True)
                field = st.selectbox(
                    "Field of study",
                    cd.HIGHER_ED_FIELDS,
                    index=None,
                    placeholder="Select field",
                )
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 2
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if field:
                            answers["field"] = field
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 4
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 4:  # Years until enrollment
                render_progress_bar(5, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="step-title">When does enrollment start?</div>', unsafe_allow_html=True)
                current_yr = cd.get_current_year()
                years_until = st.slider(
                    "Years until enrollment",
                    min_value=0, max_value=20, value=4, step=1,
                )
                enrollment_yr = current_yr + years_until
                st.markdown(f"""
                <div class="entry-info">
                    Enrollment year: <strong>{enrollment_yr}</strong>
                    ({years_until} year{"s" if years_until != 1 else ""} from now)
                </div>
                """, unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["years_until_enrollment"] = years_until
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 5
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 5:  # Calculate
                render_progress_bar(6, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Review your selections</div>', unsafe_allow_html=True)
                deg = answers.get("degree_level", "-")
                loc = answers.get("study_location", "-")
                country = answers.get("country", "-")
                field = answers.get("field", "-")
                yrs = answers.get("years_until_enrollment", 0)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Degree:** {deg}")
                    st.markdown(f"**Location:** {loc}")
                with col2:
                    st.markdown(f"**Country:** {country}")
                    st.markdown(f"**Field:** {field}")
                    st.markdown(f"**Enrollment:** {cd.get_current_year() + yrs}")
                st.markdown("")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Higher Education", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #7C3AED, #06B6D4) 1;">
                        <div style="text-align:center;">
                            <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div>
                            <div class="cost-display">{format_idr(profile.estimated_cost)}</div>
                            <div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">
                                {profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("&#8592; Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                if st.button("← Back"):
                    st.session_state["goal_step"] = 4
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── PROPERTY ─────────────────────────────────────────────────
        elif goal_type == "Property":
            render_progress_bar(current_step + 1, total_steps)
            current_year = cd.get_current_year()

            if current_step == 0:  # Property type
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Property</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What type of property?</div>', unsafe_allow_html=True)
                property_type = st.radio(
                    "Property type",
                    cd.PROPERTY_TYPES,
                    index=None,
                    label_visibility="collapsed",
                )
                if st.button("Next →", type="primary"):
                    if property_type:
                        answers["property_type"] = property_type
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # City
                render_progress_bar(2, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Property</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which city?</div>', unsafe_allow_html=True)
                city = st.selectbox("City", GoalBuilder.CITIES, index=0)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 2
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # Area
                render_progress_bar(3, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Property</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which neighbourhood? (optional)</div>', unsafe_allow_html=True)
                area = st.text_input("Area / Neighbourhood (optional)", placeholder="e.g. Kemang, Senayan, Menteng", label_visibility="collapsed")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["area"] = area or ""
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:  # Size
                render_progress_bar(4, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Property</div>', unsafe_allow_html=True)
                property_type = answers.get("property_type", "Apartment")
                size_options = cd.PROPERTY_SIZES_BY_TYPE.get(property_type, list(cd.APARTMENT_SIZES.keys()))
                st.markdown(f'<div class="step-title">What size is the property?</div>', unsafe_allow_html=True)
                size = st.selectbox("Size", size_options, index=None, placeholder="Select size")
                show_custom_building = (size == "Custom" and property_type in ("Landed House", "Shophouse / Ruko"))
                show_custom_land = (size == "Custom" and property_type in ("Landed House", "Land Only", "Shophouse / Ruko"))
                custom_building = None
                custom_total = None
                if show_custom_building:
                    custom_building = st.number_input("Building area (sqm)", min_value=1, value=100, step=1)
                if show_custom_land:
                    custom_total = st.number_input("Total land area (sqm)", min_value=1, value=200, step=1)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 2
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if size:
                            answers["size"] = size
                            if custom_building:
                                answers["custom_building_sqm"] = custom_building
                            if custom_total:
                                answers["custom_total_sqm"] = custom_total
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 4
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 4:  # Target year
                render_progress_bar(5, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Property</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="step-title">When do you plan to purchase?</div>', unsafe_allow_html=True)
                target_year = st.slider(
                    "Target purchase year",
                    min_value=current_year,
                    max_value=current_year + 20,
                    value=current_year + 10,
                    step=1,
                )
                st.markdown(f"""
                <div class="entry-info">
                    Target: <strong>{target_year}</strong>
                    <span class="current-year-badge">{current_year}</span>
                </div>
                """, unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["target_year"] = target_year
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 5
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 5:  # Calculate
                render_progress_bar(6, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Property</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Review your selections</div>', unsafe_allow_html=True)
                ptype = answers.get("property_type", "-")
                city = answers.get("city", "-")
                size = answers.get("size", "-")
                yr = answers.get("target_year", current_year)
                price_per_sqm = cd.APARTMENT_PRICE_PER_SQM.get(city, 0)
                inflation_rate = cd.PROPERTY_INFLATION_RATE
                years = max(yr - current_year, 0)
                # Fetch live data for this city
                prop_result, _ = get_all_price_data()
                JABODETABEK = {"Depok", "Bekasi", "Tangerang", "Tangerang Selatan", "Bogor"}
                if city in JABODETABEK:
                    pt = prop_result.jabo_prices.get(city)
                else:
                    pt = prop_result.prices.get(city)
                price_source = pt.source if pt else "Baseline"
                price_fresh = prop_result.freshness.display_text() if pt else f"Baseline estimate from cost_data.py"
                if pt:
                    price_per_sqm = pt.price_per_sqm
                    price_source = f"{pt.source} ({pt.reliability})"
                    price_fresh = prop_result.freshness.display_text()
                st.markdown(f"**Type:** {ptype} &nbsp;&nbsp; **City:** {city}")
                st.markdown(f"**Size:** {size} &nbsp;&nbsp; **Target year:** {yr}")
                st.markdown(f"**Price/sqm today:** {format_idr(price_per_sqm)} &nbsp;<span style='color:#7C3AED;font-size:0.8rem;'>({price_source})</span>")
                st.markdown(f"**Inflation:** {inflation_rate * 100:.0f}%/yr &nbsp;&nbsp; **Years to purchase:** {years}")
                st.caption(f"_{price_fresh}_")
                st.markdown("")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Property", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #7C3AED, #06B6D4) 1;">
                        <div style="text-align:center;">
                            <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div>
                            <div class="cost-display">{format_idr(profile.estimated_cost)}</div>
                            <div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">
                                {profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("&#8592; Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                if st.button("← Back"):
                    st.session_state["goal_step"] = 4
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── RETIREMENT ──────────────────────────────────────────────
        elif goal_type == "Retirement":
            render_progress_bar(current_step + 1, total_steps)

            if current_step == 0:  # Current age
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">How old are you now?</div>', unsafe_allow_html=True)
                current_age = st.number_input("Current age", min_value=18, max_value=70, value=25, step=1)
                if st.button("Next →", type="primary"):
                    answers["current_age"] = current_age
                    st.session_state["goal_step_answers"] = answers
                    st.session_state["goal_step"] = 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # Retirement age
                render_progress_bar(2, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">At what age do you want to retire?</div>', unsafe_allow_html=True)
                current_age = answers.get("current_age", 25)
                retirement_age = st.number_input(
                    "Retirement age",
                    min_value=current_age + 1, max_value=80, value=55, step=1,
                )
                years_to_save = retirement_age - current_age
                st.markdown(f"""
                <div class="entry-info">
                    You have <strong>{years_to_save} years</strong> to build your retirement fund
                </div>
                """, unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["retirement_age"] = retirement_age
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 2
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # City
                render_progress_bar(3, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which city do you plan to retire in?</div>', unsafe_allow_html=True)
                city = st.selectbox("Retirement city", GoalBuilder.CITIES, index=0)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:  # Lifestyle
                render_progress_bar(4, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What lifestyle do you want in retirement?</div>', unsafe_allow_html=True)
                lifestyle = st.radio(
                    "Lifestyle",
                    cd.RETIREMENT_LIFESTYLE_OPTIONS,
                    index=None,
                    label_visibility="collapsed",
                )
                show_custom = (lifestyle and "Custom" in lifestyle)
                if show_custom:
                    custom_monthly = st.number_input(
                        "Your target monthly spend (IDR)",
                        min_value=1_000_000, max_value=500_000_000, value=15_000_000, step=500_000,
                    )
                    answers["custom_monthly"] = custom_monthly
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 2
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if lifestyle:
                            answers["lifestyle"] = lifestyle
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 4
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 4:  # Life expectancy
                render_progress_bar(5, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What life expectancy do you assume?</div>', unsafe_allow_html=True)
                life_options = [75, 80, 85, "Custom — enter my own assumption"]
                life_display = ["75 years", "80 years", "85 years", "Custom"]
                life_exp_idx = st.selectbox(
                    "Life expectancy",
                    range(len(life_options)),
                    format_func=lambda i: life_display[i],
                    index=1,
                )
                life_expectancy = life_options[life_exp_idx]
                if life_expectancy == "Custom — enter my own assumption":
                    life_expectancy = st.number_input(
                        "Your life expectancy assumption",
                        min_value=60, max_value=100, value=80, step=1,
                    )
                current_age = answers.get("current_age", 25)
                retirement_age = answers.get("retirement_age", 55)
                years_in_retirement = max(life_expectancy - retirement_age, 0)
                st.markdown(f"""
                <div class="entry-info">
                    Retirement duration: <strong>{years_in_retirement} years</strong>
                    (age {retirement_age} → {life_expectancy})
                </div>
                """, unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["life_expectancy"] = life_expectancy
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 5
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 5:  # Calculate
                render_progress_bar(6, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Review your selections</div>', unsafe_allow_html=True)
                cur = answers.get("current_age", 0)
                ret = answers.get("retirement_age", 0)
                city = answers.get("city", "-")
                lifestyle = answers.get("lifestyle", "-")
                life_exp = answers.get("life_expectancy", 80)
                st.markdown(f"**Current age:** {cur} &nbsp;&nbsp; **Retirement age:** {ret}")
                st.markdown(f"**City:** {city} &nbsp;&nbsp; **Lifestyle:** {lifestyle}")
                st.markdown(f"**Life expectancy:** {life_exp}")
                st.markdown("")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Retirement", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #7C3AED, #06B6D4) 1;">
                        <div style="text-align:center;">
                            <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div>
                            <div class="cost-display">{format_idr(profile.estimated_cost)}</div>
                            <div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">
                                {profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("&#8592; Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                if st.button("← Back"):
                    st.session_state["goal_step"] = 4
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── EMERGENCY FUND ──────────────────────────────────────────
        elif goal_type == "Emergency Fund":
            render_progress_bar(current_step + 1, total_steps)

            if current_step == 0:  # Monthly salary
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Emergency Fund</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What is your monthly take-home salary?</div>', unsafe_allow_html=True)
                monthly_salary = st.number_input(
                    "Monthly take-home salary (IDR)",
                    min_value=500_000, max_value=500_000_000, value=15_000_000, step=500_000,
                )
                bracket = get_salary_bracket(monthly_salary)
                st.markdown(f'<div style="color:#7C3AED;font-size:0.85rem;font-weight:600;">Career bracket: {bracket}</div>', unsafe_allow_html=True)
                if st.button("Next →", type="primary"):
                    answers["monthly_salary"] = monthly_salary
                    st.session_state["goal_step_answers"] = answers
                    st.session_state["goal_step"] = 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # Monthly expenses
                render_progress_bar(2, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Emergency Fund</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What are your monthly fixed expenses?</div>', unsafe_allow_html=True)
                monthly_expenses = st.number_input(
                    "Monthly fixed expenses (IDR)",
                    min_value=100_000, max_value=500_000_000, value=5_000_000, step=500_000,
                    help="Rent, utilities, food, transport, loan repayments",
                )
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["monthly_expenses"] = monthly_expenses
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 2
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # Coverage → Calculate
                render_progress_bar(3, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Emergency Fund</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">How many months of expenses should this cover?</div>', unsafe_allow_html=True)
                coverage = st.radio(
                    "Coverage duration",
                    cd.EMERGENCY_FUND_COVERAGE_OPTIONS,
                    index=None,
                    label_visibility="collapsed",
                )
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown("")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    answers["coverage"] = coverage
                    gb = GoalBuilder()
                    profile = gb.build_goal("Emergency Fund", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #7C3AED, #06B6D4) 1;">
                        <div style="text-align:center;">
                            <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Emergency Fund Target</div>
                            <div class="cost-display">{format_idr(profile.estimated_cost)}</div>
                            <div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">
                                {profile.description}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("&#8592; Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── WEDDING ────────────────────────────────────────────────
        elif goal_type == "Wedding":
            render_progress_bar(current_step + 1, total_steps)
            current_year = cd.get_current_year()

            if current_step == 0:  # Scale
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">How many guests are you planning for?</div>', unsafe_allow_html=True)
                scale = st.radio(
                    "Wedding scale",
                    cd.WEDDING_SCALES,
                    index=None,
                    label_visibility="collapsed",
                )
                if st.button("Next →", type="primary"):
                    if scale:
                        answers["scale"] = scale
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # City
                render_progress_bar(2, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">In which city will the wedding be held?</div>', unsafe_allow_html=True)
                city = st.selectbox("City", GoalBuilder.CITIES, index=0)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 2
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # Target year
                render_progress_bar(3, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">When is the target date?</div>', unsafe_allow_html=True)
                target_year = st.slider(
                    "Target year",
                    min_value=current_year,
                    max_value=current_year + 10,
                    value=current_year + 2,
                    step=1,
                )
                years = max(target_year - current_year, 0)
                st.markdown(f"""
                <div class="entry-info">
                    <strong>{years} year{"s" if years != 1 else ""}</strong> from now (year {target_year})
                </div>
                """, unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["target_year"] = target_year
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:  # Venue
                render_progress_bar(4, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What type of venue?</div>', unsafe_allow_html=True)
                venue = st.radio(
                    "Venue",
                    cd.WEDDING_VENUES,
                    index=None,
                    label_visibility="collapsed",
                )
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 2
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if venue:
                            answers["venue"] = venue
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 4
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 4:  # Entertainment → Calculate
                render_progress_bar(5, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What entertainment are you planning?</div>', unsafe_allow_html=True)
                entertainment = st.radio(
                    "Entertainment",
                    cd.WEDDING_ENTERTAINMENT,
                    index=None,
                    label_visibility="collapsed",
                )
                st.markdown("")
                st.markdown("**Catering:** Standard (included in base cost)")
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown("")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    answers["entertainment"] = entertainment
                    answers["catering"] = "Standard"
                    gb = GoalBuilder()
                    profile = gb.build_goal("Wedding", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #7C3AED, #06B6D4) 1;">
                        <div style="text-align:center;">
                            <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div>
                            <div class="cost-display">{format_idr(profile.estimated_cost)}</div>
                            <div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">
                                {profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("&#8592; Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── CUSTOM ─────────────────────────────────────────────────
        elif goal_type == "Custom":
            render_progress_bar(current_step + 1, total_steps)

            if current_step == 0:  # Goal name
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Custom Goal</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What is this goal called?</div>', unsafe_allow_html=True)
                goal_name = st.text_input("Goal name", placeholder="e.g. Starting a business, Buying a car...", label_visibility="collapsed")
                if st.button("Next →", type="primary"):
                    if goal_name:
                        answers["goal_name"] = goal_name
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # Amount mode
                render_progress_bar(2, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Custom Goal</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Do you know the target amount?</div>', unsafe_allow_html=True)
                amount_mode = st.radio(
                    "Amount type",
                    ["I know the amount — I'll enter it directly", "Help me estimate — I'll describe the goal"],
                    index=None,
                    label_visibility="collapsed",
                )
                show_amount_input = (amount_mode == "I know the amount — I'll enter it directly")
                if show_amount_input:
                    target_amount = st.number_input(
                        "Target amount (IDR)",
                        min_value=0, value=100_000_000, step=5_000_000,
                    )
                    answers["target_amount"] = target_amount
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if amount_mode:
                            answers["amount_mode"] = amount_mode
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 2
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # Target year → Calculate
                render_progress_bar(3, total_steps)
                st.markdown('<div class="step-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-label">Custom Goal</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">When is the target year?</div>', unsafe_allow_html=True)
                current_year = cd.get_current_year()
                target_year = st.slider(
                    "Target year",
                    min_value=current_year,
                    max_value=current_year + 30,
                    value=current_year + 5,
                    step=1,
                )
                years = max(target_year - current_year, 0)
                st.markdown(f"""
                <div class="entry-info">
                    <strong>{years} year{"s" if years != 1 else ""}</strong> from now (year {target_year})
                </div>
                """, unsafe_allow_html=True)
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown("")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    answers["target_year"] = target_year
                    gb = GoalBuilder()
                    profile = gb.build_goal("Custom", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #7C3AED, #06B6D4) 1;">
                        <div style="text-align:center;">
                            <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div>
                            <div class="cost-display">{format_idr(profile.estimated_cost)}</div>
                            <div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">
                                {profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("&#8592; Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        # No goal type selected — reset state
        if st.button("Start over"):
            for key in ["selected_goal", "goal_type", "goal_step", "goal_step_answers", "goal_cost_result"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: FEASIBILITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

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
            min_value=1_000_000, max_value=500_000_000, value=15_000_000, step=500_000,
            help="Net monthly income after tax and deductions",
        )
        bracket = get_salary_bracket(monthly_salary)
        st.markdown(f'<div style="color:#7C3AED;font-size:0.85rem;font-weight:600;">Career bracket: {bracket}</div>', unsafe_allow_html=True)
        income_growth = st.slider(
            "Expected Annual Income Growth Rate",
            min_value=0.0, max_value=0.30, value=0.08, step=0.005,
            format="%.1f%%",
        )
    with col2:
        st.markdown("#### Goal Summary")
        st.markdown(f"""
        <div class="metric-col">
            <div class="metric-val">{format_idr(goal['estimated_cost'])}</div>
            <div class="metric-lbl">Projected Goal Cost</div>
        </div>
        <div style="height:0.75rem;"></div>
        <div class="metric-col">
            <div class="metric-val" style="font-size:1.25rem;">{goal['timeline_years']} years</div>
            <div class="metric-lbl">Years to Goal</div>
        </div>
        <div style="height:0.75rem;"></div>
        <div class="metric-col">
            <div class="metric-val" style="font-size:1rem;">{goal['goal_type']}</div>
            <div class="metric-lbl">Goal Type</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("Analyse Feasibility", type="primary"):
        # Fetch live living cost data for the goal's city
        _, living_result = get_all_price_data()
        city = goal.get("city", "")
        lc = living_result.costs.get(city)
        if lc:
            monthly_living = lc.monthly_cost
            living_source = f"{lc.source} ({lc.reliability})"
            living_fresh = living_result.freshness.display_text()
        else:
            monthly_living = LIVING_COST_MONTHLY.get(city, 6_000_000)
            living_source = "Baseline"
            living_fresh = "Baseline estimate from cost_data.py"
        monthly_required = goal["estimated_cost"] / (goal["timeline_years"] * 12)
        disposable = max(monthly_salary - monthly_living, 1)
        ratio = min(monthly_required / disposable, 2.0)

        if ratio < 0.30:
            verdict = "green"
        elif ratio < 0.50:
            verdict = "yellow"
        else:
            verdict = "red"

        result = {
            "verdict": verdict,
            "ratio": ratio,
            "monthly_required": monthly_required,
            "monthly_living": monthly_living,
            "monthly_living_source": living_source,
            "monthly_living_fresh": living_fresh,
            "disposable": disposable,
            "investment_pct_of_salary": monthly_required / monthly_salary,
        }

        verdict_text_map = {
            "green": "ACHIEVABLE",
            "yellow": "ACHIEVABLE WITH CONDITIONS",
            "red": "NOT ACHIEVABLE AS STATED",
        }
        verdict_class_map = {"green": "verdict-green", "yellow": "verdict-yellow", "red": "verdict-red"}
        icon_map = {"green": "&#9989;", "yellow": "&#9888;", "red": "&#10060;"}

        vc = verdict_class_map.get(verdict, "verdict-green")
        vt = verdict_text_map.get(verdict, "ACHIEVABLE")
        vi = icon_map.get(verdict, "&#9989;")

        st.markdown(f"""
        <div class="vestara-card {vc}">
            <div class="verdict-text">
                <div style="font-size:3rem;margin-bottom:0.5rem;">{vi}</div>
                <div style="font-size:2rem;font-weight:800;color:#F8FAFC;">{vt}</div>
                <div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">Investment ratio: {ratio:.1%}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f"""<div class="metric-col"><div class="metric-val">{format_idr(monthly_living)}</div><div class="metric-lbl">Monthly Living Cost</div><div style="font-size:0.7rem;color:#7C3AED;">{living_source}</div></div>""", unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""<div class="metric-col"><div class="metric-val">{format_idr(disposable)}</div><div class="metric-lbl">Disposable Income</div></div>""", unsafe_allow_html=True)
        with mc3:
            st.markdown(f"""<div class="metric-col"><div class="metric-val">{format_idr(monthly_required)}</div><div class="metric-lbl">Required Monthly Investment</div></div>""", unsafe_allow_html=True)

        st.session_state["feasibility_result"] = result
        st.session_state["monthly_contribution"] = monthly_required
        st.session_state["salary"] = monthly_salary
        st.session_state["income_growth"] = income_growth

        if verdict in ("yellow", "red"):
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
            </div>
            """, unsafe_allow_html=True)

            from vestara.src.engine.scenario_optimizer import run_scenario_analysis

            scenarios = run_scenario_analysis(
                goal_cost=goal["estimated_cost"],
                monthly_salary=monthly_salary,
                monthly_living_cost=monthly_living,
                current_timeline=goal["timeline_years"],
                current_contribution=monthly_required,
                goal_type=goal["goal_type"],
                current_city=goal.get("city", "Jakarta Selatan"),
            )

            if scenarios.blocked_reason:
                st.error(f"&#9888; Scenario Optimizer Blocked: {scenarios.blocked_reason}")
                st.stop()

            if scenarios.scenarios:
                for i, s in enumerate(scenarios.scenarios):
                    pill_cls = "green" if s.verdict == "green" else ("yellow" if s.verdict == "yellow" else "red")
                    with st.expander(f"&#128279; {s.lever.upper()}: {s.adjustment}", expanded=(i == 0)):
                        st.write(s.change_description)
                        st.write(f"New investment ratio: **{s.new_ratio:.1%}**")
                        st.markdown(f"Verdict: <span class='verdict-pill {pill_cls}'>{s.verdict.upper()}</span>", unsafe_allow_html=True)

            # ── Peer Benchmarking ──────────────────────────────────────
            st.markdown("---")
            st.markdown("#### Peer Benchmarking")
            st.caption("Based on 2,000 synthetic Vestara users with similar financial profiles")

            clusterer = get_clusterer()
            city_living_cost_index = int(monthly_living / 1_000_000)
            cluster_result = clusterer.predict(
                monthly_salary=monthly_salary,
                city_living_cost_index=city_living_cost_index,
                goal_cost=goal["estimated_cost"],
                timeline_years=goal["timeline_years"],
                income_growth_rate=income_growth,
                monthly_living_cost=monthly_living,
                disposable_income=disposable,
            )

            border_style = f"border:2px solid {cluster_result.color};box-shadow:0 0 20px({cluster_result.color}33);"
            st.markdown(f"""
            <div class="vestara-card" style="{border_style}">
                <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
                    <div style="font-size:2.5rem;">{cluster_result.icon}</div>
                    <div>
                        <div style="font-size:1.1rem;font-weight:700;color:#F8FAFC;">{cluster_result.archetype}</div>
                        <div style="font-size:0.8rem;color:#94A3B8;">{cluster_result.peer_count:,} synthetic peers in this cluster</div>
                    </div>
                </div>
                <div style="font-size:0.9rem;color:#94A3B8;line-height:1.6;">{cluster_result.description}</div>
            </div>
            """, unsafe_allow_html=True)

            # User vs peers comparison
            uvp = cluster_result.user_vs_peers
            st.markdown("**How you compare to your peers:**")
            comparison_cols = st.columns(4)
            comparisons = [
                ("Salary", uvp["salary_vs_peers_pct"], "vs median peer salary"),
                ("Disposable Income", uvp["disposable_vs_peers_pct"], "vs median peer disposable"),
                ("Goal Size", uvp["goal_vs_peers_pct"], "vs median peer goal"),
                ("Timeline", uvp["timeline_vs_peers_pct"], "vs median peer timeline"),
            ]
            for col, (label, pct, caption) in zip(comparison_cols, comparisons):
                with col:
                    cls_color = "#10B981" if pct > 0 else ("#EF4444" if pct < -10 else "#F59E0B")
                    arrow = "&#9650;" if pct > 0 else ("&#9660;" if pct < 0 else "&#8226;")
                    st.markdown(f"""
                    <div class="metric-col">
                        <div class="metric-val" style="font-size:1.1rem;color:{cls_color};">{arrow} {abs(pct):.1f}%</div>
                        <div class="metric-lbl">{label}</div>
                        <div style="font-size:0.7rem;color:#94A3B8;">{caption}</div>
                    </div>
                    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: RISK PROFILER
# ══════════════════════════════════════════════════════════════════════════════

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
    <div style="margin-bottom:0.25rem;"><span style="color:#7C3AED;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;">Questions {start + 1}–{end} of {len(RISK_QUESTIONS)}</span></div>
    <div class="progress-track"><div class="progress-fill" style="width:{int(progress_val * 100)}%;"></div></div>
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
        st.markdown("---")
        st.success("&#127881; All questions answered!")
        rp = RiskProfiler()
        for qid, score in answers.items():
            rp.submit_answer(qid, score)
        profile = rp.get_profile()

        score_cls = "green" if profile.percentage >= 70 else ("yellow" if profile.percentage >= 40 else "red")
        st.markdown(f"""
        <div class="profile-card" style="margin-bottom:1.5rem;">
            <div class="score-circle {score_cls}">{profile.score}/{profile.max_score}</div>
            <div style="text-align:center;margin-top:0.75rem;">
                <span class="verdict-pill {score_cls}" style="font-size:0.85rem;">{profile.percentage}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        border_cls = "konservatif" if profile.profile == "Konservatif" else ("moderat" if profile.profile == "Moderat" else "agresif")
        st.markdown(f"""
        <div class="profile-card {border_cls}" style="margin-bottom:1.5rem;">
            <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Your Risk Profile</div>
            <div style="font-size:1.75rem;font-weight:800;color:#F8FAFC;margin-bottom:0.5rem;">{profile.profile}</div>
            <div style="color:#94A3B8;font-size:0.9rem;">{profile.description}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Recommended Asset Allocation")
        from vestara.portfolio.optimizer import INSTRUMENTS
        alloc_data = []
        for instrument, pct in profile.allocation.items():
            alloc_data.append({"Instrument": instrument.replace("_", " ").title(), "Allocation": f"{pct}%"})
        st.dataframe(pd.DataFrame(alloc_data), use_container_width=True, hide_index=True)

        st.session_state["risk_profile"] = profile.to_dict()
        st.session_state["risk_profile_set"] = True


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: PORTFOLIO RECOMMENDATION
# ══════════════════════════════════════════════════════════════════════════════

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

    with st.expander("&#128279; Initial Disclosure / Penyingkapan Informasi Awal (POJK 21/2011)"):
        st.markdown("""
        **Vestara DOES:** Estimate goal costs, provide illustrative allocations, show projected growth.
        **Vestara DOES NOT:** Provide personalised advice, process transactions, guarantee accuracy.
        **Model limitations:** Trained on synthetic data; results are illustrative, not guarantees.
        """)
        st.markdown("&#128220; **OJK Investor Education:** [sifikasiuangmu.ojk.go.id](https://sifikasiuangmu.ojk.go.id)")

    st.markdown("")
    st.markdown(f"#### Illustrative Allocation — **{goal['goal_type']}** goal")
    st.markdown(f"**Risk Profile: {risk['profile']}** &nbsp;&nbsp; **Monthly investment: {format_idr(monthly_contribution)}**")

    from vestara.portfolio.optimizer import build_portfolio
    result = build_portfolio(
        risk_profile=risk["profile"],
        monthly_contribution=monthly_contribution,
        goal_amount=goal["estimated_cost"],
        timeline_years=goal["timeline_years"],
    )

    equity_pct = next((a.percentage for a in result.allocations if a.instrument == "reksa_dana_equity"), 0)
    is_property_short = (goal["goal_type"] == "Property" and goal["timeline_years"] < 5)
    if is_property_short and equity_pct > 20:
        st.warning("&#9888; **Property Goal Warning:** Equity funds can drop significantly before your target date. Consider a more conservative allocation to reduce timing risk.")

    st.markdown("")
    st.markdown("#### Monthly Allocation")
    from vestara.portfolio.optimizer import INSTRUMENT_LABELS
    alloc_rows = []
    for a in result.allocations:
        risk_label = INSTRUMENT_RISK_LABELS.get(a.instrument, "")
        badge_cls = "risk-high" if "High" in risk_label else ("risk-medium" if "Medium" in risk_label else "risk-low")
        alloc_rows.append({
            "Instrument": INSTRUMENT_LABELS.get(a.instrument, a.instrument),
            "%": f"{a.percentage:.1f}%",
            "Monthly": format_idr(a.monthly_amount),
            "Expected Return": f"{a.expected_return:.1%}",
            "Risk": risk_label,
        })
    st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-col"><div class="metric-val" style="font-size:1.1rem;">{result.blended_return:.2%}</div><div class="metric-lbl">Blended Expected Return</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-col"><div class="metric-val" style="font-size:1.1rem;">{result.blended_volatility:.2%}</div><div class="metric-lbl">Blended Volatility</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-col"><div class="metric-val" style="font-size:1rem;">{format_idr(result.projected_value_at_goal_year)}</div><div class="metric-lbl">Projected Value at Goal Year</div></div>""", unsafe_allow_html=True)

    shortfall = result.goal_amount - result.projected_value_at_goal_year
    if shortfall > 0:
        st.error(f"&#9888; Projected shortfall of **{format_idr(shortfall)}** — consider increasing monthly contribution or extending timeline.")
    else:
        st.success(f"&#9989; On track — projected value exceeds goal by **{format_idr(abs(shortfall))}**")

    st.markdown("")
    st.markdown("#### Growth Trajectory — Illustrative")
    traj_df = pd.DataFrame([{"Year": yr, "Projected Value (IDR)": val} for yr, val in result.yearly_trajectory])
    traj_df = traj_df.set_index("Year")
    st.line_chart(traj_df, y="Projected Value (IDR)", height=320)
    st.caption(f"Goal target: **{format_idr(result.goal_amount)}** at year {result.timeline_years} | Projected: **{format_idr(result.projected_value_at_goal_year)}** (illustrative only)")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📈 Dashboard":
    st.title("Dashboard")

    has_goal = st.session_state.get("goal_set", False)
    has_feasibility = st.session_state.get("feasibility_result") is not None
    has_risk = st.session_state.get("risk_profile_set", False)

    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, label, val in [
        (sc1, "Goal Set", has_goal),
        (sc2, "Feasibility Analysed", has_feasibility),
        (sc3, "Risk Profiled", has_risk),
    ]:
        with col:
            color = "#10B981" if val else "#EF4444"
            icon = "&#9989;" if val else "&#10060;"
            st.markdown(f"""
            <div class="summary-card">
                <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">{label}</div>
                <div style="font-size:1.25rem;font-weight:700;color:{color};">{icon} {'Yes' if val else 'Not yet'}</div>
            </div>
            """, unsafe_allow_html=True)

    overall = [has_goal, has_feasibility, has_risk].count(True)
    health_cls = "excellent" if overall == 3 else ("good" if overall == 2 else "needs_work")
    health_label = "Excellent" if overall == 3 else ("Good" if overall == 2 else "Needs Work")
    with sc4:
        st.markdown(f"""
        <div class="summary-card">
            <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em;color:#94A3B8;margin-bottom:0.5rem;">Overall Health</div>
            <div class="health-score {health_cls}" style="font-size:1.5rem;">{health_label}</div>
        </div>
        """, unsafe_allow_html=True)

    if has_goal:
        goal = st.session_state["goal_profile"]
        st.markdown("")
        st.markdown("---")
        st.markdown("#### Your Goal Summary")
        verdict_pill_cls = "green"
        if has_feasibility:
            fr = st.session_state.get("feasibility_result", {})
            verdict_pill_cls = fr.get("verdict", "green")
        st.markdown(f"""
        <div class="goal-progress-card">
            <div class="goal-name">&#127968; {goal['goal_type']}</div>
            <div class="goal-meta">
                <span>Timeline: {goal['timeline_years']} years</span> &middot;
                <span>Amount: {format_idr(goal['estimated_cost'])}</span>
            </div>
            <div style="margin-top:0.75rem;">
                <span class="verdict-pill {verdict_pill_cls}">
                    {f"Investment ratio: {st.session_state.get('feasibility_result', {}).get('ratio', 0):.1%}" if has_feasibility else "Pending analysis"}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if has_feasibility:
        st.markdown("")
        st.markdown("---")
        st.markdown("#### Feasibility Summary")
        st.json(st.session_state.get("feasibility_result", {}))

    if has_risk:
        st.markdown("")
        st.markdown("---")
        st.markdown("#### Risk Profile")
        st.json(st.session_state.get("risk_profile", {}))

    if all([has_goal, has_feasibility, has_risk]):
        st.balloons()
        st.success("&#127881; Your complete financial plan is ready! Head to **Portfolio Recommendation** to see your investment allocation.")
