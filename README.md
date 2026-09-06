# Life-Size Lineup

Two small browser games about how big animals really are.

- **Lineup (size).** Enter your height. An animal silhouette stands beside your own on graph paper. Drag the red corner until it looks life-size, lock it in, and score up to 100 for accuracy. Five animals, 500 points.
- **Counterweight (weight).** A large animal sits on one side of a balance. Click the bucket to drop one smaller animal, hold it to pour faster, and carry it anywhere you like to pour there — wherever they land, they count. Nothing comes back out. Lock in when you think it balances; the reveal stacks what you poured over what balances, and says what each animal weighs.

Both games pan and zoom the same way: scroll or pinch to zoom, drag to move, or use the buttons in the corner of the stage to fit everything or close in on the animal you are judging.

Play it online: https://claude.ai/code/artifact/ed0eeb0a-ec6d-494f-a9f5-700baa3f6643

Or open `life-size-lineup.html` in any browser. It is a single file with everything embedded and works offline.

## Project layout

| Path | What it is |
| --- | --- |
| `life-size-lineup.html` | The finished game. This is the only file players need. |
| `src/template.html` | The game's page, styles and code, without the silhouette data. Edit this. |
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

This rewrites `life-size-lineup.html` at the top of the folder. Python 3 is the only requirement.

## How the sizes were worked out

Each animal's height in the size game is the height of the highest point of its silhouette. Sources quote shoulder height or body length, so the silhouette's own proportions convert the quoted figure to the silhouette height. The reasoning for every animal is written into `src/build.py` and shown in the game after each round. Weights are typical adult masses matching the adult each silhouette depicts, for example a male lion and a bull elephant. Sources are Wikipedia species pages checked in September 2026, plus breed references for sheep and pigs.

## Adding animals

1. Add the species to `src/fetch_phylo.py` and run it to download candidate silhouettes.
2. Pick one, record it in `src/choices.json`, and measure it with `src/tools/measure.html` served by `src/tools/serve.py`.
3. Add its size, weight, fact and sizing note to `src/build.py`, put it in a lineup, and rebuild.

## Credits

Silhouettes are from [PhyloPic](https://www.phylopic.org). Most are public domain (CC0). Two require attribution: the human figure by Katy Lawler (CC BY 4.0) and the giraffe traced by T. Michael Keesey from a photograph by Bernard Dupont (CC BY-SA 3.0).

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

Game design by the repository owner; code written with Claude.
