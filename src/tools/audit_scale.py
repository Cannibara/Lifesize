"""Check every silhouette's scale against the drawing it is taken from.

src/animals.py scales each animal from a real dimension and the fraction of the drawing that
dimension reaches - the `scale` field. That fraction is a claim about the artwork ("a cow's withers
sit at 93% of this drawing's height") and a wrong one silently makes the animal the wrong size in
all three games, which is how a fox once came to be a third too big.

    python src/tools/audit_scale.py            report every animal, flag the doubtful ones
    python src/tools/audit_scale.py --sheets   also draw contact sheets into src/tools/audit/
    python src/tools/audit_scale.py --propose koala wombat
                                               suggest where the withers sits in a drawing that
                                               has been downloaded and chosen but not yet sized

It checks three things: that each height still follows from its recorded workings, that each weight
sits inside the range its source gives, and that the weight game draws every animal at its true
height against the animal it is weighed against.

The sheets carry a percentage grid and a green line at the recorded fraction. If the line does not
land on the withers - or whichever landmark `at` names - the number is wrong, and you can see it in
a second. They are SVG, so open them in a browser.

Needs nothing but Python 3. The PhyloPic files are potrace output using only M, c and z, so the
curves are flattened here and measured directly rather than pulling in a renderer.
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
sys.dont_write_bytecode = True    # see the note in build.py
import build                                       # noqa: E402  - the size table under test

NUM = r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"
INK = "#28303c"


# ---------------------------------------------------------------- reading the drawings
def parse_svg(path):
    """Return the drawing's outlines as closed polygons, in the file's own coordinates."""
    s = open(path, encoding="utf-8", errors="ignore").read()
    tx = ty = 0.0
    sx = sy = 1.0
    g = re.search(r"<g[^>]*transform=\"([^\"]*)\"", s)
    if g:
        t = g.group(1)
        m = re.search(r"translate\(([^)]*)\)", t)
        if m:
            v = [float(x) for x in re.findall(NUM, m.group(1))]
            tx, ty = v[0], (v[1] if len(v) > 1 else 0.0)
        m = re.search(r"scale\(([^)]*)\)", t)
        if m:
            v = [float(x) for x in re.findall(NUM, m.group(1))]
            sx, sy = v[0], (v[1] if len(v) > 1 else v[0])
    polys = []
    for d in re.findall(r'<path[^>]*\sd="([^"]*)"', s, flags=re.S):
        polys += _flatten(d, tx, ty, sx, sy)
    return polys


def _flatten(d, tx, ty, sx, sy, steps=24):
    toks = re.findall(r"[A-Za-z]|" + NUM, d)
    i, cur, start, cmd = 0, None, None, None
    polys, poly = [], []
    pt = lambda x, y: (x * sx + tx, y * sy + ty)
    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]):
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                if len(poly) > 2: polys.append(poly)
                poly, cur = [], start
                continue
        if cmd in "Mm":
            x, y = float(toks[i]), float(toks[i + 1]); i += 2
            if cmd == "m" and cur: x, y = cur[0] + x, cur[1] + y
            if len(poly) > 2: polys.append(poly)
            cur = start = (x, y)
            poly = [pt(x, y)]
            cmd = "L" if cmd == "M" else "l"        # further pairs are linetos, per the spec
        elif cmd in "Ll":
            x, y = float(toks[i]), float(toks[i + 1]); i += 2
            if cmd == "l": x, y = cur[0] + x, cur[1] + y
            cur = (x, y); poly.append(pt(x, y))
        elif cmd in "Cc":
            v = [float(toks[i + k]) for k in range(6)]; i += 6
            if cmd == "c":
                x1, y1, x2, y2, x3, y3 = (cur[0] + v[0], cur[1] + v[1], cur[0] + v[2],
                                          cur[1] + v[3], cur[0] + v[4], cur[1] + v[5])
            else:
                x1, y1, x2, y2, x3, y3 = v
            x0, y0 = cur
            for k in range(1, steps + 1):
                u = k / steps; w = 1 - u
                poly.append(pt(w * w * w * x0 + 3 * w * w * u * x1 + 3 * w * u * u * x2 + u ** 3 * x3,
                               w * w * w * y0 + 3 * w * w * u * y1 + 3 * w * u * u * y2 + u ** 3 * y3))
            cur = (x3, y3)
        elif cmd in "Hh":
            x = float(toks[i]); i += 1
            cur = ((cur[0] + x) if cmd == "h" else x, cur[1]); poly.append(pt(*cur))
        elif cmd in "Vv":
            y = float(toks[i]); i += 1
            cur = (cur[0], (cur[1] + y) if cmd == "v" else y); poly.append(pt(*cur))
        else:
            raise ValueError(f"unhandled path command {cmd!r}")
    if len(poly) > 2: polys.append(poly)
    return polys


def silhouette(key):
    path = os.path.join(SRC, "phylo", f"{key}__{build.choices[key]['uuid']}.svg")
    polys = parse_svg(path)
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    return polys, (min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------- measuring
def column_span(polys, x):
    """The topmost and bottommost ink in the vertical line at x, or None if it misses."""
    ys = []
    for poly in polys:
        n = len(poly)
        for i in range(n):
            ax, ay = poly[i]
            bx, by = poly[(i + 1) % n]
            if (ax <= x < bx) or (bx <= x < ax):
                ys.append(ay + (x - ax) / (bx - ax) * (by - ay))
    return (min(ys), max(ys)) if ys else None


def profiles(key, cols=80):
    """Top and bottom edge in each column, as a fraction of the drawing's own height."""
    polys, (x0, y0, x1, y1) = silhouette(key)
    top, bot = [], []
    for i in range(cols):
        span = column_span(polys, x0 + (i + 0.5) * (x1 - x0) / cols)
        top.append(None if span is None else 1 - (span[0] - y0) / (y1 - y0))
        bot.append(None if span is None else 1 - (span[1] - y0) / (y1 - y0))
    return top, bot


