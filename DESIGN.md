# Design guide

The house style for Life-Size Lineup. The start menu is built to this guide; anything
new should follow it, and the older paper-and-pen screens should be brought over to it
as they are touched.

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

## Colour

Defined as custom properties on `:root` in `src/template.html`, prefixed `--isl-`.

| Token | Hex | Where it goes |
| --- | --- | --- |
| `--isl-bark` | `#8a5a2c` | Card frame, control borders, label pills, the solid edge under things |
| `--isl-bark-dk` | `#6d4520` | Sign frame, badge outlines, the darker half of an edge |
| `--isl-wood` | `#c08a4c` | Sign face (top of its gradient), the balance game's tile |
| `--isl-wood-dk` | `#a86f36` | Sign face (bottom of its gradient), the balance game's tile |
| `--isl-leaf` | `#63bc4f` | The size game, step 1, vine leaves, the start button |
| `--isl-leaf-dk` | `#3f8b3a` | Start button border; `#35762f` is its pressed edge |
| `--isl-leaf-lt` | `#8ed06a` | Second leaf tone, lighter foliage |
| `--isl-cream` | `#fffdf4` | Card top, input fields |
| `--isl-paper` | `#fdf5e2` | Card bottom — the card is a soft vertical gradient between the two |
| `--isl-sand` | `#efe1c0` | Unselected tiles, the unit switch bed |
| `--isl-sun` | `#ffd873` | Selected badge, step 2, focus ring |
| `--isl-terra` | `#e0913f` | The weight game |
| `--isl-terra-dk` | `#c4712d` | Weight game border and emphasis in body copy |
| `--isl-text` | `#4a3a26` | Body text |
| `--isl-muted` | `#8a765a` | Hints, footnotes, the tagline |

Scene colours are literal rather than tokenised, since they only exist once: sky
`#86d3f5 → #b3e6fb → #ddf3fd`, far hills `#9ad97f`, near hills `#74c25f`, field
`#63b352 → #458a3c`, silhouettes `#1d4f28` at 40% opacity. Step 3 uses `#6cc4e0`, a
sky blue that belongs to the scene rather than the palette. Errors are `#c0492b`.

The game boards do the same where an object needs a material: the scale's ropes are
`#6f5a3e` and its leaves `#5f8f62`; the balance log is `#c08a4c` with `#9a6a33` underneath,
`#8a5a2c` grain and `#d8ab74` end grain. Everything else on a board — outlines, stone, the
graph paper — stays on the paper-and-pen tokens, so the wood reads as one object in the
drawing rather than as a second palette.

The paper-and-pen tokens (`--ink`, `--pen`, `--grid`, …) still drive the game board
and are unchanged; the two sets do not mix on one surface.

## Type

- **`--f-round`: Baloo 2**, with Source Sans 3 and the system stack behind it. This is
  the whole island voice: 800 for the title and buttons, 700 for labels and inputs,
  600 for the tagline, 500 for body copy.
- Small caps labels (`LIFE-SIZE`, `YOUR HEIGHT`) are 700–800 at 11.5–22px with
  `letter-spacing` between `.1em` and `.2em`, uppercase.
- Sizes are `clamp()`-ed so the card survives a phone: title
  `clamp(38px, 8.6vw, 56px)`, primary button `clamp(21px, 5vw, 28px)`.
- The game board keeps Fraunces and Caveat — that is the field notebook, a different
  place.

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

## Motion

| What | Duration | Note |
| --- | --- | --- |
| Clouds | 44s | Sideways drift, staggered by negative delays |
| Leaves | 11s | Rise and rotate, staggered |
| Primary button | 3.2s | A single bob late in the cycle, so it reads as a nudge |
| Press / hover | 80ms | `ease` on transform and box-shadow |

All of it sits inside `@media (prefers-reduced-motion: reduce)` and stops there. Nothing
animates position or size of text a player is reading.

## Working on it

Edit `src/template.html` — the styles live in one `<style>` block, with the start menu
in its own section — then run `python src/build.py` to rebuild `index.html`.
The webfonts load from Google Fonts with real fallbacks, so the page still works
offline, just in the fallback stack.
