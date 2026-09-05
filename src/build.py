"""Assemble life-size-lineup.html from template.html, the chosen PhyloPic SVGs and the size table below.

Sizing method (per animal): take the best-documented real-world dimension (usually shoulder height,
for small mammals body length), find where that dimension sits in the silhouette (fraction of the
silhouette's bounding box, read off the measurement sheets), and scale so the silhouette matches.
`h` is the resulting height of the silhouette's highest point in metres - the value players are scored on.
"""
import json, re, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.dirname(HERE)   # the repository root
OUT_NAME = "life-size-lineup.html"

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
    "cat": dict(name="Domestic cat", h=0.46,
        fact="An adult cat stands 23–25 cm at the shoulder and is about 46 cm long, not counting a 30 cm tail.",
        sizing="Shoulder height 24 cm sits at 52% of this silhouette's height, so the raised tail tip tops out near 46 cm.",
        source=f"{WIKI}: Cat"),
    "rabbit": dict(name="European rabbit", h=0.25,
        fact="A European rabbit's head and body run 36–38 cm; its ears are 7–8 cm long.",
        sizing="The 7.5 cm ears fill the top 30% of this sitting silhouette, giving about 25 cm to the ear tips.",
        source=f"{WIKI}: European rabbit"),
    "dog": dict(name="Labrador retriever", h=0.68,
        fact="The breed standard puts a Labrador at 54–57 cm at the withers and 25–36 kg.",
        sizing="Withers height 56 cm sits at 82% of this silhouette, giving 68 cm to the ear tips.",
        source=f"{WIKI}: Labrador Retriever (Kennel Club standard)"),
    "sheep": dict(name="Sheep", h=0.85,
        fact="Common breeds such as Texel and Suffolk stand roughly 65–80 cm at the withers under all that fleece.",
        sizing="Withers height 70 cm sits at 82% of this silhouette, giving 85 cm to the top of the head.",
        source="Texel and Awassi breed data (Wikipedia, FAO)"),
    "pig": dict(name="Domestic pig", h=0.84,
        fact="A grown Large White pig stands 75–90 cm at the shoulder and weighs 140–300 kg.",
        sizing="Shoulder height 80 cm sits at 95% of this silhouette; the arched back reaches about 84 cm.",
        source="Large White breed references; Wikipedia: Domestic pig"),
    "cow": dict(name="Holstein cow", h=1.55,
        fact="A mature Holstein cow stands 145–165 cm at the shoulder and weighs 680–770 kg.",
        sizing="Shoulder height 150 cm sits at 97% of this silhouette, giving 1.55 m to the ear tips.",
        source=f"{WIKI}: Holstein Friesian"),
    "horse": dict(name="Horse", h=1.98,
        fact="Light riding horses measure 14–16 hands (142–163 cm) at the withers, the highest point of the back.",
        sizing="Withers height 157 cm (15.2 hands) sits at 79% of this silhouette, giving 1.98 m to the ear tips with the head up.",
        source=f"{WIKI}: Horse"),
    # ---------------- African Savanna ----------------
    "lion": dict(name="Lion", h=1.50,
        fact="A male lion's head and body run 1.84–2.08 m, and he stands roughly 1.1 m at the shoulder.",
        sizing="Shoulder height 1.1 m sits at 73% of this silhouette, giving 1.5 m to the top of the mane.",
        source=f"{WIKI}: Lion"),
    "zebra": dict(name="Plains zebra", h=1.80,
        fact="Plains zebras stand 127–140 cm at the shoulder, with a 2.2–2.5 m body.",
        sizing="Shoulder height 133 cm sits at 74% of this silhouette, giving 1.8 m to the ear tips.",
        source=f"{WIKI}: Plains zebra"),
    "hippo": dict(name="Hippopotamus", h=1.50,
        fact="A hippo stands about 1.4 m at the shoulder (bulls up to 1.65 m) and weighs around 1.5 tonnes.",
        sizing="Shoulder height 1.45 m sits at 97% of this silhouette, giving 1.5 m to the top of the back.",
        source=f"{WIKI}: Hippopotamus"),
    "rhino": dict(name="White rhinoceros", h=1.78,
        fact="White rhino bulls stand 1.7–1.86 m at the shoulder and weigh 2–2.3 tonnes.",
        sizing="Shoulder height 1.75 m sits at 98% of this silhouette, giving 1.78 m to the top of the shoulder hump.",
        source=f"{WIKI}: White rhinoceros"),
    "elephant": dict(name="African bush elephant", h=3.45,
        fact="A bull African bush elephant averages 3.2 m at the shoulder and 6 tonnes; cows average 2.6 m.",
        sizing="Bull shoulder height 3.2 m sits at 93% of this silhouette, giving 3.45 m to the top of the head.",
        source=f"{WIKI}: African bush elephant"),
    "giraffe": dict(name="Giraffe", h=5.0,
        fact="Fully grown giraffes stand 4.3–5.7 m tall; males average about 5.3 m, females about 4.5 m.",
        sizing="Total height is quoted directly: 5.0 m for a typical adult, measured to the horn tips.",
        source=f"{WIKI}: Giraffe"),
    # ---------------- Northern Forest ----------------
    "fox": dict(name="Red fox", h=0.65,
        fact="Red foxes stand 35–50 cm at the shoulder, with a 45–90 cm body and a 30–55 cm tail.",
        sizing="Shoulder height 40 cm sits at 62% of this silhouette, giving 65 cm to the ear tips.",
        source=f"{WIKI}: Red fox"),
    "lynx": dict(name="Eurasian lynx", h=0.84,
        fact="The Eurasian lynx stands 55–75 cm at the shoulder, with a body 73–106 cm long.",
        sizing="Shoulder height 65 cm sits at 77% of this silhouette, giving 84 cm to the ear tufts.",
        source=f"{WIKI}: Eurasian lynx"),
    "wolf": dict(name="Grey wolf", h=1.00,
        fact="Grey wolves stand 80–85 cm at the shoulder and run 105–160 cm from nose to rump.",
        sizing="Shoulder height 82 cm sits at 82% of this silhouette, giving 1.0 m to the ear tips.",
        source=f"{WIKI}: Wolf"),
    "bear": dict(name="Brown bear", h=1.20,
        fact="On all fours, brown bears stand about 1–1.5 m at the shoulder; the largest coastal bears fill the top of that range.",
        sizing="The shoulder hump, 1.2 m for a large adult, is the highest point of this silhouette.",
        source=f"{WIKI}: Brown bear"),
    "reindeer": dict(name="Reindeer", h=1.50,
        fact="Reindeer stand 85–150 cm at the shoulder, and both sexes grow antlers.",
        sizing="Shoulder height 1.1 m sits at 73% of this silhouette, giving 1.5 m to the antler tips.",
        source="Wikipedia: Reindeer; Dimensions.com reindeer size guide"),
    "reddeer": dict(name="Red deer stag", h=1.97,
        fact="Red deer stags stand 95–130 cm at the shoulder and carry antlers around 71 cm long.",
        sizing="Shoulder height 1.2 m sits at 61% of this silhouette, giving 1.97 m to the antler tips.",
        source=f"{WIKI}: Red deer"),
    "moose": dict(name="Moose", h=2.20,
        fact="Moose stand 1.4–2.1 m at the shoulder; a mature bull's antlers spread 1.2–1.5 m.",
        sizing="Bull shoulder height 1.8 m sits at 82% of this silhouette, giving 2.2 m to the top of the antlers.",
        source=f"{WIKI}: Moose"),
    # ---------------- Rodents & Co. ----------------
    "mouse": dict(name="House mouse", h=0.065,
        fact="A house mouse's head and body are 7.5–10 cm long, with a tail of 5–10 cm.",
        sizing="Head-body length 8.5 cm spans about 75% of this silhouette's width, so the whole silhouette, tail included, is about 6.5 cm tall.",
        source=f"{WIKI}: House mouse"),
    "rat": dict(name="Brown rat", h=0.13,
        fact="Brown rats have a 15–28 cm body and a tail slightly shorter than that.",
        sizing="Head-body length 22 cm spans about 65% of this silhouette's width, giving about 13 cm to the top of the raised head.",
        source=f"{WIKI}: Brown rat"),
    "guineapig": dict(name="Guinea pig", h=0.11,
        fact="Guinea pigs are 20–25 cm long and weigh 0.7–1.2 kg.",
        sizing="Body length 22.5 cm equals this silhouette's width, giving 11 cm tall.",
        source=f"{WIKI}: Guinea pig"),
    "squirrel": dict(name="Red squirrel", h=0.25,
        fact="A red squirrel's head and body are 19–23 cm, with a 15–20 cm tail.",
        sizing="Sitting up, the head reaches about 17 cm, which is 68% of this silhouette, giving 25 cm to the top of the tail.",
        source=f"{WIKI}: Red squirrel"),
    "hedgehog": dict(name="European hedgehog", h=0.11,
        fact="Adult European hedgehogs reach about 26 cm long and weigh around 800 g in summer.",
        sizing="Body length 26 cm equals this silhouette's width, giving about 11 cm tall.",
        source=f"{WIKI}: European hedgehog"),
    "beaver": dict(name="North American beaver", h=0.45,
        fact="A beaver's head and body are 74–90 cm long, plus a 20–35 cm flat tail.",
        sizing="Nose-to-tail length of about 1.05 m equals this silhouette's width, giving 45 cm to the top of the head.",
        source=f"{WIKI}: North American beaver"),
    "capybara": dict(name="Capybara", h=0.65,
        fact="Capybaras stand 50–62 cm at the withers with a 106–134 cm body, the largest rodent alive.",
        sizing="Withers height 56 cm sits at 92% of this silhouette, giving about 65 cm to the ears (checked against body length).",
        source=f"{WIKI}: Capybara"),
}

