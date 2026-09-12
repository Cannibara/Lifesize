"""The animal library — the one list all three games draw on.

This file is data, nothing else. To correct a figure or add an animal, this is the only file you
need to open; src/build.py reads it and does the assembling.

Each animal carries:

    name, plural   what the game calls it. plural is only needed when adding "s" would be wrong
    h              the height of the silhouette's highest point, in metres. This is the number
                   players are scored on, and it is stored, not calculated
    scale          the workings behind h, so it can be checked against the drawing later:
                     at    the landmark the height figure describes ("withers", "back", "ear tips")
                     h_m   that landmark's real height above the ground, in metres
                     h_f   where it sits in the drawing, as a fraction of the drawing's height
                     l_m   a real length (head-body, or muzzle-to-rump for a head-up pose), or None
                     l_f   the fraction of the drawing's width that length spans
                     how   "height"  h = h_m / h_f            - the height figure is the reliable one
                           "length"  h = l_m / (l_f * aspect) - sources quote only a body length
                           "mean"    both, split - the drawing is stylised enough that its height
                                     and its length cannot both be true
    kg, mass       the weight the games use, and the range its source gives. The build refuses to
                   run unless kg sits inside lo..hi, so a figure cannot drift from its source
    fact, sizing   shown to the player after a round
    source         where the real-world figures came from

h_f is the one figure here that cannot be looked up anywhere: it is a fact about this particular
drawing rather than about the animal. src/tools/audit_scale.py proposes it and draws it on the
silhouette so it can be confirmed by eye.
"""

