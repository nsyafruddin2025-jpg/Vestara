# Synthetic Training Data Risk Analysis

## Executive Summary

The 99.9% training accuracy is a **severe red flag** that indicates either overfitting, data leakage, or a fundamental misunderstanding of what model validation means. For a course project, this combination — synthetic data + 99.9% accuracy — will be immediately challenged. For a real product, it would be grounds for not deploying.

**Complexity: High** — The synthetic data approach introduces structural risks that cannot be quantified post-hoc.

---

## 1. Why 99.9% Accuracy Is a Red Flag

### The Statistical Impossibility Claim

A 99.9% accuracy on training data means the model is making approximately 1 error per 1,000 classifications. For a real financial feasibility problem with:

- Noise from income volatility
- Irregular expense patterns (monthly bonuses, Ramadan expenditures, annual school fees)
- Psychological factors in self-reporting
- Goal ambiguity and priority shifts

**Perfect or near-perfect accuracy is statistically implausible on any real-world financial behavior dataset.**

### What 99.9% Actually Indicates

| Cause                          | Mechanism                                        | Detection Method                                         |
| ------------------------------ | ------------------------------------------------ | -------------------------------------------------------- |
| **Overfitting**                | Model memorized training set noise               | Train vs. validation accuracy gap                        |
| **Data leakage**               | Features accidentally include target             | Leakage audit on feature engineering pipeline            |
| **Training set contamination** | Validation data appeared in training             | k-fold cross-validation with proper separation           |
| **Wrong metric**               | Accuracy is wrong measure for imbalanced problem | Confusion matrix + per-class metrics                     |
| **Synthetic data homogeneity** | Synthetic data has less variance than reality    | Compare synthetic distribution moments to real reference |

### The Specific Problem with 200 Trees, 99.9%

XGBoost with 200 trees at 99.9% training accuracy:

- The model is **overly complex** for a concept that has inherent noise
- Each tree is memorizing a partition of the feature space rather than learning a generalizable rule
- Adding more trees past the point of diminishing validation returns is the classic overfitting signature

**A model that achieves 99.9% on training but 70% on validation is a model that has learned nothing useful about the real problem.**

---

## 2. Synthetic Data: What It Cannot Capture

### The Fundamental Limitation

Synthetic data is generated from a **model of reality**, not from reality itself. Every synthetic dataset embeds the assumptions of its generator. The model trained on synthetic data can only learn the structure of that generator — not the structure of actual Indonesian financial behavior.

### What Real Data Reveals That Synthetic Cannot

**1. Income Irregularity**

- Synthetic: Monthly income modeled as consistent with small Gaussian noise
- Reality: Overtime pay, freelance gigs, 13th-month bonuses (THR in Indonesia), Ramadan allowances, seasonal business cycles
- Consequence: A user flagged as "Yellow" every December due to THR might actually be "Green" 11 months/year

**2. Multi-Generational Financial Obligations**

- Synthetic: Individual-focused expense model
- Reality: Many young Indonesian professionals support parents, siblings' school fees, extended family emergencies
- Consequence: Disposable income calculations are systematically optimistic; real feasible investment rates are lower

**3. Informal Financial Behavior**

- Synthetic: All income/expenses in formal banking
- Reality: Arisan, "博大" (bokek) cycles, informal lending circles (逗小花), cash-based transactions
- Consequence: Self-reported income understates actual cash flow variability

**4. Outlier and Stress-Case Distribution Tails**

- Synthetic: Typically Gaussian or uniform distributions within defined bounds
- Reality: Power-law-like tail events — job loss, medical emergencies, family crises
- Consequence: The model's understanding of "Red" cases is extrapolated from generated data, not actual crisis experiences

**5. Psychological and Behavioral Factors**

- Synthetic: Rational actor with consistent preferences
- Reality: Loss aversion, present bias, social comparison, commitment device failures
- Consequence: A user might be "financially feasible" by income metrics but behaviorally unable to sustain investment

**6. True Feature Interactions**

- Synthetic: Interactions encoded by the generator
- Reality: Unknown interactions discovered through observation
- Consequence: The model cannot discover novel risk factors that don't exist in the synthetic generation logic

---

## 3. Course Project vs. Real Product Risk

### MGMT 655 Review: What a Professor Will Ask

**Q1: "If this model were deployed to 100,000 users, and it misclassified 0.1% as Green when they should be Red, that's 100 families who might over-invest and face financial distress. Have you quantified this harm?"**

- There is no validation data to support this calculation
- The model's false negative rate on real data is fundamentally unknowable from synthetic training

**Q2: "What is your precision and recall for each class? A model with 99.9% accuracy might have 0% recall on Red cases if there are no Red cases in the synthetic training data."**

- If the synthetic generator never produced Red examples, the model has no way to learn Red
- This is a class imbalance problem masked by overall accuracy

**Q3: "Walk me through your cross-validation strategy. Which hyperparameter choices were made on the validation set? Did you use the same data for both?"**

- Any hyperparameter tuning on training data inflates reported metrics
- Proper protocol requires a held-out test set untouched until final evaluation

