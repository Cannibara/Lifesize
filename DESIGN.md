# Design guide

The house style for Life-Size Lineup. Every screen is built to this guide — the start
menu, the header, the docks, the end sheet and all three game boards. The old
paper-and-pen chrome is gone; what survives of it is the measuring layer, and that is
described under Colour below.

The tone to aim for: a warm outdoor morning that a child wants to walk into. Animal
Crossing more than a fairground — soft light, rounded shapes, wood and leaves, nothing
shouting.

## Principles

1. **Everything is a real object.** Buttons sit on a solid edge and sink into it when
   pressed; the title is carved into a wooden sign; the card is a piece of paper on a
   bark frame. No flat rectangles that only change colour.
2. **The world is behind the glass.** The interface floats over an island — sky, sun,
   clouds, hills, field. The scene is decoration only: it never carries meaning a
   player needs, so it can be covered by the card on a small screen without loss.
   The boards stand on that same island: sky above the horizon, field below it. What
   a player reads there is the grid, the silhouettes and the pen marks, never the
   ground behind them.
3. **Silhouettes are always to scale.** Any decorative animals share one
   metres-per-pixel unit (`--pm` on the start menu), so a giraffe beside a cat is
   honestly a giraffe beside a cat. The game is about real size; the furniture must
   not lie about it.
4. **Warm, not loud.** Colour comes from wood, leaf, wheat and terracotta. Saturated
   primaries and pure black are not in the palette. Ink is dark brown, never `#000`.
5. **Round everything.** Corners 14px on controls, 20px on tiles and buttons, 24–28px
   on cards. Nothing sharp.
6. **Motion is weather.** Ambient loops are slow enough to ignore (clouds 44s, leaves
   11s) and interaction is quick (80ms). Every animation stops under
   `prefers-reduced-motion`.
7. **One thing to do.** Each screen has a single obvious green action at the bottom,
   full width, and it says what it does — "Start the lineup", not "Go".
8. **Plain warm words.** Sentence case, no exclamation marks, no cute mascot voice.
   "How big is that animal really?" is the register.
9. **The card is controls, not a manual.** The start card carries one line saying what
   the chosen game is, and after that only the things a player sets — height, lineup,
   units — and the green button. How to play is taught by the dock during the round,
   where the thing being described is on screen and can be tried straight away.
10. **The reward is proportional, and it starts low.** A close guess is worth more than a
    poor one, and the reveal has to say so before the number does: the seal presses
    harder, knocks out a wider ring and throws more leaves the closer you were, and
    turns gold at full marks. The thresholds matter as much as the effects — the ring
    starts at 40 and the leaves at 65, which is a guess within about a third. Set them
    where only an expert reaches them and an ordinary good round looks exactly like a
    bad one, which is the same as having built nothing. A poor round still gets its
    seal, quietly, and is never mocked for it. Every number that
    represents something earned climbs to its value rather than appearing at it, and
    always lands on the truth — an interrupted climb snaps to the real score, never
    stops wherever it got to.

## Colour

Defined as custom properties on `:root` in `src/template.html`, prefixed `--isl-`.

| Token | Hex | Where it goes |
| --- | --- | --- |
| `--isl-bark` | `#8a5a2c` | Card frame, control borders, label pills, the solid edge under things |
| `--isl-bark-dk` | `#6d4520` | Sign frame, badge outlines, the darker half of an edge |
| `--isl-wood` | `#c08a4c` | Sign face (top of its gradient), the balance game's tile |
| `--isl-wood-dk` | `#a86f36` | Sign face (bottom of its gradient), the balance game's tile |
| `--isl-leaf` | `#63bc4f` | The size game, vine leaves, the start button |
| `--isl-leaf-dk` | `#3f8b3a` | Start button border; `#35762f` is its pressed edge |
| `--isl-leaf-lt` | `#8ed06a` | Second leaf tone, lighter foliage |
| `--isl-cream` | `#fffdf4` | Card top, input fields |
| `--isl-paper` | `#fdf5e2` | Card bottom — the card is a soft vertical gradient between the two |
| `--isl-sand` | `#efe1c0` | Unselected tiles, the unit switch bed |
| `--isl-sun` | `#ffd873` | Selected badge, focus ring |
| `--isl-terra` | `#e0913f` | The weight game |
| `--isl-terra-dk` | `#c4712d` | Weight game border and emphasis in body copy |
| `--isl-text` | `#4a3a26` | Body text |
| `--isl-muted` | `#8a765a` | Hints, footnotes, the tagline |

