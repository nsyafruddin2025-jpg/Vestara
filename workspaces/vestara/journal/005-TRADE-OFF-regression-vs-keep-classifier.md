# TRADE-OFF: Refactor Classifier to Regression vs. Keep Classifier + Add Regressor

## Decision: Build New Regressor as Parallel Class, Keep Classifier Intact

### Options Considered

**Option A: Replace classifier with regressor entirely**

- Pros: Cleaner codebase, no dual code paths
- Cons: Lose the existing trained model; breaks existing session state if classifier is referenced elsewhere; all tests need updating

**Option B: Refactor classifier internally (change target variable)**

- Pros: Single class, clean
- Cons: In-place change = unknown breakage surface; tests that reference the old classifier signature fail silently

**Option C: Add new FeasibilityRegressor alongside existing FeasibilityClassifier** (CHOSEN)

- Pros: Existing classifier intact for A/B comparison; existing tests pass; can present both in UI during transition; regression model can be validated independently
- Cons: Dual code paths (more to maintain); users see two model outputs during transition

### Why Not Option A

Replacing the classifier entirely means re-training, re-validating, and re-testing — all before the demo. The regression refactor (C2) is a significant undertaking. If something goes wrong, there is no fallback. The safer path is to add the regressor as a parallel class.

### Why Not Option B

In-place refactoring of a trained model class is high-risk. The existing `feasibility_classifier.pkl` on disk was trained with the old architecture. Changing it in-place creates a version mismatch between the file and the code.

### Chosen Approach: Option C

The UI will show both outputs during the transition period. This is also pedagogically valuable for the MGMT 655 course: "Here is the old classifier that memorizes the ratio, here is the new regressor that actually learns from features." The course presentation becomes a before/after story.

### Duration of Dual-Code Period

Until C2 is validated with k-fold CV showing feature importance distributed across all 8 features (not dominated by one).
