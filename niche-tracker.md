# Etsy POD Niche Tracker (CEO orchestrator log)

Persistent log across pipeline cycles. After 2 weeks, saturation is re-checked and each niche/gap is marked rising / stable / saturated. Rising patterns get fed back into the next cycle as priority search terms.

**Pipeline structure (as of 2026-08-20):** A persistent CEO orchestrator (`.claude/agents/ceo.md`) runs every cycle. It reads this file first, decides the cycle's scope, delegates to four sub-agents (`trend-scout`, `phrase-miner`, `gap-finder`, `design-briefer` — see `.claude/agents/`), reviews their combined output for contradictions/low-confidence/silent failures, and is the *only* agent that writes this file, `report.html`, or pushes to GitHub. Sub-agents report to the CEO only — none of them have file-write access.

Every cycle section below starts with a `## CEO Summary` — what ran, what changed, what the CEO decided and why. Anything the CEO wouldn't resolve unilaterally (e.g. retiring a previously flagged niche/gap) is marked `⚠️ NEEDS YOUR CALL` and stays in the tracker, unresolved, until the user explicitly says to drop it — the CEO never silently deletes tracked history.

**Data quality caveat (carries forward every cycle):** Direct Etsy scraping (WebFetch/browser) is blocked (HTTP 403 / bot detection) — the Open API is the only real-data path.