### The board

The three game boards are drawn from a second set, prefixed nothing and defined beside
the island tokens. They are the island seen at ground level rather than a separate
place.

| Token | Hex | Where it goes |
| --- | --- | --- |
| `--paper` | `#fffdf4` | The board behind everything, where no sky or field reaches |
| `--sky-hi` / `--sky-lo` | `#b8e7fa` / `#ddf3fd` | Above the horizon — the bottom half of the start menu's sky |
| `--grass-hi` / `--grass-lo` | `#63b352` / `#458a3c` | Below it — the start menu's field, the same two stops |
| `--grid` / `--grid-major` | brown at 10% / 19% | Graph paper, drawn over sky and field alike so it reads on either |
| `--ink` | `#3b2d1a` | The outline on every drawn object, and the horizon itself |
| `--silhouette` | `#1d4f28` | Every animal, on all three boards and in the results table |
| `--you` | `#6d4520` | Your own figure, so you are never mistaken for the animal beside you |
| `--stone` | `#857c6d` | The boulder under the log and the column under the scale |
| `--graphite` | `#6f5c42` | Second-rank marks: guide lines, chains, the pan weave |
| `--pen` / `--pen-ink` | `#d0323a` / `#b0262d` | The measuring layer — see below |

**The pen is the one thing that is not island.** Guesses, truth outlines, drag handles,
measurement tags and the counts poured are drawn in red on top of the scene, because
they are marks a player made, not objects in the world. Nothing else on a board may use
it, and nothing the player made may use anything else.

Scene colours are literal rather than tokenised, since they only exist once: sky
`#86d3f5 → #b3e6fb → #ddf3fd`, far hills `#9ad97f`, near hills `#74c25f`, field
`#63b352 → #458a3c`, silhouettes `#1d4f28` at 40% opacity. Errors are `#c0492b`.

The boards do the same where an object needs a material: the scale's ropes are
`#6f5a3e` and its leaves `#5f8f62`; the balance log is `#c08a4c` with `#9a6a33` underneath,
`#8a5a2c` grain and `#d8ab74` end grain. The bucket keeps its galvanised gradient, because
it is the one thing on any board that is meant to read as metal.

## Type

- **`--f-round`: Baloo 2**, with Source Sans 3 and the system stack behind it. This is
  the whole voice, on every screen: 800 for titles, buttons, animal names and the
  brand, 700 for labels and inputs, 600 for the tagline, 500 for body copy.
- Small caps labels (`LIFE-SIZE`, `YOUR HEIGHT`, `ROUND 1 · HOW BIG IS A`) are 800 at
  11.5–22px with `letter-spacing` between `.1em` and `.2em`, uppercase.
- Sizes are `clamp()`-ed so the card survives a phone: title
  `clamp(38px, 8.6vw, 56px)`, primary button `clamp(21px, 5vw, 28px)`.
- **`--f-hand`: Caveat is a score and nothing else** — the round seal, the running
  total on the rail, the grand total and the score column. If a number is not what the
  player earned, it is Baloo.
- **`--f-ui`: Source Sans 3 is only the board's own SVG text** — the measurements
  written next to a silhouette. It is the pen's handwriting, so it stays with the pen.
- Fraunces is gone. Do not reach for a serif.

## Shape and depth

- **Borders:** 3px on controls, 4px on cards and the primary button, in `--isl-bark`
  or the darker shade of the control's own colour.
- **The edge:** every pressable thing rests on a solid, unblurred shadow —
  `0 6px 0` for tiles, `0 8px 0` for the primary button, `0 3px 0` for inputs. Cards
  get `0 9px 0` plus one soft ambient shadow (`0 26px 48px`) and nothing else.
- **The press:** `transform: translateY()` by exactly the edge height, with the edge
  going to `0 0 0` — the object travels down onto the page. Hover lifts 2px and
  deepens the edge by 2px.
