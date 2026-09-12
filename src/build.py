"""Assemble index.html from template.html, the chosen PhyloPic SVGs and the size table below.

Sizing method (per animal). Every silhouette is scaled from a real, sourced dimension and the
place that dimension sits in the drawing, both recorded in the `scale` field:

    at    the landmark the height figure describes ("withers", "back", "ear tips" ...)
    h_m   that landmark's real height above the ground, in metres
    h_f   where it sits in the silhouette, as a fraction of the silhouette's height
    l_m   a real length (head-body, or muzzle-to-rump for a head-up pose), in metres, or None
    l_f   the fraction of the silhouette's width that length spans
    how   "height"  h = h_m / h_f              - the height figure is the reliable one
          "length"  h = l_m / (l_f * aspect)   - sources quote only a body length
          "mean"    the geometric mean of the two - both are sourced but the drawing,
                    being stylised, cannot satisfy both, so the error is split

`h` is the resulting height of the silhouette's highest point in metres - the value players are
scored on - and `check_scale()` below asserts it still follows from the measurement. The fractions
were measured off the silhouettes themselves by src/tools/audit_scale.py; run that after touching
a figure here, and read src/tools/audit_scale.py --sheets to see them drawn on the animals.
"""
import json, re, os, math, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.dirname(HERE)   # the repository root
OUT_NAME = "index.html"

choices = json.load(open(os.path.join(HERE, "choices.json")))
bbox = json.load(open(os.path.join(HERE, "bbox.json")))

LICENSES = {
    "https://creativecommons.org/publicdomain/zero/1.0/": "CC0 1.0",
    "https://creativecommons.org/publicdomain/mark/1.0/": "Public Domain Mark 1.0",
    "https://creativecommons.org/licenses/by/4.0/": "CC BY 4.0",
    "https://creativecommons.org/licenses/by/3.0/": "CC BY 3.0",
    "https://creativecommons.org/licenses/by-sa/3.0/": "CC BY-SA 3.0",
}

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

def record(key, extra=None):
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
    if extra: rec.update(extra)
    return rec

WIKI = "Wikipedia"

