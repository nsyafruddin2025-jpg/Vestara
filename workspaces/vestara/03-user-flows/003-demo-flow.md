# 003 — Demo Flow

## Demo Script for Prof. Jack Hong and PE Fund
### April 2026 — MGMT 655 Course

**Total time:** 12–15 minutes
**Presenter:** [Your name]
**Audience:** Prof. Jack Hong + 8–12 PE fund analysts
**Setup:** Laptop with Streamlit running locally, projector connected

---

## Before the Demo Starts (1 min)

- Open terminal: `cd vestara && .venv/bin/streamlit run src/ui/app.py`
- Browser opens on port 8501 — confirm it's running
- Pull up this script on a second monitor or printed
- Clear any previous session state by refreshing the browser

**What to say:**
> "Good morning/afternoon everyone. I'll be walking you through Vestara — a goal-first investment planning platform for young Indonesian professionals. This is a working prototype, not a polished product. I want to show you both what it does and the ML architecture underneath."

---

## Slide 1: The Problem (30 seconds)

**On screen:** Just the Streamlit sidebar and Goal Builder page

**What to say:**
> "The problem is this: a 27-year-old engineer in Jakarta earning Rp 12 million a month wants to buy a 2-bedroom apartment in Jakarta Selatan. The average 2BR there costs Rp 2.4 billion. She's trying to figure out: can she actually do this? And if not, what should she change?"
>
> "Existing tools either tell her 'just invest in index funds' or give her a 50-page spreadsheet. We're building the layer above that — a goal-first planner that speaks Indonesian financial reality."

---

## Slide 2: Goal Builder — Property (1 minute)

**Action:** Select options in the UI as you describe them

1. **City:** Select "Jakarta Selatan"
2. **Goal Type:** Select "Property"
3. **Property size:** Select "2BR Standard (45–54 sqm)"
4. **Timeline:** Move slider to **7 years**

**Click "Estimate Goal Cost"**

**What to point out:**
> "This is the key insight. In the old system, we'd just take her at face value: 2BR in Jakarta Selatan, call it Rp 2.1 billion. But that's wrong — property transactions in Indonesia carry a 15% overhead: PPHTB tax, BPHTB, notary fees, and a buffer for price appreciation during the 7-year buildup."
>
> "The system now estimates **Rp 2,415,000,000** — Rp 315 million more than the raw price. That's not hidden from the user. We show the calculation."

---

## Slide 3: Feasibility Analysis — The Verdict (2 minutes)

**Navigate:** Click "📊 Feasibility Analysis" in the sidebar

**Pre-fill these values:**
- Monthly take-home salary: **Rp 12,000,000**
- Expected annual income growth: **8%** (slider at 8%)

**Click "Analyse Feasibility"**

**What to show — the numbers:**
> "Here are the numbers. Jakarta Selatan living cost: Rp 8.5 million a month. That leaves her with Rp 3.5 million in disposable income. To reach Rp 2.4 billion in 7 years, she needs to invest Rp 28.75 million a month."
>
> "That's **239% of her disposable income.** She would need to invest more than twice what she has left after living costs. This is structurally impossible."

**Point to the verdict:**
> "🔴 Red. Not achievable as stated. Now — instead of just stopping here, the system offers her four adjustment levers, in order of behavioral difficulty."

---

## Slide 4: Scenario Optimizer — The Levers (2 minutes)

**Scroll down to see all scenario expanders**

**Open each in order:**

**Option 1 — Timeline:**
> "Option 1: extend the timeline from 7 to 24 years. Monthly drops from Rp 28.75 million to Rp 8.4 million. That's 29.6% of her disposable income — which is challenging but not insane for a long-term property goal."
>
> "Property is a flexible timeline — she can delay it. We show this lever."

**Option 2 — Location:**
> "Option 2: move to Medan, where living costs are Rp 3.5 million a month instead of Rp 8.5 million. Her disposable income doubles. Same goal, same timeline — suddenly achievable."
>
> "Not realistic for most people, but it shows the math."

**Option 3 — Goal Size:**
> "Option 3: reduce the goal. A 45% smaller apartment — from 2BR Standard to a Studio — gets her to Rp 1.3 billion. Monthly drops to Rp 15.7 million. Still high, but down from Rp 28.75 million."

**Option 4 — Contribution (show as blocked):**
> "Option 4: increase her monthly contribution. But here's the critical safety gate. She currently has negative disposable income after living costs. She cannot increase her contribution — there's nothing left to invest. The system blocks this lever and tells her why."
>
> "This is C1 from our critical fixes list. Without this gate, the old system would have recommended 'invest more' when she literally cannot."

**Click on the recommended (TIMELINE) option to show it's selected**

---

## Slide 5: Risk Profiler (1.5 minutes)

**Navigate:** Click "📋 Risk Profiler" in the sidebar

> "Now that she knows what she needs to do financially, we need to understand her risk tolerance. We use a 12-question quiz aligned to the OJK framework — Indonesia's financial regulator."

**Answer the 12 questions quickly (select middle options, skip through):**

1. Loss tolerance: Agree
2. Income stability: Stable
3. Debt load: None
4. Dependents: None
5. Investment knowledge: Basic
6. Time horizon: 3–7 years (select "3-7 years")
7. Liquidity needs: 3–5 years
8. Ethical preferences: Neutral
9. Emergency fund: 3–6 months
10. Other investments: Small
11. Real estate plans: Yes
12. Retirement planning: Roughly

**Click through to see the result:**

> "Moderat. Not conservative, not aggressive. That means her portfolio should be roughly 50% growth instruments — reksa dana equity and REITs — and 50% defensive — bonds and money market."