**Data sourcing priority (as of 2026-08-20, applies to every cycle going forward):**
1. **Etsy Open API (preferred, now active).** `ETSY_API_KEY` (stored in `.env` as `keystring:sharedsecret`, per Etsy's required `x-api-key` format) went live 2026-08-20, confirmed via `openapi-ping` → HTTP 200. `https://openapi.etsy.com/v3/application/listings/active` returns real listing title, price, dates, and a true total `count` for the search term (used for computed saturation); `.../listings/{id}/images` and `.../listings/{id}/reviews` supply the thumbnail and review count for the top-ranked listing.
2. **Search fallback.** If the API key is unset or a call errors, use Google-indexed `site:etsy.com` WebSearch queries. A result only counts as "real" if it contains an actual resolvable `etsy.com/listing/...` URL — a bare title snippet with no URL does not qualify as verified for image/URL purposes, only for confirming the niche/phrase exists. **This fallback must never trigger silently — an API error is logged and reported to the user, not swallowed.**
3. **No fabrication, ever.** If no path returns a real image, price, or listing URL for a niche/gap, record it as `NO DATA AVAILABLE` — do not invent a plausible-looking placeholder. This applies to report.html card rendering too: a card with no real `image`/`url` renders a `NO DATA AVAILABLE` placeholder, not a stand-in graphic. Gap cards stay `NO DATA AVAILABLE` by design even post-API — a gap is by definition a combination no real listing fills; showing a loosely-related near-miss as if it were the gap's product would misrepresent it.

Secondary sources (Pinterest Predicts, POD seller blogs, Reddit) remain fine for directional trend commentary, always tagged as inferred. As of this cycle, all 13 tracked niches have a **computed** saturation label (real Etsy listing count for the niche's search term) rather than a directional estimate; gap verification is now API-confirmed rather than search-inferred.

---

## Cycle 1 — flagged 2026-08-19

### CEO Summary — real-API data refresh, 2026-08-20

`ETSY_API_KEY` went live today (confirmed via `openapi-ping` → HTTP 200). Re-ran all 13 tracked niches and all 5 ranked gaps against the real Etsy Open API — no search-scraping fallback was needed anywhere in this refresh; every call below returned HTTP 200 on the first try. What changed:

- **Saturation is now computed, not estimated**, for all 13 niches — each niche's search term returned a real Etsy `count` (total matching active listings), shown in the table below.
- **Four niches promoted from `unresolved` → `active`**: Afrohemian Decor (167 listings), Extra Celestial/Alien-Core (89), Circus-Core/Funhaus (145), Neo Deco (1,448). These were previously Pinterest-volume-only with no listing check; real listings now exist for all four, so "no signal yet" no longer applies. This is routine re-scoring (new evidence, not a retirement), so no `⚠️ NEEDS YOUR CALL` flag needed per pipeline rule 5.
- **Tumbler General stays `caution`/saturated**, and the real numbers make the case harder than before: the narrow term ("teacher nurse mom tumbler") returns a moderate 688, but the parent category ("tumbler") returns **1,624,589** listings — confirms this was correctly flagged as an oversaturated category, not an opportunity.
- **All 5 ranked gaps remain valid** — API-verified instead of search-inferred. Gaps 1, 2, 5 returned **0** matching listings (genuinely unfilled). Gaps 3 and 4 returned exactly **1** listing each, but in both cases it's a loose near-miss (a gothic dog-mom sticker with no Christmas tie-in; a generic dog-lover sticker with no sobriety/recovery framing) — not a real match for the specific intersection, so the gap stands. Per the no-fabrication rule, these near-miss listings are *not* shown as the gap's product image on its card — a gap card stays `NO DATA AVAILABLE` since no real product fills that intersection yet.
- **Nothing was retired.** No niche or gap needed removal this cycle.

### Niches (from Agent 1, phrase-confirmed by Agent 2; saturation computed via Etsy Open API 2026-08-20)

| Niche | Category | Status | Saturation (computed) | Etsy listings found | Real example listing (top match) |
|---|---|---|---|---|---|
| Gothmas / gothic Christmas decor | wall art, mugs, stickers | active | medium (1,978) | 1,978 | ["Gothic Moon Face Sticker: Sleepy Celestial Moon Art"](https://www.etsy.com/listing/4527674043/gothic-moon-face-sticker-sleepy) — $4.49, 0 reviews, listed 2026-06-25 |
| Nonnacore | mugs, wall art | active | medium (687) | 687 | ["Pregnancy Announcement to Grandparents Mug Set"](https://www.etsy.com/listing/1775546945/pregnancy-announcement-to-grandparents) — $19.99, 5 reviews, listed 2024-08-09 |
| Castlecore / Knightcore | wall art, t-shirts | active | medium (501) | 501 | ["Tartaria Griffin Crest Shirt, Medieval Fantasy Graphic Tee"](https://www.etsy.com/listing/4489223103/tartaria-griffin-crest-shirt-medieval) — $36.23, 0 reviews, listed 2026-04-15 |
| ADHD / neurodivergent stickers | stickers | active | high (3,962) | 3,962 | ["I Have To Say Weird Stuff Or I'll Die Sticker"](https://www.etsy.com/listing/4404433752/i-have-to-say-weird-stuff-or-ill-die) — $3.50, 38 reviews, listed 2025-11-13 |
| Chronic illness / spoonie stickers | stickers | active | high (3,204) | 3,204 | ["Chronic Illness Sticker, Hidden Disability, Spoonie Sticker"](https://www.etsy.com/listing/1536789034/chronic-illness-sticker-hidden) — $4.99, 0 reviews, listed 2023-08-23 |
| Recovery / sobriety stickers | stickers | active | medium (598) | 598 | ["Vintage Floral Pretty Sobriety Birthday Celebration Sticker"](https://www.etsy.com/listing/1768692507/vintage-floral-pretty-sobriety-birthday) — $5.00, 3 reviews, listed 2024-07-26 |
| Pet breed + hobby combo mugs | mugs | active | low (152) | 152 | ["Vizsla Mountain Mug, Out Offline Caffeinated, Dog Mom Gift"](https://www.etsy.com/listing/4559650270/vizsla-mountain-mug-out-offline) — $16.65, 0 reviews, listed 2026-08-20 |
| Occupation x sarcasm t-shirts | t-shirts | active | high (4,811) | 4,811 | ["My Badge is the Only Thing Keeping This Conversation Professional" (Halloween Nurse Shirt)](https://www.etsy.com/listing/4559704859/my-badge-is-the-only-thing-keeping-this) — $29.99, 0 reviews, listed 2026-08-21 |
| Afrohemian decor | wall art | active *(promoted from unresolved)* | low (167) | 167 | ["Modern Black Women Horizontal Wall Art - Afrocentric Boho Folk Print"](https://www.etsy.com/listing/4474469102/modern-black-women-horizontal-wall-art) — $6.80, 2 reviews, listed 2026-03-19 |
| Extra Celestial / alien-core | wall art, stickers, tumblers | active *(promoted from unresolved)* | low (89) | 89 | ["Cute Alien Cat Emotes for Twitch, Discord, YouTube"](https://www.etsy.com/listing/4337379977/cute-alien-cat-emotes-for-twitch-discord) — $6.00, 7 reviews, listed 2025-07-18 |
| Circus-core / Funhaus | wall art | active *(promoted from unresolved)* | low (145) | 145 | ["Bite Me Art Print"](https://www.etsy.com/listing/1501174256/bite-me-art-print) — $4.00, 1 review, listed 2023-07-02 |
| Neo Deco | wall art | active *(promoted from unresolved)* | medium (1,448) | 1,448 | ["Quiet Elegance — Expressionist Woman in a Modern Interior"](https://www.etsy.com/listing/4559701357/quiet-elegance-expressionist-woman-in-a) — $550.00, 0 reviews, listed 2026-08-21 |
| Tumbler general (teachers/nurses/moms) | tumblers | caution | high — narrow term medium (688), parent category 1,624,589 | 688 (narrow) / 1,624,589 (broad "tumbler") | ["Cinnamoroll Owala Tumbler 32oz"](https://www.etsy.com/listing/4525007672/cinnamoroll-owala-tumbler-32oz-pastel) — $49.99, 0 reviews, listed 2026-06-20 — explicitly flagged SATURATED, not an opportunity |

### Gaps (from Agent 3, ranked; verification now API-confirmed 2026-08-20)

| Rank | Gap | Verification (API-confirmed) | Risk note |
|---|---|---|---|
| 1 | Knightcore/Castlecore × teacher/nurse shirts | **0** matching listings (Etsy API, term "knight nurse teacher shirt") — confirmed sparse | audience overlap (fantasy-fandom vs. practical-gift-buyer) uncertain |
| 2 | Nonnacore × ADHD/spoonie self-care mugs | **0** matching listings (term "nonna spoonie adhd mug") — confirmed sparse | aesthetic fit is genuinely strong (cozy/comfort language overlaps) |
| 3 | Gothmas × pet-mom Christmas stickers | **1** loose near-miss (["Tired As Hell Sticker, Gothic Dog Mom Vinyl Decal"](https://www.etsy.com/listing/4322820743/gothic-dog-mom-vinyl-stickers-tired-as) — real gothic dog-mom sticker, but no Christmas element) — gap confirmed still open | low risk — line extension of already-validated goth-pet-mom niche |
| 4 | Sobriety × pet-mom stickers/shirts | **1** loose near-miss (["Enjoy The Simple Things Sticker, Dog Lover Gift"](https://www.etsy.com/listing/1749798508/enjoy-the-simple-things-sticker-dog) — generic mindfulness/dog-lover sticker, no sobriety/recovery framing) — gap confirmed still open | different buying occasions, audience-merge unclear |
| 5 | ADHD × sobriety/recovery | **0** matching listings (term "neurodivergent sober recovery sticker") — confirmed sparse | real clinical/community overlap; execution must stay supportive, not exploitative |
| 6 (stretch) | Sober gardener / "recovery garden" stickers | not re-queried this cycle — still inferred, not directly verified | weakest entry, audience size uncertain |

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
- ~~Re-run Etsy listing-count checks for niches at "estimated" confidence.~~ **Done 2026-08-20** — all 13 niches now have a computed saturation count via the live Etsy Open API.
- ~~Give Afrohemian, alien-core, circus-core, Neo Deco a dedicated Etsy-listing search pass.~~ **Done 2026-08-20** — all four promoted from `unresolved` to `active`; see table above.
- Verify sticker pricing comps directly (Briefs 3, 4, 5 used convention pricing, not live comps) — the niche-level sticker prices captured this cycle (Gothmas $4.49, ADHD $3.50, Spoonie $4.99, Sobriety $5.00) are a reasonable proxy but weren't queried against the exact brief sub-niches; do a targeted pass next cycle.
- Re-query the two 1-listing near-miss gaps (Gothmas × Pet-Mom Christmas, Sobriety × Pet-Mom) periodically — a single near-miss today doesn't guarantee the gap stays open.
- The 1,624,589-listing "tumbler" broad-category count is a strong reason to keep deprioritizing Tumbler General entirely rather than re-checking it every cycle.

---

## Cycle 2 — scheduled 2026-09-02 (2 weeks out)

*(To be filled by the scheduled re-check: re-score each Cycle 1 niche as rising / stable / saturated, log new date, feed rising niches back to Agent 1 as priority search terms.)*