ANIMALS = {
    # ---------------- Farm & Home ----------------
    "cat": dict(name="Domestic cat", h=0.45,
        scale=dict(at="withers", h_m=0.24, h_f=0.60, l_m=0.46, l_f=0.76, how="mean"),
        fact="An adult cat stands 23–25 cm at the shoulder and is about 46 cm long, not counting a 30 cm tail.",
        sizing="This cat is drawn long in the leg and short in the body: its 24 cm shoulder lands at 60% of the silhouette, its 46 cm body at three quarters of the width. Splitting the two puts the raised tail tip at 45 cm.",
        source=f"{WIKI}: Cat"),
    "rabbit": dict(name="European rabbit", h=0.25,
        scale=dict(at="ear tips", h_m=0.25, h_f=1.0, l_m=0.30, l_f=1.0, how="height"),
        fact="A European rabbit's head and body run 36–38 cm; its ears are 7–8 cm long.",
        sizing="A sitting rabbit stands about 25 cm to the ear tips, which is this silhouette's whole height.",
        source=f"{WIKI}: European rabbit"),
    "dog": dict(name="Labrador retriever", h=0.64,
        scale=dict(at="withers", h_m=0.56, h_f=0.87, l_m=0.90, l_f=0.84, how="height"),
        fact="The breed standard puts a Labrador at 54–57 cm at the withers and 25–36 kg.",
        sizing="Withers height 56 cm sits at 87% of this silhouette, giving 64 cm to the ear tips.",
        source=f"{WIKI}: Labrador Retriever (Kennel Club standard)"),
    "sheep": dict(name="Sheep", h=0.81,
        scale=dict(at="withers", h_m=0.70, h_f=0.865, l_m=1.10, l_f=0.94, how="height"),
        fact="Common breeds such as Texel and Suffolk stand roughly 65–80 cm at the withers under all that fleece.",
        sizing="Withers height 70 cm sits at 86% of this silhouette, giving 81 cm to the top of the head.",
        source="Texel and Awassi breed data (Wikipedia, FAO)"),
    "pig": dict(name="Domestic pig", h=0.84,
        scale=dict(at="shoulder", h_m=0.80, h_f=0.95, l_m=1.60, l_f=0.94, how="height"),
        fact="A grown Large White pig stands 75–90 cm at the shoulder and weighs 140–300 kg.",
        sizing="Shoulder height 80 cm sits at 95% of this silhouette; the arched back reaches about 84 cm.",
        source="Large White breed references; Wikipedia: Domestic pig"),
    "cow": dict(name="Holstein cow", h=1.60,
        scale=dict(at="withers", h_m=1.50, h_f=0.935, l_m=2.30, l_f=0.86, how="height"),
        fact="A mature Holstein cow stands 145–165 cm at the shoulder and weighs 680–770 kg.",
        sizing="Withers height 150 cm sits at 93% of this silhouette, giving 1.6 m to the horns.",
        source=f"{WIKI}: Holstein Friesian"),
    "horse": dict(name="Horse", h=1.81,
        scale=dict(at="withers", h_m=1.57, h_f=0.87, l_m=2.20, l_f=0.83, how="height"),
        fact="Light riding horses measure 14–16 hands (142–163 cm) at the withers, the highest point of the back.",
        sizing="Withers height 157 cm (15.2 hands) sits at 87% of this silhouette, giving 1.81 m to the ear tips — this horse carries its head low.",
        source=f"{WIKI}: Horse"),
    # ---------------- African Savanna ----------------
    "lion": dict(name="Lion", h=1.47,
        scale=dict(at="withers", h_m=1.10, h_f=0.75, l_m=1.90, l_f=0.85, how="height"),
        fact="A male lion's head and body run 1.84–2.08 m, and he stands roughly 1.1 m at the shoulder.",
        sizing="Shoulder height 1.1 m sits at 75% of this silhouette, giving 1.47 m to the top of the mane.",
        source=f"{WIKI}: Lion"),
    "zebra": dict(name="Plains zebra", h=1.67,
        scale=dict(at="withers", h_m=1.33, h_f=0.795, l_m=2.00, l_f=0.84, how="height"),
        fact="Plains zebras stand 127–140 cm at the shoulder, with a 2.2–2.5 m body.",
        sizing="Shoulder height 133 cm sits at 79% of this silhouette, giving 1.67 m to the ear tips.",
        source=f"{WIKI}: Plains zebra"),
    "hippo": dict(name="Hippopotamus", h=1.63,
        scale=dict(at="withers", h_m=1.45, h_f=0.89, l_m=3.20, l_f=0.97, how="height"),
        fact="A hippo stands about 1.4 m at the shoulder (bulls up to 1.65 m) and weighs around 1.5 tonnes.",
        sizing="Shoulder height 1.45 m sits at 89% of this silhouette, giving 1.63 m over the arch of the back.",
        source=f"{WIKI}: Hippopotamus"),
    "rhino": dict(name="White rhinoceros", h=1.77,
        scale=dict(at="withers", h_m=1.75, h_f=0.99, l_m=3.70, l_f=0.96, how="height"),
        fact="White rhino bulls stand 1.7–1.86 m at the shoulder and weigh 2–2.3 tonnes.",
        sizing="Shoulder height 1.75 m sits at 99% of this silhouette, giving 1.77 m to the top of the shoulder hump.",
        source=f"{WIKI}: White rhinoceros"),
    "elephant": dict(name="African bush elephant", h=3.30,
        scale=dict(at="shoulder", h_m=3.20, h_f=0.97, l_m=None, l_f=None, how="height"),
        fact="A bull African bush elephant averages 3.2 m at the shoulder and 6 tonnes; cows average 2.6 m.",
        sizing="Bull shoulder height 3.2 m sits at 97% of this silhouette, giving 3.3 m to the highest point of the back.",
        source=f"{WIKI}: African bush elephant"),
    "giraffe": dict(name="Giraffe", h=5.0,
        scale=dict(at="horn tips", h_m=5.00, h_f=1.0, l_m=2.90, l_f=1.0, how="height"),
        fact="Fully grown giraffes stand 4.3–5.7 m tall; males average about 5.3 m, females about 4.5 m.",
        sizing="Total height is quoted directly: 5.0 m for a typical adult, measured to the horn tips.",
        source=f"{WIKI}: Giraffe"),
    # ---------------- Northern Forest ----------------
    "fox": dict(name="Red fox", h=0.48,
        scale=dict(at="withers", h_m=0.40, h_f=0.84, l_m=0.65, l_f=0.76, how="height"),
        fact="Red foxes stand 35–50 cm at the shoulder, with a 45–90 cm body and a 30–55 cm tail.",
        sizing="Shoulder height 40 cm sits at 84% of this silhouette, giving 48 cm to the ear tips.",
        source=f"{WIKI}: Red fox"),
    "lynx": dict(name="Eurasian lynx", h=0.84,
        scale=dict(at="withers", h_m=0.65, h_f=0.77, l_m=0.95, l_f=0.82, how="height"),
        fact="The Eurasian lynx stands 55–75 cm at the shoulder, with a body 73–106 cm long.",
        sizing="Shoulder height 65 cm sits at 77% of this silhouette, giving 84 cm to the ear tufts.",
        source=f"{WIKI}: Eurasian lynx"),
    "wolf": dict(name="Grey wolf", h=0.98,
        scale=dict(at="withers", h_m=0.82, h_f=0.84, l_m=1.20, l_f=0.84, how="height"),
        fact="Grey wolves stand 80–85 cm at the shoulder and run 105–160 cm from nose to rump.",
        sizing="Shoulder height 82 cm sits at 84% of this silhouette, giving 98 cm to the ear tips.",
        source=f"{WIKI}: Wolf"),
    "bear": dict(name="Brown bear", h=1.20,
        scale=dict(at="shoulder hump", h_m=1.15, h_f=0.965, l_m=1.80, l_f=0.96, how="height"),
        fact="On all fours, brown bears stand about 1–1.5 m at the shoulder; the largest coastal bears fill the top of that range.",
        sizing="The shoulder hump, 1.15 m on a large adult, is at 96% of this silhouette; the ears just clear it at 1.2 m.",
        source=f"{WIKI}: Brown bear"),
    "reindeer": dict(name="Reindeer", h=1.62,
        scale=dict(at="withers", h_m=1.10, h_f=0.68, l_m=1.75, l_f=0.92, how="height"),
        fact="Reindeer stand 85–150 cm at the shoulder, and both sexes grow antlers.",
        sizing="Shoulder height 1.1 m sits at 68% of this silhouette, giving 1.62 m to the antler tips.",
        source="Wikipedia: Reindeer; Dimensions.com reindeer size guide"),
    "reddeer": dict(name="Red deer stag", h=2.26,
        scale=dict(at="withers", h_m=1.20, h_f=0.53, l_m=1.95, l_f=0.94, how="height"),
        fact="Red deer stags stand 95–130 cm at the shoulder and carry antlers around 71 cm long.",
        sizing="Shoulder height 1.2 m sits at 53% of this silhouette — the antlers are half of it — giving 2.26 m to their tips.",
        source=f"{WIKI}: Red deer"),
    "moose": dict(name="Moose", h=2.54,
        scale=dict(at="shoulder hump", h_m=1.80, h_f=0.71, l_m=2.70, l_f=0.92, how="height"),
        fact="Moose stand 1.4–2.1 m at the shoulder; a mature bull's antlers spread 1.2–1.5 m.",
        sizing="Bull shoulder height 1.8 m sits at 71% of this silhouette, giving 2.54 m to the top of the antlers.",
        source=f"{WIKI}: Moose"),
    # ---------------- Wild World ----------------
    "tiger": dict(name="Tiger", h=1.17,
        scale=dict(at="withers", h_m=0.95, h_f=0.94, l_m=1.90, l_f=0.82, how="mean"),
        fact="A male Bengal tiger stands 0.9–1.1 m at the shoulder, with a 1.9 m body and a metre of tail behind it.",
        sizing="Shoulder height 95 cm sits at 94% of this silhouette and the 1.9 m body reads a little short; splitting the two puts the top of the head at 1.17 m.",
        source=f"{WIKI}: Tiger"),
    "camel": dict(name="Dromedary", h=2.20, plural="dromedaries",
        scale=dict(at="withers", h_m=1.85, h_f=0.84, l_m=2.60, l_f=0.94, how="height"),
        fact="A dromedary bull stands 1.8–2.0 m at the shoulder, and the hump rises about 20 cm above that.",
        sizing="Shoulder height 1.85 m sits at 84% of this silhouette, giving 2.2 m to the crown of the hump.",
        source=f"{WIKI}: Dromedary"),
    "gorilla": dict(name="Western gorilla", h=1.35,
        scale=dict(at="back", h_m=1.00, h_f=0.75, l_m=1.20, l_f=0.94, how="mean"),
        fact="A silverback stands 1.4–1.8 m upright, but spends his day knuckle-walking with his back about a metre off the ground.",
        sizing="The back of a knuckle-walking silverback, about 1 m up, sits at 75% of this silhouette; with the body reading short the scale settles at 1.35 m to the crest of the skull.",
        source=f"{WIKI}: Western gorilla"),
    "kangaroo": dict(name="Red kangaroo", h=1.60,
        scale=dict(at="ear tips", h_m=1.60, h_f=1.0, l_m=None, l_f=None, how="height"),
        fact="A big male red kangaroo stands about 1.5 m to the top of his head, with a tail over a metre long propping him up.",
        sizing="Standing upright with his tail on the ground, a large male reaches about 1.6 m to the ear tips, which is this silhouette's whole height.",
        source=f"{WIKI}: Red kangaroo"),
    # ---------------- Rodents & Co. ----------------
    "mouse": dict(name="House mouse", h=0.053,
        scale=dict(at="back", h_m=0.030, h_f=0.84, l_m=0.085, l_f=0.73, how="mean"),
        fact="A house mouse's head and body are 7.5–10 cm long, with a tail of 5–10 cm.",
        sizing="Head and body of 8.5 cm span 73% of this silhouette's width, but the drawing is deeper-bodied than a real mouse; splitting height against length gives about 5.3 cm to the top of the back.",
        source=f"{WIKI}: House mouse"),
    "rat": dict(name="Brown rat", h=0.12,
        scale=dict(at="back", h_m=0.075, h_f=0.85, l_m=0.22, l_f=0.67, how="mean"),
        fact="Brown rats have a 15–28 cm body and a tail slightly shorter than that.",
        sizing="Head and body of 22 cm span two thirds of this silhouette's width; against a real rat's 7–8 cm back the drawing is deep, so the scale splits the two at 12 cm.",
        source=f"{WIKI}: Brown rat"),
    "guineapig": dict(name="Guinea pig", h=0.11,
        scale=dict(at="back", h_m=0.10, h_f=0.95, l_m=0.225, l_f=0.98, how="length"),
        fact="Guinea pigs are 20–25 cm long and weigh 0.7–1.2 kg.",
        sizing="Body length 22.5 cm spans this silhouette's width, giving 11 cm tall.",
        source=f"{WIKI}: Guinea pig"),
    "squirrel": dict(name="Red squirrel", h=0.24,
        scale=dict(at="head, sitting", h_m=0.17, h_f=0.72, l_m=None, l_f=None, how="height"),
        fact="A red squirrel's head and body are 19–23 cm, with a 15–20 cm tail.",
        sizing="Sitting up, the head reaches about 17 cm, which is 72% of this silhouette, giving 24 cm to the top of the tail.",
        source=f"{WIKI}: Red squirrel"),
    "hedgehog": dict(name="European hedgehog", h=0.11,
        scale=dict(at="back", h_m=0.105, h_f=0.95, l_m=0.26, l_f=1.0, how="length"),
        fact="Adult European hedgehogs reach about 26 cm long and weigh around 800 g in summer.",
        sizing="Body length 26 cm spans this silhouette's width, giving about 11 cm tall.",
        source=f"{WIKI}: European hedgehog"),
    "beaver": dict(name="North American beaver", h=0.43,
        scale=dict(at="back", h_m=0.32, h_f=0.90, l_m=0.80, l_f=0.67, how="mean"),
        fact="A beaver's head and body are 74–90 cm long, plus a 20–35 cm flat tail.",
        sizing="An 80 cm body fills two thirds of this silhouette's width, and a beaver's humped back is about 32 cm up; this drawing is the stockier of the two, so the scale splits them at 43 cm.",
        source=f"{WIKI}: North American beaver"),
    "capybara": dict(name="Capybara", h=0.60,
        scale=dict(at="withers", h_m=0.56, h_f=0.94, l_m=1.15, l_f=0.95, how="height"),
        fact="Capybaras stand 50–62 cm at the withers with a 106–134 cm body, the largest rodent alive.",
        sizing="Withers height 56 cm sits at 94% of this silhouette, giving 60 cm to the ears.",
        source=f"{WIKI}: Capybara"),
}

