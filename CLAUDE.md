# Working on Life-Size Lineup

Notes to get oriented quickly. These are observations about how the project hangs together rather
than rules — if something here is wrong or has been outgrown, trust the code and say so.

## What it is

Three small browser games about how big and how heavy animals really are:

| Mode | `S.mode` | What the player does |
| --- | --- | --- |
| Lineup | `size` | Drags an animal's silhouette until it looks life-size beside their own. |
| Counterweight | `weight` | Pours small animals onto a balance until they match one large one. |
| Balance Log | `balance` | Drops animals onto a seesaw log and keeps it level. |

All three read one shared library of animals and one set of silhouettes. The whole game ships as a
single `index.html` — every drawing and every number inlined, no scripts fetched, no server. It runs
from a `file://` URL and from GitHub Pages equally. Keeping that property has shaped most of the
decisions below, so it is worth preserving unless there is a good reason not to.

## The loop

```
edit src/animals.py or src/template.html
python src/build.py            # checks, then rewrites index.html
python src/tools/audit_scale.py  # only when a size or a drawing changed
```

`index.html` is generated. Hand edits to it are lost on the next build, and CI fails if the
committed copy is not what the sources produce.

## The shape of the repo

**The sources**

| | |
| --- | --- |
| `src/animals.py` | Every animal: name, size, weight, fact, source, and the lineups and loads. Pure data; no code. This is usually the only file you need. |
| `src/template.html` | The game — markup, CSS and the JavaScript for all three games. Everything except the animals. |
| `src/phylo/*.svg` | One PhyloPic drawing per animal. |
| `src/choices.json` | Which drawing each animal uses, plus the artist and licence the credits screen reads. |
| `src/bbox.json` | The exact rectangle each drawing's ink occupies. Written by `audit_scale.py --measure`. |

**The workshop**

| | |
| --- | --- |
| `src/build.py` | Reads the above, runs the checks, writes `index.html`. |
| `src/tools/audit_scale.py` | Checks each animal's size against its own drawing, and proposes one for a new animal. |
| `src/fetch_phylo.py` | Downloads candidate drawings from PhyloPic for the roster in that file. |
| `src/tools/*.html`, `serve.py` | Browser pages that measure a drawing by hand. `--measure` has replaced them for new animals; kept for eyeballing. |

`DESIGN.md` holds the house style — palette, shape, tone. Worth a look before touching anything
visible; the register it aims for is "a warm outdoor morning", Animal Crossing rather than
fairground.

## Reading around the repo

Three files hold most of the bulk and rarely repay opening, because of how they are made:

- `index.html` (~370 KB) is assembled by `build.py` out of `src/template.html`, `src/animals.py`
  and the drawings, so anything in it came from one of those — read the source instead. When the
  question really is what the built file ended up containing, a few lines of Python that pull out
  the one field beat reading it whole.
- `src/phylo/*.svg` (~230 KB across 32 files) are potrace bezier paths. They say nothing useful as
  text; `audit_scale.py` already reads them geometrically, so borrow that instead of opening one.
- `src/phylo/catalog.json` (~105 KB) lists the PhyloPic candidates that were considered when each
  animal was chosen. Provenance, rarely the answer to anything.

`src/template.html` (~130 KB) is normal source and sometimes genuinely needed, but usually in the
part you are working on rather than whole.

For the state of the library, asking is cheaper than reading: `python src/build.py` prints every
animal's size and weight in about thirty lines, and `python src/tools/audit_scale.py` adds the
workings behind each height, the sourced weight ranges, and the checks.

## How the build fits together

`src/template.html` contains the line `const DATA = /*__DATA__*/;`. `build.py` replaces that comment
with one JSON object and writes the result as `index.html`. That is the entire build — there is no
bundler, no minifier, no dependency.

What `DATA` holds:

```
DATA.human            the player's silhouette record
DATA.animals[key]     one record per animal (below)
DATA.sets[]           themed lineups for the size game: {id, name, blurb, members[]}
DATA.logSets[]        loads for the balance game, lightest first, same shape
```

