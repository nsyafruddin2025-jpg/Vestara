import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
"""
Vestara — Goal-First Investment Platform
Premium glassmorphism UI with Apple-inspired aesthetic.
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os

from vestara.src.engine.goal_builder import GoalBuilder, STEPS_BY_GOAL
from vestara.src.engine.risk_profiler import RiskProfiler, RISK_QUESTIONS
from vestara.src.engine.peer_clustering import get_clusterer
from vestara.src.engine.feasibility_regression import FeasibilityRegressor
from vestara.src.portfolio.optimizer import build_portfolio
from vestara.data import cost_data as cd
from vestara.data.cost_data import LIVING_COST_MONTHLY, INSTRUMENT_RISK_LABELS, BASELINE_FALLBACK_LIVING_COST_MONTHLY
from vestara.data.fetcher import (
    BASELINE_FALLBACK_PROPERTY,
    BASELINE_FALLBACK_LIVING,
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
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
    if breakdown is None:
        return
    with st.expander("View cost breakdown"):
        st.markdown(f"""
        <div style="margin-bottom:0.5rem;">
            <span style="color:#94A3B8;font-size:0.85rem;">
                Current cost: <strong style="color:#F8FAFC;">{format_idr(breakdown.current_cost)}</strong>
                &nbsp;&middot;&nbsp;
                Inflation: <strong style="color:#8B5CF6;">{breakdown.inflation_rate * 100:.0f}%/yr</strong>
                &nbsp;&middot;&nbsp;
                Years: <strong style="color:#F8FAFC;">{breakdown.years_to_goal}</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)
        for item in breakdown.items:
            if item.value == 0:
                st.markdown(f"""<div class="breakdown-row"><span class="breakdown-label">{item.label}</span><span class="breakdown-value">{item.detail}</span></div>""", unsafe_allow_html=True)
            elif isinstance(item.value, (int, float)) and item.value > 1000:
                st.markdown(f"""<div class="breakdown-row"><span class="breakdown-label">{item.label}</span><span class="breakdown-value">{format_idr(item.value)} — {item.detail}</span></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="breakdown-row"><span class="breakdown-label">{item.label}</span><span class="breakdown-value">{item.value} — {item.detail}</span></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="breakdown-total-row"><span class="breakdown-total-label">Projected Total ({cd.get_current_year() + breakdown.years_to_goal})</span><span class="breakdown-total-value">{format_idr(breakdown.projected_cost)}</span></div>""", unsafe_allow_html=True)


def render_progress_bar(current: int, total: int) -> None:
    pct = min(current / total, 1.0)
    st.markdown(f"""
    <div style="margin-bottom:0.25rem;">
        <span style="color:#8B5CF6;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;">
            Step {current} of {total}
        </span>
    </div>
    <div class="progress-track">
        <div class="progress-fill" style="width:{int(pct * 100)}%;"></div>
    </div>
    """, unsafe_allow_html=True)


st.set_page_config(
    page_title="Vestara — Plan Your Life, Then Your Investment",
    page_icon="🏔️",
    layout="wide",
)


# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM GLASSMORPHISM CSS — Apple-Inspired Design System
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

/* ═══════════════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════════════════════════════════════ */
:root {
  --bg-deep:        #060912;
  --bg-navy:        #0A0F1E;
  --bg-card:        rgba(255, 255, 255, 0.04);
  --bg-glass:       rgba(255, 255, 255, 0.06);
  --bg-glass-hover: rgba(255, 255, 255, 0.09);
  --border-glass:   rgba(255, 255, 255, 0.08);
  --border-bright:  rgba(255, 255, 255, 0.14);

  --violet-500:     #8B5CF6;
  --violet-400:     #A78BFA;
  --violet-glow:    rgba(139, 92, 246, 0.35);
  --cyan-400:       #22D3EE;
  --cyan-glow:      rgba(34, 211, 238, 0.3);

  --text-primary:   #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted:    #475569;

  --radius-sm:   12px;
  --radius-md:   20px;
  --radius-lg:   28px;
  --radius-xl:   36px;

  --shadow-card:  0 8px 32px rgba(0,0,0,0.4), 0 1px 0 rgba(255,255,255,0.04) inset;
  --shadow-glow: 0 0 40px rgba(139, 92, 246, 0.15), 0 8px 32px rgba(0,0,0,0.4);
  --shadow-pill: 0 4px 24px rgba(139, 92, 246, 0.4);

  --font: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ═══════════════════════════════════════════════════════════════════════════
   BASE RESET & TYPOGRAPHY
   ═══════════════════════════════════════════════════════════════════════════ */
* { font-family: var(--font) !important; box-sizing: border-box; }

html, body, [data-testid="stApp"] {
  background: var(--bg-deep) !important;
  background-image:
    radial-gradient(ellipse 80% 60% at 50% -10%, rgba(139,92,246,0.18) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 85% 15%, rgba(34,211,238,0.08) 0%, transparent 50%),
    radial-gradient(ellipse 50% 40% at 15% 80%, rgba(139,92,246,0.06) 0%, transparent 50%);
  min-height: 100vh;
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}

h1 { font-size: 3rem !important; font-weight: 800 !important; color: #F8FAFC !important; letter-spacing: -0.03em !important; line-height: 1.1 !important; }
h2 { font-size: 1.6rem !important; font-weight: 700 !important; color: #F8FAFC !important; letter-spacing: -0.02em !important; line-height: 1.25 !important; }
h3 { font-size: 1.15rem !important; font-weight: 600 !important; color: #F8FAFC !important; letter-spacing: -0.01em !important; }
h4 { font-size: 1rem !important; font-weight: 600 !important; color: var(--text-secondary) !important; }
p, span, div, label { color: var(--text-secondary) !important; font-size: 0.9rem !important; line-height: 1.7 !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   FLOATING NAVIGATION DOCK
   ═══════════════════════════════════════════════════════════════════════════ */

.nav-dock {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px;
  background: rgba(10, 15, 30, 0.75);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid var(--border-glass);
  border-radius: 22px;
  box-shadow:
    0 16px 48px rgba(0,0,0,0.6),
    0 0 0 1px rgba(255,255,255,0.04) inset,
    0 1px 0 rgba(255,255,255,0.08) inset;
  white-space: nowrap;
}

.nav-dock-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 14px;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  color: var(--text-muted) !important;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  border: 1px solid transparent;
  letter-spacing: 0.01em;
}
.nav-dock-item:hover {
  color: #F8FAFC !important;
  background: var(--bg-glass);
  border-color: var(--border-glass);
}
.nav-dock-item.active {
  color: #F8FAFC !important;
  background: linear-gradient(135deg, rgba(139,92,246,0.25), rgba(34,211,238,0.15));
  border-color: rgba(139,92,246,0.4);
  box-shadow: 0 0 20px rgba(139,92,246,0.2), 0 2px 8px rgba(0,0,0,0.3);
}
.nav-dock-item .nav-icon { font-size: 1.1rem !important; }
.nav-dock-divider {
  width: 1px;
  height: 24px;
  background: var(--border-glass);
  margin: 0 4px;
  flex-shrink: 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   LAYOUT SPACING
   ═══════════════════════════════════════════════════════════════════════════ */
.block-container {
  padding-top: 2.5rem !important;
  padding-bottom: 120px !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  max-width: 1200px !important;
  margin: 0 auto !important;
}
section[data-testid="stMainBlockContainer"] > div {
  padding-left: 0;
  padding-right: 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FROSTED GLASS CARDS
   ═══════════════════════════════════════════════════════════════════════════ */
.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-card);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
}
.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
}
.glass-card:hover {
  background: var(--bg-glass-hover);
  border-color: var(--border-bright);
  box-shadow: var(--shadow-glow);
  transform: translateY(-2px);
}

.glass-card-sm {
  background: var(--bg-glass);
  backdrop-filter: blur(16px) saturate(150%);
  -webkit-backdrop-filter: blur(16px) saturate(150%);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-card);
  transition: all 0.25s ease;
}
.glass-card-sm:hover {
  background: var(--bg-glass-hover);
  border-color: var(--border-bright);
  transform: translateY(-1px);
}

/* Hero card — full width, extra glow */
.hero-card {
  background: linear-gradient(135deg, rgba(139,92,246,0.12), rgba(34,211,238,0.06));
  border: 1px solid rgba(139,92,246,0.2);
  border-radius: var(--radius-xl);
  padding: 3rem;
  text-align: center;
  box-shadow: var(--shadow-glow);
  position: relative;
  overflow: hidden;
}
.hero-card::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at center, rgba(139,92,246,0.06) 0%, transparent 60%);
  pointer-events: none;
}

