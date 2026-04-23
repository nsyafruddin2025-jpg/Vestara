"""
Vestara — Goal-First Investment Platform
Streamlit UI — wraps Goal Builder, Feasibility Engine, and Portfolio Optimizer.
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os

from vestara.src.engine.goal_builder import GoalBuilder
from vestara.src.engine.risk_profiler import RiskProfiler, RISK_QUESTIONS, INSTRUMENT_LABELS
from vestara.src.portfolio.optimizer import build_portfolio, INSTRUMENT_LABELS as PORT_LABELS
from vestara.data.cost_data import LIVING_COST_MONTHLY, GOAL_TYPES

# Page config
st.set_page_config(
    page_title="Vestara — Plan Your Life, Then Your Investment",
    page_icon="🏠",
    layout="wide",
)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../../models")
SYNTHETIC_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/synthetic_training_data.csv")


# ── Model loader ────────────────────────────────────────────────────────────────

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


# ── Verdict display ─────────────────────────────────────────────────────────────

def verdict_badge(verdict: str) -> str:
    colors = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
    labels = {"green": "Achievable", "yellow": "Achievable With Conditions", "red": "Not Achievable As Stated"}
    return f"{colors.get(verdict, '⚪')} **{labels.get(verdict, verdict)}**"


def render_verdict(verdict: str, ratio: float, monthly_required: float, monthly_salary: float):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Verdict", verdict.replace("green", "🟢 Green").replace("yellow", "🟡 Yellow").replace("red", "🔴 Red"))
    with col2:
        st.metric("Monthly Investment Needed", f"Rp {monthly_required:,.0f}")
    with col3:
        st.metric("Investment-to-Salary Ratio", f"{ratio:.1%}")


# ── Sidebar navigation ─────────────────────────────────────────────────────────

st.sidebar.title("🏠 Vestara")
st.sidebar.caption("Goal-first investment planning for Indonesia")
page = st.sidebar.radio("Go to", [
    "🏗️ Goal Builder",
    "📊 Feasibility Analysis",
    "📋 Risk Profiler",
    "💼 Portfolio Recommendation",
    "📈 Dashboard",
])


# ── Page 1: Goal Builder ────────────────────────────────────────────────────────

if page == "🏗️ Goal Builder":
    st.title("🏗️ Goal Builder")
    st.markdown("### Tell us about your life goal")

    col1, col2 = st.columns([1, 1])
    with col1:
        goal_type = st.selectbox("Goal Type", GOAL_TYPES)
        city = st.selectbox("City", list(LIVING_COST_MONTHLY.keys()))

    st.markdown("---")
    st.markdown("#### Goal Details")

    answers = {}

    if goal_type == "Property":
        size_options = [
            "Studio / 1BR (24-36 sqm)",
            "2BR Standard (45-54 sqm)",
            "2BR Large / 3BR (70-90 sqm)",
            "Large / Penthouse (90-150 sqm)",
        ]
        answers["property_size"] = st.selectbox("Unit Size", size_options)
        location_detail = st.text_input("Neighbourhood (optional)", placeholder="e.g. Kemang, Senayan")
        answers["location_detail"] = location_detail

    elif goal_type == "Education":
        answers["education_level"] = st.selectbox("Education Level", [
            "TK / SD (Elementary)", "SMP (Junior High)", "SMA / SMK (Senior High)"
        ])
        answers["school_tier"] = st.selectbox("School Type", [
            "Local Private (J煲0-15M/yr)", "Mid-tier Private (15-30M/yr)",
            "Premium Private (30-60M/yr)", "International School (60-150M/yr)"
        ])

    elif goal_type == "Retirement":
        answers["current_age"] = st.number_input("Your Current Age", min_value=18, max_value=65, value=25)
        answers["retirement_age"] = st.number_input("Target Retirement Age", min_value=45, max_value=75, value=55)
        answers["retirement"] = st.selectbox("Desired Lifestyle", [
            "Basic (2-3M/month)", "Comfortable (4-6M/month)", "Premium (7-10M/month)"
        ])

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
        answers["months_covered"] = st.selectbox("Coverage", [
            "3 months (minimum)", "6 months (standard)", "12 months (conservative)"
        ])

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
                "Describe your goal", placeholder="e.g. I want to start a café franchise..."
            )
            answers["custom_amount"] = st.number_input(
                "Estimated amount if known (IDR, optional)", min_value=0, value=0, step=5_000_000
            )

    answers["timeline_years"] = st.slider("Investment Timeline (years)", 1, 40, 10)

    st.markdown("---")

    if st.button("🎯 Estimate Goal Cost", type="primary"):
        gb = GoalBuilder()
        profile = gb.build_goal(goal_type, city, answers)

        st.success(f"### Estimated Cost: Rp {profile.estimated_cost:,.0f}")
        st.caption(f"**{profile.description}** | {profile.timeline_years} years")

        # Store in session state
        st.session_state["goal_profile"] = profile.to_dict()
        st.session_state["goal_set"] = True

        st.info("👈 Proceed to **Feasibility Analysis** to check if this goal is achievable with your income.")


# ── Page 2: Feasibility Analysis ────────────────────────────────────────────────

elif page == "📊 Feasibility Analysis":
    st.title("📊 Feasibility Analysis")
    st.markdown("### How achievable is your goal?")

    if "goal_set" not in st.session_state:
        st.warning("⚠️ Please complete the **Goal Builder** first.")
        st.stop()

    goal = st.session_state["goal_profile"]

    col1, col2 = st.columns(2)
    with col1:
        monthly_salary = st.number_input(
            "Monthly Take-Home Salary (IDR)", min_value=1_000_000,
            max_value=500_000_000, value=15_000_000, step=500_000,
            help="Your net monthly income after taxes and deductions"
        )
        income_growth = st.slider(
            "Expected Annual Income Growth Rate",
            min_value=0.0, max_value=0.30, value=0.08, step=0.005,
            format="%.1f%%", help="Average annual salary increase you expect over the investment horizon"
        )
    with col2:
        st.metric("Goal Amount", f"Rp {goal['estimated_cost']:,.0f}")
        st.metric("Timeline", f"{goal['timeline_years']} years")
        st.metric("Goal Type", goal["goal_type"])
        st.metric("City", goal["city"])

    st.markdown("---")

    if st.button("🔍 Analyse Feasibility", type="primary"):
        result = compute_feasibility(
            monthly_salary=monthly_salary,
            city=goal["city"],
            goal_cost=goal["estimated_cost"],
            timeline_years=goal["timeline_years"],
            income_growth_rate=income_growth,
        )

        render_verdict(
            result["verdict"],
            result["ratio"],
            result["monthly_required"],
            monthly_salary,
        )

        st.markdown("---")
        st.markdown("#### Breakdown")

        bd_col1, bd_col2, bd_col3 = st.columns(3)
        with bd_col1:
            st.metric("Monthly Living Cost", f"Rp {result['monthly_living']:,.0f}")
        with bd_col2:
            st.metric("Disposable Income", f"Rp {result['disposable']:,.0f}")
        with bd_col3:
            st.metric("Required Monthly Investment", f"Rp {result['monthly_required']:,.0f}")

        st.session_state["feasibility_result"] = result
        st.session_state["monthly_contribution"] = result["monthly_required"]

        # Store for scenario analysis
        st.session_state["salary"] = monthly_salary
        st.session_state["income_growth"] = income_growth

        if result["verdict"] in ("yellow", "red"):
            st.markdown("---")
            st.markdown("#### 🔄 Scenario Analysis — How to flip to Green?")
            st.info("""