ANIMALS = {
    # ---------------- Farm & Home ----------------
    "cat": dict(
        name="Domestic cat", h=0.45, kg=4.5,
        scale=dict(at="withers", h_m=0.24, h_f=0.6, l_m=0.46, l_f=0.76, how="mean"),
        mass=dict(lo=4, hi=5, note="adult domestic cats typically weigh 4–5 kg"),
        fact="An adult cat stands 23–25 cm at the shoulder and is about 46 cm long, not counting a 30 cm tail.",
        sizing="This cat is drawn long in the leg and short in the body: its 24 cm shoulder lands at 60% "
               "of the silhouette, its 46 cm body at three quarters of the width. Splitting the two puts "
               "the raised tail tip at 45 cm.",
        source="Wikipedia: Cat"),
    "rabbit": dict(
        name="European rabbit", h=0.25, kg=2,
        scale=dict(at="ear tips", h_m=0.25, h_f=1, l_m=0.3, l_f=1, how="height"),
        mass=dict(lo=1.5, hi=3, note="European rabbits weigh 1.5–3 kg"),
        fact="A European rabbit's head and body run 36–38 cm; its ears are 7–8 cm long.",
        sizing="A sitting rabbit stands about 25 cm to the ear tips, which is this silhouette's whole height.",
        source="Wikipedia: European rabbit"),
    "dog": dict(
        name="Labrador retriever", h=0.64, kg=30,
        scale=dict(at="withers", h_m=0.56, h_f=0.87, l_m=0.9, l_f=0.84, how="height"),
        mass=dict(lo=25, hi=36, note="Labrador males weigh 29–36 kg, females 25–32 kg"),
        fact="The breed standard puts a Labrador at 54–57 cm at the withers and 25–36 kg.",
        sizing="Withers height 56 cm sits at 87% of this silhouette, giving 64 cm to the ear tips.",
        source="Wikipedia: Labrador Retriever (Kennel Club standard)"),
    "sheep": dict(
        name="Sheep", h=0.81, kg=70,
        scale=dict(at="withers", h_m=0.7, h_f=0.865, l_m=1.1, l_f=0.94, how="height"),
        mass=dict(lo=45, hi=100, note="ewes weigh 45–100 kg depending on breed"),
        fact="Common breeds such as Texel and Suffolk stand roughly 65–80 cm at the withers under all "
             "that fleece.",
        sizing="Withers height 70 cm sits at 86% of this silhouette, giving 81 cm to the top of the head.",
        source="Texel and Awassi breed data (Wikipedia, FAO)"),
    "pig": dict(
        name="Domestic pig", h=0.84, kg=220,
        scale=dict(at="shoulder", h_m=0.8, h_f=0.95, l_m=1.6, l_f=0.94, how="height"),
        mass=dict(lo=140, hi=300, note="adult domestic pigs weigh 140–300 kg"),
        fact="A grown Large White pig stands 75–90 cm at the shoulder and weighs 140–300 kg.",
        sizing="Shoulder height 80 cm sits at 95% of this silhouette; the arched back reaches about 84 cm.",
        source="Large White breed references; Wikipedia: Domestic pig"),
    "cow": dict(
        name="Holstein cow", h=1.6, kg=725,
        scale=dict(at="withers", h_m=1.5, h_f=0.935, l_m=2.3, l_f=0.86, how="height"),
        mass=dict(lo=680, hi=770, note="a mature Holstein cow weighs 680–770 kg"),
        fact="A mature Holstein cow stands 145–165 cm at the shoulder and weighs 680–770 kg.",
        sizing="Withers height 150 cm sits at 93% of this silhouette, giving 1.6 m to the horns.",
        source="Wikipedia: Holstein Friesian"),
    "horse": dict(
        name="Horse", h=1.81, kg=480,
        scale=dict(at="withers", h_m=1.57, h_f=0.87, l_m=2.2, l_f=0.83, how="height"),
        mass=dict(lo=380, hi=550, note="light riding horses weigh 380–550 kg"),
        fact="Light riding horses measure 14–16 hands (142–163 cm) at the withers, the highest point "
             "of the back.",
        sizing="Withers height 157 cm (15.2 hands) sits at 87% of this silhouette, giving 1.81 m to the "
               "ear tips — this horse carries its head low.",
        source="Wikipedia: Horse"),
    # ---------------- African Savanna ----------------
    "lion": dict(
        name="Lion", h=1.47, kg=190,
        scale=dict(at="withers", h_m=1.1, h_f=0.75, l_m=1.9, l_f=0.85, how="height"),
        mass=dict(lo=160, hi=225, note="male lions weigh 160–225 kg by region"),
        fact="A male lion's head and body run 1.84–2.08 m, and he stands roughly 1.1 m at the shoulder.",
        sizing="Shoulder height 1.1 m sits at 75% of this silhouette, giving 1.47 m to the top of the mane.",
        source="Wikipedia: Lion"),
    "zebra": dict(
        name="Plains zebra", h=1.67, kg=250,
        scale=dict(at="withers", h_m=1.33, h_f=0.795, l_m=2, l_f=0.84, how="height"),
        mass=dict(lo=220, hi=322, note="plains zebra males weigh 220–322 kg"),
        fact="Plains zebras stand 127–140 cm at the shoulder, with a 2.2–2.5 m body.",
        sizing="Shoulder height 133 cm sits at 79% of this silhouette, giving 1.67 m to the ear tips.",
        source="Wikipedia: Plains zebra"),
    "hippo": dict(
        name="Hippopotamus", h=1.63, kg=1480, plural="hippopotamuses",
        scale=dict(at="withers", h_m=1.45, h_f=0.89, l_m=3.2, l_f=0.97, how="height"),
        mass=dict(lo=1480, hi=1480, note="bull hippos average 1.48 tonnes"),
        fact="A hippo stands about 1.4 m at the shoulder (bulls up to 1.65 m) and weighs around 1.5 tonnes.",
        sizing="Shoulder height 1.45 m sits at 89% of this silhouette, giving 1.63 m over the arch of "
               "the back.",
        source="Wikipedia: Hippopotamus"),
    "rhino": dict(
        name="White rhinoceros", h=1.77, kg=2150, plural="white rhinoceroses",
        scale=dict(at="withers", h_m=1.75, h_f=0.99, l_m=3.7, l_f=0.96, how="height"),
        mass=dict(lo=2000, hi=2300, note="white rhino bulls weigh 2,000–2,300 kg"),
        fact="White rhino bulls stand 1.7–1.86 m at the shoulder and weigh 2–2.3 tonnes.",
        sizing="Shoulder height 1.75 m sits at 99% of this silhouette, giving 1.77 m to the top of the "
               "shoulder hump.",
        source="Wikipedia: White rhinoceros"),
    "elephant": dict(
        name="African bush elephant", h=3.3, kg=6000,
        scale=dict(at="shoulder", h_m=3.2, h_f=0.97, l_m=None, l_f=None, how="height"),
        mass=dict(lo=6000, hi=6000, note="bull African bush elephants average 6 tonnes"),
        fact="A bull African bush elephant averages 3.2 m at the shoulder and 6 tonnes; cows average 2.6 m.",
        sizing="Bull shoulder height 3.2 m sits at 97% of this silhouette, giving 3.3 m to the highest "
               "point of the back.",
        source="Wikipedia: African bush elephant"),
    "giraffe": dict(
        name="Giraffe", h=5, kg=1000,
        scale=dict(at="horn tips", h_m=5, h_f=1, l_m=2.9, l_f=1, how="height"),
        mass=dict(lo=828, hi=1192, note="adult giraffes average 1,192 kg (male) and 828 kg (female)"),
        fact="Fully grown giraffes stand 4.3–5.7 m tall; males average about 5.3 m, females about 4.5 m.",
        sizing="Total height is quoted directly: 5.0 m for a typical adult, measured to the horn tips.",
        source="Wikipedia: Giraffe"),
    # ---------------- Northern Forest ----------------
    "fox": dict(
        name="Red fox", h=0.48, kg=6, plural="red foxes",
        scale=dict(at="withers", h_m=0.4, h_f=0.84, l_m=0.65, l_f=0.76, how="height"),
        mass=dict(lo=2.2, hi=14, note="red foxes weigh 2.2–14 kg, typically about 6 kg"),
        fact="Red foxes stand 35–50 cm at the shoulder, with a 45–90 cm body and a 30–55 cm tail.",
        sizing="Shoulder height 40 cm sits at 84% of this silhouette, giving 48 cm to the ear tips.",
        source="Wikipedia: Red fox"),
    "lynx": dict(
        name="Eurasian lynx", h=0.84, kg=20, plural="Eurasian lynxes",
        scale=dict(at="withers", h_m=0.65, h_f=0.77, l_m=0.95, l_f=0.82, how="height"),
        mass=dict(lo=7, hi=32, note="Eurasian lynx weigh 12–32 kg in Russia, 7–26 kg in the west"),
        fact="The Eurasian lynx stands 55–75 cm at the shoulder, with a body 73–106 cm long.",
        sizing="Shoulder height 65 cm sits at 77% of this silhouette, giving 84 cm to the ear tufts.",
        source="Wikipedia: Eurasian lynx"),
    "wolf": dict(
        name="Grey wolf", h=0.98, kg=40, plural="grey wolves",
        scale=dict(at="withers", h_m=0.82, h_f=0.84, l_m=1.2, l_f=0.84, how="height"),
        mass=dict(lo=40, hi=40, note="grey wolves average 40 kg"),
        fact="Grey wolves stand 80–85 cm at the shoulder and run 105–160 cm from nose to rump.",
        sizing="Shoulder height 82 cm sits at 84% of this silhouette, giving 98 cm to the ear tips.",
        source="Wikipedia: Wolf"),
    "bear": dict(
        name="Brown bear", h=1.2, kg=217,
        scale=dict(at="shoulder hump", h_m=1.15, h_f=0.965, l_m=1.8, l_f=0.96, how="height"),
        mass=dict(lo=217, hi=217, note="male brown bears average 217 kg"),
        fact="On all fours, brown bears stand about 1–1.5 m at the shoulder; the largest coastal bears "
             "fill the top of that range.",
        sizing="The shoulder hump, 1.15 m on a large adult, is at 96% of this silhouette; the ears just "
               "clear it at 1.2 m.",
        source="Wikipedia: Brown bear"),
    "reindeer": dict(
        name="Reindeer", h=1.62, kg=150, plural="reindeer",
        scale=dict(at="withers", h_m=1.1, h_f=0.68, l_m=1.75, l_f=0.92, how="height"),
        mass=dict(lo=150, hi=180, note="bull reindeer weigh roughly 150–180 kg"),
        fact="Reindeer stand 85–150 cm at the shoulder, and both sexes grow antlers.",
        sizing="Shoulder height 1.1 m sits at 68% of this silhouette, giving 1.62 m to the antler tips.",
        source="Wikipedia: Reindeer; Dimensions.com reindeer size guide"),
    "reddeer": dict(
        name="Red deer stag", h=2.26, kg=200,
        scale=dict(at="withers", h_m=1.2, h_f=0.53, l_m=1.95, l_f=0.94, how="height"),
        mass=dict(lo=160, hi=240, note="red deer stags weigh 160–240 kg"),
        fact="Red deer stags stand 95–130 cm at the shoulder and carry antlers around 71 cm long.",
        sizing="Shoulder height 1.2 m sits at 53% of this silhouette — the antlers are half of it — "
               "giving 2.26 m to their tips.",
        source="Wikipedia: Red deer"),
    "moose": dict(
        name="Moose", h=2.54, kg=500, plural="moose",
        scale=dict(at="shoulder hump", h_m=1.8, h_f=0.71, l_m=2.7, l_f=0.92, how="height"),
        mass=dict(lo=380, hi=700, note="bull moose weigh 380–700 kg"),
        fact="Moose stand 1.4–2.1 m at the shoulder; a mature bull's antlers spread 1.2–1.5 m.",
        sizing="Bull shoulder height 1.8 m sits at 71% of this silhouette, giving 2.54 m to the top of "
               "the antlers.",
        source="Wikipedia: Moose"),
    # ---------------- Wild World ----------------
    "tiger": dict(
        name="Tiger", h=1.17, kg=220,
        scale=dict(at="withers", h_m=0.95, h_f=0.94, l_m=1.9, l_f=0.82, how="mean"),
        mass=dict(lo=180, hi=260, note="male Bengal tigers weigh 180–260 kg"),
        fact="A male Bengal tiger stands 0.9–1.1 m at the shoulder, with a 1.9 m body and a metre of "
             "tail behind it.",
        sizing="Shoulder height 95 cm sits at 94% of this silhouette and the 1.9 m body reads a little "
               "short; splitting the two puts the top of the head at 1.17 m.",
        source="Wikipedia: Tiger"),
    "camel": dict(
        name="Dromedary", h=2.2, kg=500, plural="dromedaries",
        scale=dict(at="withers", h_m=1.85, h_f=0.84, l_m=2.6, l_f=0.94, how="height"),
        mass=dict(lo=400, hi=600, note="dromedary bulls weigh 400–600 kg"),
        fact="A dromedary bull stands 1.8–2.0 m at the shoulder, and the hump rises about 20 cm above that.",
        sizing="Shoulder height 1.85 m sits at 84% of this silhouette, giving 2.2 m to the crown of the hump.",
        source="Wikipedia: Dromedary"),
    "gorilla": dict(
        name="Western gorilla", h=1.35, kg=157, plural="western gorillas",
        scale=dict(at="back", h_m=1, h_f=0.75, l_m=1.2, l_f=0.94, how="mean"),
        mass=dict(lo=157, hi=157, note="wild male western gorillas average 157 kg"),
        fact="A silverback stands 1.4–1.8 m upright, but spends his day knuckle-walking with his back "
             "about a metre off the ground.",
        sizing="The back of a knuckle-walking silverback, about 1 m up, sits at 75% of this silhouette; "
               "with the body reading short the scale settles at 1.35 m to the crest of the skull.",
        source="Wikipedia: Western gorilla"),
    "kangaroo": dict(
        name="Red kangaroo", h=1.6, kg=66,
        scale=dict(at="ear tips", h_m=1.6, h_f=1, l_m=None, l_f=None, how="height"),
        mass=dict(lo=55, hi=90, note="male red kangaroos weigh 55–90 kg, averaging about 66 kg"),
        fact="A big male red kangaroo stands about 1.5 m to the top of his head, with a tail over a "
             "metre long propping him up.",
        sizing="Standing upright with his tail on the ground, a large male reaches about 1.6 m to the "
               "ear tips, which is this silhouette's whole height.",
        source="Wikipedia: Red kangaroo"),
    # ---------------- Rodents & Co. ----------------
    "mouse": dict(
        name="House mouse", h=0.053, kg=0.02, plural="house mice",
        scale=dict(at="back", h_m=0.03, h_f=0.84, l_m=0.085, l_f=0.73, how="mean"),
        mass=dict(lo=0.011, hi=0.03, note="house mice weigh 11–30 g"),
        fact="A house mouse's head and body are 7.5–10 cm long, with a tail of 5–10 cm.",
        sizing="Head and body of 8.5 cm span 73% of this silhouette's width, but the drawing is "
               "deeper-bodied than a real mouse; splitting height against length gives about 5.3 cm "
               "to the top of the back.",
        source="Wikipedia: House mouse"),
    "rat": dict(
        name="Brown rat", h=0.12, kg=0.3,
        scale=dict(at="back", h_m=0.075, h_f=0.85, l_m=0.22, l_f=0.67, how="mean"),
        mass=dict(lo=0.14, hi=0.5, note="wild brown rats commonly weigh under 300 g; the range is 140–500 g"),
        fact="Brown rats have a 15–28 cm body and a tail slightly shorter than that.",
        sizing="Head and body of 22 cm span two thirds of this silhouette's width; against a real rat's "
               "7–8 cm back the drawing is deep, so the scale splits the two at 12 cm.",
        source="Wikipedia: Brown rat"),
    "guineapig": dict(
        name="Guinea pig", h=0.11, kg=1,
        scale=dict(at="back", h_m=0.1, h_f=0.95, l_m=0.225, l_f=0.98, how="length"),
        mass=dict(lo=0.7, hi=1.2, note="guinea pigs weigh 0.7–1.2 kg"),
        fact="Guinea pigs are 20–25 cm long and weigh 0.7–1.2 kg.",
        sizing="Body length 22.5 cm spans this silhouette's width, giving 11 cm tall.",
        source="Wikipedia: Guinea pig"),
    "squirrel": dict(
        name="Red squirrel", h=0.24, kg=0.3,
        scale=dict(at="head, sitting", h_m=0.17, h_f=0.72, l_m=None, l_f=None, how="height"),
        mass=dict(lo=0.25, hi=0.34, note="red squirrels weigh 250–340 g"),
        fact="A red squirrel's head and body are 19–23 cm, with a 15–20 cm tail.",
        sizing="Sitting up, the head reaches about 17 cm, which is 72% of this silhouette, giving 24 cm "
               "to the top of the tail.",
        source="Wikipedia: Red squirrel"),
    "hedgehog": dict(
        name="European hedgehog", h=0.11, kg=0.8,
        scale=dict(at="back", h_m=0.105, h_f=0.95, l_m=0.26, l_f=1, how="length"),
        mass=dict(lo=0.8, hi=0.8, note="adult European hedgehogs weigh about 800 g in summer"),
        fact="Adult European hedgehogs reach about 26 cm long and weigh around 800 g in summer.",
        sizing="Body length 26 cm spans this silhouette's width, giving about 11 cm tall.",
        source="Wikipedia: European hedgehog"),
    "beaver": dict(
        name="North American beaver", h=0.43, kg=20,
        scale=dict(at="back", h_m=0.32, h_f=0.9, l_m=0.8, l_f=0.67, how="mean"),
        mass=dict(lo=11, hi=32, note="North American beavers weigh 11–32 kg, typically about 20 kg"),
        fact="A beaver's head and body are 74–90 cm long, plus a 20–35 cm flat tail.",
        sizing="An 80 cm body fills two thirds of this silhouette's width, and a beaver's humped back is "
               "about 32 cm up; this drawing is the stockier of the two, so the scale splits them at 43 "
               "cm.",
        source="Wikipedia: North American beaver"),
    "capybara": dict(
        name="Capybara", h=0.6, kg=49,
        scale=dict(at="withers", h_m=0.56, h_f=0.94, l_m=1.15, l_f=0.95, how="height"),
        mass=dict(lo=35, hi=66, note="capybaras weigh 35–66 kg, averaging about 49 kg"),
        fact="Capybaras stand 50–62 cm at the withers with a 106–134 cm body, the largest rodent alive.",
        sizing="Withers height 56 cm sits at 94% of this silhouette, giving 60 cm to the ears.",
        source="Wikipedia: Capybara"),
}

