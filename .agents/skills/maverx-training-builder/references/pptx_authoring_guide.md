# PPTX Authoring Guide

## Golden rule

**Never redraw shapes from the master.** Always clone an existing styled slide and replace its text. The Maverx style guide says it explicitly: *"Copying elements from another slide (or deck) is always better"*.

## How the builder works

1. Open `assets/maverx_master.pptx` as the source presentation.
2. For every slide in the session plan, look up `template_slide_idx` in `assets/template_catalog.json` based on the slide's `role`.
3. Deep-copy that slide's XML into the output presentation (preserving theme, fonts, colours, footer).
4. Replace placeholder text in the cloned slide:
   - The first `title` shape with text frame → slide title.
   - Subsequent text frames → body bullets in order.
   - Existing tables → rebuilt with new rows; cell formatting preserved.
5. Write speaker notes into the slide's notes part.

## Editability rules

- **All text must be in text frames** (`shape.has_text_frame`). Never paste images of text.
- **Tables are real `python-pptx` tables**. Never raster.
- **Charts** (if added) use `python-pptx` chart APIs.
- **Logos / footers** are inherited from the cloned slide. Do not re-draw them.

## When the planner asks for a slide role that has no template

The planner is restricted (via the system prompt and `slide.schema.json`) to roles defined in `template_catalog.json`. If it ever emits an unknown role, `build_deck.py` falls back to `default_text` and `qa_deck.py` flags the slide for review.

## Swapping the master

If Maverx updates the deck:

1. Replace `assets/maverx_master.pptx` with the new file.
2. Run `python scripts/inspect_master.py assets/maverx_master.pptx assets/`.
3. Open the new master, find the slide indices for each semantic role, and update `assets/template_catalog.json`.
4. Re-run the QA suite on a known-good intake to confirm visual parity.