# Typical adult mass in kg, matching the adult each silhouette depicts, with the Wikipedia figure it came from.
WEIGHTS = {
    "cat":       (4.5,  "adult domestic cats typically weigh 4–5 kg", None),
    "rabbit":    (2.0,  "European rabbits weigh 1.5–3 kg", None),
    "dog":       (30,   "Labrador males weigh 29–36 kg, females 25–32 kg", None),
    "sheep":     (70,   "ewes weigh 45–100 kg depending on breed", None),
    "pig":       (220,  "adult domestic pigs weigh 140–300 kg", None),
    "cow":       (725,  "a mature Holstein cow weighs 680–770 kg", None),
    "horse":     (480,  "light riding horses weigh 380–550 kg", None),
    "lion":      (190,  "male lions weigh 160–225 kg by region", None),
    "zebra":     (250,  "plains zebra males weigh 220–322 kg", None),
    "hippo":     (1480, "bull hippos average 1.48 tonnes", "hippopotamuses"),
    "rhino":     (2150, "white rhino bulls weigh 2,000–2,300 kg", "white rhinoceroses"),
    "elephant":  (6000, "bull African bush elephants average 6 tonnes", None),
    "giraffe":   (1000, "adult giraffes average 1,192 kg (male) and 828 kg (female)", None),
    "fox":       (6,    "red foxes weigh 2.2–14 kg, typically about 6 kg", "red foxes"),
    "lynx":      (20,   "Eurasian lynx weigh 12–32 kg in Russia, 7–26 kg in the west", "Eurasian lynxes"),
    "wolf":      (40,   "grey wolves average 40 kg", "grey wolves"),
    "bear":      (220,  "male brown bears average 217 kg", None),
    "reindeer":  (150,  "bull reindeer weigh roughly 150–180 kg", "reindeer"),
    "reddeer":   (200,  "red deer stags weigh 160–240 kg", None),
    "moose":     (500,  "bull moose weigh 380–700 kg", "moose"),
    "mouse":     (0.02, "house mice weigh 11–30 g", "house mice"),
    "rat":       (0.3,  "wild brown rats commonly weigh under 300 g; the range is 140–500 g", None),
    "guineapig": (1.0,  "guinea pigs weigh 0.7–1.2 kg", None),
    "squirrel":  (0.3,  "red squirrels weigh 250–340 g", None),
    "hedgehog":  (0.8,  "adult European hedgehogs weigh about 800 g in summer", None),
    "beaver":    (20,   "North American beavers typically weigh 20 kg", None),
    "capybara":  (49,   "capybaras weigh 35–66 kg, averaging about 49 kg", None),
}
for _k, (_kg, _note, _plural) in WEIGHTS.items():
    ANIMALS[_k]["kg"] = _kg
    ANIMALS[_k]["kgNote"] = _note
    if _plural: ANIMALS[_k]["plural"] = _plural
