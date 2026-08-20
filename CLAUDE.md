# Etsy POD Agent — pipeline architecture

## Hierarchy

A persistent **CEO orchestrator** runs every cycle (scheduled via the "Etsy POD Niche Recheck" cloud routine, or triggered manually). It is defined in `.claude/agents/ceo.md`. Four **sub-agents** answer to the CEO only — never to each other, never directly to the user, never directly to a file:

- `.claude/agents/trend-scout.md` — raw niche findings
- `.claude/agents/phrase-miner.md` — title/copy and visual-style formulas
- `.claude/agents/gap-finder.md` — ranked underserved niche intersections
- `.claude/agents/design-briefer.md` — draft design briefs

## Rules

1. **Only the CEO writes `niche-tracker.md` or `report.html`, and only the CEO runs `git commit`/`git push`.** Sub-agents have no `Write`/`Edit` tools and (except Trend Scout, which needs `curl` for the Etsy API) no `Bash` — this is enforced at the tool-permission level in each agent's frontmatter, not just by instruction.
2. **The CEO reviews all sub-agent output before writing anything** — checking for contradictions, low-confidence data being treated as solid, and silent failures — before it touches `niche-tracker.md` or `report.html`.
3. **Data sourcing priority, enforced pipeline-wide:** Etsy Open API first (if `ETSY_API_KEY` is set — see `.env.example`), `site:etsy.com` search with a resolvable listing URL second, explicit `NO DATA AVAILABLE` third. Never a fabricated title/price/image/URL, from the CEO or any sub-agent.
4. **The CEO never unilaterally retires a previously tracked niche or gap.** If retirement looks warranted, it stays in the tracker marked `⚠️ NEEDS YOUR CALL` with reasoning, and is called out in the CEO Summary — the user decides, the CEO doesn't delete history on its own judgment.
5. **Every cycle section in `niche-tracker.md` opens with a `## CEO Summary`** — what ran, what changed, what was decided and why, and anything flagged `⚠️ NEEDS YOUR CALL`. Since the cloud routine runs unattended, this summary is also what should be relayed to the user (verbatim or near it) whenever they ask about the pipeline's status — it's the CEO's report to them.
6. **Routine logging (new niches, status re-scoring, new gaps/briefs) can proceed and be pushed automatically** — that's not irreversible, it's ordinary cycle history. What requires user sign-off is specifically *discarding* previously tracked data.

## Etsy Open API

Key/secret live only in `.env` (gitignored, never committed) — see `.env.example` for the expected shape. The CEO and Trend Scout check for `ETSY_API_KEY` automatically; no code changes are needed when the key becomes active, only confirmation that it works.
