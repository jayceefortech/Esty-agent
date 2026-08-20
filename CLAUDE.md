# Etsy POD Agent — project notes

## Etsy Open API key: pending approval

An Etsy Open API keystring/shared secret was issued on 2026-08-20 but is
**not active yet** — Etsy has it pending approval. Confirmed via:

```
curl https://openapi.etsy.com/v3/application/openapi-ping -H "x-api-key: $ETSY_API_KEY"
→ HTTP 403 {"error":"API key not found or not active, or incorrect shared secret for API key."}
```

**To retest once Etsy approves it:**

```
cd /Users/jc/etsy-pod-agent
set -a && source .env && set +a
curl -s -o /tmp/etsy_test.json -w "HTTP %{http_code}\n" \
  "https://openapi.etsy.com/v3/application/openapi-ping" \
  -H "x-api-key: $ETSY_API_KEY"
cat /tmp/etsy_test.json
```

`HTTP 200` means it's live. The pipeline and the scheduled cloud routine
already prefer the real Etsy API over search-fallback automatically once
`ETSY_API_KEY` resolves — no code changes needed, just confirm it's active.

The key itself lives only in `/Users/jc/etsy-pod-agent/.env` (gitignored,
never committed). `.env.example` documents the expected shape.

## Data sourcing rule (do not regress this)

Every niche/gap listing must come from one of, in order: (1) the real Etsy
Open API, (2) a `site:etsy.com` search result containing an actual
resolvable listing URL, or (3) be recorded as `NO DATA AVAILABLE`. Never
fabricate a price, image, or listing URL to fill a gap — see the "Data
sourcing priority" section in `niche-tracker.md` and the `thumbHTML()`
logic in `report.html` for the enforced behavior.