- Inner highlights (`inset 0 2px 0 rgba(255,255,255,.28)`) go on wood only.
- **The header is a wooden rail**, not a toolbar: the sign's own gradient and grain,
  a 4px `--isl-bark-dk` bottom, an inner highlight and a `0 4px 0` edge under it.
  Everything sitting on it is cream with a `0 1–2px 0` brown text shadow.
- **The dock is the start card, smaller**: the same cream-to-paper gradient, 4px
  `--isl-bark` frame and `0 6px 0` edge, at 22px radius instead of 28px.

## Interaction

- Focus is a 4px `--isl-sun` ring with 1px offset — visible against both cream and
  green. Never remove it.
- Toggle state lives in `aria-pressed`, and the CSS keys off
  `[aria-pressed="true"]`; the check badge is generated from that, not a class.
- Hiding is `[hidden]`, and any rule that sets `display` on a hideable element must
  also carry a `[hidden]{display:none}` at equal or greater specificity. An id
  selector setting `display:flex` silently defeats `.overlay[hidden]`.
- Tap targets stay at 44px or more; the three mode tiles become one column and go
  horizontal below 600px.
- **The seal takes the top middle on the Lineup board only.** That is where a player is
  already looking, so the count is watched rather than found. The other two boards draw
  their own verdict and count there, so it stays in their top-right corner. Centring is
  `left:50%` with a negative margin, never a transform — the press keyframes own the
  transform, and centring inside one would be wiped the moment the seal lands.
- Below 640px the zoom row moves to the top-left, so the centred seal drops to `top:58px`
  to clear it.
- Below 640px the dock breaks into two rows — the animal's name gets a full line to
  itself, then the readout and the button share the next. Letting `.who` shrink
  instead wrings the name down to a column two words wide.

## Motion

| What | Duration | Note |
| --- | --- | --- |
| Clouds | 44s | Sideways drift, staggered by negative delays |
| Leaves | 11s | Rise and rotate, staggered |
| Primary button | 3.2s | A single bob late in the cycle, so it reads as a nudge |
| Press / hover | 80ms | `ease` on transform and box-shadow |
| Reveal dock | .3s | Rises 14px into place, so the verdict arrives rather than blinks on |
| Seal press | .45s | `.52s` from 65, `.58s` and a deeper overshoot from 85 |
| Seal ring | .62–.98s | From 40 up, widening: scale 1.62, then 2.15 from 85 |
| Leaves thrown | .7–1.05s | From 65 up: 8, 14 from 85, 20 at full marks, staggered to .12s |
| Shower | 1.9–3.3s | Leaves and sparks down the whole board: 12 from 40, 24, 50, 80 at full marks |
| Round score | 400ms + 3ms a point | 400ms at nothing, 700ms at full marks — quick, but a climb worth watching |
| Running total | 620ms | Plus a .44s nudge when it grows |
| Grand total | 320ms + .9ms a point | ~770ms for a perfect game |
| Result rows | .34s each | 70ms apart, after a 140ms wait |

Stillness is resolved once, before the first paint, into a `data-motion` on the root: the
system setting unless the player has chosen otherwise on the start card, and both the CSS
and the script read that one attribute so they can never disagree. **The choice overrides
the system in both directions.** A machine set to reduce motion — which happens by
accident often enough, through a battery mode or a managed desktop — would otherwise
silently cost a player every celebration in the game with no way to ask for it back, and
they would have no reason to suspect the setting. Only a deliberate choice is stored, so
leaving it alone keeps following the machine.

**Reduced means reduced, not gone.** Under it the seal still arrives, fading rather than
flying in, and the score still climbs — briefer, but a climb — because a number changing
in place is not the motion that setting is about. What goes is everything that travels:
confetti, thrown leaves, spin, pop, slide. And because the choice is stored per browser,
a player who turned motion on elsewhere still arrives here with it off, so the start card
says so in a line beside the control whenever the machine chose and the player has not.
Silent degradation is the failure worth designing against: a reward that is simply absent
looks like a broken page, and nothing on screen suggests where it went. Nothing animates the position or size of prose a player is reading; a score
is the one exception, because the pop is the reward and it is over in a third of a second.

## Working on it

Edit `src/template.html` — the styles live in one `<style>` block, with the start menu
in its own section — then run `python src/build.py` to rebuild `index.html`.
The webfonts load from Google Fonts with real fallbacks, so the page still works
offline, just in the fallback stack.
