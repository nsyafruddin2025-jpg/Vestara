# DECISION: Todo Sharding — Why Each Fix Is a Separate Todo

## Rationale

The /analyze phase surfaced 5 critical fixes and 3 threshold/lever improvements. Each was written as a separate todo because they involve different code modules, different invariants, and different risk profiles during implementation.

### Why C1 (hard gate) is separate from C2 (regression refactor)

- C1 changes only `scenario_optimizer.py` and `app.py`
- C2 creates a new file (`feasibility_regression.py`) and changes the data generation pipeline
- Running them together exceeds the invariant budget: hard-gate logic AND regression model in one pass
- The hard gate is a one-line check; the regression refactor is a full new model

### Why C3 (property buffer) is separate from C5 (currency buffer)

- C3 changes `goal_builder.py` only for the Property goal type
- C5 changes the same file but only for Higher Education goals
- Different edge cases: property buffer is a flat 15%, currency buffer compounds over degree years
- Different UI display: property shows per-sqm breakdown, education shows currency × years × contingency

### Why T1 (threshold recalibration) is separate from C2

- C2 is about model architecture (classifier → regressor)
- T1 is about business logic (threshold calibration)
- These are independent changes that can be implemented in either order
- Keeping them separate allows parallel implementation if two agents work simultaneously

### Why no "implement all critical fixes" mega-todo

A single todo covering all 5 critical fixes would exceed the sharding budget:

- 5 different modules touched
- 5 different sets of invariants
- 3 different UI pages modified
- Cannot be described in 3 sentences

Evidence: Phase 5.11 orphan (2,407 LOC of trust integration code) failed because it was one conceptual change that exceeded the invariant budget. This todo list is designed to avoid that failure mode.