def ink_area(polys):
    """Area the drawing covers, by the shoelace formula.

    potrace winds a hole the opposite way round from the outline it sits in, so the signed areas
    cancel and what is left is the ink alone.
    """
    total = 0.0
    for poly in polys:
        n = len(poly)
        total += sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1]
                     for i in range(n)) / 2
    return abs(total)


# ---------------------------------------------------------------- heights
def report():
    """Each animal's recorded scale, what it implies, and how well the two checks agree."""
    print(f"{'animal':11s}{'h (m)':>7s}{'by height':>11s}{'by length':>11s}{'spread':>8s}  landmark")
    bad, note = [], []
    for key, v in sorted(build.ANIMALS.items(), key=lambda kv: kv[1]["h"]):
        s, b = v["scale"], build.bbox[key]
        by_h = s["h_m"] / s["h_f"]
        by_l = s["l_m"] / (s["l_f"] * b["w"] / b["h"]) if s["l_m"] else None
        spread = (max(by_h, by_l) / min(by_h, by_l) - 1) if by_l else None
        want = build.scaled_h(key)
        if abs(v["h"] - want) > max(0.04 * want, 0.005):
            bad.append(f"{key}: h={v['h']} does not follow from its measurement ({want:.3f})")
        top = profiles(key)[0]
        highest = max(t for t in top if t is not None)
        if s["h_f"] > highest + 0.01:
            bad.append(f"{key}: {s['at']} recorded at {s['h_f']:.2f}, above the drawing's own top")
        print(f"{key:11s}{v['h']:7.3f}{by_h:11.3f}"
              f"{(f'{by_l:11.3f}' if by_l else '          -')}"
              f"{(f'{spread*100:7.0f}%' if spread is not None else '       -')}"
              f"  {s['at']} at {s['h_f']*100:.0f}% ({s['how']})")
        if spread is not None and spread > 0.20:
            note.append(f"{key}: the drawing's proportions are {spread*100:.0f}% off the animal's, so "
                        f"height and length cannot both be right; `how` is {s['how']!r}")
    print()
    if note:
        print("STYLISED DRAWINGS - a judgement call, not an error:")
        for m in note: print("  -", m)
        print()
    if bad:
        print("PROBLEMS")
        for m in bad: print("  -", m)
    else:
        print("every animal's height follows from a measurement that fits its drawing")
    return 1 if bad else 0


