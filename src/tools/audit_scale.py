"""Check every silhouette's scale against the drawing it is taken from.

`src/build.py` scales each animal from a real dimension and the fraction of the silhouette that
dimension reaches (the `scale` field). That fraction is a claim about the artwork - "a cow's withers
sit at 93% of this drawing's height" - and a wrong one silently makes the animal the wrong size in
all three games. This rasterises the SVGs and checks the claims.

    python src/tools/audit_scale.py            report every animal, flag the doubtful ones
    python src/tools/audit_scale.py --sheets   also draw contact sheets into src/tools/audit/

It checks three things: that each height still follows from its recorded measurement, that each
weight sits inside the range its source gives, and that the weight game draws every animal at its
true height against the animal it is weighed against.

The sheets carry a percentage grid and a green line at the recorded fraction: if the line does not
land on the withers (or whichever landmark `at` names), the number is wrong. Needs nothing but
Python 3 - the PhyloPic files are potrace output using only M, c and z, so it rasterises them here
rather than pulling in a renderer.
"""
import json, math, os, re, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import build                                       # noqa: E402  - the size table under test

NUM = r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?"


# ---------------------------------------------------------------- rasteriser
def parse_svg(path):
    """Return the silhouette's outlines as polygons in user space."""
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


def bounds(polys):
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def rasterize(polys, W, H, box, ss=3):
    """Coverage grid, 0..1 per pixel, nonzero winding, ss x ss supersampled."""
    x0, y0, x1, y1 = box
    kx, ky = W * ss / (x1 - x0), H * ss / (y1 - y0)
    HS, WS = H * ss, W * ss
    buckets = [[] for _ in range(HS)]
    for poly in polys:
        n = len(poly)
        for k in range(n):
            ax, ay = poly[k]; bx, by = poly[(k + 1) % n]
            ax, ay = (ax - x0) * kx, (ay - y0) * ky
            bx, by = (bx - x0) * kx, (by - y0) * ky
            if ay == by: continue
            e = (ay, by, ax, bx)
            for row in range(max(0, int(math.floor(min(ay, by)))), min(HS, int(math.ceil(max(ay, by))))):
                buckets[row].append(e)
    cov = [0.0] * (W * H)
    inv = 1.0 / (ss * ss)
    for sy in range(HS):
        yc = sy + 0.5
        xs = []
        for ay, by, ax, bx in buckets[sy]:
            if (ay <= yc < by) or (by <= yc < ay):
                xs.append((ax + (yc - ay) / (by - ay) * (bx - ax), 1 if by > ay else -1))
        if not xs: continue
        xs.sort()
        wind, spanstart, row = 0, None, (sy // ss) * W
        for x, dirn in xs:
            prev, wind = wind, wind + dirn
            if prev == 0 and wind != 0:
                spanstart = x
            elif prev != 0 and wind == 0 and spanstart is not None:
                a, b = max(spanstart, 0.0), min(x, float(WS))
                spanstart = None
                if b <= a: continue
                ia, ib = int(a), int(min(b, WS - 1e-9))
                if ia == ib:
                    cov[row + ia // ss] += (b - a) * inv
                else:
                    cov[row + ia // ss] += (ia + 1 - a) * inv
                    for xx in range(ia + 1, ib): cov[row + xx // ss] += inv
                    cov[row + ib // ss] += (b - ib) * inv
    return [min(1.0, c) for c in cov]


# ---------------------------------------------------------------- measuring
def silhouette(key):
    path = os.path.join(SRC, "phylo", f"{key}__{build.choices[key]['uuid']}.svg")
    polys = parse_svg(path)
    return polys, bounds(polys)


def topline(key, cols=40, rows=400):
    """Height of the silhouette's top edge in each column, as a fraction of its own height."""
    polys, box = silhouette(key)
    cov = rasterize(polys, cols, rows, box, ss=4)
    out = []
    for x in range(cols):
        hit = [y for y in range(rows) if cov[y * cols + x] > 0.25]
        out.append(1 - hit[0] / rows if hit else None)
    return out


def report():
    """Print each animal's recorded scale, what it implies, and how well the two checks agree."""
    print(f"{'animal':11s}{'h (m)':>7s}{'by height':>11s}{'by length':>11s}{'spread':>8s}  landmark")
    bad, note = [], []
    for key, v in sorted(build.ANIMALS.items(), key=lambda kv: kv[1]["h"]):
        s, b = v["scale"], build.bbox[key]
        ar = b["w"] / b["h"]
        by_h = s["h_m"] / s["h_f"]
        by_l = s["l_m"] / (s["l_f"] * ar) if s["l_m"] else None
        spread = (max(by_h, by_l) / min(by_h, by_l) - 1) if by_l else None
        want = build.scaled_h(key)
        if abs(v["h"] - want) > max(0.04 * want, 0.005):
            bad.append(f"{key}: h={v['h']} does not follow from its measurement ({want:.3f})")
        # the recorded fraction has to land on real ink, and not at the very top unless it is meant to
        top = topline(key)
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

    The hard check is in build.check_weights(): kg has to sit inside the sourced range. The column
    printed here is a softer sanity read - the average thickness a body would need to weigh what we
    say it weighs, given the area of ink the drawing covers. It varies honestly with body plan (a
    giraffe is mostly neck and leg) and it undercounts animals drawn as line work rather than solid
    ink, the zebra and the tiger, so it is here to make a badly wrong figure obvious, not to pass
    or fail one.
    """
    print(f"\n{'animal':11s}{'kg':>9s}{'sourced range':>22s}{'in range':>10s}   implied breadth")
    for key, v in sorted(build.ANIMALS.items(), key=lambda kv: kv[1]["kg"]):
        w = build.WEIGHTS[key]
        polys, box = silhouette(key)
        bw, bh = box[2] - box[0], box[3] - box[1]
        cols = 110
        cov = rasterize(polys, cols, int(cols * bh / bw) + 1, box, ss=3)
        fill = sum(cov) / (cols * (int(cols * bh / bw) + 1))
        ink = fill * v["h"] * (v["h"] * bw / bh)                 # square metres the animal covers
        breadth = (v["kg"] / 1000.0) / ink                       # at the density of water
        span = f"{w['lo']:g}-{w['hi']:g}" if w["lo"] != w["hi"] else f"{w['lo']:g} (average only)"
        where = "-" if w["hi"] == w["lo"] else f"{(v['kg']-w['lo'])/(w['hi']-w['lo'])*100:.0f}%"
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

    Worth checking because it is the thing a player actually sees: forty foxes beside one horse
    only reads right if the fox is really a quarter of the horse. The one place the game bends it
    on purpose is the legibility floor, which stops a token becoming a speck - so find every pair
    the game can deal and report which, if any, land on that floor.
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
            print(f"  {A[r]['name']} with {build.ANIMALS[t]['name'].lower()}: "
                  f"{px:.0f}px true, drawn {drawn:.0f}px ({drawn/px-1:+.0%})")
    return len(pairs)


# ---------------------------------------------------------------- contact sheets
FONT = {c: r for c, r in zip("0123456789",
        [["111","101","101","101","111"],["010","110","010","010","111"],["111","001","111","100","111"],
         ["111","001","111","001","111"],["101","101","111","001","001"],["111","100","111","001","111"],
         ["111","100","111","101","111"],["111","001","010","010","010"],["111","101","111","101","111"],
         ["111","101","111","001","111"]])}
FONT.update({c: r for c, r in zip("abcdefghijklmnopqrstuvwxyz .%-=",
        [["111","101","111","101","101"],["110","101","110","101","110"],["111","100","100","100","111"],
         ["110","101","101","101","110"],["111","100","111","100","111"],["111","100","110","100","100"],
         ["111","100","101","101","111"],["101","101","111","101","101"],["111","010","010","010","111"],
         ["001","001","001","101","111"],["101","110","100","110","101"],["100","100","100","100","111"],
         ["101","111","111","101","101"],["101","111","111","111","101"],["111","101","101","101","111"],
         ["111","101","111","100","100"],["111","101","101","111","001"],["111","101","110","101","101"],
         ["111","100","111","001","111"],["111","010","010","010","010"],["101","101","101","101","111"],
         ["101","101","101","101","010"],["101","101","111","111","101"],["101","101","010","101","101"],
         ["101","101","111","010","010"],["111","001","010","100","111"],["000","000","000","000","000"],
         ["000","000","000","000","010"],["101","001","010","100","101"],["000","000","111","000","000"],
         ["000","111","000","111","000"]])})


class Canvas:
    def __init__(s, W, H):
        s.W, s.H, s.px = W, H, bytearray(b"\xff" * (W * H * 3))

    def dot(s, x, y, c, a=1.0):
        if 0 <= x < s.W and 0 <= y < s.H:
            i = (y * s.W + x) * 3
            for k in range(3): s.px[i + k] = int(s.px[i + k] * (1 - a) + c[k] * a)

    def hline(s, y, x0, x1, c, a=1.0):
        for x in range(int(x0), int(x1)): s.dot(x, int(y), c, a)

    def vline(s, x, y0, y1, c, a=1.0):
        for y in range(int(y0), int(y1)): s.dot(int(x), y, c, a)

    def text(s, x, y, t, c=(20, 20, 20), sc=1):
        for ch in t.lower():
            for ry, row in enumerate(FONT.get(ch, FONT[" "])):
                for rx, on in enumerate(row):
                    if on == "1":
                        for dy in range(sc):
                            for dx in range(sc): s.dot(x + rx * sc + dx, y + ry * sc + dy, c)
            x += 4 * sc

    def save(s, path):
        raw = b"".join(b"\x00" + bytes(s.px[y * s.W * 3:(y + 1) * s.W * 3]) for y in range(s.H))
        def chunk(tag, data):
            c = tag + data
            return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n"
                    + chunk(b"IHDR", struct.pack(">IIBBBBB", s.W, s.H, 8, 2, 0, 0, 0))
                    + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def sheets(out_dir, cols=3, cell=(470, 400), per=6):
    os.makedirs(out_dir, exist_ok=True)
    keys = sorted(build.ANIMALS, key=lambda k: build.ANIMALS[k]["h"])
    written = []
    for page in range(0, len(keys), per):
        group = keys[page:page + per]
        CW, CH = cell
        img = Canvas(cols * CW, math.ceil(len(group) / cols) * CH)
        for i, key in enumerate(group):
            cx, cy = (i % cols) * CW, (i // cols) * CH
            polys, box = silhouette(key)
            bw, bh = box[2] - box[0], box[3] - box[1]
            padx, padt, padb = 46, 34, 40
            sc = min((CW - 2 * padx) / bw, (CH - padt - padb) / bh)
            w, h = bw * sc, bh * sc
            ox, oy = cx + padx + (CW - 2 * padx - w) / 2, cy + padt + (CH - padt - padb - h) / 2
            cov = rasterize(polys, int(w), int(h), box, ss=3)
            for yy in range(int(h)):
                for xx in range(int(w)):
                    a = cov[yy * int(w) + xx]
                    if a > 0.004: img.dot(int(ox) + xx, int(oy) + yy, (40, 48, 60), a)
            for p in range(21):                                   # grid, every 5% of the height
                yy = oy + h - p / 20 * h
                major = p % 2 == 0
                img.hline(yy, ox - 30, ox + w + 16, (200, 0, 0), 0.5 if major else 0.2)
                if major: img.text(int(ox - 30), int(yy) - 3, str(p * 5), (150, 0, 0))
            for p in range(11):
                img.vline(ox + p / 10 * w, oy - 10, oy + h + 10, (0, 70, 190), 0.4 if p % 5 == 0 else 0.16)
            s = build.ANIMALS[key]["scale"]
            yy = oy + h - s["h_f"] * h
            img.hline(yy, ox - 38, ox + w + 44, (0, 150, 0))
            img.text(int(ox + w + 20), int(yy) - 3, f"{s['at']} {s['h_f']*100:.0f}", (0, 120, 0))
            img.text(cx + 8, cy + 10, f"{key} h={build.ANIMALS[key]['h']:.2f}m", (20, 20, 20), 2)
        path = os.path.join(out_dir, f"scale_{page // per}.png")
        img.save(path)
        written.append(path)
    return written


if __name__ == "__main__":
    code = report()
    weights()
    weigh_scale()
    if "--sheets" in sys.argv:
        out = os.path.join(HERE, "audit")
        print()
        for p in sheets(out): print("drew", os.path.relpath(p, ROOT))
    raise SystemExit(code)