/* ═══════════════════════════════════════════════════════════════════════════
   PROJECTED TOTAL — GLOWING GRADIENT PILL
   ═══════════════════════════════════════════════════════════════════════════ */
.glow-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 28px;
  background: linear-gradient(135deg, rgba(139,92,246,0.35), rgba(34,211,238,0.25));
  border: 1px solid rgba(139,92,246,0.5);
  border-radius: 999px;
  box-shadow: var(--shadow-pill), 0 0 60px rgba(139,92,246,0.2);
  color: #F8FAFC !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.01em;
  animation: pillPulse 3s ease-in-out infinite;
  position: relative;
  overflow: hidden;
}
.glow-pill::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
  animation: shimmer 3s ease-in-out infinite;
}
.glow-pill .pill-label {
  font-size: 0.7rem !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--violet-400) !important;
  opacity: 0.9;
}
.glow-pill .pill-value {
  font-size: 1.35rem !important;
  font-weight: 800 !important;
  background: linear-gradient(135deg, #F1F5F9, #A5B4FC);
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
}

@keyframes pillPulse {
  0%, 100% { box-shadow: var(--shadow-pill), 0 0 40px rgba(139,92,246,0.15); }
  50% { box-shadow: var(--shadow-pill), 0 0 80px rgba(139,92,246,0.3), 0 0 120px rgba(34,211,238,0.1); }
}
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* ═══════════════════════════════════════════════════════════════════════════
   GOAL LIST — BORDERLESS MENU
   ═══════════════════════════════════════════════════════════════════════════ */
.goal-list-container {
  margin: 1.5rem 0 2rem;
}

/* Hide the default Streamlit radio label */
.goal-list-container .st-at {
  display: none !important;
}

/* Style the radio option rows */
.goal-list-container [data-testid="stRadio"] > label {
  display: flex !important;
  align-items: center;
  gap: 0.875rem;
  padding: 0.85rem 1rem;
  border-radius: var(--radius-sm);
  background: transparent !important;
  border: none !important;
  cursor: pointer;
  transition: background 0.18s ease;
  color: var(--text-secondary) !important;
  font-size: 0.95rem !important;
  font-weight: 500 !important;
  line-height: 1.4 !important;
  margin: 0 !important;
  box-shadow: none !important;
}
.goal-list-container [data-testid="stRadio"] > label:hover {
  background: var(--bg-glass) !important;
  color: #F8FAFC !important;
}

/* Selected state — violet text + subtle underline dot */
.goal-list-container [data-testid="stRadio"] label:has([checked]) {
  color: #F8FAFC !important;
  font-weight: 600 !important;
  position: relative;
}
.goal-list-container [data-testid="stRadio"] label:has([checked])::after {
  content: '';
  position: absolute;
  bottom: 4px;
  left: 2.5rem;
  width: 20px;
  height: 2px;
  background: linear-gradient(90deg, var(--violet-500), var(--cyan-400));
  border-radius: 999px;
}

/* Selected radio dot indicator */
.goal-list-container [data-testid="stRadio"] label:has([checked]) .st-dn {
  background: var(--violet-500) !important;
  border-color: var(--violet-500) !important;
  box-shadow: 0 0 8px rgba(139,92,246,0.5) !important;
}

/* Remove default circle indicator for unselected */
.goal-list-container [data-testid="stRadio"] .st-dn {
  background: rgba(255,255,255,0.1) !important;
  border: 1.5px solid rgba(255,255,255,0.12) !important;
  width: 16px !important;
  height: 16px !important;
  min-width: 16px !important;
  border-radius: 50% !important;
  margin-right: 0 !important;
  flex-shrink: 0;
  top: auto !important;
  position: relative !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   METRIC TILES
   ═══════════════════════════════════════════════════════════════════════════ */
.metric-tile {
  background: var(--bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  text-align: center;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
}
.metric-tile:hover {
  border-color: var(--border-bright);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.metric-tile .metric-label {
  font-size: 0.7rem !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted) !important;
  margin-bottom: 0.6rem;
}
.metric-tile .metric-value {
  font-size: 1.6rem !important;
  font-weight: 800 !important;
  color: #F8FAFC !important;
  letter-spacing: -0.02em;
  line-height: 1.1 !important;
}
.metric-tile.accent .metric-value {
  background: linear-gradient(135deg, var(--violet-400), var(--cyan-400));
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
}
.metric-tile::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--violet-500), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}
.metric-tile:hover::before { opacity: 1; }

/* ═══════════════════════════════════════════════════════════════════════════
   VERDICT & STATUS BADGES
   ═══════════════════════════════════════════════════════════════════════════ */
.verdict-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 0.75rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.04em;
}
.verdict-badge.green {
  background: rgba(16,185,129,0.12);
  border: 1px solid rgba(16,185,129,0.3);
  color: #34D399 !important;
  box-shadow: 0 0 20px rgba(16,185,129,0.1);
}
.verdict-badge.yellow {
  background: rgba(245,158,11,0.12);
  border: 1px solid rgba(245,158,11,0.3);
  color: #FBBF24 !important;
  box-shadow: 0 0 20px rgba(245,158,11,0.1);
}
.verdict-badge.red {
  background: rgba(239,68,68,0.12);
  border: 1px solid rgba(239,68,68,0.3);
  color: #F87171 !important;
  box-shadow: 0 0 20px rgba(239,68,68,0.1);
}
.verdict-badge.violet {
  background: rgba(139,92,246,0.12);
  border: 1px solid rgba(139,92,246,0.3);
  color: var(--violet-400) !important;
  box-shadow: 0 0 20px rgba(139,92,246,0.1);
}

.risk-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.04em;
}
.risk-badge.high {
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.25);
  color: #F87171 !important;
}
.risk-badge.medium {
  background: rgba(245,158,11,0.1);
  border: 1px solid rgba(245,158,11,0.25);
  color: #FBBF24 !important;
}
.risk-badge.low {
  background: rgba(16,185,129,0.1);
  border: 1px solid rgba(16,185,129,0.25);
  color: #34D399 !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   STEP PROGRESS
   ═══════════════════════════════════════════════════════════════════════════ */
.step-header { margin-bottom: 2rem; }
.step-eyebrow {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--violet-400) !important;
  margin-bottom: 0.4rem;
}
.step-title { font-size: 1.6rem !important; font-weight: 800 !important; color: #F8FAFC !important; letter-spacing: -0.02em !important; }
.step-subtitle { font-size: 0.9rem !important; color: var(--text-muted) !important; margin-top: 0.25rem !important; }

.progress-track {
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 999px;
  overflow: hidden;
  margin: 1.5rem 0 2rem;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--violet-500), var(--cyan-400));
  border-radius: 999px;
  transition: width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 0 12px rgba(139,92,246,0.5);
}

