# Working on Life-Size Lineup

Notes to get oriented quickly. These are observations about how the project hangs together rather
than rules — if something here is wrong or has been outgrown, trust the code and say so.

## What it is

Three small browser games about how big and how heavy animals really are: a size lineup, a
counterweight balance, and a seesaw log. They share one library of animals and one set of
silhouettes.

The whole game ships as a single `index.html` — every drawing and every number inlined, no scripts
fetched, no server. It runs from a `file://` URL and from GitHub Pages equally. Keeping that
property has shaped most of the decisions below, so it is worth preserving unless there is a good
reason not to.

## The shape of the repo

**The game** — `index.html`. Generated, not written. Hand edits get overwritten the next time
anyone builds, so changes belong in the sources below.

**The sources**

| | |
| --- | --- |
| `src/animals.py` | Every animal: name, size, weight, fact, source, and the lineups and loads. Pure data; no code. This is usually the only file you need. |
| `src/template.html` | The game — markup, CSS and the JavaScript for all three games. Everything except the animals. |
| `src/phylo/*.svg` | One PhyloPic drawing per animal. |
| `src/choices.json` | Which drawing each animal uses, plus the artist and licence the credits screen reads. |
| `src/bbox.json` | The exact rectangle each drawing's ink occupies, measured in a browser. |

**The workshop**

| | |
| --- | --- |
| `src/build.py` | Reads the above, runs the checks, writes `index.html`. `python src/build.py`. |
| `src/tools/audit_scale.py` | Checks each animal's size against its own drawing, and proposes one for a new animal. |
| `src/fetch_phylo.py` | Downloads candidate drawings from PhyloPic for the roster in that file. |
| `src/tools/*.html`, `serve.py` | Browser pages used when measuring a newly chosen drawing. |

`DESIGN.md` holds the house style — palette, shape, tone. Worth a look before touching anything
visible; the register it aims for is "a warm outdoor morning", Animal Crossing rather than
fairground.

## The thing that is easy to get wrong

Each animal's height is stored, not computed — but it is stored alongside the workings that
produced it, in its `scale` field. One of those workings is `h_f`: *where in this particular
drawing the animal's shoulder sits*, as a fraction of the drawing's height.

`h_f` is the only figure in the project that cannot be looked up anywhere. It is a fact about the
artwork, not about the animal, and it is quietly easy to get wrong — a set of these were wrong by
up to 35% for a long time and nothing noticed, because the game looks perfectly plausible when an
animal is the wrong size. `src/tools/audit_scale.py --sheets` draws each animal with a line at its
recorded fraction; if the line is not on the shoulder, the number is wrong.

Weights are easier: they are lookups, and each records the range its source gives, so the build
refuses to run when a figure drifts outside it.

## What the build checks before it writes anything

- every height still follows from the workings recorded beside it
- every weight still sits inside the range its source gives
- every animal is reachable in all three games, and every drawing it names exists

A failing check stops the build rather than shipping a wrong number. `.github/workflows/check.yml`
runs the same thing on every push, plus a check that the committed `index.html` matches what the
sources produce.

## Adding an animal

Roughly: add the species to `src/fetch_phylo.py` and run it; pick a drawing and record it in
`choices.json`; measure its box with `src/tools/measure.html` (served by `src/tools/serve.py`); ask
`audit_scale.py --propose <key>` for a starting `h_f`; write the record into `src/animals.py`; put
it in a lineup set and a log load; rebuild; then look at the sheet to confirm the line landed
where it should. `README.md` has the longer version.

## Worth knowing

- The weight game draws both pans to one metres-per-pixel scale, so relative sizes come straight
  from the `h` values. If animals look out of proportion there, suspect the data rather than the
  rendering.
- The three games read one shared library, so an animal added for one appears in all three. The
  build enforces that it is reachable in each.
- There are no automated browser tests yet, deliberately — the library is still small enough to
  check by playing. That trade gets worse as the library grows.
- The audit is a tool for *changing* the library, not for running it. Once an animal is recorded
  and confirmed, it does not need auditing again.