def scaled_h(key):
    """The height the recorded measurement implies - see the sizing method at the top."""
    s = ANIMALS[key]["scale"]
    b = bbox[key]
    ar = b["w"] / b["h"]
    by_height = s["h_m"] / s["h_f"]
    if s["how"] == "height": return by_height
    by_length = s["l_m"] / (s["l_f"] * ar)
    if s["how"] == "length": return by_length
    return math.sqrt(by_height * by_length)

def check_scale():
    """Every `h` must still follow from its measurement, within rounding."""
    for k, v in ANIMALS.items():
        want = scaled_h(k)
        assert abs(v["h"] - want) <= max(0.04 * want, 0.005), \
            f"{k}: h={v['h']} but the measurement gives {want:.4f}"

check_scale()

# Typical adult mass, matching the adult each silhouette depicts.
#   kg      the figure the games use
#   lo, hi  the range the source gives, which kg has to sit inside; where a source quotes only an
#           average, lo and hi are that average and the check simply pins kg to it
#   note    the sentence shown to the player after a weigh-in
# check_weights() below enforces lo <= kg <= hi, so a figure can never drift from its source
# without the range moving too - and moving the range means going back to the source.
WEIGHTS = {
    "cat":       dict(kg=4.5,  lo=4,     hi=5,     note="adult domestic cats typically weigh 4–5 kg"),
    "rabbit":    dict(kg=2.0,  lo=1.5,   hi=3,     note="European rabbits weigh 1.5–3 kg"),
    "dog":       dict(kg=30,   lo=25,    hi=36,    note="Labrador males weigh 29–36 kg, females 25–32 kg"),
    "sheep":     dict(kg=70,   lo=45,    hi=100,   note="ewes weigh 45–100 kg depending on breed"),
    "pig":       dict(kg=220,  lo=140,   hi=300,   note="adult domestic pigs weigh 140–300 kg"),
    "cow":       dict(kg=725,  lo=680,   hi=770,   note="a mature Holstein cow weighs 680–770 kg"),
    "horse":     dict(kg=480,  lo=380,   hi=550,   note="light riding horses weigh 380–550 kg"),
    "lion":      dict(kg=190,  lo=160,   hi=225,   note="male lions weigh 160–225 kg by region"),
    "zebra":     dict(kg=250,  lo=220,   hi=322,   note="plains zebra males weigh 220–322 kg"),
    "hippo":     dict(kg=1480, lo=1480,  hi=1480,  note="bull hippos average 1.48 tonnes", plural="hippopotamuses"),
    "rhino":     dict(kg=2150, lo=2000,  hi=2300,  note="white rhino bulls weigh 2,000–2,300 kg", plural="white rhinoceroses"),
    "elephant":  dict(kg=6000, lo=6000,  hi=6000,  note="bull African bush elephants average 6 tonnes"),
    "giraffe":   dict(kg=1000, lo=828,   hi=1192,  note="adult giraffes average 1,192 kg (male) and 828 kg (female)"),
    "fox":       dict(kg=6,    lo=2.2,   hi=14,    note="red foxes weigh 2.2–14 kg, typically about 6 kg", plural="red foxes"),
    "lynx":      dict(kg=20,   lo=7,     hi=32,    note="Eurasian lynx weigh 12–32 kg in Russia, 7–26 kg in the west", plural="Eurasian lynxes"),
    "wolf":      dict(kg=40,   lo=40,    hi=40,    note="grey wolves average 40 kg", plural="grey wolves"),
    "bear":      dict(kg=217,  lo=217,   hi=217,   note="male brown bears average 217 kg"),
    "reindeer":  dict(kg=150,  lo=150,   hi=180,   note="bull reindeer weigh roughly 150–180 kg", plural="reindeer"),
    "reddeer":   dict(kg=200,  lo=160,   hi=240,   note="red deer stags weigh 160–240 kg"),
    "moose":     dict(kg=500,  lo=380,   hi=700,   note="bull moose weigh 380–700 kg", plural="moose"),
    "mouse":     dict(kg=0.02, lo=0.011, hi=0.030, note="house mice weigh 11–30 g", plural="house mice"),
    "rat":       dict(kg=0.3,  lo=0.14,  hi=0.5,   note="wild brown rats commonly weigh under 300 g; the range is 140–500 g"),
    "guineapig": dict(kg=1.0,  lo=0.7,   hi=1.2,   note="guinea pigs weigh 0.7–1.2 kg"),
    "squirrel":  dict(kg=0.3,  lo=0.25,  hi=0.34,  note="red squirrels weigh 250–340 g"),
    "hedgehog":  dict(kg=0.8,  lo=0.8,   hi=0.8,   note="adult European hedgehogs weigh about 800 g in summer"),
    "beaver":    dict(kg=20,   lo=11,    hi=32,    note="North American beavers weigh 11–32 kg, typically about 20 kg"),
    "capybara":  dict(kg=49,   lo=35,    hi=66,    note="capybaras weigh 35–66 kg, averaging about 49 kg"),
    "tiger":     dict(kg=220,  lo=180,   hi=260,   note="male Bengal tigers weigh 180–260 kg"),
    "camel":     dict(kg=500,  lo=400,   hi=600,   note="dromedary bulls weigh 400–600 kg", plural="dromedaries"),
    "gorilla":   dict(kg=157,  lo=157,   hi=157,   note="wild male western gorillas average 157 kg", plural="western gorillas"),
    "kangaroo":  dict(kg=66,   lo=55,    hi=90,    note="male red kangaroos weigh 55–90 kg, averaging about 66 kg"),
}
for _k, _w in WEIGHTS.items():
    ANIMALS[_k]["kg"] = _w["kg"]
    ANIMALS[_k]["kgNote"] = _w["note"]
    if _w.get("plural"): ANIMALS[_k]["plural"] = _w["plural"]

