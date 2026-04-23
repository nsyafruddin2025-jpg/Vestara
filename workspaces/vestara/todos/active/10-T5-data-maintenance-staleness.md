# T5: Data Maintenance — Staleness Dating and Volatility Flags in UI

## Problem

The cost database has no `last_updated` field or staleness tracking. Users see property prices in Jakarta Selatan from 2025 with no indication of when that data was collected or whether it's still current. There is also no mechanism to flag high-volatility cities.

## Spec

Implements: `specs/cost-database.md` § "Data Quality Standards" and "Maintenance Requirement"

## Changes

### `vestara/data/cost_data.py` — Add metadata

```python
COST_DATA_METADATA = {
    "property": {
        "last_updated": "2025-01-15",
        "source": "JRES (Jakarta Real Estate Survey) 2024, propertty.com Q4 2024",
    },
    "school_fees": {
        "last_updated": "2025-02-01",
        "source": "School websites, BPS education survey 2023",
    },
    "living_costs": {
        "last_updated": "2025-01-20",
        "source": "BPS SUSENAS 2023, Numbeo 2024",
    },
}

def get_data_age(category: str) -> int:
    """Returns days since last update."""
    import datetime
    last = datetime.date.fromisoformat(COST_DATA_METADATA[category]["last_updated"])
    return (datetime.date.today() - last).days
```

### `vestara/src/ui/app.py` — Display data freshness

Add a collapsible "Data Sources" section at the bottom of the Goal Builder (visible after goal is set):

```
**Data last updated**: January 2025
**Sources**: Jakarta Real Estate Survey 2024, BPS SUSENAS 2023, school websites
**Note**: Cost estimates are indicative. Actual prices may vary. We update our data quarterly.
```

### `vestara/src/ui/app.py` — High-volatility city warning

When user selects a high-volatility city (Jakarta Selatan, Surabaya CBD):

```
ℹ️ Property prices in Jakarta Selatan have shown significant appreciation (20-40%)
in recent 3-year periods. Your cost estimate may need updating as you approach
your goal date.
```

### `vestara/data/cost_data.py` — Add last_updated to goal profile

```python
@dataclass
class GoalProfile:
    ...
    data_source: str
    data_last_updated: str
    price_volatility_tier: Optional[str]
```

## Tests

`tests/unit/test_cost_data.py`:

- `test_property_prices_have_last_updated()`: assert all cities have last_updated
- `test_high_volatility_cities_have_tier()`: assert Jakarta Selatan has tier="high"
- `test_data_age_calculated_correctly()`: get_data_age returns positive int
- `test_goal_profile_includes_data_metadata()`: GoalProfile has data_source field

## Constraints

- Data freshness display must not block the user journey — collapsible or footer placement
- Volatility warning should be dismissible but default to visible
