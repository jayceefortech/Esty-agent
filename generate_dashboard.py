#!/usr/bin/env python3
"""
Regenerates index.html (the pipeline dashboard) from niche-tracker.md.

niche-tracker.md is the single source of truth. This script is meant to be
run by the CEO orchestrator at the end of every cycle (after it writes
niche-tracker.md and report.html) so the dashboard never needs manual edits.
It fails loudly (non-zero exit, clear message) rather than silently emitting
a dashboard with missing/fabricated data if the tracker's structure can't be
parsed as expected.

Usage: python3 generate_dashboard.py [--no-open]
"""
import datetime
import html
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRACKER = ROOT / "niche-tracker.md"
OUTPUT = ROOT / "index.html"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.M)


class TrackerParseError(SystemExit):
    def __init__(self, msg):
        super().__init__(f"FATAL: could not parse niche-tracker.md — {msg}\n"
                          f"Refusing to generate a dashboard from incomplete/guessed data.")


def sectionize(md):
    """Split markdown into a flat list of {level, title, body} sections,
    where body runs until the next heading of the same or shallower level."""
    heads = [(m.start(), len(m.group(1)), m.group(2).strip(), m.end())
             for m in HEADING_RE.finditer(md)]
    sections = []
    for i, (start, level, title, hend) in enumerate(heads):
        body_end = len(md)
        for j in range(i + 1, len(heads)):
            if heads[j][1] <= level:
                body_end = heads[j][0]
                break
        sections.append({"level": level, "title": title, "body": md[hend:body_end]})
    return sections


def find_section(sections, prefix):
    prefix = prefix.lower()
    for s in sections:
        if s["title"].lower().startswith(prefix):
            return s
    return None


def parse_table(text):
    lines = [l for l in text.splitlines() if l.strip().startswith("|")]
    if len(lines) < 2:
        return None
    header = [c.strip() for c in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) == len(header):
            rows.append(cells)
    return header, rows


def col_index(header, *substrings):
    for i, h in enumerate(header):
        hl = h.lower()
        if any(s in hl for s in substrings):
            return i
    return None


LINK_RE = re.compile(r"\[(.*?)\]\((https?://[^)]+)\)")
IMG_LINK_RE = re.compile(r"\[img\]\((https?://[^)]+)\)")
PRICE_RE = re.compile(r"\$([\d,]+(?:\.\d+)?)")
REVIEWS_RE = re.compile(r"(\d+)\s+reviews?\b")
LISTED_RE = re.compile(r"listed (\d{4}-\d{2}-\d{2})")
COUNT_RE = re.compile(r"([\d,]+)")
STATUS_ANNOTATION_RE = re.compile(r"^(\w+)\s*(?:\*\((.*?)\)\*)?\s*$")
SAT_LEVEL_RE = re.compile(r"\b(low|medium|high)\b", re.I)
BOLD_NUM_RE = re.compile(r"\*\*(\d+)\*\*")


def parse_niches_table(body):
    tbl = parse_table(body)
    if not tbl:
        return []
    header, rows = tbl
    i_name = col_index(header, "niche")
    i_cat = col_index(header, "categ")
    i_status = col_index(header, "status")
    i_sat = col_index(header, "saturation")
    i_count = col_index(header, "listings found", "etsy listings")
    i_example = col_index(header, "example")
    if None in (i_name, i_status, i_example):
        raise TrackerParseError("Niches table is missing a Niche/Status/Example column")

    niches = []
    for cells in rows:
        name = cells[i_name]
        category = [c.strip() for c in cells[i_cat].split(",")] if i_cat is not None else []

        status_raw = cells[i_status]
        m = STATUS_ANNOTATION_RE.match(status_raw)
        status = m.group(1).lower() if m else status_raw.lower()
        status_note = m.group(2) if m and m.group(2) else None

        sat_cell = cells[i_sat] if i_sat is not None else ""
        satm = SAT_LEVEL_RE.search(sat_cell)
        sat_level = satm.group(1).lower() if satm else "unknown"

        count_cell = cells[i_count] if i_count is not None else ""
        countm = COUNT_RE.search(count_cell)
        count = int(countm.group(1).replace(",", "")) if countm else None

        example_cell = cells[i_example]
        links = LINK_RE.findall(example_cell)
        title, url = (links[0] if links else ("", None))
        img_m = IMG_LINK_RE.search(example_cell)
        img = img_m.group(1) if img_m else None
        price_m = PRICE_RE.search(example_cell)
        price = f"${price_m.group(1)}" if price_m else None
        reviews_m = REVIEWS_RE.search(example_cell)
        reviews = int(reviews_m.group(1)) if reviews_m else None
        listed_m = LISTED_RE.search(example_cell)
        listed = listed_m.group(1) if listed_m else None
        extra_note = None
        if listed_m:
            trailing = example_cell[listed_m.end():].strip(" —-")
            extra_note = trailing or None

        niches.append({
            "name": name, "category": category, "status": status,
            "statusNote": status_note, "satLevel": sat_level, "satDetail": sat_cell,
            "count": count, "countDisplay": count_cell, "title": title, "url": url,
            "img": img, "price": price, "reviews": reviews, "listed": listed,
            "note": extra_note,
        })
    return niches


