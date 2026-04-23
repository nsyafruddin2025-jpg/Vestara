# RISK: Synthetic Data Limitations Will Surface at MGMT 655 Presentation

## Risk Statement

The synthetic training data has fundamental limitations that a professor or investor will immediately identify:

1. No real Indonesian user profiles — no income volatility, no multi-generational obligations, no informal financial instruments
2. Labels derived from the same formula as features — model memorizes, doesn't learn
3. 99.9% accuracy will be challenged as a red flag, not a success metric

## Risk Likelihood: HIGH

A professor reviewing this for a machine learning decision-making course will:

1. Ask why 99.9% accuracy on synthetic data is presented as a positive
2. Push on where the training data came from
3. Ask what the model would do differently with real data

## Mitigation Strategy

### For the Course Presentation

Acknowledge explicitly and early: "We trained on synthetic data because we have no real users yet. The 99.9% accuracy is a known limitation — it reflects the homogeneity of synthetic data, not model quality. Our validation shows the model does not outperform the rule-based threshold for boundary cases."

### Structural Fix (C2 — Regression Refactor)

The regression refactor partially addresses this: a model that predicts `months_to_goal` (regression) and then classifies the residual is genuinely different from the rule-based formula, even if trained on synthetic data.

### What Real Data Would Reveal

Document explicitly in the presentation: "Real Indonesian user data would reveal: income irregularity (THR, Ramadan bonuses), multi-generational obligations (arisan, parent support), informal savings (gold, beras), and tail-risk distributions that our synthetic data cannot capture."

### Defensive Framing

Frame as a learning journey: "We discovered that our initial approach (classification with synthetic data) had label contamination. We refactored to regression. Here is the comparison. This is what the scientific process looks like."

## Residual Risk After Mitigations

Even with C2 complete, the synthetic data still cannot represent real Indonesian financial behaviour. The model's predictions for real users will diverge from its synthetic training. This is a fundamental limitation of the MVP and must be acknowledged in any investor or academic presentation.