.step-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 0.75rem !important;
  font-weight: 700 !important;
  flex-shrink: 0;
}
.step-indicator.done {
  background: linear-gradient(135deg, var(--violet-500), var(--cyan-400));
  color: white !important;
}
.step-indicator.active {
  background: var(--bg-glass);
  border: 2px solid var(--violet-500);
  color: var(--violet-400) !important;
  box-shadow: 0 0 16px rgba(139,92,246,0.3);
}
.step-indicator.pending {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  color: var(--text-muted) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FORM INPUTS
   ═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextArea"] textarea {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid var(--border-glass) !important;
  color: #F8FAFC !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.9rem !important;
  padding: 0.7rem 1rem !important;
  transition: all 0.2s ease !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testdata="stSelectbox"] > div > div:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: rgba(139,92,246,0.5) !important;
  box-shadow: 0 0 0 3px rgba(139,92,246,0.12) !important;
  background: rgba(255,255,255,0.07) !important;
}
[data-testid="stRadio"] label {
  color: var(--text-secondary) !important;
  font-size: 0.88rem !important;
  line-height: 1.6 !important;
}
[data-testid="stRadio"] label:hover { color: #F8FAFC !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════════════════════ */
.st-dg > div > button,
[data-testid="stFormSubmitButton"] > div > button {
  background: linear-gradient(135deg, var(--violet-500), #7C3AED) !important;
  color: white !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 700 !important;
  letter-spacing: 0.01em !important;
  padding: 0.8rem 2rem !important;
  box-shadow: 0 4px 20px rgba(139,92,246,0.35) !important;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
  font-size: 0.88rem !important;
}
.st-dg > div > button:hover,
[data-testid="stFormSubmitButton"] > div > button:hover {
  filter: brightness(1.1) !important;
  box-shadow: 0 6px 30px rgba(139,92,246,0.5) !important;
  transform: translateY(-2px) scale(1.01) !important;
}
.st-dg > div > button:active,
[data-testid="stFormSubmitButton"] > div > button:active {
  transform: translateY(0px) scale(0.99) !important;
}

/* Ghost / secondary button */
.secondary-btn {
  background: var(--bg-glass) !important;
  border: 1px solid var(--border-bright) !important;
  color: var(--text-secondary) !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  padding: 0.75rem 1.75rem !important;
  font-size: 0.88rem !important;
  transition: all 0.2s ease !important;
  cursor: pointer;
}
.secondary-btn:hover {
  background: var(--bg-glass-hover) !important;
  border-color: var(--violet-500) !important;
  color: #F8FAFC !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   ANIMATIONS
   ═══════════════════════════════════════════════════════════════════════════ */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.96) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes glowPulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
.animate-fade-up { animation: fadeSlideUp 0.4s ease-out forwards; }
.animate-scale-in { animation: scaleIn 0.5s cubic-bezier(0.34,1.56,0.64,1) forwards; }
.delay-1 { animation-delay: 0.08s; opacity: 0; }
.delay-2 { animation-delay: 0.16s; opacity: 0; }
.delay-3 { animation-delay: 0.24s; opacity: 0; }
.delay-4 { animation-delay: 0.32s; opacity: 0; }

/* ═══════════════════════════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.14); }

/* ═══════════════════════════════════════════════════════════════════════════
   PROFILE / RISK CARDS
   ═══════════════════════════════════════════════════════════════════════════ */
.profile-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1.5px solid var(--border-glass);
  border-radius: var(--radius-lg);
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}
.profile-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-glow);
}
.profile-card.konservatif { border-color: rgba(34,211,238,0.4); }
.profile-card.konservatif:hover { box-shadow: 0 0 40px rgba(34,211,238,0.15), var(--shadow-card); }
.profile-card.moderat { border-color: rgba(139,92,246,0.4); }
.profile-card.moderat:hover { box-shadow: 0 0 40px rgba(139,92,246,0.15), var(--shadow-card); }
.profile-card.agresif { border-color: rgba(245,158,11,0.4); }
.profile-card.agresif:hover { box-shadow: 0 0 40px rgba(245,158,11,0.15), var(--shadow-card); }

/* ═══════════════════════════════════════════════════════════════════════════
   SCORE CIRCLE
   ═══════════════════════════════════════════════════════════════════════════ */
.score-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  font-size: 2rem !important;
  font-weight: 800 !important;
  border: 3px solid;
  position: relative;
}
.score-circle.green {
  background: rgba(16,185,129,0.08);
  border-color: #10B981;
  color: #34D399 !important;
  box-shadow: 0 0 30px rgba(16,185,129,0.15);
}
.score-circle.yellow {
  background: rgba(245,158,11,0.08);
  border-color: #F59E0B;
  color: #FBBF24 !important;
  box-shadow: 0 0 30px rgba(245,158,11,0.15);
}
.score-circle.red {
  background: rgba(239,68,68,0.08);
  border-color: #EF4444;
  color: #F87171 !important;
  box-shadow: 0 0 30px rgba(239,68,68,0.15);
}

/* ═══════════════════════════════════════════════════════════════════════════
   BREAKDOWN TABLE
   ═══════════════════════════════════════════════════════════════════════════ */
.breakdown-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.breakdown-row:last-child { border-bottom: none; }
.breakdown-label { color: var(--text-secondary) !important; font-size: 0.88rem !important; }
.breakdown-value { color: #F8FAFC !important; font-weight: 600 !important; font-size: 0.88rem !important; }
.breakdown-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, rgba(139,92,246,0.12), rgba(34,211,238,0.06));
  border: 1px solid rgba(139,92,246,0.2);
  border-radius: var(--radius-sm);
  margin-top: 0.75rem;
}
.breakdown-total-label { color: #F8FAFC !important; font-weight: 700 !important; font-size: 0.95rem !important; }
.breakdown-total-value {
  color: var(--violet-400) !important;
  font-weight: 800 !important;
  font-size: 1rem !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   COMPARISON BAR
   ═══════════════════════════════════════════════════════════════════════════ */
.compare-bar {
  background: rgba(255,255,255,0.06);
  border-radius: 6px;
  height: 6px;
  overflow: hidden;
  margin: 0.5rem 0;
}
.compare-fill {
  height: 100%;
  border-radius: 6px;
  background: linear-gradient(90deg, var(--violet-500), var(--cyan-400));
  box-shadow: 0 0 8px rgba(139,92,246,0.4);
}

/* ═══════════════════════════════════════════════════════════════════════════
   PEER CLUSTER CARDS
   ═══════════════════════════════════════════════════════════════════════════ */
.peer-card {
  background: var(--bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1.5px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: all 0.25s ease;
}
.peer-card:hover {
  border-color: var(--border-bright);
  transform: translateY(-1px);
}

/* ═══════════════════════════════════════════════════════════════════════════
   DISCLAIMER
   ═══════════════════════════════════════════════════════════════════════════ */
.disclaimer {
  background: rgba(245,158,11,0.06);
  border: 1px solid rgba(245,158,11,0.18);
  border-radius: var(--radius-md);
  padding: 1.25rem 1.5rem;
  font-size: 0.8rem !important;
  color: var(--text-muted) !important;
  line-height: 1.6 !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   HIDE DEFAULTS
   ═══════════════════════════════════════════════════════════════════════════ */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
[data-testid="stAlert"] { border-radius: var(--radius-sm) !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   DIVIDERS & SECTION HEADERS
   ═══════════════════════════════════════════════════════════════════════════ */
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-glass), transparent);
  margin: 2rem 0;
}
.section-title {
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--text-muted) !important;
  margin-bottom: 1.25rem;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FLOAT LABEL
   ═══════════════════════════════════════════════════════════════════════════ */
.float-label {
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted) !important;
  margin-bottom: 0.5rem;
  display: block;
}

/* ═══════════════════════════════════════════════════════════════════════════
   PORTFOLIO ALLOCATION BAR
   ═══════════════════════════════════════════════════════════════════════════ */
.alloc-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.alloc-row:last-child { border-bottom: none; }
.alloc-name { font-size: 0.88rem !important; color: var(--text-secondary) !important; flex: 1; }
.alloc-pct { font-size: 0.88rem !important; font-weight: 700 !important; color: #F8FAFC !important; width: 48px; text-align: right; }
.alloc-bar-track {
  flex: 2;
  height: 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 999px;
  overflow: hidden;
}
.alloc-bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--violet-500), var(--cyan-400));
}

