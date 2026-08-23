# R³DC project page

Static, single-file project page for **R³DC: Knowing What to Revise — Reliability-Aware Depth Completion for Trustworthy Cross-Domain Sparse Perception** (Mohammad & Bayazıt, İTÜ).

No build step, no dependencies. One `index.html` with inline CSS and vanilla JS.

## Deploy

**Option A — project page** (`https://<user>.github.io/r3dc/`)

```bash
# from the repo root
mkdir -p docs
cp index.html docs/
cp /path/to/R3DC_RADI_Q1_JOURNAL_PR.pdf docs/
git add docs && git commit -m "Add project page" && git push
```

Then: **Settings → Pages → Source: Deploy from a branch → `main` / `/docs`**.

**Option B — user or org site** (`https://<user>.github.io/`)

Push `index.html` to the root of the `<user>.github.io` repository. Pages serves it automatically.

**Option C — `gh-pages` branch**

```bash
git checkout --orphan gh-pages
git rm -rf . && cp /path/to/index.html .
git add index.html && git commit -m "Project page" && git push -u origin gh-pages
```

Add an empty `.nojekyll` file at the served root if you ever add directories or files starting with `_`.

## Before publishing — replace these

| Where | Placeholder | Replace with |
|---|---|---|
| "Read the paper" button | `R3DC_RADI_Q1_JOURNAL_PR.pdf` | the PDF, placed beside `index.html`, or an arXiv link |
| "Code" button | `https://github.com/yourusername/r3dc` | the real repository URL |
| `<meta property="og:*">` | — | add `og:image` (1200×630) once you have a teaser figure |

The OpenReview link (`odj32HFuaj`) and both author ORCIDs are taken from the paper and are already correct.

## Adding figures

The page currently carries no raster images — every visual is drawn in the browser. Figures 1, 8, 9 and 13 from the paper would slot naturally into two places:

- a qualitative strip after the hero (RGB / sparse / GT / D₁ / R̂ / |error| across the four domains — Figure 1);
- beside the negative-result section (Figure 4b, REC against validation RMSE), which would make the inversion argument visible rather than only stated.

Export them at 2× and reference with `<img loading="lazy">` inside a `.wrap` container.

## Numbers

Every figure on the page is taken from the manuscript: Tables 6, 7, 8, 10, 11, 16, 19 and Sections 3–5.1. If a table changes during review, the corresponding row in `index.html` is plain HTML — search for the value and edit in place. The interactive gate demo reads from the `V` array near the top of the `<script>` block, which mirrors Table 16 exactly.

## Content notes

- Colour carries meaning: teal = trusted pixel, plum = doubted pixel, matching the reliability scale the model predicts. Keep that mapping if you restyle.
- Responsive to 360 px, keyboard-focusable, and `prefers-reduced-motion` is respected.
- Fonts load from Google Fonts (Archivo, Source Serif 4, IBM Plex Mono). Self-host them if your institution blocks external font requests.
