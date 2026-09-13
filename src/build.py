"""Assemble index.html from template.html, the chosen PhyloPic SVGs and the size table below.

Sizing method (per animal): take the best-documented real-world dimension (usually shoulder height,
for small mammals body length), find where that dimension sits in the silhouette (fraction of the
silhouette's bounding box, read off the measurement sheets), and scale so the silhouette matches.
`h` is the resulting height of the silhouette's highest point in metres - the value players are scored on.
"""
import json, re, os, shutil

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
    # ---------------- Jungle & Rainforest ----------------
    "tiger": dict(name="Tiger", h=1.15,
        fact="A Bengal tiger is 1.7–1.9 m in head and body and stands about 1 m at the shoulder, the largest cat alive.",
        sizing="Shoulder height 1.0 m sits at 88% of this silhouette, giving 1.15 m to the top of the head.",
        source=f"{WIKI}: Tiger"),
    "leopard": dict(name="Leopard", h=0.76,
        fact="Leopards stand 60–70 cm at the shoulder and haul kills heavier than themselves up into trees.",
        sizing="Shoulder height 65 cm sits at 85% of this silhouette, giving 76 cm to the raised head.",
        source=f"{WIKI}: Leopard"),
    "jaguar": dict(name="Jaguar", h=0.88,
        fact="Jaguars stand 68–75 cm at the shoulder, the heaviest cat in the Americas and the one with the strongest bite.",
        sizing="Shoulder height 72 cm sits at 82% of this silhouette; the raised tail tops it out at 88 cm.",
        source=f"{WIKI}: Jaguar"),
    "gorilla": dict(name="Western gorilla", h=1.30,
        fact="A silverback stands 1.4–1.65 m upright and weighs as much as two men, but travels on his knuckles.",
        sizing="Upright he would be 1.55 m; folded into this knuckle-walking stance the crown of his head, the highest point here, is about 1.3 m up.",
        source=f"{WIKI}: Western gorilla"),
    "chimp": dict(name="Chimpanzee", h=1.00,
        fact="Chimpanzees stand 1.0–1.5 m upright; males weigh 40–70 kg.",
        sizing="The head, the highest point of this knuckle-walking silhouette, is about 1.0 m up — the low end of the upright height quoted for an adult.",
        source=f"{WIKI}: Chimpanzee"),
    "orangutan": dict(name="Bornean orangutan", h=1.05, plural="orangutans",
        fact="A flanged male Bornean orangutan stands about 1.2–1.4 m, and his arm span is wider than he is tall.",
        sizing="Standing height 1.37 m drops to about 1.05 m at the shoulders in this four-legged stance, the silhouette's highest point.",
        source=f"{WIKI}: Bornean orangutan"),
    # ---------------- Australia ----------------
    "kangaroo": dict(name="Red kangaroo", h=1.60,
        fact="A big male red kangaroo stands 1.5–1.8 m propped on his toes and tail, and crosses 8 m in one hop.",
        sizing="Standing height is quoted directly: 1.6 m for a large male, measured to the ear tips of this upright silhouette.",
        source=f"{WIKI}: Red kangaroo"),
    "koala": dict(name="Koala", h=0.75,
        fact="Koalas are 60–85 cm long and sleep up to 20 hours a day wedged in the fork of a gum tree.",
        sizing="Head-and-body length 72 cm runs nearly the full height of this silhouette, a koala sitting upright against a trunk.",
        source=f"{WIKI}: Koala"),
    "wombat": dict(name="Common wombat", h=0.42,
        fact="Common wombats are about 1 m long, dig burrows 20 m deep, and leave cube-shaped droppings.",
        sizing="Shoulder height 40 cm sits at 96% of this silhouette, giving 42 cm over the arched back.",
        source=f"{WIKI}: Common wombat"),
    "tasdevil": dict(name="Tasmanian devil", h=0.33, plural="Tasmanian devils",
        fact="The Tasmanian devil is the largest carnivorous marsupial: 57–65 cm of body, a 25 cm tail, and pound for pound the strongest bite of any mammal.",
        sizing="Shoulder height 30 cm sits at 92% of this silhouette, giving 33 cm to the top of the head.",
        source=f"{WIKI}: Tasmanian devil"),
    "emu": dict(name="Emu", h=1.75,
        fact="Emus stand 1.5–1.9 m tall, the second-tallest bird alive, and run at 48 km/h.",
        sizing="Standing height is quoted directly: 1.75 m for an adult, measured to the top of the head.",
        source=f"{WIKI}: Emu"),
    "platypus": dict(name="Platypus", h=0.20, plural="platypuses",
        fact="A platypus is 40–50 cm from bill to tail, lays eggs, and the males carry a venomous spur.",
        sizing="Nose-to-tail length 45 cm equals this silhouette's width, giving about 20 cm to the top of the head.",
        source=f"{WIKI}: Platypus"),
    # ---------------- Birds ----------------
    "ostrich": dict(name="Common ostrich", h=2.10, plural="ostriches",
        fact="Male ostriches stand 2.1–2.8 m tall, lay the largest egg of any living bird and run at 70 km/h.",
        sizing="Standing height is quoted directly: 2.1 m for a male, measured to the top of the head.",
        source=f"{WIKI}: Common ostrich"),
    "penguin": dict(name="Emperor penguin", h=1.15,
        fact="Emperor penguins stand about 1.15 m tall, the largest penguin alive, and dive deeper than 500 m.",
        sizing="Standing height is quoted directly: 1.15 m, measured to the top of the head.",
        source=f"{WIKI}: Emperor penguin"),
    "swan": dict(name="Mute swan", h=1.10,
        fact="Mute swans are 1.4–1.6 m from bill to tail and are among the heaviest birds that still fly.",
        sizing="Bill-to-tail length 1.5 m equals this swimming silhouette's width, putting the head about 1.1 m above the keel.",
        source=f"{WIKI}: Mute swan"),
    "chicken": dict(name="Chicken", h=0.42,
        fact="A laying hen stands about 40 cm tall; there are more chickens on earth than all other birds put together.",
        sizing="Standing height is quoted directly: 42 cm to the top of the comb.",
        source=f"{WIKI}: Chicken"),
    "eagle": dict(name="Golden eagle", h=0.85,
        fact="Golden eagles are 66–102 cm from bill to tail and span 1.8–2.3 m across the wings.",
        sizing="Bill-to-tail length 85 cm runs the full height of this perched silhouette.",
        source=f"{WIKI}: Golden eagle"),
    "flamingo": dict(name="Greater flamingo", h=1.25,
        fact="Greater flamingos stand 1.1–1.5 m tall but weigh only 2–4 kg — nearly all of it leg and neck.",
        sizing="Standing height is quoted directly: 1.25 m to the top of the head.",
        source=f"{WIKI}: Greater flamingo"),
    # ---------------- Polar & Ice ----------------
    "polarbear": dict(name="Polar bear", h=1.35,
        fact="A male polar bear stands about 1.3 m at the shoulder, measures 2.4–3 m nose to tail, and is the largest land carnivore.",
        sizing="Shoulder height 1.3 m sits at 97% of this silhouette, the shoulder hump being its highest point.",
        source=f"{WIKI}: Polar bear"),
    "walrus": dict(name="Walrus", h=1.60, plural="walruses",
        fact="A Pacific bull walrus is 3–3.6 m long and carries tusks up to a metre.",
        sizing="Propped on his fore-flippers as here, a 3.2 m bull holds his head about 1.6 m up, which lays 2.75 m of him along the ice.",
        source=f"{WIKI}: Walrus"),
    "seal": dict(name="Harp seal", h=0.65,
        fact="Harp seals are 1.7–1.9 m long; their pups are born on the ice and weaned in twelve days.",
        sizing="Nose-to-tail length 1.8 m equals this silhouette's width, putting the raised head about 65 cm up.",
        source=f"{WIKI}: Harp seal"),
    "arcticfox": dict(name="Arctic fox", h=0.37, plural="Arctic foxes",
        fact="Arctic foxes stand about 30 cm at the shoulder and stay warm at −50 °C in the deepest fur of any mammal.",
        sizing="Shoulder height 30 cm sits at 82% of this silhouette, giving 37 cm to the ear tips.",
        source=f"{WIKI}: Arctic fox"),
    "muskox": dict(name="Muskox", h=1.30, plural="muskoxen",
        fact="Muskoxen stand 1.1–1.5 m at the shoulder under a coat that hangs almost to the ground.",
        sizing="Shoulder height 1.3 m is the top of this silhouette's humped shoulder, its highest point.",
        source=f"{WIKI}: Muskox"),
    "wolverine": dict(name="Wolverine", h=0.40,
        fact="Wolverines are 65–107 cm long and stand 36–45 cm at the shoulder, yet drive bears off a carcass.",
        sizing="Shoulder height 38 cm sits at 96% of this silhouette's back, giving about 40 cm overall.",
        source=f"{WIKI}: Wolverine"),
    # ---------------- Asia ----------------
    "camel": dict(name="Dromedary camel", h=2.15,
        fact="Dromedaries stand 1.8–2 m at the shoulder; the hump, which stores fat and not water, adds another 20 cm.",
        sizing="Shoulder height 1.9 m sits at 88% of this silhouette, putting the top of the hump at 2.15 m.",
        source=f"{WIKI}: Dromedary"),
    "asianelephant": dict(name="Asian elephant", h=2.85, plural="Asian elephants",
        fact="Asian bulls stand 2.4–3 m at the shoulder and weigh about 4 tonnes — smaller than their African cousins, with smaller ears.",
        sizing="Bull shoulder height 2.75 m sits at 96% of this silhouette, giving 2.85 m to the domed top of the head.",
        source=f"{WIKI}: Asian elephant"),
    "panda": dict(name="Giant panda", h=0.85,
        fact="Giant pandas are 1.2–1.9 m long, stand 60–90 cm at the shoulder, and spend 12 hours a day eating bamboo.",
        sizing="Shoulder height 80 cm sits at 95% of this silhouette, giving 85 cm over the back.",
        source=f"{WIKI}: Giant panda"),
    "waterbuffalo": dict(name="Wild water buffalo", h=1.75, plural="water buffalo",
        fact="Wild water buffalo stand 1.5–1.9 m at the shoulder and carry the widest horns of any bovid, up to 2 m tip to tip.",
        sizing="Shoulder height 1.65 m sits at 95% of this silhouette, giving 1.75 m over the shoulder.",
        source=f"{WIKI}: Wild water buffalo"),
    "snowleopard": dict(name="Snow leopard", h=0.60,
        fact="Snow leopards stand about 56 cm at the shoulder and carry a tail nearly as long as their body to balance on cliffs.",
        sizing="Shoulder height 56 cm sits at 95% of this silhouette, giving about 60 cm to the top of the head.",
        source=f"{WIKI}: Snow leopard"),
    "redpanda": dict(name="Red panda", h=0.32,
        fact="Red pandas are 51–63 cm in head and body with a tail nearly as long again, and are no relation to the giant panda.",
        sizing="Shoulder height 28 cm sits at 88% of this silhouette, giving about 32 cm to the top of the head.",
        source=f"{WIKI}: Red panda"),
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
    "tiger":     (220,  "Bengal tiger males weigh 180–260 kg", None),
    "leopard":   (60,   "male leopards weigh 37–90 kg", None),
    "jaguar":    (85,   "male jaguars weigh 56–96 kg, more in the Pantanal", None),
    "gorilla":   (160,  "silverback western gorillas weigh 145–191 kg", None),
    "chimp":     (50,   "male chimpanzees weigh 40–70 kg", None),
    "orangutan": (75,   "flanged male Bornean orangutans weigh 50–100 kg", None),
    "kangaroo":  (66,   "male red kangaroos weigh 55–90 kg", None),
    "koala":     (10,   "koalas weigh 4–15 kg, the southern ones heaviest", None),
    "wombat":    (26,   "common wombats weigh 20–35 kg", None),
    "tasdevil":  (8,    "male Tasmanian devils weigh about 8 kg", None),
    "emu":       (35,   "emus weigh 18–60 kg, typically about 35 kg", None),
    "platypus":  (1.7,  "platypuses weigh 0.7–2.4 kg", None),
    "ostrich":   (110,  "male ostriches weigh 100–130 kg", None),
    "penguin":   (30,   "emperor penguins weigh 22–45 kg", None),
    "swan":      (11,   "mute swan cobs weigh 10–12 kg", None),
    "chicken":   (2.2,  "laying hens weigh 1.8–2.7 kg", None),
    "eagle":     (4.5,  "female golden eagles weigh 3.6–6.7 kg, males 2.5–4.5 kg", None),
    "flamingo":  (3,    "greater flamingos weigh 2–4 kg", None),
    "polarbear": (450,  "male polar bears weigh 350–700 kg", None),
    "walrus":    (1200, "Pacific bull walruses weigh 800–1,700 kg", None),
    "seal":      (130,  "harp seals weigh 130–140 kg", None),
    "arcticfox": (3.5,  "arctic foxes weigh 3–3.5 kg", None),
    "muskox":    (285,  "muskox bulls average 285 kg", None),
    "wolverine": (14,   "male wolverines weigh 11–18 kg", None),
    "camel":     (500,  "male dromedaries weigh 400–690 kg", None),
    "asianelephant": (4000, "Asian bull elephants average 4 tonnes", None),
    "panda":     (110,  "male giant pandas weigh 100–115 kg", None),
    "waterbuffalo": (900, "wild water buffalo weigh 700–1,200 kg", None),
    "snowleopard": (40, "snow leopards weigh 22–55 kg", None),
    "redpanda":  (5,    "red pandas weigh 3.2–15 kg, typically about 5 kg", None),
}
for _k, (_kg, _note, _plural) in WEIGHTS.items():
    ANIMALS[_k]["kg"] = _kg
    ANIMALS[_k]["kgNote"] = _note
    if _plural: ANIMALS[_k]["plural"] = _plural
