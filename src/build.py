"""Assemble index.html from template.html, the chosen PhyloPic drawings and src/animals.py.

Run it after changing anything:

    python src/build.py

There is no data in this file. The animals, their sizes and weights, and the lineups and loads all
live in src/animals.py, which is the file to open when adding or correcting one. This file reads
them, checks them, and glues everything into the single index.html a player opens.

Three checks run before anything is written, so a figure that has drifted stops the build rather
than reaching the game:

    check_scale()    every height still follows from the workings recorded beside it
    check_weights()  every weight still sits inside the range its source gives
    check_library()  every animal is reachable in all three games

The workings themselves are build-time only; index.html carries just what the game reads.
"""
import json, re, os, math, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.dirname(HERE)   # the repository root
OUT_NAME = "index.html"

# animals.py is a data file people edit by hand, and Python decides whether its cached bytecode is
# still good from the file's timestamp-to-the-second and its length. Correcting a figure without
# changing either - 0.48 to 0.65, or 220 to 217 - can leave a stale cache serving the old number
# with nothing to show for it. Never caching it costs a few milliseconds and removes the trap.
sys.dont_write_bytecode = True
_cache = os.path.join(HERE, "__pycache__")
for _f in (os.listdir(_cache) if os.path.isdir(_cache) else []):
    if _f.startswith("animals."):
        try: os.remove(os.path.join(_cache, _f))
        except OSError: pass

import animals as library
ANIMALS, SETS, LOG_SETS = library.ANIMALS, library.SETS, library.LOG_SETS

choices = json.load(open(os.path.join(HERE, "choices.json")))
bbox = json.load(open(os.path.join(HERE, "bbox.json")))

LICENSES = {
    "https://creativecommons.org/publicdomain/zero/1.0/": "CC0 1.0",
    "https://creativecommons.org/publicdomain/mark/1.0/": "Public Domain Mark 1.0",
    "https://creativecommons.org/licenses/by/4.0/": "CC BY 4.0",
    "https://creativecommons.org/licenses/by/3.0/": "CC BY 3.0",
    "https://creativecommons.org/licenses/by-sa/3.0/": "CC BY-SA 3.0",
}

# what the game actually reads off an animal; `scale` and `mass` are workings and stay behind
PLAYED = ("name", "h", "kg", "plural", "fact", "sizing", "source")


def inner_svg(key):
    path = os.path.join(HERE, "phylo", f"{key}__{choices[key]['uuid']}.svg")
    s = open(path, encoding="utf-8", errors="ignore").read()
    m = re.search(r"<svg[^>]*>", s)
    body = s[m.end(): s.rfind("</svg>")]
    body = re.sub(r"<metadata>.*?</metadata>", "", body, flags=re.S)
    body = re.sub(r'\s(fill|stroke)="[^"]*"', "", body)          # colour comes from CSS
    body = body.replace("<path", '<path vector-effect="non-scaling-stroke"')
    body = re.sub(r"\s+", " ", body).strip()
    return body


def record(key, played=None):
    c, b = choices[key], bbox[key]
    rec = {
        "key": key,
        "vb": [round(b["x"], 2), round(b["y"], 2), round(b["w"], 2), round(b["h"], 2)],
        "svg": inner_svg(key),
        "credit": {
            "by": c["attribution"] or c["contributor"],
            "license": LICENSES.get(c["license"], c["license"]),
            "url": f"https://www.phylopic.org/images/{c['uuid']}",
        },
        "sci": c["sci"],
    }
    if played:
        rec.update({k: played[k] for k in PLAYED if k in played})
        rec["kgNote"] = played["mass"]["note"]
    return rec


def scaled_h(key):
    """The height an animal's recorded workings imply - see the notes in src/animals.py."""
    s = ANIMALS[key]["scale"]
    b = bbox[key]
    by_height = s["h_m"] / s["h_f"]
    if s["how"] == "height": return by_height
    by_length = s["l_m"] / (s["l_f"] * b["w"] / b["h"])
    if s["how"] == "length": return by_length
    return math.sqrt(by_height * by_length)


def check_scale():
    """Every h must still follow from its measurement, within rounding."""
    for k, v in ANIMALS.items():
        want = scaled_h(k)
        assert abs(v["h"] - want) <= max(0.04 * want, 0.005), \
            f"{k}: h={v['h']} but the measurement gives {want:.4f}"


def check_weights():
    """Every weight has to sit inside the range its source gives, and cite that source."""
    for k, v in ANIMALS.items():
        m = v["mass"]
        assert m["lo"] <= v["kg"] <= m["hi"], \
            f"{k}: {v['kg']} kg is outside the sourced range {m['lo']}-{m['hi']}"
        assert v.get("source"), f"{k}: no source recorded"


def check_library():
    """One central library: every animal has to be reachable in all three games.

    The size game draws from SETS, the balance game from LOG_SETS, and the weight game pairs
    anything in ANIMALS, so an animal missing from either list is one a player can never meet.
    """
    for group, name in ((SETS, "SETS"), (LOG_SETS, "LOG_SETS")):
        for s in group:
            unknown = [m for m in s["members"] if m not in ANIMALS]
            assert not unknown, f"{name} {s['id']}: no such animal {unknown}"
            assert len(s["members"]) >= 5, f"{name} {s['id']}: needs at least five members"
        missing = sorted(set(ANIMALS) - {m for s in group for m in s["members"]})
        assert not missing, f"not in any {name}, so unreachable in that game: {missing}"
    assert len(LOG_SETS) >= 5, "the balance game plays five loads"
    # the weight game needs a heavy reference and something 3-60x lighter to pour against it
    for k, v in ANIMALS.items():
        if v["kg"] < 30: continue
        assert any(k != t and 3 <= v["kg"] / u["kg"] <= 60 and u["h"] / v["h"] <= 0.6
                   for t, u in ANIMALS.items()), f"{k} can be a reference with nothing to weigh against it"


def check_drawings():
    """Every animal needs a drawing that has been chosen and measured."""
    for k in ANIMALS:
        assert k in choices, f"{k}: no silhouette chosen in choices.json"
        assert k in bbox, f"{k}: no measurement in bbox.json"
        path = os.path.join(HERE, "phylo", f"{k}__{choices[k]['uuid']}.svg")
        assert os.path.exists(path), f"{k}: {os.path.relpath(path, OUT_DIR)} is missing"


def main():
    check_drawings(); check_scale(); check_weights(); check_library()

    data = {
        "human": record("human"),
        "animals": {k: record(k, v) for k, v in ANIMALS.items()},
        "sets": SETS,
        "logSets": LOG_SETS,
    }
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read().replace("/*__DATA__*/", payload)

    out = os.path.join(OUT_DIR, OUT_NAME)
    open(out, "w", encoding="utf-8", newline=chr(10)).write(html)
    print(f"wrote {out} ({os.path.getsize(out)/1024:.0f} KB), "
          f"{len(ANIMALS)} animals in {len(SETS)} sets and {len(LOG_SETS)} loads")
    for k, v in sorted(ANIMALS.items(), key=lambda kv: kv[1]["h"]):
        b = bbox[k]
        print(f"  {k:10s} {v['name']:24s} h={v['h']:6.3f} m  w={v['h']*b['w']/b['h']:6.3f} m  "
              f"{v['kg']:7.2f} kg  ({v['scale']['at']} at {v['scale']['h_f']*100:.0f}%, {v['scale']['how']})")


if __name__ == "__main__":
    main()