# ---------------------------------------------------------------- weights
def weights():
    """Weights against their sources, and against the space the drawing takes up.

    The hard check is build.check_weights(): kg has to sit inside the sourced range. The column
    printed here is a softer sanity read - the average thickness a body would need to weigh what we
    say it weighs, given the area of ink the drawing covers. It varies honestly with body plan (a
    giraffe is mostly neck and leg) and it undercounts animals drawn as line work rather than solid
    ink, the zebra and the tiger, so it is here to make a badly wrong figure obvious, not to pass or
    fail one.
    """
    print(f"\n{'animal':11s}{'kg':>9s}{'sourced range':>22s}{'in range':>10s}   implied breadth")
    for key, v in sorted(build.ANIMALS.items(), key=lambda kv: kv[1]["kg"]):
        m = v["mass"]
        polys, (x0, y0, x1, y1) = silhouette(key)
        metres_per_unit = v["h"] / (y1 - y0)
        ink = ink_area(polys) * metres_per_unit ** 2          # square metres the animal covers
        breadth = (v["kg"] / 1000.0) / ink                     # at the density of water
        span = f"{m['lo']:g}-{m['hi']:g}" if m["lo"] != m["hi"] else f"{m['lo']:g} (average only)"
        where = "-" if m["hi"] == m["lo"] else f"{(v['kg']-m['lo'])/(m['hi']-m['lo'])*100:.0f}%"
        print(f"{key:11s}{v['kg']:9.2f}{span:>22s}{where:>10s}"
              f"{breadth:12.3f} m  ({breadth / v['h']:.2f}x its height)")


# ---------------------------------------------------------------- the weight game's own scale
def js_const(name, pattern):
    """Read a number out of the template, so this check cannot drift from the game."""
    src = open(os.path.join(SRC, "template.html"), encoding="utf-8").read()
    m = re.search(pattern, src)
    assert m, f"could not find {name} in template.html - this check needs updating"
    return float(m.group(1))


def weigh_scale():
    """In the weight game both sides share one scale, so a token's height is the true height ratio.

    Worth checking because it is the thing a player actually sees: forty foxes beside one horse only
    reads right if the fox is really a quarter of the horse. The one place the game bends it on
    purpose is the legibility floor, which stops a token becoming a speck - so find every pair the
    game can deal and report which, if any, land on that floor.
    """
    pan_half = js_const("PAN_HALF", r"PAN_HALF\s*=\s*(\d+)")
    ref_max = js_const("REF_MAX", r"REF_MAX\s*=\s*(\d+)")
    plate = js_const("plate fraction", r"let rw = ([\d.]+) \* PAN_HALF \* 2")
    floor_h = js_const("token floor", r"if \(h < (\d+)\) h = \d+")
    floor_m = js_const("token minimum", r"if \(m < (\d+)\)")
    min_ref = js_const("reference mass", r"A\[k\]\.kg >= (\d+)")
    lo = js_const("lowest multiple", r"A\[r\]\.kg / A\[k\]\.kg >= (\d+)")
    hi = js_const("highest multiple", r"A\[r\]\.kg / A\[k\]\.kg <= (\d+)")
    tall = js_const("tallest target", r"A\[k\]\.h / A\[r\]\.h <= ([\d.]+)")

    A = build.ANIMALS
    ar = lambda k: build.bbox[k]["w"] / build.bbox[k]["h"]
    pairs = [(r, t) for r in A if A[r]["kg"] >= min_ref for t in A
             if t != r and lo <= A[r]["kg"] / A[t]["kg"] <= hi and A[t]["h"] / A[r]["h"] <= tall]
    bent = []
    for r, t in pairs:
        ref_px = min(ref_max, plate * pan_half * 2 / ar(r))      # the reference fills the plate
        px = ref_px * (A[t]["h"] / A[r]["h"])                    # the target, at the true ratio
        drawn = max(px, floor_h)
        if max(drawn * ar(t), drawn) < floor_m:
            drawn *= floor_m / max(drawn * ar(t), drawn)
        if drawn > px * 1.005:
            bent.append((r, t, px, drawn))
    print(f"\n{len(pairs)} pairs the weight game can deal, from {len({p[0] for p in pairs})} references.")
    if not bent:
        print("every one of them is drawn at the animals' true height ratio.")
    else:
        print(f"{len(bent)} of them {'sits' if len(bent) == 1 else 'sit'} on the legibility floor "
              f"and {'is' if len(bent) == 1 else 'are'} drawn larger than life:")
        for r, t, px, drawn in sorted(bent, key=lambda b: -b[3] / b[2]):
            print(f"  {A[r]['name']} with {A[t]['name'].lower()}: "
                  f"{px:.0f}px true, drawn {drawn:.0f}px ({drawn/px-1:+.0%})")
    return len(pairs)