assert set(WEIGHTS) == set(ANIMALS), set(WEIGHTS) ^ set(ANIMALS)

SETS = [
    dict(id="farm", name="Farm & Home", blurb="Cat, rabbit, Labrador, chicken, sheep, pig, cow, horse. Five are picked each game.",
         members=["cat", "rabbit", "dog", "chicken", "sheep", "pig", "cow", "horse"]),
    dict(id="savanna", name="African Savanna", blurb="Lion, zebra, hippo, rhino, elephant, giraffe. Five are picked each game.",
         members=["lion", "zebra", "hippo", "rhino", "elephant", "giraffe"]),
    dict(id="forest", name="Northern Forest", blurb="Fox, lynx, wolf, brown bear, reindeer, red deer, moose. Five are picked each game.",
         members=["fox", "lynx", "wolf", "bear", "reindeer", "reddeer", "moose"]),
    dict(id="rodents", name="Rodents & Co.", blurb="Mouse, rat, guinea pig, squirrel, hedgehog, beaver, capybara. Five are picked each game.",
         members=["mouse", "rat", "guineapig", "squirrel", "hedgehog", "beaver", "capybara"]),
    dict(id="jungle", name="Jungle & Rainforest", blurb="Tiger, leopard, jaguar, gorilla, chimpanzee, orangutan. Five are picked each game.",
         members=["tiger", "leopard", "jaguar", "gorilla", "chimp", "orangutan"]),
    dict(id="australia", name="Australia", blurb="Red kangaroo, koala, wombat, Tasmanian devil, emu, platypus. Five are picked each game.",
         members=["kangaroo", "koala", "wombat", "tasdevil", "emu", "platypus"]),
    dict(id="birds", name="Birds", blurb="Ostrich, emperor penguin, mute swan, chicken, golden eagle, flamingo. Five are picked each game.",
         members=["ostrich", "penguin", "swan", "chicken", "eagle", "flamingo"]),
    dict(id="polar", name="Polar & Ice", blurb="Polar bear, walrus, harp seal, arctic fox, muskox, wolverine. Five are picked each game.",
         members=["polarbear", "walrus", "seal", "arcticfox", "muskox", "wolverine"]),
    dict(id="asia", name="Asia", blurb="Dromedary camel, Asian elephant, giant panda, water buffalo, snow leopard, red panda. Five are picked each game.",
         members=["camel", "asianelephant", "panda", "waterbuffalo", "snowleopard", "redpanda"]),
]
for _s in SETS:
    assert all(m in ANIMALS for m in _s["members"]), _s["id"]

