# Etsy POD Agent — pipeline architecture

## Hierarchy

A persistent **CEO orchestrator** runs every cycle (scheduled via the "Etsy POD Niche Recheck" cloud routine, or triggered manually). It is defined in `.claude/agents/ceo.md`. Five **sub-agents** answer to the CEO only — never to each other, never directly to the user, never directly to a file — delegated to in this order:

- `.claude/agents/trend-scout.md` — raw niche findings
- `.claude/agents/phrase-miner.md` — title/copy and visual-style formulas
- `.claude/agents/gap-finder.md` — ranked underserved niche intersections
- `.claude/agents/review-miner.md` — real Etsy buyer-review language (desired outcomes, complaints, pre-purchase problem phrases, purchase-driving details, unmet needs) for the niches behind this cycle's ranked gaps; skips a niche with `insufficient data` rather than guessing when fewer than 15 real reviews are pooled for it
- `.claude/agents/design-briefer.md` — draft design briefs, informed by Review Miner's findings when available; titles and descriptions follow fixed copywriting rules (keyword-front-loaded titles with banned filler words; hook/identity-line/feature→benefit/CTA descriptions) documented in the agent file itself

## Rules

1. **Only the CEO writes `niche-tracker.md` or `report.html`, and only the CEO runs `git commit`/`git push`.** Sub-agents have no `Write`/`Edit` tools and (except Trend Scout and Review Miner, which both need `curl` for the Etsy API) no `Bash` — this is enforced at the tool-permission level in each agent's frontmatter, not just by instruction.
2. **The CEO reviews all sub-agent output before writing anything** — checking for contradictions, low-confidence data being treated as solid, and silent failures — before it touches `niche-tracker.md` or `report.html`.
3. **Data sourcing priority, enforced pipeline-wide:** Etsy Open API first (if `ETSY_API_KEY` is set — see `.env.example`), `site:etsy.com` search with a resolvable listing URL second, explicit `NO DATA AVAILABLE` third. Never a fabricated title/price/image/URL, from the CEO or any sub-agent.
4. **The CEO never unilaterally retires a previously tracked niche or gap.** If retirement looks warranted, it stays in the tracker marked `⚠️ NEEDS YOUR CALL` with reasoning, and is called out in the CEO Summary — the user decides, the CEO doesn't delete history on its own judgment.
5. **Every cycle section in `niche-tracker.md` opens with a `## CEO Summary`** — what ran, what changed, what was decided and why, and anything flagged `⚠️ NEEDS YOUR CALL`. Since the cloud routine runs unattended, this summary is also what should be relayed to the user (verbatim or near it) whenever they ask about the pipeline's status — it's the CEO's report to them.
6. **Routine logging (new niches, status re-scoring, new gaps/briefs) can proceed and be pushed automatically** — that's not irreversible, it's ordinary cycle history. What requires user sign-off is specifically *discarding* previously tracked data.

## Etsy Open API

Key/secret live only in `.env` (gitignored, never committed) — see `.env.example` for the expected shape. The CEO and Trend Scout check for `ETSY_API_KEY` automatically; no code changes are needed when the key becomes active, only confirmation that it works.

## Live dashboard (Nichescope)

**Live URL: https://jayceefortech.github.io/Esty-agent/** — served by GitHub Pages from the `main` branch root, publishing `index.html` directly.

- The repo was made **public** on 2026-08-20 specifically so GitHub Pages could serve it (Pages on a private repo requires a paid GitHub plan). That means the full repo — code, `niche-tracker.md`'s research history, agent prompts — is publicly visible on GitHub now, not just the dashboard page.
- No extra publish step is needed: the CEO's existing end-of-cycle `git push` to `main` (see `.claude/agents/ceo.md`) is what GitHub Pages watches, so every cycle's `python3 generate_dashboard.py` + push auto-rebuilds the live site within a few minutes.
- `index.html` is a generated file (see `generate_dashboard.py`) — never hand-edit it directly; edit `niche-tracker.md` (data) or `dashboard_template.html` (layout/design) and regenerate.

## Earnings Estimate tab — assumptions, not real data

The "Earnings Estimate" tab models potential monthly revenue/profit per niche from **assumed** inputs the user controls (views/listing, conversion rate, listings live) plus each niche's real suggested price and saturation level — it is a planning tool, not a forecast, since no niche has been published or sold yet. **Once real Etsy sales data exists for a published niche, replace that niche's assumed conversion rate with its actual historical conversion rate** rather than the shared default — this is a deliberate placeholder, not a permanent design choice.