/* Selectbox text color fix */
[data-testid="stSelectbox"] span {
    color: #F8FAFC !important;
}
[data-testid="stSelectbox"] > div > div {
    color: #F8FAFC !important;
    background-color: #1E1E2E !important;
}
[data-testid="stSelectbox"] span { color: #F8FAFC !important; }
[data-testid="stSelectbox"] > div > div { color: #F8FAFC !important; background-color: #1A1A2E !important; }
details summary { color: #F8FAFC !important; padding-left: 1.5rem !important; }
details summary p { color: #F8FAFC !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FLOATING NAV DOCK COMPONENT
# ─────────────────────────────────────────────────────────────────────────────
def nav_dock():
    pages = ["🏠 Goals", "📊 Feasibility", "🎯 Risk Profile", "💼 Portfolio", "📈 Dashboard"]
    if "page" not in st.session_state:
        st.session_state["page"] = "🏠 Goals"

    cols = st.columns(len(pages) + 2)
    for i, page_name in enumerate(pages):
        active = st.session_state["page"] == page_name
        clicked = cols[i + 1].button(
            page_name,
            key=f"nav_{page_name}",
            use_container_width=True,
        )
        if clicked:
            st.session_state["page"] = page_name
            st.rerun()

nav_dock()

# ── Sidebar data attribution ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**📊 Property data:**")
    st.markdown("Colliers Indonesia Q1 2025")
    st.markdown("")
    st.markdown("🔜 **Coming soon:**")
    st.markdown("Bandung · Surabaya · Yogyakarta")
    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: GOALS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("page", "🏠 Goals") == "🏠 Goals":

    st.markdown('<div class="step-header animate-fade-up">'
                '<div class="step-eyebrow">Step 1 of 4</div>'
                '<div class="step-title">What\'s your life goal?</div>'
                '<div class="step-subtitle">Choose the milestone you\'re investing toward</div>'
                '</div>', unsafe_allow_html=True)

    # Progress bar
    total_steps = 4
    current = 1
    pct = int(current / total_steps * 100)
    st.markdown(f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)

    # Goal definitions: (icon, display_label, goal_type_key, enabled)
    goals = [
        ("🏠", "Property", "Property", True),
        ("🛡️", "Emergency Fund", "Emergency Fund", True),
        ("🌴", "Retirement", "Retirement", True),
        ("🎓", "Education  🔜 Coming Soon", "Education", False),
        ("🎓", "Higher Education  🔜 Coming Soon", "Higher Education", False),
        ("💍", "Wedding  🔜 Coming Soon", "Wedding", False),
        ("✨", "Custom  🔜 Coming Soon", "Custom", False),
    ]

    # Build a lookup: display_label -> goal_type_key
    goal_label_to_type = {label: gtype for _, label, gtype, _ in goals}

    # Active goals only for radio
    active_goals = [(icon, label, gtype) for icon, label, gtype, enabled in goals if enabled]

    st.markdown('<div class="goal-list-container">', unsafe_allow_html=True)

    # Use st.radio for active goals only
    active_options = [f"{icon}  {label}" for icon, label, _ in active_goals]
    selected_label = st.radio(
        "Select your goal",
        active_options,
        index=0,
        label_visibility="collapsed",
        key="goal_radio",
    )

    # Show coming soon goals as disabled info badges
    coming_soon = [label for icon, label, _, enabled in goals if not enabled]
    if coming_soon:
        st.markdown(
            "<br>".join(f"<span style='color:#64748B;font-size:0.85rem;'>  {g}</span>" for g in coming_soon),
            unsafe_allow_html=True,
        )

    selected = ""
    for icon, label, gtype in active_goals:
        if f"{icon}  {label}" == selected_label:
            selected = gtype
            break

    if selected:
        st.session_state["goal_type"] = selected
        st.session_state["selected_goal"] = selected

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Multi-step wizard for goal types ─────────────────────────────
    if selected:
        # Initialise step tracking when goal type changes
        if st.session_state.get("goal_type") != selected:
            st.session_state["goal_type"] = selected
            st.session_state["goal_step"] = 0
            st.session_state["goal_step_answers"] = {}

        goal_type = selected
        steps = STEPS_BY_GOAL.get(goal_type, [])
        total_goal_steps = 6 if goal_type == "Property" else len(steps)
        current_step = st.session_state.get("goal_step", 0)
        answers = st.session_state.get("goal_step_answers", {})


        # ── EDUCATION ────────────────────────────────────────────────
        if goal_type == "Education":
            render_progress_bar(current_step + 1, total_goal_steps)

            if current_step == 0:
                education_level = st.radio("Education level", cd.EDUCATION_LEVELS, index=None, label_visibility="collapsed")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if education_level:
                            answers["education_level"] = education_level
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 1
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:
                render_progress_bar(2, total_goal_steps)
                st.markdown('<div class="step-title">What type of school?</div>', unsafe_allow_html=True)
                school_type = st.radio("School type", cd.EDUCATION_SCHOOL_TYPES, index=None)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if school_type:
                            answers["school_type"] = school_type
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 2
                            st.rerun()

            elif current_step == 2:
                render_progress_bar(3, total_goal_steps)
                st.markdown('<div class="step-title">How old is your child now?</div>', unsafe_allow_html=True)
                child_age = st.number_input("Child's current age", min_value=0, max_value=20, value=6, step=1)
                education_level = answers.get("education_level", "Primary")
                entry_age = cd.EDUCATION_ENTRY_AGE.get(education_level, 6)
                years_until = max(entry_age - child_age, 0)
                entry_year = cd.get_current_year() + years_until
                if years_until > 0:
                    st.markdown(f"""<div class="entry-info"><strong>Entry year:</strong> {years_until} years from now (year {entry_year}) — your child will enter <strong>{education_level}</strong> at age {entry_age}</div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="entry-info" style="border-color:#EF4444;"><strong>Note:</strong> Your child is already past the entry age for {education_level}. Cost is calculated from today.</div>""", unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["child_age"] = child_age
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()

            elif current_step == 3:
                render_progress_bar(4, total_goal_steps)
                st.markdown('<div class="step-title">Which city will your child attend school in?</div>', unsafe_allow_html=True)
                city = st.radio("City", GoalBuilder.CITIES, index=0, key="education_city_radio", horizontal=False)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 2
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 4
                        st.rerun()

            elif current_step == 4:
                render_progress_bar(5, total_goal_steps)
                answers["city"] = answers.get("city", GoalBuilder.CITIES[0])
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
                    st.markdown(f"**Entry year:** {entry_year} ({years_until} years)")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Education", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""<div class="glass-card" style="border: 1.5px solid rgba(139,92,246,0.4);margin-top:1rem;"><div style="text-align:center;"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div><div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#8B5CF6,#22D3EE);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{format_idr(profile.estimated_cost)}</div><div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">{profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal</div></div></div>""", unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("<- Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── HIGHER EDUCATION ────────────────────────────────────────
        elif goal_type == "Higher Education":
            render_progress_bar(current_step + 1, total_goal_steps)

            if current_step == 0:
                st.markdown('<div class="step-title">What degree is your child aiming for?</div>', unsafe_allow_html=True)
                degree_level = st.radio("Degree level", cd.HIGHER_ED_DEGREE_LEVELS, index=None, label_visibility="collapsed")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if degree_level:
                            answers["degree_level"] = degree_level
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 1
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:
                render_progress_bar(2, total_goal_steps)
                st.markdown('<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Will they study in Indonesia or abroad?</div>', unsafe_allow_html=True)
                location = st.radio("Study location", ["In Indonesia", "Abroad"], index=None, label_visibility="collapsed")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
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

            elif current_step == 2:
                render_progress_bar(3, total_goal_steps)
                st.markdown('<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                location = answers.get("study_location", "In Indonesia")
                if location == "Abroad":
                    st.markdown('<div class="step-title">Which country will they study in?</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="step-title">Study location confirmed: Indonesia</div>', unsafe_allow_html=True)
                country = st.selectbox("Country", ["Indonesia"] + cd.HIGHER_ED_ABROAD_COUNTRIES, index=None, placeholder="Select country" if location == "Abroad" else None)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
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

            elif current_step == 3:
                render_progress_bar(4, total_goal_steps)
                st.markdown('<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What field of study?</div>', unsafe_allow_html=True)
                field = st.selectbox("Field of study", cd.HIGHER_ED_FIELDS, index=None, placeholder="Select field")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
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

            elif current_step == 4:
                render_progress_bar(5, total_goal_steps)
                st.markdown('<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">When does enrollment start?</div>', unsafe_allow_html=True)
                current_yr = cd.get_current_year()
                years_until = st.slider("Years until enrollment", min_value=0, max_value=20, value=4, step=1)
                enrollment_yr = current_yr + years_until
                st.markdown(f"""<div class="entry-info">Enrollment year: <strong>{enrollment_yr}</strong> ({years_until} year{"s" if years_until != 1 else ""} from now)</div>""", unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["years_until_enrollment"] = years_until
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 5
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 5:
                render_progress_bar(6, total_goal_steps)
                st.markdown('<div class="step-label">Higher Education</div>', unsafe_allow_html=True)
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
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Higher Education", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""<div class="glass-card" style="border: 1.5px solid rgba(139,92,246,0.4);margin-top:1rem;"><div style="text-align:center;"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div><div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#8B5CF6,#22D3EE);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{format_idr(profile.estimated_cost)}</div><div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">{profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal</div></div></div>""", unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("<- Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                if st.button("< Back"):
                    st.session_state["goal_step"] = 4
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── PROPERTY ────────────────────────────────────────────────
        elif goal_type == "Property":
            current_year = cd.get_current_year()

            if current_step == 0:
                property_type = st.radio("Property type", cd.PROPERTY_TYPES, index=None, label_visibility="collapsed")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if property_type:
                            answers["property_type"] = property_type
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 1
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:
                render_progress_bar(2, total_goal_steps)
                st.markdown('<div class="step-title">Which city?</div>', unsafe_allow_html=True)
                city = st.selectbox("City", cd.ACTIVE_CITIES, key="city_main")
                st.caption("🔜 Bandung, Surabaya, Yogyakarta — Coming Soon")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 2
                        st.rerun()

            elif current_step == 2:
                render_progress_bar(3, total_goal_steps)
                st.markdown('<div class="step-title">Which area?</div>', unsafe_allow_html=True)
                city = answers.get("city", "Jakarta")
                area = st.selectbox("Area", cd.CITY_AREAS.get(city, []), key="city_area")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["area"] = area
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()

            elif current_step == 3:
                render_progress_bar(4, total_goal_steps)
                property_type = st.session_state.get("goal_step_answers", {}).get("property_type", "Apartment")
                sizes = cd.PROPERTY_SIZES_BY_TYPE.get(property_type, list(cd.APARTMENT_SIZES.keys()))
                st.markdown('<div class="step-title">What size is the property?</div>', unsafe_allow_html=True)
                size = st.selectbox("Size", sizes, index=None, placeholder="Select size", key="property_size_select")
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
                    if st.button("< Back"):
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

            elif current_step == 4:
                render_progress_bar(5, total_goal_steps)
                st.markdown('<div class="step-title">When do you plan to purchase?</div>', unsafe_allow_html=True)
                target_year = st.slider("Target purchase year", min_value=current_year, max_value=current_year + 20, value=current_year + 10, step=1)
                st.markdown(f"""<div class="entry-info">Target: <strong>{target_year}</strong> <span class="current-year-badge">{current_year}</span></div>""", unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["target_year"] = target_year
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 5
                        st.rerun()

            elif current_step == 5:
                render_progress_bar(current_step + 1, total_goal_steps)
                st.markdown('<div class="step-title">Review your selections</div>', unsafe_allow_html=True)
                ptype = answers.get("property_type", "-")
                city = answers.get("city", "-")
                size = answers.get("size", "-")
                yr = answers.get("target_year", current_year)
                inflation_rate = cd.PROPERTY_INFLATION_RATE
                years = max(yr - current_year, 0)
                st.markdown(f"**Type:** {ptype} &nbsp;&nbsp; **City:** {city}")
                st.markdown(f"**Size:** {size} &nbsp;&nbsp; **Target year:** {yr}")
                st.markdown(f"**Inflation:** {inflation_rate * 100:.0f}%/yr &nbsp;&nbsp; **Years to purchase:** {years}")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Property", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""<div class="glass-card" style="border: 1.5px solid rgba(139,92,246,0.4);margin-top:1rem;"><div style="text-align:center;"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div><div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#8B5CF6,#22D3EE);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{format_idr(profile.estimated_cost)}</div><div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">{profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal</div></div></div>""", unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("<- Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                if st.button("< Back"):
                    st.session_state["goal_step"] = 4
                    st.rerun()

        # ── RETIREMENT ─────────────────────────────────────────────
        elif goal_type == "Retirement":
            render_progress_bar(current_step + 1, total_goal_steps)

            if current_step == 0:
                st.markdown('<div class="step-title">How old are you now?</div>', unsafe_allow_html=True)
                current_age = st.number_input("Current age", min_value=18, max_value=70, value=25, step=1)
                if st.button("Next →", type="primary"):
                    answers["current_age"] = current_age
                    st.session_state["goal_step_answers"] = answers
                    st.session_state["goal_step"] = 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:
                render_progress_bar(2, total_goal_steps)
                st.markdown('<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">At what age do you want to retire?</div>', unsafe_allow_html=True)
                current_age = answers.get("current_age", 25)
                retirement_age = st.number_input("Retirement age", min_value=current_age + 1, max_value=80, value=55, step=1)
                years_to_save = retirement_age - current_age
                st.markdown(f"""<div class="entry-info">You have <strong>{years_to_save} years</strong> to build your retirement fund</div>""", unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["retirement_age"] = retirement_age
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 2
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:
                render_progress_bar(3, total_goal_steps)
                st.markdown('<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which city do you plan to retire in?</div>', unsafe_allow_html=True)
                city = st.selectbox("City", cd.ACTIVE_CITIES, key="retirement_city_main")
                st.caption("🔜 Bandung, Surabaya, Yogyakarta — Coming Soon")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:
                render_progress_bar(4, total_goal_steps)
                st.markdown('<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Which area?</div>', unsafe_allow_html=True)
                city = answers.get("city", "Jakarta")
                area = st.selectbox("Area", cd.CITY_AREAS.get(city, []), key="retirement_city_area")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 2
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["area"] = area
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 4
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 4:
                render_progress_bar(5, total_goal_steps)
                st.markdown('<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What lifestyle do you want in retirement?</div>', unsafe_allow_html=True)
                lifestyle = st.radio("Lifestyle", cd.RETIREMENT_LIFESTYLE_OPTIONS, index=None, label_visibility="collapsed")
                show_custom = (lifestyle and "Custom" in lifestyle)
                if show_custom:
                    custom_monthly = st.number_input("Your target monthly spend (IDR)", min_value=1_000_000, max_value=500_000_000, value=15_000_000, step=500_000)
                    answers["custom_monthly"] = custom_monthly
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 3
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if lifestyle:
                            answers["lifestyle"] = lifestyle
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 5
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 5:
                render_progress_bar(6, total_goal_steps)
                st.markdown('<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What life expectancy do you assume?</div>', unsafe_allow_html=True)
                life_options = [75, 80, 85, "Custom — enter my own assumption"]
                life_display = ["75 years", "80 years", "85 years", "Custom"]
                life_exp_idx = st.selectbox("Life expectancy", range(len(life_options)), format_func=lambda i: life_display[i], index=1)
                life_expectancy = life_options[life_exp_idx]
                if life_expectancy == "Custom — enter my own assumption":
                    life_expectancy = st.number_input("Your life expectancy assumption", min_value=60, max_value=100, value=80, step=1)
                retirement_age = answers.get("retirement_age", 55)
                years_in_retirement = max(life_expectancy - retirement_age, 0)
                st.markdown(f"""<div class="entry-info">Retirement duration: <strong>{years_in_retirement} years</strong> (age {retirement_age} → {life_expectancy})</div>""", unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 4
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["life_expectancy"] = life_expectancy
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 6
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 6:
                render_progress_bar(7, total_goal_steps)
                st.markdown('<div class="step-label">Retirement</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Review your selections</div>', unsafe_allow_html=True)
                cur = answers.get("current_age", 0)
                ret = answers.get("retirement_age", 0)
                city = answers.get("city", "-")
                area = answers.get("area", "-")
                lifestyle = answers.get("lifestyle", "-")
                life_exp = answers.get("life_expectancy", 80)
                st.markdown(f"**Current age:** {cur} &nbsp;&nbsp; **Retirement age:** {ret}")
                st.markdown(f"**City:** {city} &nbsp;&nbsp; **Area:** {area} &nbsp;&nbsp; **Lifestyle:** {lifestyle}")
                st.markdown(f"**Life expectancy:** {life_exp}")
                if st.button("Calculate Goal Cost", type="primary", use_container_width=True):
                    gb = GoalBuilder()
                    profile = gb.build_goal("Retirement", answers)
                    st.session_state["goal_profile"] = profile.to_dict()
                    st.session_state["goal_set"] = True
                    st.session_state["goal_cost_result"] = profile
                    st.markdown(f"""<div class="glass-card" style="border: 1.5px solid rgba(139,92,246,0.4);margin-top:1rem;"><div style="text-align:center;"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div><div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#8B5CF6,#22D3EE);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{format_idr(profile.estimated_cost)}</div><div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">{profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal</div></div></div>""", unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("<- Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                if st.button("< Back"):
                    st.session_state["goal_step"] = 4
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── EMERGENCY FUND ─────────────────────────────────────────
        elif goal_type == "Emergency Fund":
            render_progress_bar(current_step + 1, total_goal_steps)

            if current_step == 0:
                st.markdown('<div class="step-title">What is your monthly take-home salary?</div>', unsafe_allow_html=True)
                monthly_salary = st.number_input("Monthly take-home salary (IDR)", min_value=500_000, max_value=500_000_000, value=15_000_000, step=500_000)
                bracket = get_salary_bracket(monthly_salary)
                st.markdown(f'<div style="color:#8B5CF6;font-size:0.85rem;font-weight:600;">Career bracket: {bracket}</div>', unsafe_allow_html=True)
                if st.button("Next →", type="primary"):
                    answers["monthly_salary"] = monthly_salary
                    st.session_state["goal_step_answers"] = answers
                    st.session_state["goal_step"] = 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:
                render_progress_bar(2, total_goal_steps)
                st.markdown('<div class="step-label">Emergency Fund</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What are your monthly fixed expenses?</div>', unsafe_allow_html=True)
                monthly_expenses = st.number_input("Monthly fixed expenses (IDR)", min_value=100_000, max_value=500_000_000, value=5_000_000, step=500_000)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["monthly_expenses"] = monthly_expenses
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 2
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:
                render_progress_bar(3, total_goal_steps)
                st.markdown('<div class="step-label">Emergency Fund</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">How many months of expenses should this cover?</div>', unsafe_allow_html=True)
                coverage = st.radio("Coverage duration", cd.EMERGENCY_FUND_COVERAGE_OPTIONS, index=None, label_visibility="collapsed")
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
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
                    st.markdown(f"""<div class="glass-card" style="border: 1.5px solid rgba(139,92,246,0.4);margin-top:1rem;"><div style="text-align:center;"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#94A3B8;margin-bottom:0.5rem;">Emergency Fund Target</div><div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#8B5CF6,#22D3EE);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{format_idr(profile.estimated_cost)}</div><div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">{profile.description}</div></div></div>""", unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("<- Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── WEDDING ────────────────────────────────────────────────
        elif goal_type == "Wedding":
            render_progress_bar(current_step + 1, total_goal_steps)
            current_year = cd.get_current_year()

            if current_step == 0:
                st.markdown('<div class="step-title">How many guests are you planning for?</div>', unsafe_allow_html=True)
                scale = st.radio("Wedding scale", cd.WEDDING_SCALES, index=None, label_visibility="collapsed")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if scale:
                            answers["scale"] = scale
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 1
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:
                render_progress_bar(2, total_goal_steps)
                st.markdown('<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">In which city will the wedding be held?</div>', unsafe_allow_html=True)
                city = st.radio("City", GoalBuilder.CITIES, index=0, key="wedding_city_radio", horizontal=False)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["city"] = city
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 2
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 2:
                render_progress_bar(3, total_goal_steps)
                st.markdown('<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">When is the target date?</div>', unsafe_allow_html=True)
                target_year = st.slider("Target year", min_value=current_year, max_value=current_year + 10, value=current_year + 2, step=1)
                years = max(target_year - current_year, 0)
                st.markdown(f"""<div class="entry-info"><strong>{years} year{"s" if years != 1 else ""}</strong> from now (year {target_year})</div>""", unsafe_allow_html=True)
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 1
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        answers["target_year"] = target_year
                        st.session_state["goal_step_answers"] = answers
                        st.session_state["goal_step"] = 3
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 3:
                render_progress_bar(4, total_goal_steps)
                st.markdown('<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What type of venue?</div>', unsafe_allow_html=True)
                venue = st.radio("Venue", cd.WEDDING_VENUES, index=None, label_visibility="collapsed")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
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

            elif current_step == 4:
                render_progress_bar(5, total_goal_steps)
                st.markdown('<div class="step-label">Wedding</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">What entertainment are you planning?</div>', unsafe_allow_html=True)
                entertainment = st.radio("Entertainment", cd.WEDDING_ENTERTAINMENT, index=None, label_visibility="collapsed")
                st.markdown("**Catering:** Standard (included in base cost)")
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
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
                    st.markdown(f"""<div class="glass-card" style="border: 1.5px solid rgba(139,92,246,0.4);margin-top:1rem;"><div style="text-align:center;"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div><div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#8B5CF6,#22D3EE);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{format_idr(profile.estimated_cost)}</div><div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">{profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal</div></div></div>""", unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("<- Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                st.markdown('</div>', unsafe_allow_html=True)

        # ── CUSTOM ─────────────────────────────────────────────────
        elif goal_type == "Custom":
            render_progress_bar(current_step + 1, total_goal_steps)

            if current_step == 0:
                st.markdown('<div class="step-title">What is this goal called?</div>', unsafe_allow_html=True)
                goal_name = st.text_input("Goal name", placeholder="e.g. Starting a business, Buying a car...", label_visibility="collapsed")
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
                        st.session_state["goal_step"] = 0
                        st.rerun()
                with col_s:
                    if st.button("Next →", type="primary"):
                        if goal_name:
                            answers["goal_name"] = goal_name
                            st.session_state["goal_step_answers"] = answers
                            st.session_state["goal_step"] = 1
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            elif current_step == 1:
                render_progress_bar(2, total_goal_steps)
                st.markdown('<div class="step-label">Custom Goal</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">Do you know the target amount?</div>', unsafe_allow_html=True)
                amount_mode = st.radio("Amount type", ["I know the amount — I'll enter it directly", "Help me estimate — I'll describe the goal"], index=None, label_visibility="collapsed")
                if amount_mode == "I know the amount — I'll enter it directly":
                    target_amount = st.number_input("Target amount (IDR)", min_value=0, value=100_000_000, step=5_000_000)
                    answers["target_amount"] = target_amount
                col_b, col_s = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
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

            elif current_step == 2:
                render_progress_bar(3, total_goal_steps)
                st.markdown('<div class="step-label">Custom Goal</div>', unsafe_allow_html=True)
                st.markdown('<div class="step-title">When is the target year?</div>', unsafe_allow_html=True)
                current_year = cd.get_current_year()
                target_year = st.slider("Target year", min_value=current_year, max_value=current_year + 30, value=current_year + 5, step=1)
                years = max(target_year - current_year, 0)
                st.markdown(f"""<div class="entry-info"><strong>{years} year{"s" if years != 1 else ""}</strong> from now (year {target_year})</div>""", unsafe_allow_html=True)
                col_b, _ = st.columns([1, 1])
                with col_b:
                    if st.button("< Back"):
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
                    st.markdown(f"""<div class="glass-card" style="border: 1.5px solid rgba(139,92,246,0.4);margin-top:1rem;"><div style="text-align:center;"><div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#94A3B8;margin-bottom:0.5rem;">Projected Total Cost</div><div style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#8B5CF6,#22D3EE);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{format_idr(profile.estimated_cost)}</div><div style="font-size:0.9rem;color:#94A3B8;margin-top:0.5rem;">{profile.description} &nbsp;&middot;&nbsp; {profile.timeline_years} years to goal</div></div></div>""", unsafe_allow_html=True)
                    if profile.breakdown:
                        render_cost_breakdown(profile.breakdown)
                    st.info("<- Proceed to **Feasibility Analysis** to check if this goal is achievable.")
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: FEASIBILITY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.get("page") == "📊 Feasibility":

    st.markdown('<div class="step-header animate-fade-up">'
                '<div class="step-eyebrow">Step 2 of 4</div>'
                '<div class="step-title">Feasibility Analysis</div>'
                '<div class="step-subtitle">See how your goal stacks up against your finances</div>'
                '</div>', unsafe_allow_html=True)

    total_steps = 4
    pct = int(2 / total_steps * 100)
    st.markdown(f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)

    if not st.session_state.get("goal_set"):
        st.info("👆 Set your goal first on the Goals page.")

    if st.session_state.get("goal_set"):
        gp = st.session_state["goal_profile"]
        fee = st.number_input("Monthly income (IDR)", 500_000, 10_000_000_000, 15_000_000, step=500_000, key="fee_income")
        expenses = st.number_input("Monthly expenses (IDR)", 0, 10_000_000_000, 8_000_000, step=500_000, key="fee_expenses")
        existing = st.number_input("Existing investments (IDR)", 0, 10_000_000_000, 10_000_000, step=1_000_000, key="fee_existing")

        if st.button("Analyse Feasibility", use_container_width=True):
            available = fee - expenses
            monthly_salary = fee
            monthly_living = BASELINE_FALLBACK_LIVING_COST_MONTHLY.get(gp.get("city", "Jakarta"), 5_000_000)
            city_living_cost_index = monthly_living / 1_000_000
            disposable = max(monthly_salary - monthly_living, 1)

            # Cache trained regressor in session state
            if "feasibility_regressor" not in st.session_state:
                st.session_state["feasibility_regressor"] = FeasibilityRegressor()
                st.session_state["feasibility_regressor"].train(2000)
            regressor = st.session_state["feasibility_regressor"]

            ml_result = regressor.predict_with_result(
                monthly_salary=monthly_salary,
                city_living_cost_index=city_living_cost_index,
                goal_cost=gp["estimated_cost"],
                timeline_years=gp["timeline_years"],
                income_growth_rate=0.08,
                monthly_living_cost=monthly_living,
                disposable_income=disposable,
            )

            confidence_map = {"HIGH": 85, "MEDIUM": 60, "LOW": 35}
            feasibility_score = confidence_map.get(ml_result.confidence, 60)

            result = {
                "ratio": ml_result.confidence,
                "monthly_surplus": available,
                "existing_investments": existing,
                "required_monthly": gp["estimated_cost"] / (gp["timeline_years"] * 12),
                "verdict": ml_result.verdict,
                "feasibility_score": feasibility_score,
                "predicted_months": ml_result.predicted_months,
                "confidence": ml_result.confidence,
            }
            st.session_state["feasibility_result"] = result

        if st.session_state.get("feasibility_result"):
            fr = st.session_state["feasibility_result"]
            score = fr["feasibility_score"]
            score_cls = "green" if score >= 70 else ("yellow" if score >= 40 else "red")
            score_color = "#10B981" if score >= 70 else ("#F59E0B" if score >= 40 else "#EF4444")

            st.markdown(f'''
            <div class="glass-card animate-scale-in" style="text-align:center; margin-bottom:2rem;">
                <div style="margin-bottom:1.5rem;">
                    <div class="step-eyebrow" style="margin-bottom:0.5rem;">Feasibility Score</div>
                    <div class="score-circle {score_cls}" style="font-size:2.5rem;">{score}</div>
                </div>
                <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
                    <span class="verdict-badge {fr['verdict']}">
                        {'✓ Achievable' if fr['verdict']=='green' else ('⚠ Tight Fit' if fr['verdict']=='yellow' else '✗ Not Feasible')}
                    </span>
                    <span class="verdict-badge violet">Investment Ratio: {fr['ratio']}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'''<div class="metric-tile"><div class="metric-label">Monthly Surplus</div><div class="metric-value">IDR {fr['monthly_surplus']:,.0f}</div></div>''', unsafe_allow_html=True)
            with c2:
                st.markdown(f'''<div class="metric-tile"><div class="metric-label">Required Monthly</div><div class="metric-value">IDR {fr['required_monthly']:,.0f}</div></div>''', unsafe_allow_html=True)
            with c3:
                st.markdown(f'''<div class="metric-tile"><div class="metric-label">Existing Savings</div><div class="metric-value">IDR {fr['existing_investments']:,.0f}</div></div>''', unsafe_allow_html=True)

            # Comparison bar
            max_val = max(fr['monthly_surplus'], fr['required_monthly'])
            sur_pct = min(int(fr['monthly_surplus'] / max_val * 100), 100)
            req_pct = min(int(fr['required_monthly'] / max_val * 100), 100)
            st.markdown(f'''
            <div class="glass-card-sm" style="margin-top:1.5rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
                    <span style="color:var(--text-secondary);font-size:0.8rem;">Available</span>
                    <span style="color:var(--text-primary);font-weight:700;font-size:0.88rem;">{sur_pct}%</span>
                </div>
                <div class="compare-bar"><div class="compare-fill" style="width:{sur_pct}%;background:linear-gradient(90deg,#10B981,#34D399);"></div></div>
                <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;margin-top:0.75rem;">
                    <span style="color:var(--text-secondary);font-size:0.8rem;">Required</span>
                    <span style="color:var(--text-primary);font-weight:700;font-size:0.88rem;">{req_pct}%</span>
                </div>
                <div class="compare-bar"><div class="compare-fill" style="width:{req_pct}%;"></div></div>
            </div>
            ''', unsafe_allow_html=True)

            # Peer clustering
            clusterer = get_clusterer()
            cluster_result = clusterer.predict(
                monthly_salary=monthly_salary,
                city_living_cost_index=city_living_cost_index,
                goal_cost=gp["estimated_cost"],
                timeline_years=gp["timeline_years"],
                income_growth_rate=0.08,
                monthly_living_cost=monthly_living,
                disposable_income=disposable,
            )
            st.markdown(f'''
            <div class="glass-card" style="margin-top:1.5rem;">
                <div class="step-eyebrow" style="margin-bottom:0.5rem;">Your Financial Archetype</div>
                <div style="display:flex;align-items:center;gap:1rem;margin-top:0.75rem;">
                    <div style="font-size:2rem;">{cluster_result.icon}</div>
                    <div>
                        <div style="font-weight:700;font-size:1rem;color:var(--text-primary);">{cluster_result.archetype}</div>
                        <div style="font-size:0.85rem;color:var(--text-secondary);">{cluster_result.description}</div>
                        <div style="font-size:0.78rem;color:var(--text-secondary);margin-top:0.25rem;">Comparing against {cluster_result.peer_count} peers in your segment</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown('<div class="disclaimer" style="margin-top:2rem;">'
                'ℹ️ This analysis is for illustrative purposes only and does not constitute financial advice. '
                'Consult a licensed financial advisor for personalised recommendations.'
                '</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: RISK PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.get("page") == "🎯 Risk Profile":

    st.markdown('<div class="step-header animate-fade-up">'
                '<div class="step-eyebrow">Step 3 of 4</div>'
                '<div class="step-title">Risk Profile</div>'
                '<div class="step-subtitle">Understand your comfort with market ups and downs</div>'
                '</div>', unsafe_allow_html=True)

    total_steps = 4
    pct = int(3 / total_steps * 100)
    st.markdown(f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)

    rp = RiskProfiler()

    # Show answered questions count
    answered = st.session_state.get("risk_answers", {})
    st.markdown(f'<p style="color:var(--text-muted);font-size:0.8rem;margin-bottom:1.5rem;">'
                f'Questions answered: {len(answered)} / {len(RISK_QUESTIONS)}</p>', unsafe_allow_html=True)

    with st.form("risk_form"):
        for i, q in enumerate(RISK_QUESTIONS):
            st.markdown('<div class="glass-card-sm" style="margin-bottom:1rem;padding:1rem;">', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-bottom:0.75rem;color:var(--text-primary);font-weight:600;font-size:0.92rem;">{i+1}. {q["question"]}</div>', unsafe_allow_html=True)
            option_texts = [opt["text"] for opt in q["options"]]
            selected = st.radio(
                label=" ",
                options=option_texts,
                key=f"risk_q_{i}",
                index=None,
                label_visibility="collapsed",
                format_func=lambda x: x,
            )
            st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("Calculate My Risk Profile", use_container_width=True)

    if submitted or st.session_state.get("risk_profile_set"):
        # Build answers dict from per-question radio keys (risk_q_{i})
        answers = {}
        for i, q in enumerate(RISK_QUESTIONS):
            selected_text = st.session_state.get(f"risk_q_{i}")
            if selected_text:
                answers[q["id"]] = selected_text
        st.session_state["risk_answers"] = answers

        if len(answers) >= 5:
            rp.reset()
            for qid, selected_text in answers.items():
                for q in RISK_QUESTIONS:
                    if q["id"] == qid:
                        for opt in q["options"]:
                            if opt["text"] == selected_text:
                                rp.submit_answer(qid, opt["score"])
                                break
            profile = rp.get_profile()
            if profile:
                st.session_state["risk_profile"] = {"profile": profile.profile, "score": profile.score}
                st.session_state["risk_profile_set"] = True

    if st.session_state.get("risk_profile_set"):
        rp_data = st.session_state["risk_profile"]
        profile_type = rp_data["profile"]
        score = rp_data["score"]

        type_colors = {"konservatif": "#22D3EE", "moderat": "#8B5CF6", "agresif": "#F59E0B"}
        type_labels = {"konservatif": "Konservatif", "moderat": "Moderat", "agresif": "Agresif"}
        color = type_colors.get(profile_type, "#8B5CF6")

        st.markdown(f'''
        <div class="glass-card animate-scale-in" style="text-align:center;margin:2rem 0;">
            <div style="margin-bottom:1.5rem;">
                <div class="step-eyebrow" style="margin-bottom:0.75rem;">Your Risk Profile</div>
                <div style="font-size:2.5rem;font-weight:900;letter-spacing:-0.03em;color:{color};">{type_labels.get(profile_type, profile_type).upper()}</div>
                <div style="font-size:1rem;color:var(--text-muted);margin-top:0.5rem;">Score: {score}/100</div>
            </div>
            <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:1rem;">
                <span class="risk-badge {'low' if profile_type=='konservatif' else ('medium' if profile_type=='moderat' else 'high')}">
                    {'Lower Risk · Lower Return' if profile_type=='konservatif' else ('Balanced Risk · Balanced Return' if profile_type=='moderat' else 'Higher Risk · Higher Return')}
                </span>
            </div>
        </div>
        ''', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: PORTFOLIO
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.get("page") == "💼 Portfolio":

    st.markdown('<div class="step-header animate-fade-up">'
                '<div class="step-eyebrow">Step 4 of 4</div>'
                '<div class="step-title">Your Portfolio</div>'
                '<div class="step-subtitle">AI-optimised allocation aligned to your risk profile</div>'
                '</div>', unsafe_allow_html=True)

    total_steps = 4
    pct = 100
    st.markdown(f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)

    if not st.session_state.get("risk_profile_set"):
        st.info("👆 Complete your Risk Profile first to generate an optimised portfolio.")

    if st.session_state.get("risk_profile_set") and st.session_state.get("goal_set"):
        gp = st.session_state["goal_profile"]
        rp = st.session_state["risk_profile"]

        if st.button("Generate Optimised Portfolio", use_container_width=True):
            result = build_portfolio(
                risk_profile=rp["profile"],
                monthly_contribution=gp["estimated_cost"] / (gp["timeline_years"] * 12),
                goal_amount=gp["estimated_cost"],
                timeline_years=gp["timeline_years"],
            )
            st.session_state["portfolio_result"] = result

        if st.session_state.get("portfolio_result"):
            pr = st.session_state["portfolio_result"]

            # Hero projected total pill
            st.markdown(f'''
            <div class="hero-card animate-scale-in" style="text-align:center;margin-bottom:2rem;">
                <div class="glow-pill" style="margin:0 auto;">
                    <span class="pill-label">Projected Total</span>
                    <span class="pill-value">IDR {pr.projected_value_at_goal_year:,.0f}</span>
                </div>
                <div style="margin-top:1.5rem;">
                    <span class="verdict-badge green">On Track ✓</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            # Summary metrics
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                monthly_contribution = gp["estimated_cost"] / (gp["timeline_years"] * 12)
                st.markdown(f'''<div class="metric-tile"><div class="metric-label">Monthly Contribution</div><div class="metric-value" style="font-size:1.1rem;">IDR {monthly_contribution:,.0f}</div></div>''', unsafe_allow_html=True)
            with c2:
                st.markdown(f'''<div class="metric-tile"><div class="metric-label">Blended Return</div><div class="metric-value accent" style="font-size:1.1rem;">{pr.blended_return:.2%}</div></div>''', unsafe_allow_html=True)
            with c3:
                st.markdown(f'''<div class="metric-tile"><div class="metric-label">Blended Volatility</div><div class="metric-value" style="font-size:1.1rem;">{pr.blended_volatility:.2%}</div></div>''', unsafe_allow_html=True)
            with c4:
                shortfall = pr.goal_amount - pr.projected_value_at_goal_year
                if shortfall > 0:
                    st.markdown(f'''<div class="metric-tile" style="border-color:rgba(239,68,68,0.3);"><div class="metric-label">Shortfall</div><div class="metric-value" style="font-size:1.1rem;color:#F87171;">IDR {shortfall:,.0f}</div></div>''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''<div class="metric-tile" style="border-color:rgba(16,185,129,0.3);"><div class="metric-label">Surplus</div><div class="metric-value" style="font-size:1.1rem;color:#34D399;">IDR {abs(shortfall):,.0f}</div></div>''', unsafe_allow_html=True)

            # Allocation
            st.markdown('<div class="section-title" style="margin-top:2rem;">Allocation Breakdown</div>', unsafe_allow_html=True)
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)

            INSTRUMENT_LABELS = {
                "saham": "Equities",
                "obligasi": "Fixed Income",
                "reksadana": "Mutual Funds",
                "deposito": "Deposits",
                "emtas": "Gold",
                "properti": "Property",
                "cash": "Cash",
            }

            for alloc in pr.allocations:
                label = INSTRUMENT_LABELS.get(alloc.instrument, alloc.instrument)
                bar_pct = int(alloc.percentage)
                st.markdown(f'''
                <div class="alloc-row">
                    <span class="alloc-name">{label}</span>
                    <div class="alloc-bar-track"><div class="alloc-bar-fill" style="width:{bar_pct}%;"></div></div>
                    <span class="alloc-pct">{bar_pct}%</span>
                </div>
                ''', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Growth trajectory
            st.markdown('<div class="section-title" style="margin-top:2rem;">Growth Trajectory</div>', unsafe_allow_html=True)
            traj_df = pd.DataFrame([{"Year": yr, "Value (IDR)": val} for yr, val in pr.yearly_trajectory])
            traj_df = traj_df.set_index("Year")
            st.line_chart(traj_df, y="Value (IDR)", height=280)
            st.markdown('<div class="disclaimer" style="margin-top:1rem;">'
                        '⚠️ Projections are illustrative only and not guaranteed. Past performance does not indicate future results.'
                        '</div>', unsafe_allow_html=True)

    if not st.session_state.get("goal_set"):
        st.markdown('<div class="glass-card" style="text-align:center;padding:4rem;">'
                    '<div style="font-size:3rem;margin-bottom:1rem;">📋</div>'
                    '<div style="font-size:1.2rem;font-weight:700;color:var(--text-primary);margin-bottom:0.5rem;">No goal set yet</div>'
                    '<div style="color:var(--text-muted);">Start with the Goals page to build your portfolio</div>'
                    '</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.get("page") == "📈 Dashboard":

    st.markdown('<div class="step-header animate-fade-up">'
                '<div class="step-title">Your Financial Journey</div>'
                '<div class="step-subtitle">A complete overview of your Vestara plan</div>'
                '</div>', unsafe_allow_html=True)

    has_goal = st.session_state.get("goal_set", False)
    has_feasibility = st.session_state.get("feasibility_result") is not None
    has_risk = st.session_state.get("risk_profile_set", False)
    has_portfolio = st.session_state.get("portfolio_result") is not None

    # Health metrics
    c1, c2, c3, c4 = st.columns(4)
    items = [
        (c1, "Goal Set", has_goal, "🏠"),
        (c2, "Feasibility Analysed", has_feasibility, "📊"),
        (c3, "Risk Profiled", has_risk, "🎯"),
        (c4, "Portfolio Ready", has_portfolio, "💼"),
    ]
    for col, label, val, icon in items:
        with col:
            cls = "verdict-badge green" if val else "verdict-badge red"
            label_txt = "Complete" if val else "Not yet"
            st.markdown(f'''
            <div class="glass-card-sm" style="text-align:center;">
                <div style="font-size:1.75rem;margin-bottom:0.5rem;">{icon}</div>
                <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--text-muted);margin-bottom:0.4rem;">{label}</div>
                <span class="{cls}">{label_txt}</span>
            </div>
            ''', unsafe_allow_html=True)

    overall = [has_goal, has_feasibility, has_risk, has_portfolio].count(True)
    health_cls = "green" if overall == 4 else ("yellow" if overall >= 2 else "red")
    health_label = "Excellent" if overall == 4 else ("Good Progress" if overall >= 2 else "Getting Started")
    st.markdown(f'''
    <div class="glass-card animate-scale-in" style="text-align:center;margin:2rem 0;">
        <div class="step-eyebrow" style="margin-bottom:0.75rem;">Overall Health</div>
        <div class="score-circle {health_cls}" style="margin:0 auto 1rem;">{overall}/4</div>
        <span class="verdict-badge {health_cls}">{health_label}</span>
    </div>
    ''', unsafe_allow_html=True)

    if has_goal:
        gp = st.session_state["goal_profile"]
        st.markdown('<div class="section-title">Goal Summary</div>', unsafe_allow_html=True)
        st.markdown(f'''
        <div class="glass-card">
            <div class="breakdown-row">
                <span class="breakdown-label">Goal Type</span>
                <span class="breakdown-value" style="text-transform:capitalize;">{gp['goal_type']}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Timeline</span>
                <span class="breakdown-value">{gp['timeline_years']} years</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Estimated Cost</span>
                <span class="breakdown-value" style="color:var(--violet-400);">IDR {gp['estimated_cost']:,.0f}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Monthly Budget</span>
                <span class="breakdown-value">IDR {gp['estimated_cost'] / (gp['timeline_years'] * 12):,.0f}</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    if has_feasibility:
        fr = st.session_state["feasibility_result"]
        st.markdown('<div class="section-title">Feasibility Summary</div>', unsafe_allow_html=True)
        st.markdown(f'''
        <div class="glass-card">
            <div class="breakdown-row">
                <span class="breakdown-label">Feasibility Score</span>
                <span class="breakdown-value">{fr['feasibility_score']}/100</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Investment Ratio</span>
                <span class="breakdown-value">{fr['ratio']}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Monthly Surplus</span>
                <span class="breakdown-value">IDR {fr['monthly_surplus']:,.0f}</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    if has_portfolio:
        pr = st.session_state["portfolio_result"]
        st.markdown('<div class="section-title">Portfolio Summary</div>', unsafe_allow_html=True)
        st.markdown(f'''
        <div class="glass-card">
            <div class="breakdown-row">
                <span class="breakdown-label">Projected Value</span>
                <span class="breakdown-value" style="color:var(--violet-400);">IDR {pr.projected_value_at_goal_year:,.0f}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Monthly Contribution</span>
                <span class="breakdown-value">IDR {gp['estimated_cost'] / (gp['timeline_years'] * 12):,.0f}</span>
            </div>
            <div class="breakdown-row">
                <span class="breakdown-label">Blended Return</span>
                <span class="breakdown-value">{pr.blended_return:.2%}</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    if not any([has_goal, has_feasibility, has_risk, has_portfolio]):
        st.markdown('''
        <div class="glass-card" style="text-align:center;padding:4rem;">
            <div style="font-size:4rem;margin-bottom:1.5rem;">🚀</div>
            <div style="font-size:1.5rem;font-weight:800;color:var(--text-primary);margin-bottom:0.75rem;">Start Your Journey</div>
            <div style="color:var(--text-muted);max-width:400px;margin:0 auto 2rem;">Begin by setting your life goal and let Vestara guide you through the rest.</div>
        </div>
        ''', unsafe_allow_html=True)
