# Prioritised Fixes

## Priority 1 — Before Demo Day

These must be fixed before any external demo.

### 1. Session Persistence (Critical)
**Problem:** Every refresh loses all state. Demo flow breaks mid-session.
**Fix:** Add Streamlit session persistence or Supabase backend.
**Effort:** 2-3 hours.
**Impact:** Demo must work across page refreshes.

### 2. English-Only UI (This session)
**Problem:** Mixed Bahasa Indonesia and English creates bad impression in English-language demo.
**Fix:** Replace all Indonesian text with English (completed in Part 1).
**Effort:** Done.
**Impact:** Professional demo presentation.

### 3. Property Types Expansion (This session)
**Problem:** 4 property types insufficient for Indonesian market.
**Fix:** Expand to 9 types with landed house premium calculation (completed in Part 1).
**Effort:** Done.
**Impact:** Credible property goal estimation.

---

## Priority 2 — Before Beta (Post-Demo)

### 4. Real Property Data Integration
**Problem:** City-level averages create &#177;20% error on property costs.
**Fix:** Integrate 99.co or Rumah123 API for neighbourhood-level pricing.
**Effort:** 1-2 days.
**Impact:** Meaningful property planning.

### 5. Income Growth Wiring
**Problem:** Income growth slider exists but doesn't affect feasibility calculation.
**Fix:** Connect growth rate to disposable income projection across timeline.
**Effort:** 2-3 hours.
**Impact:** More accurate feasibility for growing careers.

### 6. Custom Monthly Expenses Input
**Problem:** Users must use city average living costs.
**Fix:** Allow manual monthly expense input (completed in Part 1 for retirement/emergency).
**Effort:** Done.
**Impact:** Accurate disposable income for high/low spenders.

---

## Priority 3 — Before V1 Launch

### 7. ML Model Deployment
**Problem:** `feasibility_classifier.pkl` exists but not used in production.
**Fix:** Add `sklearn` to requirements.txt, wire the model.
**Effort:** 1 day.
**Impact:** Better feasibility accuracy with ML vs rule-based.

### 8. PDF Plan Export
**Problem:** No way to save/share a financial plan.
**Fix:** Generate PDF summary with goal, feasibility, and allocation.
**Effort:** 1 day.
**Impact:** User engagement and sharing.

### 9. Inflation Adjustment
**Problem:** Goal costs shown in today's rupees, not future value.
**Fix:** Add CPI projection to goal amounts and chart.
**Effort:** 2 hours.
**Impact:** More accurate long-horizon planning.

### 10. Investment Return Decomposition
**Problem:** Growth chart doesn't show contributions vs returns separately.
**Fix:** Decompose chart into two series.
**Effort:** 2 hours.
**Impact:** Educational clarity.

---

## Priority 4 — Roadmap

### 11. Multi-Goal Planning
Support simultaneous planning for multiple goals with priority weighting.

### 12. Tax Planning
Basic Indonesian tax implications (PPh 23, capital gains, withholding).

### 13. Product Integration
Partner with Ajaib/Bibit API to execute allocations shown in Vestara.

### 14. POJK Licensing
Path A licensing to provide personalised investment advice (not just educational tools).

### 15. User Behaviour Data
Track actual goal achievement rates to calibrate feasibility model.

---

## What NOT to Build

### Don't build a roboadvisor
The regulatory burden (POJK 21/2011 Path A) and ML data requirements are not worth it for MVP. Goal-first educational tool is the right scope.

### Don't add cryptocurrency
Outside Indonesian regulatory framework for this product. Could be a separate product.

### Don't expand to insurance
Life insurance needs separate licensing and actuarial models. Keep scope tight.

### Don't build for other markets yet
Indonesia-first. India expansion (mentioned in long-term roadmap) needs separate regulatory work.