def parse_gaps_table(body):
    tbl = parse_table(body)
    if not tbl:
        return []
    header, rows = tbl
    i_rank = col_index(header, "rank")
    i_gap = col_index(header, "gap")
    i_verify = col_index(header, "verif")
    i_risk = col_index(header, "risk")
    if None in (i_rank, i_gap):
        raise TrackerParseError("Gaps table is missing a Rank/Gap column")

    gaps = []
    for cells in rows:
        rank_m = re.search(r"\d+", cells[i_rank])
        if not rank_m:
            continue
        rank = int(rank_m.group())
        rank_label = cells[i_rank]
        verify = cells[i_verify] if i_verify is not None else ""
        near_miss_m = BOLD_NUM_RE.search(verify)
        near_miss_count = int(near_miss_m.group(1)) if near_miss_m else None
        near_miss_links = LINK_RE.findall(verify)
        near_miss_url = near_miss_links[0][1] if near_miss_links else None
        near_miss_title = near_miss_links[0][0] if near_miss_links else None
        gaps.append({
            "rank": rank, "rankLabel": rank_label, "name": cells[i_gap],
            "verification": verify, "risk": cells[i_risk] if i_risk is not None else "",
            "nearMissCount": near_miss_count, "nearMissUrl": near_miss_url,
            "nearMissTitle": near_miss_title, "brief": None,
        })
    return gaps


BRIEF_HEAD_RE = re.compile(r"\*\*BRIEF (\d+)\s*—\s*(.*?)\*\*")
BRIEF_FIELD_RE = re.compile(r"^-\s*\*\*(.*?):\*\*\s*(.*)$", re.M)
FIELD_KEY_MAP = [
    ("exact text", "exactText"),
    ("style direction", "style"),
    ("product type", "productType"),
    ("target audience", "audience"),
    ("suggested price", "price"),
]


def parse_briefs(body):
    heads = list(BRIEF_HEAD_RE.finditer(body))
    briefs = {}
    for i, m in enumerate(heads):
        num = int(m.group(1))
        title = m.group(2)
        block_end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        block = body[m.end():block_end]
        fields = {"title": title}
        for fm in BRIEF_FIELD_RE.finditer(block):
            label, value = fm.group(1).lower(), fm.group(2).strip()
            for prefix, key in FIELD_KEY_MAP:
                if label.startswith(prefix):
                    fields[key] = value
                    break
        briefs[num] = fields
    return briefs


RUN_LOG_RE = re.compile(r"\*\*Run log:\*\*\s*(.*)")


def parse_run_log(body):
    m = RUN_LOG_RE.search(body)
    if not m:
        return None
    line = m.group(1)
    parts = [p.strip() for p in line.split("·")]  # · separator
    completed = None
    next_scheduled = None
    agents = []
    for p in parts:
        cm = re.match(r"completed (\d{4}-\d{2}-\d{2})", p)
        nm = re.match(r"next cycle scheduled (\d{4}-\d{2}-\d{2})", p)
        am = re.match(r"([^:]+):\s*(\w+)(?:\s*\((.*?)\))?", p)
        if cm:
            completed = cm.group(1)
        elif nm:
            next_scheduled = nm.group(1)
        elif am:
            agents.append({"name": am.group(1).strip(), "status": am.group(2).strip(),
                            "detail": am.group(3)})
    return {"completed": completed, "nextScheduled": next_scheduled, "agents": agents}


