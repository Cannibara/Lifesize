# Life-Size Lineup

Three small browser games about how big and how heavy animals really are. Fifty-seven animals, from a house mouse to a bull elephant, plus you.

- **Lineup (size).** Enter your height. An animal silhouette stands beside your own on graph paper. Drag the red corner until it looks life-size, lock it in, and score up to 100 for accuracy. Five animals, 500 points. Nine themed sets to pick from — farm, savanna, northern forest, rodents, jungle, Australia, birds, polar and Asia — or let it surprise you.
- **Counterweight (weight).** A large animal sits on one side of a balance. Click the bucket to drop one smaller animal and hold to pour faster; right-drag the bucket (or drag it with a finger) to carry it anywhere on the paper and pour there — wherever they land, they count. Nothing comes back out. Lock in when you think it balances; the reveal stacks what you poured over what balances, and says what each animal weighs.

- **Balance Log (balance).** A wooden log lies across a boulder like a seesaw. Click above it to drop the animal waiting in the dock; it falls, bounces once and settles, carrying its weight at its centre of gravity. The log turns on the sum of weight × distance from the rock, so a pig near the middle answers four dogs out at the end. Tip past about twenty degrees and animals slide off and are lost. Ten animals a load, ten points for each one still aboard, five loads. Each load is drawn at random from a weight tier, so the rounds always work upward from the hedgerow to the heavyweights but never repeat the same five loads.

All three games pan and zoom the same way: scroll or pinch to zoom, drag to move, or use the buttons in the corner of the stage to fit everything or close in on the part you are judging.

Play it online: https://claude.ai/code/artifact/ed0eeb0a-ec6d-494f-a9f5-700baa3f6643

Or open `index.html` in any browser. It is a single file with everything embedded and works offline.

## Project layout

| Path | What it is |
| --- | --- |
| `index.html` | The finished game. This is the only file players need. |
| `src/template.html` | The game's page, styles and code, without the silhouette data. Edit this. |
| `DESIGN.md` | The house style: principles, colour tokens, type, shape and motion. Follow it. |
| `src/build.py` | Stitches the template, the silhouettes and the size table into the finished file. |
| `src/choices.json` | Which PhyloPic silhouette was chosen for each animal, with licence and credit. |
| `src/bbox.json` | Measured bounding box of each silhouette. |
| `src/phylo/` | The silhouette SVG files and PhyloPic catalogue of candidates. |
| `src/fetch_phylo.py` | Downloads candidate silhouettes from the PhyloPic API for a list of species. |
| `src/tools/` | Helper pages used during development to rasterise and measure silhouettes. |

## Rebuilding after a change

Edit `src/template.html` (page and code) or the size and weight tables inside `src/build.py`, then run:

```
python src/build.py
```

This rewrites `index.html` at the top of the folder. Python 3 is the only requirement.

## How the sizes were worked out

Each animal's height in the size game is the height of the highest point of its silhouette. Sources quote shoulder height or body length, so the silhouette's own proportions convert the quoted figure to the silhouette height. The reasoning for every animal is written into `src/build.py` and shown in the game after each round. Weights are typical adult masses matching the adult each silhouette depicts, for example a male lion and a bull elephant. Sources are Wikipedia species pages checked in September 2026, plus breed references for sheep and pigs.

## How the balance log works

The log is a beam turning about the boulder's crown. Every animal resting on it contributes
weight × distance from the rock, and the log turns on the sum, slowed by its own rotational
inertia — which is why a load of elephants swings more slowly than a load of mice. It hangs a
little below its rest, so it forgives a small imbalance and no more. Animals are solved as
upright boxes against three surfaces — the log, each other and the earth — with real Coulomb
friction: they bounce once on landing, hold their footing up to about twenty degrees of tilt,
slide below the friction limit past that, and never spin.

Each load draws its animals to one shared scale, set by the tallest of them, so the log is as
long in metres as those animals need it to be. That is what the lever arms shown on the board
are measured in. The eleven loads are grouped into five weight tiers, and each game takes one
load from each tier in turn, lightest first.