# ---------------------------------------------------------------- proposing a new animal
def propose(key):
    """Suggest where a quadruped's withers sits in a drawing, as a starting number to confirm.

    The withers is the one figure in an animal's record that cannot be looked up: it is a fact about
    this particular drawing, not about the animal. This finds the feet - the columns whose lowest
    ink is on the ground - and reads the top edge above the outermost group at each end, which for a
    quadruped standing in profile is the shoulder at one end and the rump at the other.

    Treat the answer as a draft. Measured against the quadrupeds already sized by hand, the better
    of its two candidates lands within 3 points on twelve of twenty-one and misses by as much as 12
    on animals whose outermost feet are not the front ones, or whose antlers or hump overhang the
    legs - and 12 points is a 15% error in the animal's size. So take the number, put it in the
    record, then run --sheets and check the green line landed on the shoulder.
    """
    top, bot = profiles(key)
    on = [i for i, b in enumerate(bot) if b is not None and b < 0.06]
    groups = []
    for i in on:
        if groups and i - groups[-1][-1] <= 2: groups[-1].append(i)
        else: groups.append([i])
    groups = [g for g in groups if len(g) >= 2]
    b = build.bbox[key]
    print(f"\n{key}: aspect {b['w']/b['h']:.3f}, highest point at "
          f"{max(t for t in top if t is not None)*100:.0f}% of its own height")
    if len(groups) < 2:
        print("  no clear pair of foot groups - not a quadruped standing in profile, "
              "so measure this one by eye on the sheet")
        return
    for g, end in ((groups[0], "left"), (groups[-1], "right")):
        mid = g[len(g) // 2]
        window = [top[i] for i in range(max(0, mid - 2), min(len(top), mid + 3)) if top[i] is not None]
        print(f"  top edge above the {end}-hand feet (x={mid/len(top)*100:.0f}% of the width): "
              f"h_f = {max(window):.3f}")
    print("  one of those two is the withers and the other the rump - confirm which on the sheet")


# ---------------------------------------------------------------- contact sheets
def sheets(out_dir, cols=3, cell=(470, 400), per=6, only=None):
    """Draw the animals with a percentage grid and a line at the recorded fraction, as SVG."""
    os.makedirs(out_dir, exist_ok=True)
    keys = list(only) if only else sorted(build.ANIMALS, key=lambda k: build.ANIMALS[k]["h"])
    CW, CH = cell
    written = []
    for page in range(0, len(keys), per):
        group = keys[page:page + per]
        W, H = cols * CW, math.ceil(len(group) / cols) * CH
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace">',
               f'<rect width="{W}" height="{H}" fill="#fff"/>']
        for i, key in enumerate(group):
            cx, cy = (i % cols) * CW, (i // cols) * CH
            polys, (bx0, by0, bx1, by1) = silhouette(key)
            bw, bh = bx1 - bx0, by1 - by0
            padx, padt, padb = 52, 34, 40
            sc = min((CW - 2 * padx) / bw, (CH - padt - padb) / bh)
            w, h = bw * sc, bh * sc
            ox, oy = cx + padx + (CW - 2 * padx - w) / 2, cy + padt + (CH - padt - padb - h) / 2
            out.append(f'<rect x="{cx+1}" y="{cy+1}" width="{CW-2}" height="{CH-2}" '
                       f'fill="none" stroke="#c8cdd4"/>')
            out.append(f'<svg x="{ox:.1f}" y="{oy:.1f}" width="{w:.1f}" height="{h:.1f}" '
                       f'viewBox="{bx0:.2f} {by0:.2f} {bw:.2f} {bh:.2f}">'
                       f'<g fill="{INK}">{build.inner_svg(key)}</g></svg>')
            for p in range(21):                                   # height, every 5%, labelled at 10%
                yy = oy + h - p / 20 * h
                major = p % 2 == 0
                out.append(f'<path d="M{ox-32:.1f} {yy:.1f}H{ox+w+16:.1f}" stroke="#c00" '
                           f'stroke-width="{.8 if major else .6}" opacity="{.5 if major else .22}"/>')
                if major:
                    out.append(f'<text x="{ox-36:.1f}" y="{yy+3:.1f}" font-size="9" fill="#a00" '
                               f'text-anchor="end">{p*5}</text>')
            for p in range(11):                                   # width, every 10%
                xx = ox + p / 10 * w
                major = p % 5 == 0
                out.append(f'<path d="M{xx:.1f} {oy-10:.1f}V{oy+h+10:.1f}" stroke="#0046be" '
                           f'stroke-width="{.8 if major else .6}" opacity="{.4 if major else .18}"/>')
            rec = build.ANIMALS.get(key)
            if rec:
                s = rec["scale"]
                yy = oy + h - s["h_f"] * h
                out.append(f'<path d="M{ox-40:.1f} {yy:.1f}H{min(ox+w+46, cx+CW-8):.1f}" '
                           f'stroke="#0a9612" stroke-width="1.2"/>')
                out.append(f'<text x="{min(ox+w+46, cx+CW-8):.1f}" y="{yy-4:.1f}" font-size="10" '
                           f'fill="#0a7a10" text-anchor="end">{s["at"]} {s["h_f"]*100:.0f}%</text>')
            label = f'{key}  h={rec["h"]:.2f} m' if rec else f'{key}  not sized yet'
            out.append(f'<text x="{cx+10}" y="{cy+22}" font-size="14" font-weight="700" '
                       f'fill="#1c1c1c">{label}</text>')
        out.append("</svg>")
        path = os.path.join(out_dir, f"scale_{page // per}.svg")
        open(path, "w", encoding="utf-8").write("\n".join(out))
        written.append(path)
    return written


if __name__ == "__main__":
    out = os.path.join(HERE, "audit")
    if "--propose" in sys.argv:
        wanted = sys.argv[sys.argv.index("--propose") + 1:]
        unknown = [k for k in wanted if k not in build.choices]
        if not wanted or unknown:
            raise SystemExit(f"--propose needs keys that are in src/choices.json; "
                             f"{unknown or 'none'} {'is' if len(unknown) == 1 else 'are'} not")
        for k in wanted: propose(k)
        print()
        for p in sheets(out, only=wanted): print("drew", os.path.relpath(p, ROOT))
        raise SystemExit(0)
    code = report()
    weights()
    weigh_scale()
    if "--sheets" in sys.argv:
        print()
        for p in sheets(out): print("drew", os.path.relpath(p, ROOT))
    raise SystemExit(code)
