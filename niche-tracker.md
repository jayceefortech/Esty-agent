# Etsy POD Niche Tracker (CEO orchestrator log)

Persistent log across pipeline cycles. After 2 weeks, saturation is re-checked and each niche/gap is marked rising / stable / saturated. Rising patterns get fed back into the next cycle as priority search terms.

**Pipeline structure (as of 2026-08-20):** A persistent CEO orchestrator (`.claude/agents/ceo.md`) runs every cycle. It reads this file first, decides the cycle's scope, delegates to four sub-agents (`trend-scout`, `phrase-miner`, `gap-finder`, `design-briefer` — see `.claude/agents/`), reviews their combined output for contradictions/low-confidence/silent failures, and is the *only* agent that writes this file, `report.html`, or pushes to GitHub. Sub-agents report to the CEO only — none of them have file-write access.

Every cycle section below starts with a `## CEO Summary` — what ran, what changed, what the CEO decided and why. Anything the CEO wouldn't resolve unilaterally (e.g. retiring a previously flagged niche/gap) is marked `⚠️ NEEDS YOUR CALL` and stays in the tracker, unresolved, until the user explicitly says to drop it — the CEO never silently deletes tracked history.

**Data quality caveat (carries forward every cycle):** Direct Etsy scraping (WebFetch/browser) is blocked (HTTP 403 / bot detection).

**Data sourcing priority (as of 2026-08-19, applies to every cycle going forward):**
1. **Etsy Open API (preferred).** If an `ETSY_API_KEY` is available in the environment, use Etsy's official Open API v3 (`https://openapi.etsy.com/v3/application/listings/active`, header `x-api-key: $ETSY_API_KEY`) for real listing title, price, image URL, and listing URL (`https://www.etsy.com/listing/{listing_id}`). No key is configured yet — pending signup at developers.etsy.com and a decision on where the key gets stored for the cloud routine.
2. **Search fallback.** If no API key is set, use Google-indexed `site:etsy.com` WebSearch queries as before. A result only counts as "real" if it contains an actual resolvable `etsy.com/listing/...` URL — a bare title snippet with no URL does not qualify as verified for image/URL purposes, only for confirming the niche/phrase exists.
3. **No fabrication, ever.** If neither path returns a real image, price, or listing URL for a niche/gap, record it as `NO DATA AVAILABLE` — do not invent a plausible-looking placeholder (no fake swatch styled to look like a photo, no estimated price presented as if verified). Loud, visible gaps are correct; fabricated-but-plausible entries are not. This applies to report.html card rendering too: a card with no real `image`/`url` renders a `NO DATA AVAILABLE` placeholder, not a stand-in graphic.

Secondary sources (Pinterest Predicts, POD seller blogs, Reddit) remain fine for directional trend commentary, always tagged as inferred. Saturation scores are directional estimates, not computed ratios, unless a real listing-count number was captured.

---

## Cycle 1 — flagged 2026-08-19

### Niches (from Agent 1, phrase-confirmed by Agent 2)

| Niche | Category | Status | Confidence | Notes |
|---|---|---|---|---|
| Gothmas / gothic Christmas decor | wall art, mugs, stickers | active | medium | real listing titles confirmed |
| Nonnacore | mugs, wall art | active | medium | named in Etsy's own 2026 trend report |
| Castlecore / Knightcore | wall art, t-shirts | active | medium-high | strong real-listing depth, Comfort Colors tee convention |
| ADHD / neurodivergent stickers | stickers | active | high | strong real-listing depth |
| Chronic illness / spoonie stickers | stickers | active | high | strong real-listing depth |
| Recovery / sobriety stickers | stickers | active | high | strong real-listing depth |
| Pet breed + hobby combo mugs | mugs | active | low-medium | "hiking club" specific angle unconfirmed in real listings |
| Occupation x sarcasm t-shirts | t-shirts | active | medium | parent niche broadly saturated, sub-combos less so |
| Afrohemian decor | wall art | unresolved | low | Pinterest volume only (+220% "afrobohemian"), no Etsy listing check yet |
| Extra Celestial / alien-core | wall art, stickers, tumblers | unresolved | low | Pinterest volume only (+80-115%), no Etsy listing check yet |
| Circus-core / Funhaus | wall art | unresolved | low | Pinterest volume only (+130%), no Etsy listing check yet |
| Neo Deco | wall art | unresolved | low | Pinterest volume only (+35%), no Etsy listing check yet |
| Tumbler general (teachers/nurses/moms) | tumblers | caution | medium | explicitly flagged SATURATED, not an opportunity |