**Q4: "What would happen if a user's income distribution changed — say, they got promoted and their income increased 40%? Would your model retrain? Would the thresholds update?"**

- Static model + dynamic user reality = concept drift problem
- Synthetic data cannot validate concept drift handling

**Q5: "How many real Indonesian investment decisions did you observe to validate that your 'feasibility' prediction matches reality?"**

- Zero — by the team's own admission
- This makes the entire classifier a theoretical construct, not a validated tool

---

## 4. The Specific Failure Mode: Synthetic Data Homogeneity

### The Generation Process Problem

If the synthetic data generator used:

- Normal distributions for continuous variables
- Fixed category probabilities for categorical variables
- Predefined correlation structures

Then **the model learned the generator, not the domain.**

The 99.9% accuracy is achievable because the generator's output is internally consistent. But:

| Metric                | Synthetic Data         | Real Indonesian Data             |
| --------------------- | ---------------------- | -------------------------------- |
| Income variance       | Bounded, parameterized | Long-tailed, seasonal, irregular |
| Expense categories    | Fixed set              | Open-ended, culturally specific  |
| Goal types            | Defined enumeration    | Evolving, mixed                  |
| Correlation structure | Linear assumptions     | Non-linear, context-dependent    |

The model performs at ceiling on training because training and test come from the same generator — they are the same distribution. **Any real-world deployment immediately exposes the model to distributional shift it has never seen.**

---

## 5. Validation Strategy to Make This More Defensible

If the synthetic approach must be used, the following would substantially improve defensibility:

### Minimum Viable Validation Stack

**1. Adversarial Validation**

- Train a classifier to distinguish synthetic from real data
- Features the classifier uses most are the ones most different between synthetic and reality
- This reveals exactly where the synthetic data diverges from real-world distributions

**2. Distribution Moment Comparison**

- Compare mean, variance, skewness, kurtosis of each feature between synthetic and real reference data
- Document all moments where synthetic diverges by >2 SD from real reference
- These divergences are the model's blind spots

**3. Sensitivity Analysis on Thresholds**

- Take the trained model, vary the threshold boundaries by ±5pp
- Measure how many users flip verdict categories
- High sensitivity = fragile model that cannot be trusted for high-stakes decisions

**4. Stress Testing with Real Scenario Injection**

- Take 20-30 real user profiles from Indonesian financial forums,Reddit r/Indonesia, or qualitative interviews
- Run through the model
- Compare model output to what financial advisors would recommend
- Even qualitative validation is better than zero validation

**5. External Benchmark Comparison**

- Compare Vestara's verdicts against:
  - OVO/GoPay financial health scores (if accessible)
  - BI financial literacy survey classifications
  - Academic studies on Indonesian household financial stress
- Convergence with any external source strengthens credibility

**6. Uncertainty Quantification**

- Replace point predictions with confidence intervals
- If the model is 99.9% confident on training but the true confidence on real data should be 60-70%, the model needs to express that uncertainty
- Bayesian approaches or dropout-based uncertainty would make this visible

---

## 6. What Real Data Would Reveal

If the team had access to even a small real dataset (50-200 users with consent), they would discover:

| Discovery                                                            | Why It Matters                                                |
| -------------------------------------------------------------------- | ------------------------------------------------------------- |
| Income spikes correlate with calendar events (THR, year-end bonuses) | Threshold timing matters; static monthly snapshot misses this |
| Family obligation amounts are non-linear with income                 | Disposable income formulas are wrong at low/high incomes      |
| Goal priority is unstable in first 3 months                          | Re-classification rates are high; "feasibility" is dynamic    |
| Self-reported expenses are systematically under-reported             | Users believe they save more than they do                     |
| Users with "Green" verdicts still fail investment plans              | The model predicts capacity but not behavior                  |

---

## 7. Risk Register

| Risk                                                       | Likelihood    | Impact                                                     | Severity |
| ---------------------------------------------------------- | ------------- | ---------------------------------------------------------- | -------- |
| Model fails immediately on real user deployment            | **Very High** | Wrong verdicts cause financial harm                        | Critical |
| Class imbalance: model has never seen real Red cases       | **High**      | False Green verdicts on distressed users                   | Critical |
| Overfitting to synthetic distribution is unmeasurable      | **High**      | No way to bound error rate on real users                   | Critical |
| 99.9% accuracy misleads stakeholders into trusting model   | **High**      | Business decisions made on broken foundation               | Major    |
| No back-testing possible                                   | **High**      | Cannot prove thresholds work until real deployment         | Major    |
| Regulatory scrutiny if product scales (OJK implications)   | **Medium**    | Indonesian financial regulator may require validation data | Major    |
| Negative press if users lose money based on wrong verdicts | **Medium**    | Reputational damage, trust collapse                        | Major    |

---

## 8. Conclusion

The synthetic data + 99.9% accuracy combination is the **most vulnerable element of this project** in a MGMT 655 review. A professor will immediately identify this as methodologically indefensible without external validation.

The honest framing should be: "This is a prototype that demonstrates the concept works in a controlled environment. Real-world deployment requires validation against actual Indonesian financial behavior data."

If the team presents 99.9% accuracy as a strength rather than a warning sign, they will lose credibility on the spot.
