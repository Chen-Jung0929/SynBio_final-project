# Implementation Notes — Animation-Assisted Slide Deck

This presentation utilizes a custom slideshow framework designed under the aesthetic constraints of the **Kami** design system.

---

## 1. Directory Structure

All presentation assets, HTML templates, CSS rules, and JavaScript logic are encapsulated inside the `slides/` directory to prevent workspace pollution:

```
SynBio final/
  slides/
    index.html                   <- Paging framework & slide markup
    styles.css                   <- Kami parchment & ink-blue design system styles
    README_ANIMATION.md          <- This implementation note
    scripts/
      anime.min.js               <- Local copy of Anime.js (DOM animation engine)
      d3.min.js                  <- Local copy of D3.js (SVG scientific plotting)
      rough-notation.js          <- Local copy of Rough Notation (sketch annotations)
      presentation.js            <- Presentation routing and animation triggers
    assets/
      (logos, diagrams, and static images)
```

---

## 2. Animation Engine & Library Allocation

| Scene / Element | Slide | Library Used | Rationale / Motion Concept |
| :--- | :--- | :--- | :--- |
| **Scene 1 — Why AND Gate?** | Slide 4 | `D3.js` & `Anime.js` | Generates 1D overlap distributions and animates their physical merge into a 2D scatter plot before drawing decision thresholds. |
| **Scene 2 — Computational Flow** | Slide 6 | `Anime.js` | Reveals flowchart stages sequentially with arrows. Supports interactive clicks to inspect detail cards. |
| **Volcano Plot** | Slide 7 | `D3.js` & `Anime.js` | Draws 200 gene points that fade in and highlights the top candidate pair (UBE2S & CCR6). |
| **Scene 3 — ML & SHAP Values** | Slide 8 | `D3.js`, `Anime.js` & `Rough Notation` | Animates horizontal bars growing dynamically from a center zero-axis representing positive/negative prediction forces (push/pull logic). Highlights disclaimer with rough notation box. |
| **Scene 4 — Selection & Bounds** | Slide 9 | `D3.js` & `Rough Notation` | Draws normal vs. tumor clusters, overlays decision thresholds ($K_A, K_B$), and highlights correlation caveat (`r = 0.714`). |
| **Scene 5 — Hill-Equation Kinetics** | Slide 10 | `Anime.js` & `D3.js` | Sequentially reveals mathematical terms, sweeps a colored gradient contour heatmap representing non-linear activation kinetics, and draws the 0.25 threshold boundary. |
| **Scene 6 — Transferability** | Slide 11 | `D3.js`, `Anime.js` & `Rough Notation` | Shows side-by-side metric comparisons between Discovery and Validation datasets. Animates bars rising and draws a prominent hand-drawn border around the validation sensitivity collapse warning. |

---

## 3. Reduced-Motion Mode

A strict accessibility fallback is built into the presentation:
- **How to Toggle**: Click the **"Reduced Motion: OFF"** button in the top-right corner of the slides, or press the **`R`** key on your keyboard.
- **Under the Hood**:
  - The `document.body` gets tagged with the `.reduced-motion` CSS class.
  - This immediately bypasses all CSS transition duration variables (`0s !important`), pauses active Anime.js timelines, and forces elements to render in their final states instantly.
  - When loading D3 visualization code, the `isReducedMotion` state is checked. If `true`, the code renders fully loaded shapes, boundary lines, heatmap cells, and annotations directly without triggering animations.
  - The UI button turns red, reading **"Reduced Motion: ON"**.

---

## 4. How to Preview the Deck

The slide deck is self-contained and has **no external internet dependencies** (all javascript engines are stored locally under `scripts/` and fonts utilize local system stacks with Google webfont fallbacks).

1. Open a terminal in the project directory:
   ```bash
   cd "SynBio final/slides"
   ```
2. You can open `index.html` directly in any web browser:
   - On macOS: `open index.html`
   - On Windows: `start index.html`
   - Or run a local python webserver to preview:
     ```bash
     python3 -m http.server 8000
     ```
     Then navigate to `http://localhost:8000` in your web browser.
