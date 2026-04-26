# Before Demo Day

## Must Have (Demo-Blocking)

### 1. Session Persistence
**Problem:** Streamlit session state is lost on refresh. Demo flow breaks.
**Fix:** Add `st.session_state` persistence via Supabase or Streamlit Cloud secrets.
**Deadline:** Before first external demo.

### 2. English UI (DONE)
All Bahasa Indonesia text replaced with English.
No further action needed.

### 3. Property Type Expansion (DONE)
9 property types with landed house premium implemented.
No further action needed.

### 4. Custom Retirement / Emergency Input (DONE)
Custom monthly expense input added.
No further action needed.

### 5. Salary Bracket Indicator (DONE)
Fresh Graduate / Mid Career / Senior Professional shown as helper text.
No further action needed.

---

## Should Have (Demo-Enhancing)

### 6. Demo Script
**Problem:** No defined demo flow. Live demos without scripts go off-rail.
**Fix:** Write a 5-minute demo script covering:
1. Property goal: Rp 500M apartment in South Jakarta, 10 years
2. Feasibility: Yellow → scenario optimizer → flip to Green
3. Risk profile: 12 questions in 2 minutes
4. Portfolio: Illustrative allocation shown
5. Dashboard: Complete plan summary
**Deadline:** Day before demo.

### 7. Realistic Demo Data
**Problem:** Default values (Rp 15M salary) are too low for meaningful demo.
**Fix:** Pre-populate with compelling scenario:
- Salary: Rp 25M/month (Mid Career)
- Goal: Property, Rp 800M, 7 years
- City: Jakarta Selatan
- Profile: Should be Yellow or Green with clear scenarios
**Deadline:** Day before demo.

### 8. Disclaimer Visibility Check
**Problem:** Disclaimer must be visible before portfolio page content.
**Fix:** Verify amber disclaimer banner is above the fold on portfolio page.
**Deadline:** Day before demo.

---

## Nice to Have (Demo Polish)

### 9. Growth Chart Labelling
**Problem:** Chart axis labels could be clearer.
**Fix:** Add "Goal Target" line annotation on chart.
**Deadline:** Day before demo.

### 10. Error State UX
**Problem:** No defined behaviour for edge cases (zero salary, 0-year timeline).
**Fix:** Add guard rails and user-friendly error messages.
**Deadline:** Day before demo.
