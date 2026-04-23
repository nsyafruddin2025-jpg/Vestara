# T7: Streamlit UI — Session State Wiring and Error Handling

## Problem

The Streamlit UI has several gaps: (1) no error handling when required session state is missing (broken navigation), (2) no way to reset the session, (3) no sidebar showing progress through all 4 steps, (4) the Dashboard page is the only state that verifies session completeness.

## Spec

Implements: `specs/goal-builder.md` (session state contract)

## Changes

### `vestara/src/ui/app.py` — Navigation guard

Add at the top of every page handler:

```python
def require_goal(fn):
    def wrapper(*args, **kwargs):
        if "goal_set" not in st.session_state or not st.session_state["goal_set"]:
            st.warning("⚠️ Please complete the **Goal Builder** first.")
            st.stop()
        return fn(*args, **kwargs)
    return wrapper

def require_risk_profile(fn):
    def wrapper(*args, **kwargs):
        if "risk_profile_set" not in st.session_state or not st.session_state["risk_profile_set"]:
            st.warning("⚠️ Please complete the **Risk Profiler** first.")
            st.stop()
        return fn(*args, **kwargs)
    return wrapper
```

Apply `@require_goal` to Feasibility Analysis and Portfolio pages.
Apply `@require_goal` and `@require_risk_profile` to Portfolio page.

### Sidebar progress tracker

Add at top of `app.py`, before page routing:

```python
st.sidebar.title("Your Progress")
steps = [
    ("🏗️ Goal Builder", "goal_set" in st.session_state and st.session_state["goal_set"]),
    ("📊 Feasibility", "feasibility_result" in st.session_state),
    ("📋 Risk Profiler", "risk_profile_set" in st.session_state),
    ("💼 Portfolio", "risk_profile_set" in st.session_state),
]
for label, done in steps:
    if done:
        st.sidebar.success(f"✅ {label}")
    else:
        st.sidebar.checkbox(label, value=False, disabled=True)
```

### Reset functionality

In sidebar:

```python
if st.sidebar.button("🔄 Start Over"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```

### Error boundaries

Wrap each page handler in a try/except that shows a user-friendly error:

```python
try:
    # page content
except Exception as e:
    st.error(f"Something went wrong. Please try again or restart from the Goal Builder.")
    st.exception(e)
```

## Tests

`tests/integration/test_ui_navigation.py`:

- `test_navigation_blocked_without_goal()`: mock missing goal_set, assert warning shown
- `test_navigation_blocked_without_risk_profile()`: mock missing risk_profile_set, assert warning
- `test_reset_clears_all_session_state()`: assert all keys cleared after reset

## Constraints

- Error messages must be user-friendly, not raw Python tracebacks
- Progress checkboxes in sidebar must reflect actual session state, not just URL routing
