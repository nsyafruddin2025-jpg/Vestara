# 003 — Product Roadmap

## Phase 1 (Current): Indonesia MVP

**Scope:**
- 10 Indonesian cities (Jakarta Selatan, Jakarta Pusat, Jakarta Utara, Bandung, Surabaya, Yogyakarta, Medan, Bali/Denpasar, Semarang, Makassar)
- 7 goal types (Property, Education, Retirement, Emergency Fund, Wedding, Higher Education, Custom)
- Rule-based feasibility computation + ML regressor (regression refactor)
- 12-question risk profiler → Konservatif/Moderat/Agresif → instrument allocation
- 4-lever scenario optimizer (timeline, location, goal size, contribution)
- Streamlit UI — single-user, no persistence, in-memory session state

**What this phase is not:**
- Not a regulated financial product
- Not providing investment advice (no OJK license)
- Not connecting to real investment accounts
- Not processing real payments

**What "MVP" means here:**
A demo-ready prototype that proves the concept and generates interest from:
- Angel investors (for seed funding)
- University course evaluator (MGMT 655)
- Potential co-founders (CTO, product)

**Go-to-market for Phase 1:**
- Direct outreach to Indonesian 22-35 professionals via LinkedIn and Twitter/X
- Demo at MGMT 655 course (Prof Jack Hong, April 2026)
- No paid acquisition, no app store — landing page + direct scheduling

---

## Phase 2: Real Property Data Integration

**What:** Replace synthetic property cost estimates with real-time data from Indonesian property platforms.

**API targets:**
- **Rumah123.com** — property listing API (price per sqm by neighborhood, new vs. secondary market)
- **OLX Indonesia** — similar property data
- **Bank Indonesia Property Price Index** — city-level historical appreciation

**Why this matters:**
The single biggest driver of feasibility inaccuracy is property cost estimation. A 2BR in Jakarta Selatan could be Rp 2.1B or Rp 3.5B depending on neighborhood (Kemang vs. Tebet). Synthetic data uses a single city-level average. Real data would let the model use neighborhood as an input and capture price appreciation risk.

**Effort estimate:** 3–4 weeks for API integration + data pipeline

**Revenue model for this phase:**
Still free. Data integration is a product improvement, not a revenue stream.

---

## Phase 3: Actual Investment Execution

**What:** Let users invest directly through Vestara, earning revenue via:

**Revenue mechanisms:**
1. **Affiliate commissions** from Bibit, Bareksa, or Tokopedia Modal (IDR 50–200K per completed mutual fund registration)
2. **AUM fee** — 0.1–0.3% annual fee on assets invested through the platform (requires investment advisor license)
3. **Premium subscription** — advanced features: multi-goal tracking, tax optimization, estate planning (Rp 99K/month)

**API targets:**
- **Bibit API** — open for research partnerships; their tech team is accessible via Bandung tech community
- **GoPay / OVO integration** — for automatic monthly deduction from salary account
- **Bank transfers (BCA, Mandiri, BNI, BRI)** — for initial capital mobilization

**Regulatory requirement:**
Executing investments for users requires an **OJK license as Penasihat Investasi (Investment Advisor)**. This is Phase 5's primary workstream. Phase 3 proceeds under the assumption that execution is educational/simulation-only until the license is obtained.

**Effort estimate:** 6–8 weeks for affiliate integration

---

## Phase 4: India Expansion

**Why India:**
- Second-largest emerging market population with similar financial inclusion challenges
- Young demographic (median age 28) with growing middle class
- Same advisor-dependency culture as Indonesia (people trust financial advisors more than self-directed investing)
- No equivalent product: goal-based financial planning is underserved in India, especially for first-generation investors

**What changes:**
- Replace all Indonesian cost data with Indian equivalents (property by city, school fees, cost of living)
- Add new instruments: Indian mutual funds (ELSS for tax saving), PPF, NPS, FDs, REITs India
- New risk profiler questions adapted to Indian context (EPF vs. NPS decision, tax bracket considerations)
- Hindi language support
- UPI payment integration instead of GoPay/OVO

**What stays the same:**
- Goal-first architecture
- ML regression model (retrained on Indian synthetic data)
- 4-lever scenario optimizer (timeline, location, goal size, contribution)
- Streamlit UI pattern

**Effort estimate:** 8–12 weeks

**India-specific risks:**
- Regulatory complexity (SEBI regulations for investment advisors are stricter than OJK)
- Property market is more volatile and less transparent than Indonesia's
- Multiple languages require localization investment

---

## Phase 5: OJK Licensing for Full Advisory

**What:**
Obtain **Penasihat Investasi license** from OJK (Otoritas Jasa Keuangan). This is the regulatory requirement to legally provide personalized investment recommendations in Indonesia.

**Process:**
1. Register as PT (limited company) with minimum Rp 1B paid-up capital
2. Submit license application to OJK with:
   - Proof of capital adequacy
   - CV and certifications of at least 2 licensed investment advisors on staff
   - Product documentation (investment policy statement, risk disclosure framework)
   - IT system description (data security, audit trails)
3.等待审批：OJK processing time is typically 6–12 months

**What changes after licensing:**
- Vestara can legally call recommendations "investment advice" instead of "educational projection"
- Can charge AUM fees (0.1–0.3% of assets under advisory)
- Can process and retain customer financial data (subject to data protection compliance)
- Can integrate with fund managers' APIs for direct execution

**What this enables:**
- Revenue from AUM fees (sustainable, scales with user assets)
- Partnership with mutual fund managers (Amundi, Schroder, Manulife Indonesia) who pay distribution fees
- White-label to banks (BCA, Mandiri digital banking apps) who want goal-based planning for their customers

**Effort estimate:** 12–18 months including application processing

---

## Competitive Landscape

| Competitor | Approach | Vestara Differentiation |
|-----------|----------|----------------------|
| Bibit | Robo-advisor, goal-based, mutual funds | More comprehensive goal types, scenario optimization, Indonesia-first |
| Bareksa | Fund supermarket, some goal tools | Vestara is more guided and educational |
| Financial Freedom (ID) | Spreadsheet-based financial planning | Real ML + instrument optimization |
| Fisabilami (ID) | Islamic financial planning | Different target audience (sharia-compliant) |
| ET Money (India) | Indian goal-based investing | First-mover advantage in Indonesia |
| Sqribl / Finmates | Youth financial literacy | B2C app focus vs. Vestara's planning focus |

---

## Roadmap Timeline (Indicative)

```
2026 Q2 (Current)  Phase 1: Indonesia MVP — demo, feedback, iteration
2026 Q3            Phase 2: Property data API integration
2026 Q4            Phase 3: Affiliate investment execution (Bibit/Bareksa)
2027 Q1            Phase 1 India expansion (if Indonesia traction confirmed)
2027 Q3            Phase 5: OJK license application
2028 Q1            Phase 5: License approved (if no delays)
```

---

## What Could Change This Roadmap

**Accelerators:**
- Angel investment of Rp 500M–1B enables hiring a backend engineer + data analyst
- Partnership with a bank (BCA/Mandiri digital) gives both distribution and credibility
- Acquisition of a licensed investment advisor company bypasses Phase 5 timeline

**Risks:**
- OJK regulatory changes could make Phase 5 licensing harder or more expensive
- Bibit/Bareksa build their own goal-planning features (competitive response)
- IDR depreciation accelerates, making abroad education goals unaffordable for most users (market shrinks)
- Indian expansion fails due to regulatory complexity (reverse pivot to deeper Indonesia coverage instead)