# Themed lineups for the size game. Five members are drawn from a set each game, so a set wants
# six or more if the same five are not to come up twice running.
SETS = [
    dict(id="farm", name="Farm & Home",
         blurb="Cat, rabbit, Labrador, sheep, pig, cow, horse. Five are picked each game.",
         members=['cat', 'rabbit', 'dog', 'sheep', 'pig', 'cow', 'horse']),
    dict(id="savanna", name="African Savanna",
         blurb="Lion, zebra, hippo, rhino, elephant, giraffe. Five are picked each game.",
         members=['lion', 'zebra', 'hippo', 'rhino', 'elephant', 'giraffe']),
    dict(id="forest", name="Northern Forest",
         blurb="Fox, lynx, wolf, brown bear, reindeer, red deer, moose. Five are picked each game.",
         members=['fox', 'lynx', 'wolf', 'bear', 'reindeer', 'reddeer', 'moose']),
    dict(id="world", name="Wild World",
         blurb="Tiger, dromedary, gorilla, red kangaroo, capybara, giraffe — one from each corner of "
               "the map. Five are picked each game.",
         members=['tiger', 'camel', 'gorilla', 'kangaroo', 'capybara', 'giraffe']),
    dict(id="rodents", name="Rodents & Co.",
         blurb="Mouse, rat, guinea pig, squirrel, hedgehog, beaver, capybara. Five are picked each game.",
         members=['mouse', 'rat', 'guineapig', 'squirrel', 'hedgehog', 'beaver', 'capybara']),
]