def check_weights():
    """Every weight has to sit inside the range its source gives, and cite that source."""
    for k, w in WEIGHTS.items():
        assert w["lo"] <= w["kg"] <= w["hi"], \
            f"{k}: {w['kg']} kg is outside the sourced range {w['lo']}-{w['hi']}"
        assert ANIMALS[k].get("source"), f"{k}: no source recorded"

check_weights()
assert set(WEIGHTS) == set(ANIMALS), set(WEIGHTS) ^ set(ANIMALS)

SETS = [
    dict(id="farm", name="Farm & Home", blurb="Cat, rabbit, Labrador, sheep, pig, cow, horse. Five are picked each game.",
         members=["cat", "rabbit", "dog", "sheep", "pig", "cow", "horse"]),
    dict(id="savanna", name="African Savanna", blurb="Lion, zebra, hippo, rhino, elephant, giraffe. Five are picked each game.",
         members=["lion", "zebra", "hippo", "rhino", "elephant", "giraffe"]),
    dict(id="forest", name="Northern Forest", blurb="Fox, lynx, wolf, brown bear, reindeer, red deer, moose. Five are picked each game.",
         members=["fox", "lynx", "wolf", "bear", "reindeer", "reddeer", "moose"]),
    dict(id="world", name="Wild World", blurb="Tiger, dromedary, gorilla, red kangaroo, capybara, giraffe — one from each corner of the map. Five are picked each game.",
         members=["tiger", "camel", "gorilla", "kangaroo", "capybara", "giraffe"]),
    dict(id="rodents", name="Rodents & Co.", blurb="Mouse, rat, guinea pig, squirrel, hedgehog, beaver, capybara. Five are picked each game.",
         members=["mouse", "rat", "guineapig", "squirrel", "hedgehog", "beaver", "capybara"]),
]

