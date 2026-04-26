# What Was Auto-Approved vs Human Reviewed

## Auto-Approved (No Human Gate)

These were approved autonomously by agents under COC rules:

| Decision | Rule that auto-approved | Rationale |
|----------|-------------------------|-----------|
| Algorithm thresholds (30/50% green/yellow) | Agents can calibrate thresholds | Technical calibration |
| CSS colour palette | Frontend specialist agent | Design expertise |
| Return assumptions (4.5-12%) | Financial domain patterns | Industry consensus |
| Instrument list (6 instruments) | Framework specialist | Standard Indonesian instruments |
| Streamlit component choices | react-specialist | UI best practices |
| Dockerfile multi-stage pattern | nexus-specialist | Standard deployment |
| Property price per sqm data | Data calibration | Market data approximation |

## Human Reviewed (Structural Gates)

These required explicit human approval:

| Decision | Gate | Who reviewed |
|----------|------|-------------|
| Product brief (goal-first philosophy) | `/analyze` → `/todos` | Human wrote brief |
| Regulatory pathway (Path B) | `/analyze` approval | Human decision |
| Country selection (Indonesia) | `/analyze` approval | Human decision |
| Synthetic data approach | `/todos` approval | Human decision |
| Project roadmap | `/todos` structural gate | Human approved plan |
| Naming conventions (Vestara) | `/codify` structural gate | Human reviewed |
| Knowledge capture | `/codify` structural gate | Human approved |

## Rules That Blocked Auto-Approval

| Rule | Effect |
|------|--------|
| `zero-tolerance.md` | No stubs, no placeholders — every method fully implemented |
| `security.md` | No hardcoded secrets, parameterized queries enforced |
| `env-models.md` | All API keys from .env, no hardcoded model names |
| `terrene-naming.md` | TF entity naming conventions validated |

## Quality Gates (MUST)

At `/implement` completion, these ran as parallel background agents (near-zero parent context cost):

- **reviewer**: Code review, doc validation, cross-reference accuracy
- **security-reviewer**: Security audit — secrets, injection, compliance

Both converged before the session ended. No blocking issues found.