---

## Slide 6: Portfolio Recommendation (2 minutes)

**Navigate:** Click "💼 Portfolio Recommendation" in the sidebar

> "Now we have everything we need. Goal: Rp 2.4 billion in 7 years. Risk profile: Moderat. Required monthly: Rp 28.75 million — though she knows this isn't achievable as stated."

**Point to the allocation table:**

> "This is the recommended monthly split. Notice: Deposito 15%, ORI government bonds 25%, Pasar Uang 10%, Pendapatan Tetap 20%, Equity 22%, REITs 8%."
>
> "Total blended expected return: 7.79%. Not the 12% she might hope for from pure equity — but appropriate for her risk profile and timeline."

**Show the growth chart:**

> "Here's the year-by-year projection. The line climbs, but at year 7 she's still short of Rp 2.4 billion with the required contribution — because the required amount is simply too high for her current income."
>
> "The system shows this shortfall explicitly: 'Projected shortfall of Rp 17.5 billion.' She can see that no portfolio optimization will solve a fundamental income-to-goal mismatch."

---

## Slide 7: The ML Architecture (2 minutes)

**Open a new terminal tab or show the code printout:**

> "Let me show you what happens under the hood. The old system was a GradientBoostingClassifier — a machine learning model that predicted green/yellow/red directly. When we tested it, it achieved **99.9% accuracy**."

**Pause.**

> "That's not impressive. That's a red flag. 99.9% accuracy on a financial planning model means the model has memorized the answer, not learned the behavior."

**Show the feature importance printout (if available):**
> "The model's feature importance was 100% on something called 'investment-to-income ratio' — which is the exact formula we use to generate the labels. The model was just doing the formula, not learning anything about financial behavior."

**Show the regression output:**
> "We refactored to a GradientBoostingRegressor. Instead of predicting the verdict directly, it predicts: 'how many months will this goal take to achieve?' The verdict — green, yellow, red — is derived from comparing the prediction to the user's actual timeline."
>
> "CV RMSE: 6,755 months. Which sounds terrible until you realize the model is correctly learning that some goals are near-impossible — it predicts 999 months for unreachable goals. That's the right answer, just uncomfortable."

---

## Slide 8: The COC Decisions (1 minute)

**Show the Streamlit app code or refer to the commit log:**

> "We made five critical fixes during the /analyze phase, following our COC protocol:"
>
> "C1: Hard gate when ratio exceeds 100% — contribution lever blocked, explained to user"
> "C2: Regression model replacing classifier — eliminates label contamination"
> "C3: 15% contingency buffer on property — covers transaction costs and appreciation"
> "C4: Equity cap at 40% for timelines under 3 years — protects near-term goals from market drawdown"
> "C5: IDR depreciation buffer on abroad education — 4% per year, 10% extra buffer"
>
> "Each one has a commit SHA. Each one has a test. If anyone质疑 these decisions, we can trace them."

---

## Slide 9: Roadmap (30 seconds)

> "Phase 1 — Indonesia MVP, 10 cities, 7 goal types. We're here."
> "Phase 2 — Real property data API integration (Rumah123, OLX)"
> "Phase 3 — Actual investment execution via Bibit/Bareksa API"
> "Phase 4 — India expansion"
> "Phase 5 — OJK licensing for full investment advisory"
>
> "Revenue model: affiliate commissions on investment products, eventually AUM fees."

---

## Slide 10: Q&A (2 minutes)

**What to expect:**
- "Why not use mean-variance optimization?" → We use rule-based allocation because Indonesian instrument correlations aren't well-documented. When we have 5 years of Bibit user data, we can do proper optimization.
- "What's your competitive advantage over Bibit?" → Bibit is a robo-advisor. We're goal-first — they start with 'how much do you want to invest.' We start with 'what do you want to achieve.' Different question, different UX.
- "How do you handle users with no disposable income?" → We show Red and explain why. We don't recommend they take on debt to invest. The hard gate prevents offering false hope.
- "Why Indonesia first?" → 270M population, underbanked, smartphone penetration, no equivalent product. The market timing is similar to where India was 5 years ago.

---

## Running the Demo: Checklist

**Before you start:**
- [ ] Streamlit app runs without errors: `.venv/bin/streamlit run src/ui/app.py`
- [ ] All session state cleared (refresh browser)
- [ ] Property goal pre-loaded (or re-run quickly)
- [ ] Feasibility analysis pre-run with the exact numbers: salary 12M, city Jakarta Selatan, goal Rp 2,415,000,000, timeline 7 years
- [ ] Scenario optimizer shows 3 scenarios + blocked contribution
- [ ] Risk profiler pre-answered with Moderat result ready
- [ ] Portfolio page shows Moderat allocation + shortfall warning

**Key numbers to have memorized:**
- Property 2BR Jakarta Selatan: 50 sqm × 42M × 1.15 = **Rp 2,415,000,000**
- Disposable on 12M salary in Jakarta Selatan: **Rp 3,500,000**
- Monthly required for 2.4B in 7 years: **Rp 28,750,000**
- Investment ratio: **239.6%**
- Timeline extension to Green: **7 → 24 years**
- CV RMSE: **6,755 months**

**CO NOT:**
- Don't show the raw code unless asked — the demo is about the product, not the implementation
- Don't say "we use AI/ML" without specifics — say "GradientBoostingRegressor" or "rule-based computation"
- Don't promise regulatory approval for Phase 5 — say "we are aware of the licensing requirement and have modeled the timeline at 12–18 months"
- Don't badmouth competitors — stay factual ("Bibit starts with 'how much to invest,'" not "Bibit is bad")