**Priority adjustments** (easiest to hardest):
1. **Extend timeline** — giving your money more time to compound
2. **Adjust location** — choosing a lower-cost city or neighbourhood
3. **Reduce goal size** — a smaller target with the same timeline
4. **Increase monthly contribution** — investing more each month

*Below are the minimum viable changes calculated for your profile.*
""")

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

            # HARD GATE: if ratio >100%, scenario optimizer is blocked
            if scenarios.blocked_reason:
                st.error("⚠️ Scenario Optimizer Blocked")
                st.write(scenarios.blocked_reason)
                st.stop()

            if scenarios.scenarios:
                for i, s in enumerate(scenarios.scenarios):
                    with st.expander(f"📌 {s.lever.upper()}: {s.adjustment}", expanded=(i == 0)):
                        st.write(s.change_description)
                        st.write(f"New investment ratio: **{s.new_ratio:.1%}** → Verdict: **{s.verdict.upper()}**")
                        if i == 0:
                            st.session_state["recommended_scenario"] = s
            else:
                st.warning("No viable scenario found within reasonable parameters.")


# ── Page 3: Risk Profiler ───────────────────────────────────────────────────────

elif page == "📋 Risk Profiler":
    st.title("📋 Risk Profiler")
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

    st.progress(min(end / len(RISK_QUESTIONS), 1.0))
    st.caption(f"Questions {start + 1}–{end} of {len(RISK_QUESTIONS)}")

    for q in page_questions:
        st.markdown(f"**{q['id'].replace('q', 'Q').replace('_', ' ').title()}. {q['question']}**")
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
            if st.button("← Previous"):
                st.session_state["risk_page"] -= 1
                st.rerun()
    with col_next:
        if end < len(RISK_QUESTIONS):
            if st.button("Next →"):
                st.session_state["risk_page"] += 1
                st.rerun()

    if len(answers) == 12:
        st.markdown("---")
        st.success("🎉 All questions answered!")
        rp = RiskProfiler()
        for qid, score in answers.items():
            rp.submit_answer(qid, score)
        profile = rp.get_profile()

        st.markdown(f"### Your Risk Profile: **{profile.profile}**")
        st.markdown(f"**Score: {profile.score}/{profile.max_score} ({profile.percentage}%)**")
        st.info(profile.description)

        st.markdown("#### Recommended Asset Allocation")
        alloc_data = []
        for instrument, pct in profile.allocation.items():
            label = INSTRUMENT_LABELS[instrument]
            alloc_data.append({"Instrument": label, "Allocation": f"{pct}%", "%": pct})

        df = pd.DataFrame(alloc_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.session_state["risk_profile"] = profile.to_dict()
        st.session_state["risk_profile_set"] = True


# ── Page 4: Portfolio Recommendation ──────────────────────────────────────────

elif page == "💼 Portfolio Recommendation":
    st.title("💼 Portfolio Recommendation")

    if "goal_set" not in st.session_state:
        st.warning("⚠️ Please complete **Goal Builder** first.")
        st.stop()
    if "risk_profile_set" not in st.session_state:
        st.warning("⚠️ Please complete the **Risk Profiler** first.")
        st.stop()

    goal = st.session_state["goal_profile"]
    risk = st.session_state["risk_profile"]

    monthly_contribution = st.session_state.get("monthly_contribution", goal["estimated_cost"] / (goal["timeline_years"] * 12))

    st.markdown(f"### Portfolio for **{goal['goal_type']}** goal in **{goal['city']}**")
    st.markdown(f"**Risk Profile: {risk['profile']}** | Monthly investment: **Rp {monthly_contribution:,.0f}**")

    result = build_portfolio(
        risk_profile=risk["profile"],
        monthly_contribution=monthly_contribution,
        goal_amount=goal["estimated_cost"],
        timeline_years=goal["timeline_years"],
    )

    st.markdown("---")
    st.markdown("#### 📊 Monthly Allocation")

    alloc_rows = []
    for a in result.allocations:
        alloc_rows.append({
            "Instrument": PORT_LABELS[a.instrument],
            "% of Portfolio": f"{a.percentage:.1f}%",
            "Monthly Amount (IDR)": f"Rp {a.monthly_amount:,.0f}",
            "Expected Annual Return": f"{a.expected_return:.1%}",
            "10-Year Growth": f"{a.expected_growth_10yr:.1%}",
        })
    st.dataframe(pd.DataFrame(alloc_rows), use_container_width=True, hide_index=True)

    col_summary1, col_summary2, col_summary3 = st.columns(3)
    with col_summary1:
        st.metric("Blended Expected Return", f"{result.blended_return:.2%}")
    with col_summary2:
        st.metric("Blended Volatility", f"{result.blended_volatility:.2%}")
    with col_summary3:
        st.metric("Projected Value at Goal Year", f"Rp {result.projected_value_at_goal_year:,.0f}")

    shortfall = result.goal_amount - result.projected_value_at_goal_year
    if shortfall > 0:
        st.error(f"⚠️ Projected shortfall of **Rp {shortfall:,.0f}** — consider increasing monthly contribution or extending timeline.")
    else:
        st.success(f"✅ On track — projected value exceeds goal by **Rp {abs(shortfall):,.0f}**")

    st.markdown("---")
    st.markdown("#### 📈 Growth Trajectory to Your Goal")

    trajectory_df = pd.DataFrame(
        [{"Year": year, "Projected Value (IDR)": value} for year, value in result.yearly_trajectory],
    )
    trajectory_df = trajectory_df.set_index("Year")

    # Goal reference line
    goal_amount = result.goal_amount

    st.line_chart(
        trajectory_df,
        y="Projected Value (IDR)",
        height=320,
    )
    st.caption(f"Goal target: **Rp {goal_amount:,.0f}** at year {result.timeline_years} | "
               f"Projected: **Rp {result.projected_value_at_goal_year:,.0f}**")


# ── Page 5: Dashboard ──────────────────────────────────────────────────────────

elif page == "📈 Dashboard":
    st.title("📈 Dashboard")

    has_goal = st.session_state.get("goal_set", False)
    has_feasibility = st.session_state.get("feasibility_result") is not None
    has_risk = st.session_state.get("risk_profile_set", False)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Goal Set", "✅ Yes" if has_goal else "❌ Not yet")
    with col2:
        st.metric("Feasibility Analysed", "✅ Yes" if has_feasibility else "❌ Not yet")
    with col3:
        st.metric("Risk Profiled", "✅ Yes" if has_risk else "❌ Not yet")

    if has_goal:
        goal = st.session_state["goal_profile"]
        st.markdown("---")
        st.markdown("#### 🎯 Your Goal Summary")
        st.json(goal)

    if has_feasibility:
        result = st.session_state["feasibility_result"]
        st.markdown("---")
        st.markdown("#### 📊 Feasibility Summary")
        st.json(result)

    if has_risk:
        risk = st.session_state["risk_profile"]
        st.markdown("---")
        st.markdown("#### 📋 Risk Profile")
        st.json(risk)

    if all([has_goal, has_feasibility, has_risk]):
        st.balloons()
        st.success("🎉 Your complete financial plan is ready! Head to **Portfolio Recommendation** to see your investment allocation.")