### Gaps (from Agent 3, ranked)

| Rank | Gap | Verification | Risk note |
|---|---|---|---|
| 1 | Knightcore/Castlecore × teacher/nurse shirts | real search-verified, confirmed sparse | audience overlap (fantasy-fandom vs. practical-gift-buyer) uncertain |
| 2 | Nonnacore × ADHD/spoonie self-care mugs | real search-verified, confirmed sparse | aesthetic fit is genuinely strong (cozy/comfort language overlaps) |
| 3 | Gothmas × pet-mom Christmas stickers | real search-verified, confirmed sparse | low risk — line extension of already-validated goth-pet-mom niche |
| 4 | Sobriety × pet-mom stickers/shirts | real search-verified, confirmed sparse | different buying occasions, audience-merge unclear |
| 5 | ADHD × sobriety/recovery | real search-verified, confirmed sparse | real clinical/community overlap; execution must stay supportive, not exploitative |
| 6 (stretch) | Sober gardener / "recovery garden" stickers | inferred, not directly verified | weakest entry, audience size uncertain |

**Ruled out (do not re-brief as gaps):** goth × nurse (saturated), wrestling coach × funny (saturated).

### Design briefs (from Agent 4) — 5 produced, ready for Canva/Fiverr

**BRIEF 1 — Knightcore × School Nurse/Teacher**
- **Exact text:** Title: "Knight Nurse Educator, Unisex Medieval Tee, School Nurse Aesthetic, Comfort Colors® Meme Shirt, Healer of the Realm, Ren Faire Nurse Life". On-garment graphic: **"HEALER OF THE REALM"** with small subtext **"School Nurse Est. [Year]"**
- **Style direction:** Comfort Colors garment-dyed faded tee (sage or faded black); minimalist medieval line-art icon — a caduceus redrawn as a crossed sword-and-staff crest; goth-floral border (roses/thorns) around the crest; centered badge/crest layout, single ink color for the linework.
- **Product type:** T-shirt
- **Target audience:** School nurses and clinical educators who read fantasy romance/romantasy or are into cottagecore-adjacent medieval aesthetics — gift-buyable for nurse appreciation week/graduation.
- **Suggested price:** $26–$28 (comp-verified: real castlecore/knightcore Comfort Colors tees on Etsy run $26.05–$28; one outlier listing at $68.89, treat as non-representative).

**BRIEF 2 — Nonnacore × ADHD/Spoonie Self-Care Mug**
- **Exact text:** Title: "Personalized Nonna Spoonie Mug: Rest Is Productive Too, Custom Name Chronic Illness Self-Care Gift". On-mug graphic: **"Nonna Said Sit Down And Rest"** with small script tagline **"[Custom Name]'s Spoonie Corner"**
- **Style direction:** Warm terracotta/olive palette from Nonnacore, retro Italian majolica floral border around the rim; soft rounded script typography for "Nonna Said..." (cozy permission-giving tone, not edgy/sarcastic); small holographic spoon icon tucked into the floral border as a nod to spoon theory.
- **Product type:** Mug
- **Target audience:** Women 25–45 managing chronic illness/ADHD who respond to "cozy grandmother energy" self-care messaging rather than clinical or sarcastic framing.
- **Suggested price:** $18–$22 (comp-verified: real spoonie mugs on Etsy cluster $14–$27, personalized/custom listings trend toward the upper half).

