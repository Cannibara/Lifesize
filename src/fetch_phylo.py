import json, urllib.request, urllib.parse, os, time, sys, re

API = "https://api.phylopic.org"
BUILD = 553
OUT = "phylo"
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

species = {
  # key: (common name, scientific name)
  "cat": ("Domestic cat", "Felis catus"),
  "rabbit": ("European rabbit", "Oryctolagus cuniculus"),
  "dog": ("Domestic dog", "Canis familiaris"),
  "sheep": ("Sheep", "Ovis aries"),
  "horse": ("Horse", "Equus caballus"),
  "pig": ("Domestic pig", "Sus domesticus"),
  "cow": ("Cattle", "Bos taurus"),
  "lion": ("Lion", "Panthera leo"),
  "zebra": ("Plains zebra", "Equus quagga"),
  "hippo": ("Hippopotamus", "Hippopotamus amphibius"),
  "elephant": ("African bush elephant", "Loxodonta africana"),
  "giraffe": ("Giraffe", "Giraffa camelopardalis"),
  "rhino": ("White rhinoceros", "Ceratotherium simum"),
  "fox": ("Red fox", "Vulpes vulpes"),
  "wolf": ("Grey wolf", "Canis lupus"),
  "bear": ("Brown bear", "Ursus arctos"),
  "moose": ("Moose", "Alces alces"),
  "reindeer": ("Reindeer", "Rangifer tarandus"),
  "reddeer": ("Red deer", "Cervus elaphus"),
  "lynx": ("Eurasian lynx", "Lynx lynx"),
  "mouse": ("House mouse", "Mus musculus"),
  "guineapig": ("Guinea pig", "Cavia porcellus"),
  "squirrel": ("Red squirrel", "Sciurus vulgaris"),
  "greysquirrel": ("Eastern grey squirrel", "Sciurus carolinensis"),
  "beaver": ("North American beaver", "Castor canadensis"),
  "eurbeaver": ("Eurasian beaver", "Castor fiber"),
  "capybara": ("Capybara", "Hydrochoerus hydrochaeris"),
  "rat": ("Brown rat", "Rattus norvegicus"),
  "hedgehog": ("European hedgehog", "Erinaceus europaeus"),
  "kangaroo": ("Red kangaroo", "Osphranter rufus"),
  "camel": ("Dromedary", "Camelus dromedarius"),
  "tiger": ("Tiger", "Panthera tigris"),
  "gorilla": ("Western gorilla", "Gorilla gorilla"),
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
print("done")