# Loads for the balance-log game. Everything on one log shares a scale and a weight range, so the
# round is a torque puzzle rather than one elephant surrounded by dust. Kept lightest-load first:
# a game plays five of them, one drawn from each fifth of the list, so it climbs from the small
# animals to the heavyweights.
LOG_SETS = [
    dict(id="nest", name="Nest",
         blurb="Mouse, rat, squirrel, hedgehog, guinea pig.",
         members=['mouse', 'rat', 'squirrel', 'hedgehog', 'guineapig']),
    dict(id="hedgerow", name="Hedgerow",
         blurb="Rat, squirrel, hedgehog, guinea pig, rabbit, cat.",
         members=['rat', 'squirrel', 'hedgehog', 'guineapig', 'rabbit', 'cat']),
    dict(id="riverbank", name="Riverbank",
         blurb="Cat, fox, beaver, lynx, Labrador, capybara.",
         members=['cat', 'fox', 'beaver', 'lynx', 'dog', 'capybara']),
    dict(id="pasture", name="Pasture",
         blurb="Wolf, sheep, reindeer, lion, brown bear, pig.",
         members=['wolf', 'sheep', 'reindeer', 'lion', 'bear', 'pig']),
    dict(id="farcountry", name="Far Country",
         blurb="Capybara, red kangaroo, gorilla, tiger, dromedary.",
         members=['capybara', 'kangaroo', 'gorilla', 'tiger', 'camel']),
    dict(id="highland", name="Highland",
         blurb="Red deer, zebra, horse, moose, Holstein cow.",
         members=['reddeer', 'zebra', 'horse', 'moose', 'cow']),
    dict(id="heavyweights", name="Heavyweights",
         blurb="Cow, giraffe, hippo, rhino, elephant.",
         members=['cow', 'giraffe', 'hippo', 'rhino', 'elephant']),
]