Each animal record carries `key`, `vb` (the drawing's tight bounding box), `svg` (its path markup),
`credit`, `sci`, and the played fields — `name`, `h`, `kg`, `plural`, `fact`, `sizing`, `source`,
`kgNote`. The `PLAYED` tuple in `build.py` decides that list; the `scale` and `mass` workings stay
behind in `animals.py` rather than shipping, because the game never reads them.

`build.py` sets `sys.dont_write_bytecode` before importing `animals.py`. Python validates cached
bytecode from a file's timestamp-to-the-second and its length, so correcting a figure without
changing either — 0.48 to 0.65, or 220 to 217 — could otherwise leave a stale cache serving the old
number silently. Worth leaving in place.

## An animal's record

```python
"fox": dict(
    name="Red fox", h=0.48, kg=6, plural="red foxes",
    scale=dict(at="withers", h_m=0.4, h_f=0.84, l_m=0.65, l_f=0.76, how="height"),
    mass=dict(lo=2.2, hi=14, note="red foxes weigh 2.2–14 kg, typically about 6 kg"),
    fact="...",      # shown after a round
    sizing="...",    # how this height was arrived at, shown in the reveal
    source="Wikipedia: Red fox"),
```

`h` is the height of the silhouette's **highest point** in metres — ear tips, antlers, the crown of
a hump, whichever the drawing tops out at. It is stored, never computed at build or play time; the
`scale` field beside it is the workings, kept so the number can be checked later.

`how` says which dimension the scale follows: `height` (`h_m / h_f`), `length`
(`l_m / (l_f × aspect)`), or `mean` — the geometric mean of both, used where a drawing is stylised
enough that its height and its length cannot both be true. `plural` is only needed when adding "s"
would be wrong.

## The thing that is easy to get wrong

`h_f` — *where in this particular drawing the animal's shoulder sits*, as a fraction of the
drawing's height — is the only figure in the project that cannot be looked up anywhere. It is a
fact about the artwork, not about the animal, and it is quietly easy to get wrong: a set of these
were wrong by up to 35% for a long time and nothing noticed, because the game looks perfectly
plausible when an animal is the wrong size.

`python src/tools/audit_scale.py --sheets` draws each animal into `src/tools/audit/` as SVG, with a
percentage grid and a green line at its recorded fraction. If the line is not on the shoulder, the
number is wrong. That look is the check; everything else the audit does is arithmetic it can do on
its own.

Weights are easier: they are lookups, and each records the range its source gives.

## What the build checks before it writes anything

- `check_drawings` — every animal has a chosen drawing on disk and a measured box
- `check_scale` — every height still follows from the workings recorded beside it
- `check_weights` — every weight still sits inside the range its source gives, and cites a source
- `check_library` — every animal is reachable in all three games, every set has at least five
  members, and every heavy enough animal has something it can be weighed against

A failing check stops the build rather than shipping a wrong number.
`.github/workflows/check.yml` runs the same thing on every push, plus a check that the committed
`index.html` matches what the sources produce.

## Inside src/template.html

Two `<script>` blocks, no modules and no imports. The first is a handful of lines that install
`window.__lslErr` and the `error`/`unhandledrejection` listeners, deliberately ahead of everything
else so a failure in the game still surfaces. The second is the game itself, one IIFE. Banner
comments mark its four parts:

```
SIZE GAME • WEIGHT GAME (Counterweight) • BALANCE GAME (Balance Log) • END / START / CREDITS
```

Above them sit the shared pieces: `DATA`, the `S` state object, the silhouette `<symbol>`
definitions, the camera and zoom helpers, unit formatting (`fmt`, `fmtKg`, `fmtTorque`), and the
start-menu parade.

**State.** `S` holds what is common — `mode`, `phase`, `unit`, `humanH`, `round`, `results`,
`queue`, `set`, `animal`, `guessH`, `trueH`, and the size game's `cam`. Each of the two physics
games keeps its own runtime object beside it: `Wg` for the weighing scale, `Lg` for the log. Phases
run `start` → `guess`/`wguess`/`bguess` → `reveal`/`wreveal`/`breveal` → `end`, one triple per mode.

**Silhouettes.** Each is added once as an SVG `<symbol>` whose `viewBox` is the drawing's tight
bounding box, then drawn with `<use>`. `ar(rec)` is that box's aspect. Anything that sets a width
and height in that ratio will not distort the animal.

**How each game decides scale** — this is where sizes become pixels:

- *Size game*: the player's own height sets metres-per-pixel; the animal is drawn against it.
- *Weight game*: `tokenDims()`. The reference animal fills 70% of its plate's width, capped at
  `REF_MAX` so its two label lines still clear the beam. Every poured animal is then drawn at
  `refH × (target.h / ref.h)` — the true height ratio, so both pans share one scale. Two legibility
  floors (18px tall, 26px on the longer side) stop a token becoming a speck; the audit reports any
  pairing that lands on them.
- *Balance game*: `Lg.mpp = tallest animal's h / TOKEN_TALL`, so a whole load shares one scale and
  the log is as long in metres as those animals need. Design space is `LDW × LDH` (1600 × 840); the
  weighing scene's is `DW × DH` (1200 × 700). A camera pans and zooms over the top of both.

**Which animals a round uses.** `makeWeighQueue()` picks three references (≥30 kg) and targets 3–60×
lighter and no more than 0.6× as tall. `pickLoads()` takes five of `DATA.logSets`, one from each
fifth of the list, so a game climbs from small animals to heavyweights however many loads exist.
`makeDropQueue()` fills a load's ten drops.

**Docks.** Four bottom panels — `guessDock`, `weighDock`, `balanceDock`, `revealDock` — and each
mode is responsible for hiding the other three. Forgetting one leaves a stale panel on screen; that
has happened.

**Driving it without clicking.** `window.LSL` exposes the internals: `LSL.DATA`, `LSL.S`, `LSL.Wg`,
`LSL.Lg`, `startSizeGame/startWeightGame/startBalanceGame`, `nextRound/nextWeighRound/
nextBalanceRound`, `lockIn/lockWeigh/lockBalance`, `spawnToken`, `dropNext`, and the camera helpers.
That is the cheapest way to check a change — play a few rounds through it in a headless browser
rather than by hand.

**Errors.** `window.__lslErr` catches uncaught errors and rejections and shows them in the page, so
a broken frame is visible rather than silent.

## Adding an animal

1. Add the species to the roster in `src/fetch_phylo.py` and run it. It downloads up to eight
   candidates each and prints which species still need one chosen.
2. Pick one — plenty are dorsal views, skulls or swimming poses, so this needs eyes — and record it
   in `src/choices.json` with its uuid, licence, contributor and attribution.
3. `python src/tools/audit_scale.py --measure` writes its ink box into `src/bbox.json`. It only
   fills in what is missing; existing entries are left alone, because the built file carries the
   box rounded to two decimals and a re-measure can shift it enough to fail CI for no real change.
4. `python src/tools/audit_scale.py --propose <key>` for a starting `h_f`. It is a draft: against
   the animals already sized by hand it lands within 3 points on twelve of twenty-one, and misses by
   as much as 12 where the outermost feet are not the front ones. It says so rather than guessing
   when a drawing is not a quadruped in profile.
5. Write the record into `src/animals.py`, put it in a lineup set and a log load, and rebuild.
6. `--sheets`, then look. The green line has to land where `at` says.

## Worth knowing

- If animals look out of proportion in the weight game, suspect the data rather than the rendering —
  both pans already share one scale, so the `h` values are what show.
- The three games read one shared library, so an animal added for one appears in all three, and the
  build enforces that it is reachable in each.
- There are no automated browser tests yet, deliberately — the library is still small enough to
  check by playing. That trade gets worse as the library grows; `window.LSL` is the seam to hang
  them on when it does.
- The audit is a tool for *changing* the library, not for running it. Once an animal is recorded and
  confirmed it does not need auditing again.
- The only thing `index.html` fetches from the network is the Google Fonts stylesheet, and every
  family has a real fallback stack, so offline it reads plainly rather than breaking.
- Sizes and weights are sourced figures with the source recorded. If a number needs changing,
  change the range and the note with it rather than the figure alone.