# Loads for the balance-log game. Everything on one log shares a scale and a weight range, so the
# round is a torque puzzle rather than a single elephant surrounded by dust. `tier` is how heavy the
# load is: the five rounds work up through tiers 0 to 4, one load drawn at random from each tier, so
# round 1 is always the hedgerow sort of thing and round 5 the heavyweights.
LOG_SETS = [
    dict(id="hedgerow", tier=0, name="Hedgerow", blurb="Rat, squirrel, hedgehog, guinea pig, rabbit, cat.",
         members=["rat", "squirrel", "hedgehog", "guineapig", "rabbit", "cat"]),
    dict(id="aviary", tier=0, name="Aviary", blurb="Chicken, flamingo, golden eagle, mute swan.",
         members=["chicken", "flamingo", "eagle", "swan"]),
    dict(id="riverbank", tier=1, name="Riverbank", blurb="Cat, fox, beaver, lynx, Labrador, capybara.",
         members=["cat", "fox", "beaver", "lynx", "dog", "capybara"]),
    dict(id="snowline", tier=1, name="Snowline", blurb="Arctic fox, red panda, wolverine, emperor penguin, snow leopard.",
         members=["arcticfox", "redpanda", "wolverine", "penguin", "snowleopard"]),
    dict(id="outback", tier=1, name="Outback", blurb="Tasmanian devil, koala, wombat, emu, red kangaroo.",
         members=["tasdevil", "koala", "wombat", "emu", "kangaroo"]),
    dict(id="pasture", tier=2, name="Pasture", blurb="Wolf, sheep, reindeer, lion, brown bear, pig.",
         members=["wolf", "sheep", "reindeer", "lion", "bear", "pig"]),
    dict(id="canopy", tier=2, name="Canopy", blurb="Snow leopard, chimpanzee, leopard, orangutan, jaguar, giant panda, gorilla.",
         members=["snowleopard", "chimp", "leopard", "orangutan", "jaguar", "panda", "gorilla"]),
    dict(id="highland", tier=3, name="Highland", blurb="Red deer, zebra, horse, moose, Holstein cow.",
         members=["reddeer", "zebra", "horse", "moose", "cow"]),
    dict(id="packice", tier=3, name="Pack Ice", blurb="Harp seal, muskox, polar bear, walrus.",
         members=["seal", "muskox", "polarbear", "walrus"]),
    dict(id="heavyweights", tier=4, name="Heavyweights", blurb="Cow, giraffe, hippo, rhino, elephant.",
         members=["cow", "giraffe", "hippo", "rhino", "elephant"]),
    dict(id="asiangiants", tier=4, name="Asian Giants", blurb="Tiger, dromedary camel, water buffalo, Asian elephant.",
         members=["tiger", "camel", "waterbuffalo", "asianelephant"]),
]
for _s in LOG_SETS:
    assert all(m in ANIMALS for m in _s["members"]), _s["id"]
assert sorted({_s["tier"] for _s in LOG_SETS}) == list(range(5)), "every round needs a tier of loads"

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
print(f"wrote {out} ({os.path.getsize(out)/1024:.0f} KB), {len(ANIMALS)} animals in {len(SETS)} sets and {len(LOG_SETS)} loads")
for k, v in ANIMALS.items():
    b = bbox[k]; print(f"  {k:10s} {v['name']:24s} h={v['h']:5.2f} m  w={v['h']*b['w']/b['h']:5.2f} m")