# Loads for the balance-log game. Everything on one log shares a scale and a weight range, so the
# round is a torque puzzle rather than a single elephant surrounded by dust. Kept in order, lightest
# load first: a game plays five of them, one drawn from each fifth of this list, so it always climbs
# from the small animals to the heavyweights.
LOG_SETS = [
    dict(id="nest", name="Nest", blurb="Mouse, rat, squirrel, hedgehog, guinea pig.",
         members=["mouse", "rat", "squirrel", "hedgehog", "guineapig"]),
    dict(id="hedgerow", name="Hedgerow", blurb="Rat, squirrel, hedgehog, guinea pig, rabbit, cat.",
         members=["rat", "squirrel", "hedgehog", "guineapig", "rabbit", "cat"]),
    dict(id="riverbank", name="Riverbank", blurb="Cat, fox, beaver, lynx, Labrador, capybara.",
         members=["cat", "fox", "beaver", "lynx", "dog", "capybara"]),
    dict(id="pasture", name="Pasture", blurb="Wolf, sheep, reindeer, lion, brown bear, pig.",
         members=["wolf", "sheep", "reindeer", "lion", "bear", "pig"]),
    dict(id="farcountry", name="Far Country", blurb="Capybara, red kangaroo, gorilla, tiger, dromedary.",
         members=["capybara", "kangaroo", "gorilla", "tiger", "camel"]),
    dict(id="highland", name="Highland", blurb="Red deer, zebra, horse, moose, Holstein cow.",
         members=["reddeer", "zebra", "horse", "moose", "cow"]),
    dict(id="heavyweights", name="Heavyweights", blurb="Cow, giraffe, hippo, rhino, elephant.",
         members=["cow", "giraffe", "hippo", "rhino", "elephant"]),
]

