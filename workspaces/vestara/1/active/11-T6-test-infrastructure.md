# T6: Test Infrastructure — Set Up pytest + Coverage

## Problem

The Vestara codebase has no tests directory, no conftest.py, and no CI configuration. All bug fixes in `/implement` need regression tests. The course project also needs to demonstrate testing discipline.

## Spec

Implements: `rules/testing.md` (3-tier testing structure) and `specs/` contracts

## Changes

### Create test structure

```
vestara/
  tests/
    __init__.py
    conftest.py
    unit/
      __init__.py
      test_goal_builder.py
      test_scenario_optimizer.py
      test_feasibility_classifier.py
      test_threshold_calibrator.py
      test_portfolio_optimizer.py
      test_risk_profiler.py
    integration/
      __init__.py
      test_wiring.py       # facade wiring tests (per facade-manager-detection.md)
    regression/
      __init__.py
```

### `vestara/tests/conftest.py`

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

@pytest.fixture
def goal_builder():
    from vestara.src.engine.goal_builder import GoalBuilder
    return GoalBuilder()

@pytest.fixture
def scenario_optimizer():
    from vestara.src.engine.scenario_optimizer import run_scenario_analysis
    return run_scenario_analysis

@pytest.fixture
def portfolio_optimizer():
    from vestara.src.portfolio.optimizer import build_portfolio
    return build_portfolio

@pytest.fixture
def risk_profiler():
    from vestara.src.engine.risk_profiler import RiskProfiler
    return RiskProfiler
```

### `vestara/pyproject.toml` — Add test configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["vestara"]
omit = ["vestara/tests/*", "vestara/.venv/*"]
```

### GitHub Actions CI

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: "3.11" }
      - run: pip install pytest pytest-cov scikit-learn pandas numpy streamlit xgboost
      - run: pytest tests/ --cov=vestara --cov-report=term-missing
```

## Tests

No additional tests — this task creates infrastructure for tests in other todos.

## Constraints

- All test files must import from `vestara.*`, not relative imports
- conftest.py must be at `vestara/tests/conftest.py`, not project root
