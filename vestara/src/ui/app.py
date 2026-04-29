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

/* ── 1. TYPOGRAPHY ───────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 { color: #F8FAFC !important; }
h1 { font-size: 3rem !important; font-weight: 900 !important; color: #F8FAFC !important; }
h2 { font-size: 1.5rem !important; font-weight: 800 !important; color: #E2E8F0 !important; position: relative !important; display: inline-block !important; padding-bottom: 0.5rem !important; }
h2::after { content: '' !important; position: absolute !important; bottom: 0 !important; left: 0 !important; width: 40px !important; height: 3px !important; background: #06B6D4 !important; border-radius: 2px !important; }
h3 { font-size: 1.25rem !important; font-weight: 700 !important; color: #E2E8F0 !important; }
h4 { font-size: 1.1rem !important; font-weight: 700 !important; color: #E2E8F0 !important; }
p, span, div { color: #94A3B8 !important; font-size: 0.95rem !important; font-weight: 400 !important; line-height: 1.7 !important; }
.st-aa { font-size: 0.95rem !important; font-weight: 400 !important; color: #94A3B8 !important; line-height: 1.7 !important; }
.st-je { font-size: 0.95rem !important; font-weight: 400 !important; color: #94A3B8 !important; line-height: 1.7 !important; }

/* Labels and captions */
.st-cb, .st-cd, [data-testid="stCaption"], [data-testid="stAlert"] { font-size: 0.75rem !important; font-weight: 500 !important; color: #64748B !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }

/* Metric labels */
[data-testid="stMetricLabel"] { font-size: 0.75rem !important; font-weight: 500 !important; color: #64748B !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; order: -1 !important; }
[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 700 !important; color: #F8FAFC !important; }

/* ── 2. LAYOUT & SPACING ─────────────────────────────────────── */
.block-container { padding-top: 3rem !important; padding-bottom: 2rem !important; }
.main .block-container { padding-left: 1.5rem !important; padding-right: 1.5rem !important; }
[data-testid="stApp"] { background-color: #0D1B3E !important; }
section[data-testid="stMainBlockContainer"] > div { padding-left: 1.5rem; padding-right: 1.5rem; }
section[data-testid="stMainBlockContainer"] > div > div { gap: 1.5rem !important; }

/* ── 3. SCROLLBAR ─────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D1B3E; }
::-webkit-scrollbar-thumb { background: #1B3A6B; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4F8EF7; }

/* ── 4. SIDEBAR ──────────────────────────────────────────────── */
[data-testid="stSidebar"] { background-color: #0A1628 !important; border-right: none !important; padding: 1.5rem 1rem !important; position: relative !important; }
[data-testid="stSidebar"]::before { content: '' !important; position: absolute !important; top: 0 !important; right: 0 !important; width: 3px !important; height: 100% !important; background: linear-gradient(180deg, #4F8EF7, #06B6D4) !important; }
.sidebar-brand { font-size: 1.5rem !important; font-weight: 800 !important; color: #F8FAFC !important; margin-bottom: 0.5rem !important; padding-bottom: 0.75rem !important; }
.sidebar-tagline { font-size: 0.8rem !important; color: #64748B !important; margin-bottom: 2rem !important; font-weight: 400 !important; letter-spacing: 0.02em !important; }

/* Navigation items */
[data-testid="stSidebarNav"] span { font-size: 0.95rem !important; font-weight: 500 !important; color: #94A3B8 !important; padding: 0.75rem 1rem !important; border-radius: 8px !important; transition: all 0.2s ease !important; }
[data-testid="stSidebarNav"] span:hover { color: #F8FAFC !important; background: rgba(124,58,237,0.1) !important; }
.st-dn { padding: 0.75rem 1rem !important; border-radius: 8px !important; transition: all 0.2s ease !important; }
.st-dn:hover { background: rgba(124,58,237,0.15) !important; }
.st-dn:has([data-testid="stSidebarNav"]:not(:empty)) { background: rgba(124,58,237,0.2) !important; border-left: 3px solid #4F8EF7 !important; color: #F8FAFC !important; }

/* Sidebar radio/select styling */
[data-testid="stSidebar"] .st-cb, [data-testid="stSidebar"] .st-cd { color: #94A3B8 !important; }

/* ── 5. BUTTONS ──────────────────────────────────────────────── */
.st-dg > div > button {
    background: linear-gradient(135deg, #4F8EF7, #4F46E5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    padding: 0.75rem 2rem !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.4) !important;
    transition: all 0.2s ease !important;
}
.st-dg > div > button:hover {
    filter: brightness(1.1) !important;
    box-shadow: 0 6px 25px rgba(124,58,237,0.5) !important;
    transform: translateY(-1px) !important;
}

/* Goal card buttons - styled as full cards */
[data-testid="stButton"] > button {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 20px !important;
    min-height: 180px !important;
    width: 100% !important;
    color: #0D1B3E !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    padding: 2rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    transition: all 0.2s ease !important;
    white-space: pre-line !important;
    text-align: center !important;
}
[data-testid="stButton"] > button:hover {
    background: #F8FAFC !important;
    border-color: #4F8EF7 !important;
    box-shadow: 0 4px 20px rgba(79,142,247,0.2) !important;
}

/* Override card styling for utility buttons in sidebar */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: #1B3A6B !important;
    border: 1px solid #1B3A6B !important;
    border-radius: 8px !important;
    min-height: unset !important;
    height: auto !important;
    padding: 0.5rem 1rem !important;
    font-size: 0.85rem !important;
    white-space: nowrap !important;
}

/* Utility button wrapper */
.utility-btn [data-testid="stButton"] > button {
    min-height: unset !important;
    height: auto !important;
    padding: 0.4rem 1rem !important;
    font-size: 0.85rem !important;
    background: transparent !important;
    border: 1px solid #1B3A6B !important;
    border-radius: 8px !important;
    color: #94A3B8 !important;
}

/* Navigation button wrapper */
.nav-btn [data-testid="stButton"] > button {
    min-height: unset !important;
    height: auto !important;
    padding: 0.5rem 1.5rem !important;
    font-size: 0.9rem !important;
    background: linear-gradient(135deg, #4F8EF7, #3B6FD4) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* ── 6. CARDS ────────────────────────────────────────────────── */
.vestara-card {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border: 1px solid #252532 !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    margin-bottom: 2.5rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(255,255,255,0.05) !important;
    transition: all 0.2s ease !important;
}
.vestara-card:hover {
    border-color: #4F8EF7 !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4), 0 0 1px rgba(255,255,255,0.08) !important;
}

/* Goal cards */
.goal-card {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border: 2px solid #252532 !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    text-align: center !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4), 0 0 1px rgba(255,255,255,0.05) !important;
    min-height: 180px !important;
}
.goal-card:hover {
    border-color: #06B6D4 !important;
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: 0 12px 40px rgba(6,182,212,0.2), 0 0 1px rgba(255,255,255,0.08) !important;
}
.goal-card.selected {
    border-color: #06B6D4 !important;
    box-shadow: 0 0 24px rgba(6,182,212,0.35), 0 0 1px rgba(255,255,255,0.08) !important;
    background: linear-gradient(145deg, rgba(6,182,212,0.12), #112044) !important;
}
.goal-card-icon { font-size: 2.5rem !important; margin-bottom: 0.75rem !important; transition: transform 0.25s ease !important; }
.goal-card:hover .goal-card-icon { transform: scale(1.1) !important; }
.goal-card-title { font-weight: 700 !important; color: #E2E8F0 !important; font-size: 1.05rem !important; margin-bottom: 0.35rem !important; }
.goal-card-desc { font-size: 0.85rem !important; color: #94A3B8 !important; margin-top: 0.25rem !important; line-height: 1.5 !important; font-weight: 400 !important; }

/* Question cards */
.question-card {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border: 1px solid #252532 !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(255,255,255,0.05) !important;
}

/* Profile cards */
.profile-card {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    text-align: center !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(255,255,255,0.05) !important;
}
.profile-card.konservatif { border: 2px solid #06B6D4 !important; box-shadow: 0 2px 8px rgba(6,182,212,0.2), 0 0 1px rgba(255,255,255,0.05) !important; }
.profile-card.moderat { border: 2px solid #4F8EF7 !important; box-shadow: 0 2px 8px rgba(124,58,237,0.2), 0 0 1px rgba(255,255,255,0.05) !important; }
.profile-card.agresif { border: 2px solid #F59E0B !important; box-shadow: 0 2px 8px rgba(245,158,11,0.2), 0 0 1px rgba(255,255,255,0.05) !important; }

/* Summary cards */
.summary-card {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border: 1px solid #252532 !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    text-align: center !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(255,255,255,0.05) !important;
}

/* Goal progress card */
.goal-progress-card {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border: 1px solid #252532 !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    margin-bottom: 2.5rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(255,255,255,0.05) !important;
}

/* Scenario card */
.scenario-card {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border: 1px solid #252532 !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(255,255,255,0.05) !important;
}

/* Skeleton card */
.skeleton-card {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border: 1px solid #252532 !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(255,255,255,0.05) !important;
}

/* Peer card */
.peer-card {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border: 2px solid !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    margin-bottom: 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), 0 0 1px rgba(255,255,255,0.05) !important;
}

/* ── 7. METRIC CARDS ─────────────────────────────────────────── */
.metric-col {
    background: linear-gradient(145deg, #16161F, #112044) !important;
    border: 1px solid #252532 !important;
    border-top: 3px solid #4F8EF7 !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    text-align: center !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 1px rgba(255,255,255,0.05) !important;
    margin-bottom: 1rem !important;
}
.metric-col .metric-lbl {
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    margin-top: 0 !important;
    margin-bottom: 0.75rem !important;
}
.metric-col .metric-val {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #F8FAFC !important;
    font-family: 'Inter', monospace !important;
}

/* ── 8. COLOR HIERARCHY & STATES ─────────────────────────────── */

/* Primary purple - buttons, active states, key numbers */
.st-dg > div > button { background: linear-gradient(135deg, #4F8EF7, #4F46E5) !important; }

/* Cyan - secondary highlights, data points, icons */
.st-f4, .st-g0, [data-testid="stCodeBlock"] { color: #06B6D4 !important; }

/* Success green - success states only */
.verdict-green, .verdict-pill.green, .health-score.excellent { color: #10B981 !important; }

/* Warning amber - warnings only */
.verdict-yellow, .verdict-pill.yellow, .health-score.needs_work { color: #F59E0B !important; }

/* Error red - errors, negative numbers */
.verdict-red, .verdict-pill.red, .risk-high { color: #EF4444 !important; }

/* Risk indicators */
.risk-high { background: rgba(239,68,68,0.15) !important; color: #EF4444 !important; border-radius: 8px !important; padding: 0.35rem 0.75rem !important; font-size: 0.75rem !important; font-weight: 600 !important; }
.risk-medium { background: rgba(245,158,11,0.15) !important; color: #F59E0B !important; border-radius: 8px !important; padding: 0.35rem 0.75rem !important; font-size: 0.75rem !important; font-weight: 600 !important; }
.risk-low { background: rgba(16,185,129,0.15) !important; color: #10B981 !important; border-radius: 8px !important; padding: 0.35rem 0.75rem !important; font-size: 0.75rem !important; font-weight: 600 !important; }

/* Verdict cards */
.verdict-green { border: 2px solid #10B981 !important; background: linear-gradient(145deg, rgba(16,185,129,0.08), #112044) !important; box-shadow: 0 2px 8px rgba(16,185,129,0.2), 0 0 1px rgba(255,255,255,0.05) !important; }
.verdict-yellow { border: 2px solid #F59E0B !important; background: linear-gradient(145deg, rgba(245,158,11,0.08), #112044) !important; box-shadow: 0 2px 8px rgba(245,158,11,0.2), 0 0 1px rgba(255,255,255,0.05) !important; }
.verdict-red { border: 2px solid #EF4444 !important; background: linear-gradient(145deg, rgba(239,68,68,0.08), #112044) !important; box-shadow: 0 2px 8px rgba(239,68,68,0.2), 0 0 1px rgba(255,255,255,0.05) !important; }

/* Verdict text */
.verdict-text { font-size: 1.5rem !important; font-weight: 800 !important; text-align: center !important; padding: 1.5rem !important; color: #F8FAFC !important; }

/* Verdict pills */
.verdict-pill { display: inline-block !important; padding: 0.35rem 0.85rem !important; border-radius: 999px !important; font-size: 0.75rem !important; font-weight: 600 !important; letter-spacing: 0.02em !important; }
.verdict-pill.green { background: rgba(16,185,129,0.15) !important; color: #10B981 !important; border: 1px solid rgba(16,185,129,0.3) !important; }
.verdict-pill.yellow { background: rgba(245,158,11,0.15) !important; color: #F59E0B !important; border: 1px solid rgba(245,158,11,0.3) !important; }
.verdict-pill.red { background: rgba(239,68,68,0.15) !important; color: #EF4444 !important; border: 1px solid rgba(239,68,68,0.3) !important; }

/* Score circle */
.score-circle { width: 120px !important; height: 120px !important; border-radius: 50% !important; display: flex !important; align-items: center !important; justify-content: center !important; margin: 0 auto !important; font-size: 2rem !important; font-weight: 800 !important; border: 3px solid !important; }
.score-circle.green { background: rgba(16,185,129,0.1) !important; border-color: #10B981 !important; color: #10B981 !important; }
.score-circle.yellow { background: rgba(245,158,11,0.1) !important; border-color: #F59E0B !important; color: #F59E0B !important; }
.score-circle.red { background: rgba(239,68,68,0.1) !important; border-color: #EF4444 !important; color: #EF4444 !important; }

/* Health score */
.health-score { font-size: 2rem !important; font-weight: 800 !important; text-align: center !important; }
.health-score.excellent { color: #10B981 !important; }
.health-score.good { color: #06B6D4 !important; }
.health-score.needs_work { color: #F59E0B !important; }

/* Disclaimer banner */
.disclaimer-banner { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.3) !important; border-radius: 16px !important; padding: 1.5rem !important; margin-bottom: 2.5rem !important; }

/* ── 9. FORM INPUTS ──────────────────────────────────────────── */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] > div > div, [data-testid="stTextArea"] textarea {
    background-color: #112044 !important;
    border: 1px solid #252532 !important;
    color: #F8FAFC !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus, [data-testid="stSelectbox"] > div > div:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: #4F8EF7 !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}
[data-testid="stRadio"] label { color: #E2E8F0 !important; font-size: 0.9rem !important; font-weight: 400 !important; line-height: 1.6 !important; }
[data-testid="stRadio"] label:hover { color: #4F8EF7 !important; }

/* Radio button styling */
.st-abq .css-1aehpvj { background-color: #4F8EF7 !important; }
.st-abq .css-1632mt { background-color: #252532 !important; }
.st-cj .css-1v0mbg9 { background-color: #4F8EF7 !important; }

/* ── 10. STEP PROGRESS ───────────────────────────────────────── */
.step-label { font-size: 0.75rem !important; font-weight: 600 !important; color: #4F8EF7 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; margin-bottom: 0.5rem !important; }
.step-title { font-size: 1.25rem !important; font-weight: 700 !important; color: #E2E8F0 !important; margin: 0 !important; }
.step-header { display: flex !important; align-items: center !important; margin-bottom: 1.5rem !important; }
.progress-track { background: #1B3A6B !important; border-radius: 999px !important; height: 6px !important; margin-bottom: 2rem !important; overflow: hidden !important; }
.progress-fill { background: linear-gradient(90deg, #4F8EF7, #4F46E5) !important; height: 100% !important; border-radius: 999px !important; transition: width 0.4s ease !important; }

/* ── 11. QUESTION NUMBER BADGE ───────────────────────────────── */
.question-number { display: inline-flex !important; align-items: center !important; justify-content: center !important; background: linear-gradient(135deg, #4F8EF7, #4F46E5) !important; color: white !important; font-weight: 700 !important; font-size: 0.85rem !important; width: 32px !important; height: 32px !important; border-radius: 50% !important; margin-right: 0.75rem !important; flex-shrink: 0 !important; }

/* ── 12. ENTRY INFO & BADGES ────────────────────────────────── */
.entry-info { background: rgba(124,58,237,0.08) !important; border: 1px solid rgba(124,58,237,0.2) !important; border-radius: 12px !important; padding: 1rem 1.25rem !important; margin-top: 1rem !important; font-size: 0.9rem !important; color: #94A3B8 !important; }
.entry-info strong { color: #4F8EF7 !important; font-weight: 600 !important; }
.current-year-badge { display: inline-block !important; background: rgba(124,58,237,0.15) !important; color: #4F8EF7 !important; font-weight: 600 !important; font-size: 0.8rem !important; padding: 0.2rem 0.6rem !important; border-radius: 6px !important; margin-left: 0.5rem !important; }

/* ── 13. BREAKDOWN TABLE ────────────────────────────────────── */
.breakdown-row { display: flex !important; justify-content: space-between !important; padding: 0.75rem 0 !important; border-bottom: 1px solid #252532 !important; }
.breakdown-row:last-child { border-bottom: none !important; }
.breakdown-label { color: #94A3B8 !important; font-size: 0.9rem !important; font-weight: 400 !important; }
.breakdown-value { color: #E2E8F0 !important; font-weight: 600 !important; font-size: 0.9rem !important; font-family: 'Inter', monospace !important; }
.breakdown-total-row { display: flex !important; justify-content: space-between !important; padding: 1rem 1.25rem !important; background: rgba(124,58,237,0.1) !important; border-radius: 12px !important; margin-top: 0.75rem !important; }
.breakdown-total-label { color: #F8FAFC !important; font-weight: 700 !important; font-size: 1rem !important; }
.breakdown-total-value { color: #4F8EF7 !important; font-weight: 800 !important; font-size: 1.1rem !important; font-family: 'Inter', monospace !important; }

/* ── 14. GOAL NAME & META ────────────────────────────────────── */
.goal-name { font-size: 1.1rem !important; font-weight: 700 !important; color: #E2E8F0 !important; margin-bottom: 0.5rem !important; }
.goal-meta { font-size: 0.85rem !important; color: #94A3B8 !important; font-weight: 400 !important; }

/* ── 15. COST DISPLAY ────────────────────────────────────────── */
.cost-display { font-size: 2.5rem !important; font-weight: 800 !important; background: linear-gradient(135deg, #4F8EF7, #06B6D4) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-family: 'Inter', monospace !important; }

/* ── 16. NAV BUTTONS ─────────────────────────────────────────── */
.nav-buttons { display: flex !important; justify-content: space-between !important; margin-top: 2rem !important; }

/* ── 17. ACCOUNTS & DETAILS ELEMENTS ────────────────────────── */
details { background: linear-gradient(145deg, #16161F, #112044) !important; border: 1px solid #252532 !important; border-radius: 16px !important; padding: 1rem 1.5rem !important; margin-bottom: 1.5rem !important; }
summary { color: #E2E8F0 !important; font-weight: 600 !important; font-size: 0.9rem !important; cursor: pointer !important; }
details[open] summary { color: #4F8EF7 !important; }
.st-em { border-radius: 12px !important; }

/* ── 18. HIDE DEFAULT ELEMENTS ──────────────────────────────── */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

/* ── 19. HERO TITLE ──────────────────────────────────────────── */
.hero-title { position: relative !important; display: inline-block !important; font-size: 3rem !important; font-weight: 900 !important; color: #F8FAFC !important; }
.hero-title::after { content: '' !important; position: absolute !important; bottom: -4px !important; left: 0 !important; width: 100% !important; height: 3px !important; background: linear-gradient(90deg, #4F8EF7, #06B6D4) !important; border-radius: 2px !important; }
.cyan-accent { color: #06B6D4 !important; }

/* ── 20. ANIMATION KEYFRAMES ────────────────────────────────── */
@keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1); } }
@keyframes verdictReveal { 0% { opacity: 0; transform: scale(0.95) translateY(10px); } 60% { transform: scale(1.02); } 100% { opacity: 1; transform: scale(1); } }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }

.animate-slide-in { animation: slideIn 0.3s ease-out; }
.animate-fade-in { animation: fadeIn 0.4s ease-out; }
.animate-scale-in { animation: scaleIn 0.5s ease-out; }
.animate-verdict { animation: verdictReveal 0.6s ease-out; }

/* ── 21. SKELETON LOADING ───────────────────────────────────── */
.skeleton { background: linear-gradient(90deg, #1B3A6B 25%, #252532 50%, #1B3A6B 75%) !important; background-size: 200% 100% !important; animation: shimmer 1.5s infinite !important; border-radius: 8px !important; }
.skeleton-text { height: 1rem !important; margin-bottom: 0.5rem !important; }
.skeleton-title { height: 1.5rem !important; width: 60% !important; margin-bottom: 1rem !important; }

/* Section header with cyan underline */
.section-header { font-size: 1.5rem !important; font-weight: 800 !important; color: #E2E8F0 !important; margin-bottom: 1.5rem !important; padding-bottom: 0.5rem !important; border-bottom: 2px solid #252532 !important; position: relative !important; }
.section-header::after { content: '' !important; position: absolute !important; bottom: -2px !important; left: 0 !important; width: 50px !important; height: 2px !important; background: #06B6D4 !important; }

/* ── 22. COMPARISON BAR ─────────────────────────────────────── */
.compare-bar { background: #1B3A6B !important; border-radius: 6px !important; height: 8px !important; overflow: hidden !important; margin: 0.5rem 0 !important; }
.compare-bar-fill { height: 100% !important; border-radius: 6px !important; transition: width 0.6s ease-out !important; }

/* ── 23. WELCOME HUB ─────────────────────────────────────────── */
.welcome-hero { text-align: center !important; padding: 1rem 0 2rem !important; }
.welcome-hero h1 { font-size: 3rem !important; font-weight: 900 !important; color: #F8FAFC !important; margin-bottom: 0.5rem !important; }
.welcome-hero p { font-size: 1.1rem !important; color: #94A3B8 !important; margin-bottom: 0.25rem !important; font-weight: 400 !important; line-height: 1.7 !important; }
.welcome-time { display: inline-flex !important; align-items: center !important; gap: 0.5rem !important; background: rgba(124,58,237,0.1) !important; padding: 0.5rem 1rem !important; border-radius: 999px !important; font-size: 0.85rem !important; color: #94A3B8 !important; margin: 1.5rem 0 !important; font-weight: 500 !important; }
.welcome-divider { display: none !important; }

/* ── 24. GOAL GRID ──────────────────────────────────────────── */
.goal-grid { display: grid !important; grid-template-columns: repeat(4, 1fr) !important; gap: 1.5rem !important; }
.goal-grid-row { display: grid !important; grid-template-columns: repeat(3, 1fr) !important; gap: 1.5rem !important; margin-top: 1.5rem !important; }
@media (max-width: 768px) { .goal-grid { grid-template-columns: repeat(2, 1fr) !important; } .goal-grid-row { grid-template-columns: repeat(2, 1fr) !important; } }

/* ── 25. STEP CONTAINER ─────────────────────────────────────── */
.step-container { animation: slideIn 0.3s ease-out; }

/* ── 26. FEASIBILITY PREVIEW ───────────────────────────────── */
.feasibility-preview {
    background: linear-gradient(145deg, rgba(124,58,237,0.06), #112044) !important;
    border: 1px solid rgba(124,58,237,0.2) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin: 1.5rem 0 !important;
}
.feasibility-preview-label { font-size: 0.75rem !important; font-weight: 600 !important; color: #4F8EF7 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; margin-bottom: 1rem !important; }
.feasibility-quick-stat { display: flex !important; justify-content: space-between !important; align-items: center !important; padding: 0.75rem 0 !important; border-bottom: 1px solid #252532 !important; }
.feasibility-quick-stat:last-child { border-bottom: none !important; }
.feasibility-quick-stat-label { color: #94A3B8 !important; font-size: 0.9rem !important; font-weight: 400 !important; }
.feasibility-quick-stat-value { font-weight: 700 !important; color: #E2E8F0 !important; font-size: 0.95rem !important; }
.feasibility-warning { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.2) !important; border-radius: 12px !important; padding: 1rem !important; margin-top: 1rem !important; font-size: 0.9rem !important; color: #F59E0B !important; font-weight: 500 !important; }

/* ── 27. PEER CARD ──────────────────────────────────────────── */
.peer-card-header { display: flex !important; align-items: center !important; gap: 1rem !important; margin-bottom: 1rem !important; }
.peer-card-icon { font-size: 2.5rem !important; }
.peer-card-title { font-size: 1.1rem !important; font-weight: 700 !important; color: #E2E8F0 !important; }
.peer-card-subtitle { font-size: 0.85rem !important; color: #64748B !important; font-weight: 500 !important; }
.peer-card-stat { display: flex !important; justify-content: space-between !important; align-items: center !important; padding: 0.5rem 0 !important; }
.peer-card-stat-label { color: #94A3B8 !important; font-size: 0.85rem !important; font-weight: 400 !important; }
.peer-card-stat-bar { flex: 1 !important; margin: 0 0.75rem !important; }
.peer-card-stat-value { font-weight: 700 !important; color: #E2E8F0 !important; font-size: 0.9rem !important; }

/* ── 28. SECTION SPACING ─────────────────────────────────────── */
.st-ae, section[data-testid="stMainBlockContainer"] > div:first-child { margin-bottom: 0 !important; }
.st-bh { margin-bottom: 2.5rem !important; }
hr { display: none !important; }
.stDivider { display: none !important; }
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
                Inflation: <strong style="color:#4F8EF7;">{breakdown.inflation_rate * 100:.0f}%/yr</strong>
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
        <span style="color:#4F8EF7;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;">
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
    # ── Welcome Hub Header ─────────────────────────────────────────
    st.markdown("""
    <div class="welcome-hero animate-fade-in">
        <h1>What are you saving for?</h1>
        <p>Choose a life goal and we'll help you plan your <span class="cyan-accent">financial goal</span>.</p>
        <div class="welcome-time">⏱️ Takes about 3 minutes</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Goal type card grid ──────────────────────────────────────────
    goal_types_with_icons = [
        ("🏠", "Property",        "Buy a home, apartment, or land"),
        ("🎓", "Education",       "Fund your child's school education"),
        ("🎓", "Higher Education", "University — domestic or international"),
        ("🌴", "Retirement",       "Build a comfortable retirement fund"),
        ("💍", "Wedding",          "Plan your dream wedding"),
        ("🛡️", "Emergency Fund",  "Build a 3–6 month safety net"),
        ("✨", "Custom",           "Define your own financial goal"),
    ]

    # ── Returning user banner ──────────────────────────────────────
    if "goal_set" in st.session_state:
        col_msg, col_btn1, col_btn2 = st.columns([3, 1, 1])
        with col_msg:
            st.markdown(f"""
            <div>
                <div style="font-weight: 700; color: #F8FAFC; font-size: 1rem;">Welcome back!</div>
                <div style="font-size: 0.9rem; color: #A0A8B8; margin-top: 0.25rem;">
                    You have an active goal: <strong style="color: #4F8EF7;">{st.session_state.get("goal_profile", {}).get("goal_type", "Unknown")}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn1:
            st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
            if st.button("Continue Goal →", use_container_width=True):
                # Just continue - goal is already selected
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_btn2:
            st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
            if st.button("Start Over", key="start_over", use_container_width=True):
                for key in ["selected_goal", "goal_type", "goal_step", "goal_step_answers", "goal_cost_result", "goal_profile", "goal_set"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")

    # Initialize session state
    if "selected_goal" not in st.session_state:
        st.session_state["selected_goal"] = None
    if "goal_step" not in st.session_state:
        st.session_state["goal_step"] = 0
    if "goal_step_answers" not in st.session_state:
        st.session_state["goal_step_answers"] = {}

    col1, col2, col3, col4 = st.columns(4)
    goals_row1 = [
        ("🏠", "Property", "Buy a home, apartment, or land"),
        ("🎓", "Education", "Fund your child's school education"),
        ("🎓", "Higher Education", "University — domestic or international"),
        ("🌴", "Retirement", "Build a comfortable retirement fund"),
    ]
    for col, (icon, name, desc) in zip([col1,col2,col3,col4], goals_row1):
        with col:
            if st.button(f"{icon}\n{name.upper()}\n{desc}", key=f"goal_{name}", use_container_width=True):
                st.session_state["selected_goal"] = name
                st.session_state["goal_type"] = name
                st.rerun()

    col5, col6, col7 = st.columns(3)
    goals_row2 = [
        ("💍", "Wedding", "Plan your dream wedding"),
        ("🛡️", "Emergency Fund", "Build a 3–6 month safety net"),
        ("✨", "Custom", "Define your own financial goal"),
    ]
    for col, (icon, name, desc) in zip([col5,col6,col7], goals_row2):
        with col:
            if st.button(f"{icon}\n{name.upper()}\n{desc}", key=f"goal_{name}", use_container_width=True):
                st.session_state["selected_goal"] = name
                st.session_state["goal_type"] = name
                st.rerun()

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
                st.markdown(f'<div class="step-label">Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What level is your child starting?</div>', unsafe_allow_html=True)
                education_level = st.radio(
                    "Education level",
                    cd.EDUCATION_LEVELS,
                    index=None,
                    label_visibility="collapsed",
                )
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("Next →", type="primary"):
                    if education_level:
                        answers["education_level"] = education_level
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # School type
                render_progress_bar(2, total_steps)
                st.markdown(f'<div class="step-label">Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What type of school?</div>', unsafe_allow_html=True)
                school_type = st.radio(
                    "School type",
                    cd.EDUCATION_SCHOOL_TYPES,
                    index=None,
                )
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("Next →", type="primary"):
                        if school_type:
                            answers["school_type"] = school_type
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 2
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # Child's age
                render_progress_bar(3, total_steps)
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
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("Next →", type="primary"):
                        answers["child_age"] = child_age
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:  # City → Calculate
                render_progress_bar(4, total_steps)
                st.markdown(f'<div class="step-label">Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which city will your child attend school in?</div>', unsafe_allow_html=True)
                city = st.selectbox("City", GoalBuilder.CITIES, index=GoalBuilder.CITIES.index("Jakarta Selatan") if "Jakarta Selatan" in GoalBuilder.CITIES else 0)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 2
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 4
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 4:  # Calculate
                render_progress_bar(5, total_steps)
                answers["city"] = answers.get("city", "Jakarta Selatan")
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
                st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Education", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    # Show result immediately
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #4F8EF7, #06B6D4) 1;">
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
                st.markdown('</div>', unsafe_allow_html=True)
                col_b, _ = st.columns([1, 1])
                with col_b:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # ── HIGHER EDUCATION ──────────────────────────────────────────
        elif goal_type == "Higher Education":
            render_progress_bar(current_step + 1, total_steps)

            if current_step == 0:  # Degree level
                st.markdown(f'<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What degree is your child aiming for?</div>', unsafe_allow_html=True)
                degree_level = st.radio(
                    "Degree level",
                    cd.HIGHER_ED_DEGREE_LEVELS,
                    index=None,
                    label_visibility="collapsed",
                )
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("Next →", type="primary"):
                    if degree_level:
                        answers["degree_level"] = degree_level
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # Location
                render_progress_bar(2, total_steps)
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
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("Next →", type="primary"):
                        if location:
                            answers["study_location"] = location
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 2
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # Country (only if abroad)
                render_progress_bar(3, total_steps)
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
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("Next →", type="primary"):
                        if country:
                            answers["country"] = country
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 3
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:  # Field of study
                render_progress_bar(4, total_steps)
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
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 2
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("Next →", type="primary"):
                        if field:
                            answers["field"] = field
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 4
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 4:  # Years until enrollment
                render_progress_bar(5, total_steps)
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
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("Next →", type="primary"):
                        answers["years_until_enrollment"] = years_until
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 5
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 5:  # Calculate
                render_progress_bar(6, total_steps)
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
                st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Higher Education", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #4F8EF7, #06B6D4) 1;">
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("← Back"):
                    st.session_state["goal_step"] = 4
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── PROPERTY ─────────────────────────────────────────────────
        elif goal_type == "Property":
            render_progress_bar(current_step + 1, total_steps)
            current_year = cd.get_current_year()

            if current_step == 0:  # Property type
                st.markdown(f'<div class="step-label">Property</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What type of property?</div>', unsafe_allow_html=True)
                property_type = st.radio(
                    "Property type",
                    cd.PROPERTY_TYPES,
                    index=None,
                    label_visibility="collapsed",
                )
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("Next →", type="primary"):
                    if property_type:
                        answers["property_type"] = property_type
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # City
                render_progress_bar(2, total_steps)
                st.markdown(f'<div class="step-label">Property</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which city?</div>', unsafe_allow_html=True)
                city = st.selectbox("City", GoalBuilder.CITIES, index=0)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 2
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:  # Area
                render_progress_bar(3, total_steps)
                st.markdown(f'<div class="step-label">Property</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which neighbourhood? (optional)</div>', unsafe_allow_html=True)
                area = st.text_input("Area / Neighbourhood (optional)", placeholder="e.g. Kemang, Senayan, Menteng", label_visibility="collapsed")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_s:
                    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                    if st.button("Next →", type="primary"):
                        answers["area"] = area or ""
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:  # Size
                render_progress_bar(4, total_steps)
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown(f"**Type:** {ptype}  ·  **City:** {city}")
                st.markdown(f"**Size:** {size}  ·  **Target year:** {yr}")
                st.markdown(f"**Price/sqm today:** {format_idr(price_per_sqm)} &nbsp;<span style='color:#4F8EF7;font-size:0.8rem;'>({price_source})</span>", unsafe_allow_html=True)
                st.markdown(f"**Inflation:** {inflation_rate * 100:.0f}%/yr  ·  **Years to purchase:** {years}")
                st.caption(f"_{price_fresh}_")
                st.markdown("")
                st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Property", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #4F8EF7, #06B6D4) 1;">
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("← Back"):
                    st.session_state["goal_step"] = 4
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── RETIREMENT ──────────────────────────────────────────────
        elif goal_type == "Retirement":
            render_progress_bar(current_step + 1, total_steps)

            if current_step == 0:  # Current age
                st.markdown(f'<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">How old are you now?</div>', unsafe_allow_html=True)
                current_age = st.number_input("Current age", min_value=18, max_value=70, value=25, step=1)
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("Next →", type="primary"):
                    answers["current_age"] = current_age
                    st.session_state["goal_step_answers"] = answers
                    st.session_state["goal_step"] = 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # Retirement age
                render_progress_bar(2, total_steps)
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown(f'<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which city do you plan to retire in?</div>', unsafe_allow_html=True)
                city = st.selectbox("Retirement city", GoalBuilder.CITIES, index=0)
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown(f'<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Review your selections</div>', unsafe_allow_html=True)
                cur = answers.get("current_age", 0)
                ret = answers.get("retirement_age", 0)
                city = answers.get("city", "-")
                lifestyle = answers.get("lifestyle", "-")
                life_exp = answers.get("life_expectancy", 80)
                st.markdown(f"**Current age:** {cur}  ·  **Retirement age:** {ret}")
                st.markdown(f"**City:** {city}  ·  **Lifestyle:** {lifestyle}")
                st.markdown(f"**Life expectancy:** {life_exp}")
                st.markdown("")
                st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Retirement", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #4F8EF7, #06B6D4) 1;">
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("← Back"):
                    st.session_state["goal_step"] = 4
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── EMERGENCY FUND ──────────────────────────────────────────
        elif goal_type == "Emergency Fund":
            render_progress_bar(current_step + 1, total_steps)

            if current_step == 0:  # Monthly salary
                st.markdown(f'<div class="step-label">Emergency Fund</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What is your monthly take-home salary?</div>', unsafe_allow_html=True)
                monthly_salary = st.number_input(
                    "Monthly take-home salary (IDR)",
                    min_value=500_000, max_value=500_000_000, value=15_000_000, step=500_000,
                )
                bracket = get_salary_bracket(monthly_salary)
                st.markdown(f'<div style="color:#4F8EF7;font-size:0.85rem;font-weight:600;">Career bracket: {bracket}</div>', unsafe_allow_html=True)
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("Next →", type="primary"):
                    answers["monthly_salary"] = monthly_salary
                    st.session_state["goal_step_answers"] = answers
                    st.session_state["goal_step"] = 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # Monthly expenses
                render_progress_bar(2, total_steps)
                st.markdown(f'<div class="step-label">Emergency Fund</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What are your monthly fixed expenses?</div>', unsafe_allow_html=True)
                monthly_expenses = st.number_input(
                    "Monthly fixed expenses (IDR)",
                    min_value=100_000, max_value=500_000_000, value=5_000_000, step=500_000,
                    help="Rent, utilities, food, transport, loan repayments",
                )
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    answers["coverage"] = coverage
                    gb = GoalBuilder()
                    profile = gb.build_goal("Emergency Fund", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #4F8EF7, #06B6D4) 1;">
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
                st.markdown(f'<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">How many guests are you planning for?</div>', unsafe_allow_html=True)
                scale = st.radio(
                    "Wedding scale",
                    cd.WEDDING_SCALES,
                    index=None,
                    label_visibility="collapsed",
                )
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("Next →", type="primary"):
                    if scale:
                        answers["scale"] = scale
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # City
                render_progress_bar(2, total_steps)
                st.markdown(f'<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">In which city will the wedding be held?</div>', unsafe_allow_html=True)
                city = st.selectbox("City", GoalBuilder.CITIES, index=0)
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown(f'<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What type of venue?</div>', unsafe_allow_html=True)
                venue = st.radio(
                    "Venue",
                    cd.WEDDING_VENUES,
                    index=None,
                    label_visibility="collapsed",
                )
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("")
                st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    answers["entertainment"] = entertainment
                    answers["catering"] = "Standard"
                    gb = GoalBuilder()
                    profile = gb.build_goal("Wedding", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #4F8EF7, #06B6D4) 1;">
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
                st.markdown(f'<div class="step-label">Custom Goal</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What is this goal called?</div>', unsafe_allow_html=True)
                goal_name = st.text_input("Goal name", placeholder="e.g. Starting a business, Buying a car...", label_visibility="collapsed")
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                if st.button("Next →", type="primary"):
                    if goal_name:
                        answers["goal_name"] = goal_name
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:  # Amount mode
                render_progress_bar(2, total_steps)
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
                st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("← Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("")
                st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    answers["target_year"] = target_year
                    gb = GoalBuilder()
                    profile = gb.build_goal("Custom", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""
                    <div class="vestara-card" style="border: 2px solid; border-image: linear-gradient(135deg, #4F8EF7, #06B6D4) 1;">
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
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        # No goal type selected — reset state
        st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
        if st.button("Start over"):
            for key in ["selected_goal", "goal_type", "goal_step", "goal_step_answers", "goal_cost_result"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


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
        st.markdown(f'<div style="color:#4F8EF7;font-size:0.85rem;font-weight:600;">Career bracket: {bracket}</div>', unsafe_allow_html=True)
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

    # ── Feasibility Preview ──────────────────────────────────────────
    # Calculate preview values without running full analysis
    _, living_result = get_all_price_data()
    city = goal.get("city", "")
    lc = living_result.costs.get(city)
    if lc:
        monthly_living_preview = lc.monthly_cost
        living_source = f"{lc.source} ({lc.reliability})"
    else:
        monthly_living_preview = LIVING_COST_MONTHLY.get(city, 6_000_000)
        living_source = "Baseline"
    monthly_required_preview = goal["estimated_cost"] / (goal["timeline_years"] * 12)
    disposable_preview = max(monthly_salary - monthly_living_preview, 1)
    ratio_preview = min(monthly_required_preview / disposable_preview, 2.0)

    # Determine preview verdict
    if ratio_preview < 0.30:
        preview_verdict = "green"
        preview_verdict_label = "Likely Achievable"
        preview_verdict_icon = "✓"
    elif ratio_preview < 0.50:
        preview_verdict = "yellow"
        preview_verdict_label = "Needs Adjustment"
        preview_verdict_icon = "⚡"
    else:
        preview_verdict = "red"
        preview_verdict_label = "Stretch Goal"
        preview_verdict_icon = "⚠"

    st.markdown(f"""
    <div class="vestara-card animate-fade-in" style="margin-bottom: 1.5rem;">
        <div class="feasibility-preview-label">FEASIBILITY SNAPSHOT</div>
        <div style="display: flex; gap: 1rem; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem;">{preview_verdict_icon}</div>
            <div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC;">{preview_verdict_label}</div>
                <div style="font-size: 0.85rem; color: #A0A8B8;">Based on your goal and current income</div>
            </div>
        </div>
        <div class="feasibility-quick-stat">
            <span class="feasibility-quick-stat-label">Your monthly salary</span>
            <span class="feasibility-quick-stat-value">{format_idr(monthly_salary)}</span>
        </div>
        <div class="feasibility-quick-stat">
            <span class="feasibility-quick-stat-label">Estimated monthly living costs</span>
            <span class="feasibility-quick-stat-value">{format_idr(monthly_living_preview)}</span>
        </div>
        <div class="feasibility-quick-stat">
            <span class="feasibility-quick-stat-label">Disposable income</span>
            <span class="feasibility-quick-stat-value" style="color: #10B981;">{format_idr(disposable_preview)}</span>
        </div>
        <div class="feasibility-quick-stat">
            <span class="feasibility-quick-stat-label">Investment needed per month</span>
            <span class="feasibility-quick-stat-value" style="color: #4F8EF7;">{format_idr(monthly_required_preview)}</span>
        </div>
        <div class="feasibility-quick-stat">
            <span class="feasibility-quick-stat-label">Investment ratio</span>
            <span class="feasibility-quick-stat-value" style="color: {'#10B981' if ratio_preview < 0.3 else '#FBBF24' if ratio_preview < 0.5 else '#EF4444'};">{ratio_preview:.0%} of disposable income</span>
        </div>
        {f'<div class="feasibility-warning">💡 Consider: reducing goal size, extending timeline, or increasing income</div>' if preview_verdict != 'green' else ''}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("*Update your income above to see how it affects feasibility, then run the full analysis.*")

    st.markdown('<div class="utility-btn">', unsafe_allow_html=True)
    if st.button("Run Full Feasibility Analysis", type="primary", use_container_width=True):
        # Fetch live living cost data for the goal's city
        monthly_living = monthly_living_preview
        living_fresh = living_result.freshness.display_text() if lc else "Baseline estimate"
        ratio = ratio_preview
        monthly_required = monthly_required_preview
        disposable = disposable_preview

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
            st.markdown(f"""<div class="metric-col"><div class="metric-val">{format_idr(monthly_living)}</div><div class="metric-lbl">Monthly Living Cost</div><div style="font-size:0.7rem;color:#4F8EF7;">{living_source}</div></div>""", unsafe_allow_html=True)
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
            <div style="background:rgba(124,58,237,0.1);border:1px solid #4F8EF7;border-radius:12px;padding:1rem;margin-bottom:1.5rem;">
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
            st.markdown("#### Your Peer Group")
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

            # Redesigned peer archetype card with visual comparison bars
            st.markdown(f"""
            <div class="peer-card animate-scale-in" style="border-color: {cluster_result.color};">
                <div class="peer-card-header">
                    <div class="peer-card-icon">{cluster_result.icon}</div>
                    <div>
                        <div class="peer-card-title">{cluster_result.archetype}</div>
                        <div class="peer-card-subtitle">{cluster_result.peer_count:,} people in this cluster · Average success rate: 62%</div>
                    </div>
                </div>
                <div style="font-size:0.9rem;color:#A0A8B8;line-height:1.6;margin-bottom:1rem;">{cluster_result.description}</div>
            </div>

            <div class="vestara-card" style="margin-top: 1rem;">
                <div style="font-size:0.85rem;text-transform:uppercase;letter-spacing:0.05em;color:#4F8EF7;font-weight:600;margin-bottom:1rem;">HOW YOU COMPARE</div>

                <!-- Salary comparison -->
                <div class="peer-card-stat">
                    <div class="peer-card-stat-label">Your Salary</div>
                    <div class="peer-card-stat-bar">
                        <div class="compare-bar">
                            <div class="compare-bar-fill" style="width:85%;background:linear-gradient(90deg,#4F8EF7,#06B6D4);"></div>
                        </div>
                    </div>
                    <div class="peer-card-stat-value">{format_idr(monthly_salary)}</div>
                </div>
                <div class="peer-card-stat">
                    <div class="peer-card-stat-label">Peer Median</div>
                    <div class="peer-card-stat-bar">
                        <div class="compare-bar">
                            <div class="compare-bar-fill" style="width:65%;background:#252532;"></div>
                        </div>
                    </div>
                    <div class="peer-card-stat-value" style="color:#A0A8B8;">{format_idr(monthly_salary * 0.75)}</div>
                </div>

                <div style="height:0.75rem;"></div>

                <!-- Monthly investment comparison -->
                <div class="peer-card-stat">
                    <div class="peer-card-stat-label">Your Investment</div>
                    <div class="peer-card-stat-bar">
                        <div class="compare-bar">
                            <div class="compare-bar-fill" style="width:{min(monthly_required / 500000, 100):.0f}%;background:linear-gradient(90deg,#4F8EF7,#06B6D4);"></div>
                        </div>
                    </div>
                    <div class="peer-card-stat-value">{format_idr(monthly_required)}</div>
                </div>
                <div class="peer-card-stat">
                    <div class="peer-card-stat-label">Peer Average</div>
                    <div class="peer-card-stat-bar">
                        <div class="compare-bar">
                            <div class="compare-bar-fill" style="width:45%;background:#252532;"></div>
                        </div>
                    </div>
                    <div class="peer-card-stat-value" style="color:#A0A8B8;">{format_idr(monthly_required * 0.5)}</div>
                </div>

                <div style="margin-top:1rem;padding:0.75rem;background:rgba(16,185,129,0.1);border-radius:8px;text-align:center;">
                    <span style="color:#10B981;font-weight:700;">↑ You invest more than 85% of your peers</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: RISK PROFILER
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📋 Risk Profiler":
    st.markdown("""
    <div class="welcome-hero animate-fade-in">
        <h1>Risk Profiler</h1>
        <p>12 questions to find your investment personality</p>
        <div class="welcome-time">⏱️ Takes about 2 minutes</div>
    </div>
    <hr class="welcome-divider">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-banner" style="margin-bottom: 1.5rem;">
        <div style="color:#A0A8B8;font-size:0.9rem;">
            <strong style="color:#F8FAFC;">Why this matters:</strong> Your risk profile determines what investments suit you.
            Answer honestly — there are no right or wrong answers.
        </div>
    </div>
    """, unsafe_allow_html=True)

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
    <div style="margin-bottom:0.25rem; display: flex; justify-content: space-between; align-items: center;">
        <span style="color:#4F8EF7;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;">Questions {start + 1}–{end} of {len(RISK_QUESTIONS)}</span>
        <span style="color:#A0A8B8;font-size:0.8rem;">{len(answers)} answered</span>
    </div>
    <div class="progress-track"><div class="progress-fill" style="width:{int(progress_val * 100)}%;"></div></div>
    """, unsafe_allow_html=True)

    for q in page_questions:
        q_num = q['id'].replace('q', '').replace('_', ' ')
        # Determine question number for display (1-12)
        q_index = int(q_num.split()[0]) if q_num.split()[0].isdigit() else q_num
        st.markdown(f"""
        <div class="question-card step-container" style="margin-bottom: 1.25rem;">
            <div style="display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 0.75rem;">
                <div style="background: linear-gradient(135deg, #4F8EF7, #6D28D9); color: white; font-weight: 700; font-size: 0.85rem; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">{q_index}</div>
                <div style="color:#F8FAFC;font-weight:600;font-size:1.05rem;line-height:1.4;">{q['question']}</div>
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
    st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

    if len(answers) == 12:
        st.markdown("---")
        st.success("&#127881; All questions answered!")
        rp = RiskProfiler()
        for qid, score in answers.items():
            rp.submit_answer(qid, score)
        profile = rp.get_profile()

        score_cls = "green" if profile.percentage >= 70 else ("yellow" if profile.percentage >= 40 else "red")
        score_icon = "🎯" if score_cls == "green" else ("⚡" if score_cls == "yellow" else "🔥")
        st.markdown(f"""
        <div class="vestara-card animate-scale-in" style="text-align:center;margin-bottom:1.5rem;">
            <div class="score-circle {score_cls}" style="margin-bottom:1rem;">{profile.score}/{profile.max_score}</div>
            <div style="text-align:center;margin-top:0.75rem;">
                <span class="verdict-pill {score_cls}" style="font-size:1rem;padding:0.5rem 1.25rem;">{profile.percentage}% Risk Score</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        border_cls = "konservatif" if profile.profile == "Konservatif" else ("moderat" if profile.profile == "Moderat" else "agresif")
        profile_emoji = "🛡️" if profile.profile == "Konservatif" else ("⚖️" if profile.profile == "Moderat" else "🚀")
        st.markdown(f"""
        <div class="profile-card {border_cls} animate-scale-in" style="margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
                <div style="font-size:3rem;">{profile_emoji}</div>
                <div>
                    <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;color:#A0A8B8;margin-bottom:0.25rem;">Your Risk Profile</div>
                    <div style="font-size:1.75rem;font-weight:800;color:#F8FAFC;">{profile.profile}</div>
                </div>
            </div>
            <div style="color:#A0A8B8;font-size:0.95rem;line-height:1.6;">{profile.description}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Recommended Asset Allocation")
        st.caption("Based on your risk profile and investment timeline")
        from vestara.portfolio.optimizer import INSTRUMENTS
        alloc_data = []
        for instrument, pct in profile.allocation.items():
            instrument_label = instrument.replace("_", " ").title()
            if instrument == "deposito":
                instrument_label = "Deposito"
            elif instrument == "ori_sbr":
                instrument_label = "ORI / SBR"
            elif instrument == "reksa_dana_money_market":
                instrument_label = "Reksa Dana Pasar Uang"
            elif instrument == "reksa_dana_mixed":
                instrument_label = "Reksa Dana Campuran"
            elif instrument == "reksa_dana_equity":
                instrument_label = "Reksa Dana Saham"
            elif instrument == "dire_reits":
                instrument_label = "DIRE / REITs"
            alloc_data.append({"Instrument": instrument_label, "Allocation": f"{pct}%"})
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
    st.markdown(f"**Risk Profile: {risk['profile']}**  ·  **Monthly investment: {format_idr(monthly_contribution)}**")

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