def check_library():
    """One central library: every animal has to be reachable in all three games.

    The size game draws from SETS, the balance game from LOG_SETS, and the weight game pairs
    anything in ANIMALS, so an animal missing from either list is one a player can never meet.
    """
    for _group, _name in ((SETS, "SETS"), (LOG_SETS, "LOG_SETS")):
        for _s in _group:
            unknown = [m for m in _s["members"] if m not in ANIMALS]
            assert not unknown, f"{_name} {_s['id']}: no such animal {unknown}"
            assert len(_s["members"]) >= 5, f"{_name} {_s['id']}: needs at least five members"
        missing = sorted(set(ANIMALS) - {m for _s in _group for m in _s["members"]})
        assert not missing, f"not in any {_name}, so unreachable in that game: {missing}"
    assert len(LOG_SETS) >= 5, "the balance game plays five loads"
    # the weight game needs a heavy reference and something 3-60x lighter to pour against it
    for _k, _v in ANIMALS.items():
        if _v["kg"] < 30: continue
        assert any(_k != _t and 3 <= _v["kg"] / _u["kg"] <= 60 and _u["h"] / _v["h"] <= 0.6
                   for _t, _u in ANIMALS.items()), f"{_k} can be a reference with nothing to weigh against it"

check_library()

def main():
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
