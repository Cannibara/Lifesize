"""Download candidate silhouettes from PhyloPic for every species in the roster below.

The roster is the library the three games share, and it is deliberately longer than what is
wired up: a species here is a candidate, and only becomes an animal in the game once someone
picks one of its silhouettes into src/choices.json, measures it with src/tools/measure.html and
gives it a size, a weight and a fact in src/build.py. Run this from anywhere:

    python src/fetch_phylo.py

It writes up to eight candidates per species into src/phylo/ and a catalogue of everything it
found into src/phylo/catalog.json, then lists which species are still waiting to be chosen.
"""
import json, urllib.request, urllib.parse, os, time, sys, re

API = "https://api.phylopic.org"
BUILD = 553
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "phylo")
os.makedirs(OUT, exist_ok=True)

def get(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "size-guess-game/0.1"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            time.sleep(1.5)
            err = e
    raise err

def getj(path):
    return json.loads(get(API + path).decode("utf-8"))

# key: (common name, scientific name). Grouped the way the lineup sets are grouped; a set wants
# seven or eight members so that the five it shows are a different five next time.
species = {
  # ---- Farm & Home ----
  "cat": ("Domestic cat", "Felis catus"),
  "rabbit": ("European rabbit", "Oryctolagus cuniculus"),
  "dog": ("Domestic dog", "Canis familiaris"),
  "sheep": ("Sheep", "Ovis aries"),
  "goat": ("Goat", "Capra hircus"),
  "horse": ("Horse", "Equus caballus"),
  "donkey": ("Donkey", "Equus asinus"),
  "pig": ("Domestic pig", "Sus domesticus"),
  "cow": ("Cattle", "Bos taurus"),
  "chicken": ("Chicken", "Gallus gallus"),
  # ---- African Savanna ----
  "lion": ("Lion", "Panthera leo"),
  "cheetah": ("Cheetah", "Acinonyx jubatus"),
  "zebra": ("Plains zebra", "Equus quagga"),
  "wildebeest": ("Blue wildebeest", "Connochaetes taurinus"),
  "buffalo": ("African buffalo", "Syncerus caffer"),
  "warthog": ("Common warthog", "Phacochoerus africanus"),
  "ostrich": ("Common ostrich", "Struthio camelus"),
  "hippo": ("Hippopotamus", "Hippopotamus amphibius"),
  "elephant": ("African bush elephant", "Loxodonta africana"),
  "giraffe": ("Giraffe", "Giraffa camelopardalis"),
  "rhino": ("White rhinoceros", "Ceratotherium simum"),
  # ---- Northern Forest ----
  "fox": ("Red fox", "Vulpes vulpes"),
  "badger": ("European badger", "Meles meles"),
  "otter": ("European otter", "Lutra lutra"),
  "raccoon": ("Raccoon", "Procyon lotor"),
  "wolf": ("Grey wolf", "Canis lupus"),
  "lynx": ("Eurasian lynx", "Lynx lynx"),
  "boar": ("Wild boar", "Sus scrofa"),
  "bear": ("Brown bear", "Ursus arctos"),
  "moose": ("Moose", "Alces alces"),
  "reindeer": ("Reindeer", "Rangifer tarandus"),
  "reddeer": ("Red deer", "Cervus elaphus"),
  # ---- Asia ----
  "tiger": ("Tiger", "Panthera tigris"),
  "snowleopard": ("Snow leopard", "Panthera uncia"),
  "panda": ("Giant panda", "Ailuropoda melanoleuca"),
  "orangutan": ("Bornean orangutan", "Pongo pygmaeus"),
  "camel": ("Dromedary", "Camelus dromedarius"),
  "waterbuffalo": ("Water buffalo", "Bubalus bubalis"),
  "yak": ("Domestic yak", "Bos grunniens"),
  "gorilla": ("Western gorilla", "Gorilla gorilla"),
  # ---- Australia ----
  "kangaroo": ("Red kangaroo", "Osphranter rufus"),
  "koala": ("Koala", "Phascolarctos cinereus"),
  "wombat": ("Common wombat", "Vombatus ursinus"),
  "emu": ("Emu", "Dromaius novaehollandiae"),
  "platypus": ("Platypus", "Ornithorhynchus anatinus"),
  # ---- Ice & Coast ----
  "polarbear": ("Polar bear", "Ursus maritimus"),
  "walrus": ("Walrus", "Odobenus rosmarus"),
  "penguin": ("Emperor penguin", "Aptenodytes forsteri"),
  "muskox": ("Muskox", "Ovibos moschatus"),
  # ---- Rodents & Co. ----
  "mouse": ("House mouse", "Mus musculus"),
  "rat": ("Brown rat", "Rattus norvegicus"),
  "hamster": ("Golden hamster", "Mesocricetus auratus"),
  "guineapig": ("Guinea pig", "Cavia porcellus"),
  "chipmunk": ("Eastern chipmunk", "Tamias striatus"),
  "squirrel": ("Red squirrel", "Sciurus vulgaris"),
  "greysquirrel": ("Eastern grey squirrel", "Sciurus carolinensis"),
  "hedgehog": ("European hedgehog", "Erinaceus europaeus"),
  "mole": ("European mole", "Talpa europaea"),
  "porcupine": ("Crested porcupine", "Hystrix cristata"),
  "skunk": ("Striped skunk", "Mephitis mephitis"),
  "meerkat": ("Meerkat", "Suricata suricatta"),
  "beaver": ("North American beaver", "Castor canadensis"),
  "eurbeaver": ("Eurasian beaver", "Castor fiber"),
  "capybara": ("Capybara", "Hydrochoerus hydrochaeris"),
  # ---- the player ----
  "human": ("Human", "Homo sapiens"),
}

result = {}
for key, (common, sci) in species.items():
    q = urllib.parse.quote(sci.lower())
    try:
        nodes = getj(f"/nodes?build={BUILD}&filter_name={q}&page=0")
    except Exception as e:
        print(key, "node lookup failed", e); result[key] = {"common": common, "sci": sci, "error": str(e)}; continue
    items = nodes.get("_links", {}).get("items", [])
    if not items:
        # try autocomplete for close name
        ac = getj(f"/autocomplete?build={BUILD}&query={urllib.parse.quote(sci.split()[0].lower())}")
        print(key, "NO NODE for", sci, "autocomplete:", ac.get("matches", [])[:8])
        result[key] = {"common": common, "sci": sci, "error": "no node"}; continue
    # prefer exact title match
    node = None
    for it in items:
        if it["title"].lower() == sci.lower():
            node = it; break
    node = node or items[0]
    uuid = re.search(r"/nodes/([0-9a-f-]+)", node["href"]).group(1)
    imgs = []
    page = 0
    while True:
        try:
            lst = getj(f"/images?build={BUILD}&filter_clade={uuid}&page={page}&embed_items=true")
        except Exception as e:
            break
        emb = lst.get("_embedded", {}).get("items", [])
        for im in emb:
            L = im["_links"]
            iu = re.search(r"/images/([0-9a-f-]+)", L["self"]["href"]).group(1)
            imgs.append({
                "uuid": iu,
                "title": L["self"].get("title"),
                "license": L["license"]["href"],
                "contributor": L.get("contributor", {}).get("title"),
                "attribution": im.get("attribution"),
                "vector": L["vectorFile"]["href"],
                "sizes": L["vectorFile"].get("sizes"),
                "specific": L.get("specificNode", {}).get("title"),
            })
        if not lst.get("_links", {}).get("next") or page >= 1:
            break
        page += 1
    print(f"{key:14s} node={node['title']:35s} images={len(imgs)}")
    result[key] = {"common": common, "sci": sci, "node": node["title"], "node_uuid": uuid, "images": imgs}
    # download vectors (cap 8)
    for im in imgs[:8]:
        fn = os.path.join(OUT, f"{key}__{im['uuid']}.svg")
        if not os.path.exists(fn):
            try:
                data = get(im["vector"])
                open(fn, "wb").write(data)
            except Exception as e:
                print("  download failed", im["uuid"], e)
    time.sleep(0.3)

json.dump(result, open(os.path.join(OUT, "catalog.json"), "w"), indent=1)

# what is downloaded but not yet part of the game
chosen_path = os.path.join(HERE, "choices.json")
chosen = set(json.load(open(chosen_path))) if os.path.exists(chosen_path) else set()
waiting = [k for k in species if k not in chosen and result.get(k, {}).get("images")]
print(f"\ndone: {len(species)} species, {len(chosen)} already chosen into choices.json")
if waiting:
    print(f"{len(waiting)} still to pick a silhouette for: {', '.join(sorted(waiting))}")
    print("for each: choose one from src/phylo/, record it in src/choices.json, measure it with")
    print("src/tools/measure.html, then give it a size and weight in src/build.py.")