CYCLE_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")

GRAPH_STOPWORDS = {
    "and", "the", "of", "for", "in", "on", "to", "x", "general", "decor", "combo", "hobby",
    "stickers", "sticker", "mugs", "mug", "shirts", "shirt", "t", "tumblers", "tumbler",
    "self", "care", "core", "gift", "gifts",
}
WORD_RE = re.compile(r"[a-z0-9]+")
CATEGORY_COLORS = {
    "wall art": "#7dd3fc",
    "mugs": "#fbbf6f",
    "stickers": "#f472b6",
    "t-shirts": "#a78bfa",
    "tumblers": "#34d399",
}
DEFAULT_NODE_COLOR = "#94a3b8"


def keywords(text):
    out = []
    for w in WORD_RE.findall(text.lower()):
        if len(w) < 3 or w in GRAPH_STOPWORDS:
            continue
        if w.endswith("s") and len(w) > 3:
            w = w[:-1]
        out.append(w)
    return set(out)


def gap_product_category(brief):
    if not brief or not brief.get("productType"):
        return None
    p = brief["productType"].lower()
    if "shirt" in p or "tee" in p:
        return "t-shirts"
    if "mug" in p:
        return "mugs"
    if "sticker" in p:
        return "stickers"
    if "tumbler" in p:
        return "tumblers"
    if "wall" in p or "print" in p or "canvas" in p or "art" in p:
        return "wall art"
    return None


def build_graph(niches, gaps):
    nodes = []
    kw_by_id = {}

    counts = [n["count"] for n in niches if n["count"] is not None]
    min_c, max_c = (min(counts), max(counts)) if counts else (1, 1)

    def niche_radius(count):
        if count is None or max_c <= min_c:
            return 18
        lo, hi = 10, 26
        t = (math.log(count) - math.log(min_c)) / (math.log(max_c) - math.log(min_c))
        return hi - t * (hi - lo)  # smaller count -> bigger radius

    for n in niches:
        nid = "niche:" + n["name"]
        primary_cat = n["category"][0] if n["category"] else None
        nodes.append({
            "id": nid, "kind": "niche", "label": n["name"], "name": n["name"],
            "category": primary_cat, "color": CATEGORY_COLORS.get(primary_cat, DEFAULT_NODE_COLOR),
            "satLevel": n["satLevel"], "count": n["count"], "example": n["title"] or None,
            "price": n["price"], "url": n["url"], "r": round(niche_radius(n["count"]), 1),
        })
        kw_by_id[nid] = keywords(n["name"])

    for g in gaps:
        gid = f"gap:{g['rank']}:{g['name']}"
        cat = gap_product_category(g.get("brief"))
        nmc = g.get("nearMissCount")
        r = 32 - (nmc * 4 if nmc else 0) if nmc is not None else 30
        nodes.append({
            "id": gid, "kind": "gap", "label": g["name"], "name": g["name"],
            "category": cat, "color": CATEGORY_COLORS.get(cat, DEFAULT_NODE_COLOR),
            "satLevel": None, "count": None,
            "example": (g.get("brief") or {}).get("exactText"),
            "price": (g.get("brief") or {}).get("price"), "url": None, "r": round(r, 1),
        })
        kw_by_id[gid] = keywords(g["name"])

    links = []
    ids = [n["id"] for n in nodes]
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            a_is_gap = a.startswith("gap:")
            b_is_gap = b.startswith("gap:")
            if a_is_gap == b_is_gap and a_is_gap:
                continue  # skip gap-gap edges; clustering happens via shared niche hubs
            shared = kw_by_id[a] & kw_by_id[b]
            if shared:
                links.append({"source": a, "target": b, "weight": len(shared)})

    return {"nodes": nodes, "links": links}


