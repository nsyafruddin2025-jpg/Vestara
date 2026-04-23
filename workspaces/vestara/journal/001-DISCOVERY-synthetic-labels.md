# DISCOVERY: Synthetic Data Labels Contaminate ML Signal

## Finding

The GradientBoostingClassifier achieves 99.9% training accuracy because its
training labels were generated using the same formula (`investment_to_income_ratio`)
that becomes the model's primary feature. This is not a model quality signal —
it is a data contamination signal.

## Mechanism

```
label = "green" if ratio < 0.30
label = "yellow" if 0.30 <= ratio < 0.50
label = "red" if ratio >= 0.50

model feature: investment_to_income_ratio = monthly_required / disposable
```

The model learns the label generation rule exactly, achieving perfect accuracy
on training data because it has access to the rule's output as an input feature.

## Why This Wasn't Obvious

The contamination was invisible because:

1. The synthetic data pipeline and model training are in separate files
2. The label function (`label_verdict()`) looks like business logic, not data processing
3. The model achieved high accuracy on a test set — suggesting generalization
4. The test set was drawn from the same synthetic distribution, so contamination
   is equally present in train and test

## Pattern

This is a specific instance of a general ML failure mode: **label leakage through
feature engineering that encodes the target**. It commonly occurs when:

- Labels are derived from formula applied to input features
- Feature engineering happens before train/test split
- Synthetic data generation embeds the target variable's logic

## Action

Refactor feasibility engine to regression form. Predict `months_to_goal`,
then classify the residual vs. the user's stated timeline. This breaks the
label-feature contamination loop while preserving the gradient-boosted architecture.

## Generalization

Before training any ML model on synthetic data: audit the generation pipeline
for label contamination. Ask: "Does any feature in the training set encode
information about how the label was generated?" If yes, the ML adds no value
over the label generation rule.
