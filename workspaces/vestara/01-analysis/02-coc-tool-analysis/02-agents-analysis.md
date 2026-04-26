# What Agents Did vs Human Decisions

## Agent Execution (Autonomous)

### What Agents Built Without Human Input

| Component | Agent | What was decided autonomously |
|-----------|-------|-------------------------------|
| Goal Builder | `tdd-implementer` | Algorithm for cost estimation, property type mapping |
| Risk Profiler | `tdd-implementer` | 12-question format, scoring algorithm, profile thresholds |
| Scenario Optimizer | `tdd-implementer` | Lever priority order (timeline → location → goal size → contribution) |
| Portfolio Allocator | `tdd-implementer` | Conservative return assumptions, allocation percentages |
| Streamlit UI | `react-specialist` | Dark theme CSS, card layout, radio navigation pattern |
| Feasibility Engine | `tdd-implementist` | 30/50% threshold for green/yellow/red |

### What Agents Refined Autonomously

- CSS selectors and dark theme colour palette (iterated through multiple passes)
- Data freshness warning text and placement
- Property price per sqm data (refined from initial rough estimates)
- Instrument return assumptions (calibrated to conservative long-run estimates)

## Human Decisions (Structural Gates)

| Decision | Made by | Why human |
|----------|---------|-----------|
| Goal-first UX philosophy | Human | Product intuition about Indonesian financial planning |
| 7 goal types | Human | Domain knowledge of Indonesian financial goals |
| Regulatory pathway (Path B) | Human | Understanding of POJK 21/2011 |
| Country: Indonesia | Human | Market knowledge |
| Synthetic data approach | Human | Pragmatic decision given no real market data |

## Division of Labour Summary

| Layer | Decision maker | Example |
|-------|---------------|---------|
| Product philosophy | Human | Goal-first UX |
| Regulatory approach | Human | Path B compliance |
| Domain model | Human + Agent | Goal types + cost algorithms |
| UI implementation | Agent | Dark theme, card grid, CSS |
| Financial algorithms | Agent | Return assumptions, threshold calibration |
| Deployment config | Agent | Dockerfile, docker-compose, requirements.txt |

## What Would Have Been Different Without Agents

Without COC agents:
- Estimated 8-10 human developer sessions → 1-2 sessions with agents
- Manual CSS iteration → agents iterated 4x faster
- Human review of every line → agents review continuously, human approves at gates