def main():
    if not TRACKER.exists():
        raise TrackerParseError(f"{TRACKER} does not exist")
    md = TRACKER.read_text()
    top = sectionize(md)
    cycles = [s for s in top if s["level"] == 2 and s["title"].lower().startswith("cycle")]
    if not cycles:
        raise TrackerParseError("no '## Cycle N — ...' sections found")

    history = []
    latest = None
    for cyc in cycles:
        num_m = re.search(r"cycle\s+(\d+)", cyc["title"], re.I)
        if not num_m:
            continue
        num = int(num_m.group(1))
        date_m = CYCLE_DATE_RE.search(cyc["title"])
        cyc_date = date_m.group(1) if date_m else None
        sub = sectionize(cyc["body"])
        niches_sec = find_section(sub, "niches")
        niches = parse_niches_table(niches_sec["body"]) if niches_sec else []
        if niches:
            history.append({
                "cycle": num, "date": cyc_date,
                "niches": [{"name": n["name"], "status": n["status"], "satLevel": n["satLevel"]}
                           for n in niches],
            })
            if latest is None or num > latest["num"]:
                gaps_sec = find_section(sub, "gaps")
                gaps = parse_gaps_table(gaps_sec["body"]) if gaps_sec else []
                briefs_sec = find_section(sub, "design briefs")
                briefs = parse_briefs(briefs_sec["body"]) if briefs_sec else {}
                for g in gaps:
                    g["brief"] = briefs.get(g["rank"])
                ceo_sec = find_section(sub, "ceo summary")
                run_log = parse_run_log(ceo_sec["body"]) if ceo_sec else None
                ceo_text = None
                if ceo_sec:
                    ceo_text = RUN_LOG_RE.sub("", ceo_sec["body"]).strip()
                latest = {
                    "num": num, "date": cyc_date, "title": cyc["title"],
                    "niches": niches, "gaps": gaps, "runLog": run_log,
                    "ceoText": ceo_text,
                }

    if latest is None:
        raise TrackerParseError("no cycle with a parseable Niches table was found")

    next_scheduled = None
    if latest["runLog"] and latest["runLog"]["nextScheduled"]:
        next_scheduled = latest["runLog"]["nextScheduled"]
    else:
        for cyc in cycles:
            num_m = re.search(r"cycle\s+(\d+)", cyc["title"], re.I)
            if num_m and int(num_m.group(1)) > latest["num"]:
                date_m = CYCLE_DATE_RE.search(cyc["title"])
                if date_m:
                    next_scheduled = date_m.group(1)
                    break

    history.sort(key=lambda h: h["cycle"])
    history_niche_names = []
    seen = set()
    for h in history:
        for n in h["niches"]:
            if n["name"] not in seen:
                seen.add(n["name"])
                history_niche_names.append(n["name"])

    product_types = sorted({t for n in latest["niches"] for t in n["category"] if t})

    data = {
        "generatedAt": datetime.datetime.now().isoformat(timespec="seconds"),
        "cycle": {"number": latest["num"], "date": latest["date"], "title": latest["title"]},
        "pipeline": {
            "lastRun": (latest["runLog"] or {}).get("completed") or latest["date"],
            "nextScheduled": next_scheduled,
            "agents": (latest["runLog"] or {}).get("agents") or [],
            "summary": latest["ceoText"],
        },
        "niches": latest["niches"],
        "gaps": latest["gaps"],
        "history": history,
        "historyNicheNames": history_niche_names,
        "productTypes": product_types,
        "graph": build_graph(latest["niches"], latest["gaps"]),
        "categoryColors": CATEGORY_COLORS,
    }

    render(data)
    print(f"Wrote {OUTPUT} from {TRACKER} (cycle {latest['num']}, "
          f"{len(latest['niches'])} niches, {len(latest['gaps'])} gaps).")

    if "--no-open" not in sys.argv:
        try:
            subprocess.run(["open", str(OUTPUT)], check=True)
        except Exception as e:
            print(f"NOTE: could not auto-open browser ({e}). Open {OUTPUT} manually.",
                  file=sys.stderr)


D3_BUNDLE = ROOT / "vendor" / "d3.v7.min.js"


def render(data):
    if not D3_BUNDLE.exists():
        raise TrackerParseError(f"{D3_BUNDLE} is missing — the node-graph tab needs it "
                                 f"bundled inline so index.html stays a single offline file")
    data_json = json.dumps(data, indent=2)
    tpl = (ROOT / "dashboard_template.html").read_text()
    out = tpl.replace("/*__DATA_JSON__*/null", data_json)
    out = out.replace("/*__D3_BUNDLE__*/", D3_BUNDLE.read_text())
    OUTPUT.write_text(out)


if __name__ == "__main__":
    main()