**BRIEF 3 — Gothmas × Pet-Mom Christmas Sticker**
- **Exact text:** Title: "Gothic Christmas Dog Mom Sticker Bundle, Skull & Ornament Pet Mom Holiday Decal". On-sticker text: **"Goth Mom, Merry Christmas"** styled as blackletter, wrapped around a dog silhouette wearing a small ornament collar.
- **Style direction:** Black, dark green, and blood-red palette; blackletter/gothic type for the headline; skull-and-ornament hybrid iconography (skull with holly instead of a Santa hat); die-cut kiss-cut vinyl sticker.
- **Product type:** Sticker (kiss-cut, waterproof vinyl)
- **Target audience:** Goth-identifying pet owners already buying from "goth mommy"/"gothic dog" Etsy sellers, wanting a seasonal add-on.
- **Suggested price:** $3.50–$5 (standard Etsy sticker convention — not comp-verified, flagged as estimate).

**BRIEF 4 — Sobriety × Pet-Mom Sticker/Shirt**
- **Exact text (sticker):** Title: "Sobriety Pet Mom Sticker Pack: Recovery Gift, Dog Mom Sponsor Sponsee Decals". On-sticker text: **"Sober AND a Dog Mom (Barely Surviving Either)"**
- **Style direction:** Clean inspirational-quote minimalism (not clinical) crossed with a simple line-art dog icon; broken-chain motif reworked as a dog-leash link breaking open; soft neutral palette (sage, cream, warm gray) to keep pet-mom warmth in the mix.
- **Product type:** Sticker (primary); same design adaptable to a Comfort Colors tee as a secondary SKU.
- **Target audience:** People in recovery (1+ year sobriety milestone, sponsors buying for sponsees) who are also active pet owners — sold as a milestone/anniversary gift, not daily-wear identity statement.
- **Suggested price:** $4–$5 sticker pack (convention, not comp-verified); $24–$26 if produced as a tee (in line with Brief 1's Comfort Colors comps).

**BRIEF 5 — ADHD/Neurodivergent × Sobriety/Recovery** *(sensitive intersection — kept supportive/in-community, not sarcastic or mocking; grounded in genuine dual-diagnosis community language, not novelty)*
- **Exact text:** Title: "Neurodivergent in Recovery Sticker: ADHD Sobriety Support, Dual Diagnosis Pride". On-sticker text: **"Neurodivergent AND Sober — Both Are Hard, Both Are Worth It"**
- **Style direction:** Pastel pride-flag color coding (from the ADHD/neurodivergent niche) combined with sobriety niche's clean inspirational-quote minimalism — no broken-chain/addiction iconography (avoid glamorizing/trivializing); soft rounded sans-serif type; simple sun-rising icon (shared growth/new-day motif).
- **Product type:** Sticker (kiss-cut vinyl), holographic finish optional.
- **Target audience:** Adults in dual-diagnosis recovery (neurodivergence + substance recovery) seeking community-affirming, non-mocking representation — likely reached via recovery support groups and ADHD community spaces, not general gift-shopping traffic.
- **Suggested price:** $3.50–$5 (convention, not comp-verified — recommend a small test batch given the smaller, more specific audience).

**Pricing scope note:** All 3 sticker prices (Briefs 3, 4, 5) are convention-based estimates, not live comps — verify against `site:etsy.com` sticker pack pricing in these specific sub-niches before finalizing.

### Open follow-ups for next cycle
- Re-run Etsy listing-count checks (via Everbee/EtsyHunt-style tool or authenticated access) for niches currently at "estimated" confidence — no niche yet has a real computed saturation ratio.
- Give Afrohemian, alien-core, circus-core, Neo Deco a dedicated Etsy-listing search pass — currently Pinterest-volume-only, unverified as gaps.
- Verify sticker pricing comps directly (Briefs 3, 4, 5 used convention pricing, not live comps).

---

## Cycle 2 — scheduled 2026-09-02 (2 weeks out)

*(To be filled by the scheduled re-check: re-score each Cycle 1 niche as rising / stable / saturated, log new date, feed rising niches back to Agent 1 as priority search terms.)*