## Adding animals

1. Add the species to `src/fetch_phylo.py` and run it to download candidate silhouettes.
2. Pick one, record it in `src/choices.json`, and measure it with `src/tools/measure.html` served by `src/tools/serve.py`.
3. Add its size, weight, fact and sizing note to `src/build.py`, put it in a lineup, and rebuild.

## Credits

Silhouettes are from [PhyloPic](https://www.phylopic.org). Most are public domain (CC0 or Public Domain Mark). Five ask for attribution and get it in the table below: the human figure by Katy Lawler (CC BY 4.0), the giraffe and the ostrich (CC BY-SA 3.0), and the chimpanzee and Tasmanian devil (CC BY 3.0). None are licensed non-commercially.

| Animal | Credit | Licence | Source |
| --- | --- | --- | --- |
| Human | Katy Lawler | CC BY 4.0 | [PhyloPic](https://www.phylopic.org/images/036b96de-4bca-408e-adb6-2154fcd724ef) |
| Domestic cat | Mozillian | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/81e1f778-d176-47ba-a0c4-01f54e1157a9) |
| European rabbit | Ferran Sayol | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/ad7d2a9d-ef0d-46f2-895d-7c67bb8e6355) |
| Domestic dog | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/22689036-9e7f-44b7-aab9-1436aa4de091) |
| Sheep | Katy Lawler | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/14012740-e356-464b-b84d-fa6c4a0b34a9) |
| Domestic pig | Mozillian | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/216ee85d-1696-49ae-a62c-d1da6fef06fc) |
| Cattle | Steven Traver | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/415714b4-859c-4d1c-9ce0-9e1081613df7) |
| Horse | An Ignorant Atheist | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/26d41545-17ea-4be5-8296-05d6ffd05360) |
| Lion | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/76a5e7ce-53fa-46ae-af9e-fabd8b863dcf) |
| Plains zebra | Andy Wilson | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/22f808e2-da14-4bfe-9672-0e5422d27212) |
| Hippopotamus | An Ignorant Atheist | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/e130f877-a96c-48d8-9f26-bb131021397f) |
| White rhinoceros | An Ignorant Atheist | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/8896498f-faf5-47df-82eb-1d7db9cbbf6f) |
| African bush elephant | Steven Traver | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/62398ac0-f0c3-48f8-8455-53512a05fbc4) |
| Giraffe | Bernard Dupont (photograph) and T. Michael Keesey (tracing) | CC BY-SA 3.0 | [PhyloPic](https://www.phylopic.org/images/b35f867d-26e8-4c48-806e-0f07f18b1844) |
| Red fox | An Ignorant Atheist | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/4a2143fc-4bfb-4188-b0fa-f2d2094349a4) |
| Eurasian lynx | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/27a2173a-5903-46fc-83c5-29ed7f421046) |
| Grey wolf | Steven Traver | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/5036f260-5a0d-42c5-a0bd-9eb0729e54e0) |
| Brown bear | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/c7fbe213-1eac-4f81-80d0-674c3bd2d6b0) |
| Reindeer | Mason McNair | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/d2e268c1-1937-4308-9fa4-9adc55cc5e8b) |
| Red deer | Ferran Sayol | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/cc03f5c2-933f-4c40-9c64-7f8727556fdb) |
| Moose | T. Michael Keesey | Public Domain Mark 1.0 | [PhyloPic](https://www.phylopic.org/images/1a20a65d-1342-4833-a9dd-1611b9fb383c) |
| House mouse | Jiro Wada | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/c8f71c27-71db-4b34-ac2d-e97fea8762cf) |
| Brown rat | Arcadia Science | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/6b8ecf3f-a5c2-4ca4-adbc-1c7280c380d4) |
| Guinea pig | Daniel Stadtmauer | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/75836dad-906e-4066-8518-ab60f0f96b73) |
| Red squirrel | Ferran Sayol | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/23c700c9-e695-404a-8d0c-146e1fc4bada) |
| European hedgehog | Steven Traver | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/6ecff71e-fcfc-4cb9-b773-9e6e21607587) |
| North American beaver | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/be8670c2-a5bd-4b44-88e8-92f8b0c7f4c6) |
| Capybara | Skye M | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/9c234021-ce53-45d9-8fdd-b0ca3115a451) |
| Tiger | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/135296df-6e7a-4c02-bd22-85ca4aefcc85) |
| Leopard | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/78dbe564-bcba-4dc3-8bdc-fb95fc288580) |
| Jaguar | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/c5362c8a-0c93-41f5-9d4d-674dbe231318) |
| Western gorilla | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/142e0571-3b5f-443d-a887-b572a224ea22) |
| Chimpanzee | Kai R. Caspar | CC BY 3.0 | [PhyloPic](https://www.phylopic.org/images/34f93016-ee49-428c-8504-c7c4739232bc) |
| Bornean orangutan | T. Michael Keesey | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/0173bfdd-b5ab-4e8f-9053-b33830690ac5) |
| Red kangaroo | Guillaume Dera | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/b1619eda-7265-4c5a-9af5-527875ab2677) |
| Koala | Gavin Prideaux | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/0904270e-b105-46e0-b81f-c4911d47d467) |
| Common wombat | Rachel T Mason | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/ee5c20bd-f70e-44be-a5f4-675592eb2694) |
| Tasmanian devil | Soledad Miranda-Rottmann | CC BY 3.0 | [PhyloPic](https://www.phylopic.org/images/fc8ff6ad-d1b6-4d87-a1ef-297f8301345e) |
| Emu | Andy Wilson | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/bae88982-352f-43d0-b2ed-8d7661fa1d6f) |
| Platypus | Rachel T Mason | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/162021b6-349b-4a64-906f-33d4a191b30e) |
| Common ostrich | Matt Martyniuk (vectorized by T. Michael Keesey) | CC BY-SA 3.0 | [PhyloPic](https://www.phylopic.org/images/14ddbf4d-7749-4153-bbe1-8d0c6ffdf142) |
| Emperor penguin | Guillaume Dera | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/f2e02022-2700-484d-a66d-b2a900030371) |
| Mute swan | Andy Wilson | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/95f4447f-2ef4-4061-ad9f-3de17e71afeb) |
| Chicken | Arcadia Science | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/f16a316c-6580-4cc0-b6b5-fd2e895ba225) |
| Golden eagle | Anthony Caravaggi | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/b2b60a18-fd7d-49b2-a15d-54a62cdcac6b) |
| Greater flamingo | Ferran Sayol | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/a1244226-f2c2-41dc-b113-f1c6545958ce) |
| Polar bear | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/a12876cb-0930-4310-8ea8-2378df8164e3) |
| Walrus | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/d2575005-1fcb-4a86-8c83-e3bda619adf2) |
| Harp seal | Tracy A. Heath | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/5e359baf-a5f7-4101-8f61-6d42beb52756) |
| Arctic fox | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/8e5dfa51-961d-48be-acda-fd7a00f0e565) |
| Muskox | Laura Barbero-Palacios | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/2238533e-7b2c-4497-a414-eaece410cb88) |
| Wolverine | Steven Traver | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/1f9bbb79-f060-47c1-9954-ea78812d3b91) |
| Dromedary | Steven Traver | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/e52676dd-272c-4b14-8c99-ea5dc98942e5) |
| Asian elephant | Kai Caspar | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/91e44407-08f2-4b96-b8a6-ab4ce6d4d38d) |
| Giant panda | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/887ea34b-b62a-4126-9e98-434d6000dd0c) |
| Wild water buffalo | Cristopher Silva | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/d36c5902-5124-41e5-a880-15b0b1d1070d) |
| Snow leopard | Margot Michaud | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/cb44ff49-165e-4c97-9a94-98f512dda64f) |
| Red panda | Xavier A. Jenkins | CC0 1.0 | [PhyloPic](https://www.phylopic.org/images/02990f6d-82d3-45a9-b85e-99deb69d2a96) |

Game design by the repository owner; code written with Claude.