assert set(WEIGHTS) == set(ANIMALS), set(WEIGHTS) ^ set(ANIMALS)

SETS = [
    dict(id="farm", name="Farm & Home", blurb="Cat, rabbit, Labrador, sheep, pig, cow, horse. Five are picked each game.",
         members=["cat", "rabbit", "dog", "sheep", "pig", "cow", "horse"]),
    dict(id="savanna", name="African Savanna", blurb="Lion, zebra, hippo, rhino, elephant, giraffe. Five are picked each game.",
         members=["lion", "zebra", "hippo", "rhino", "elephant", "giraffe"]),
    dict(id="forest", name="Northern Forest", blurb="Fox, lynx, wolf, brown bear, reindeer, red deer, moose. Five are picked each game.",
         members=["fox", "lynx", "wolf", "bear", "reindeer", "reddeer", "moose"]),
    dict(id="rodents", name="Rodents & Co.", blurb="Mouse, rat, guinea pig, squirrel, hedgehog, beaver, capybara. Five are picked each game.",
         members=["mouse", "rat", "guineapig", "squirrel", "hedgehog", "beaver", "capybara"]),
]

data = {
    "human": record("human"),
    "animals": {k: record(k, v) for k, v in ANIMALS.items()},
    "sets": SETS,
}
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read().replace("/*__DATA__*/", payload)

out = os.path.join(OUT_DIR, OUT_NAME)
open(out, "w", encoding="utf-8", newline=chr(10)).write(html)
print(f"wrote {out} ({os.path.getsize(out)/1024:.0f} KB), {len(ANIMALS)} animals in {len(SETS)} sets")
for k, v in ANIMALS.items():
    b = bbox[k]; print(f"  {k:10s} {v['name']:24s} h={v['h']:5.2f} m  w={v['h']*b['w']/b['h']:5.2f} m")
