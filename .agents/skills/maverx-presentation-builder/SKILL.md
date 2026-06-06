---
name: maverx-presentation-builder
description: Create Maverx-branded training presentation artifacts from a validated normalized lesson_plan.json produced by maverx-training-builder. Use when Codex needs to turn the lesson plan into one PPTX deck per session, plus DOCX pre-bites, post-bites, and handouts, using the bundled Maverx slide dictionary, template deck, template YAML, and visual self-review workflow.
---

# Maverx Presentation Builder

This skill turns a final `lesson_plan.json` into delivery artifacts:

- one `.pptx` deck per session
- one pre-bite `.docx` per session
- one post-bite `.docx` per session
- one handout `.docx` per session when `session.handout` is present

Consume only the final lesson plan JSON. Do not re-run intake or redesign the
didactic arc unless the user explicitly asks for lesson-plan changes.

## Resources

- `assets/slides/templates.pptx`: editable Maverx source deck.
- `assets/slides/slide_dictionary.md`: style guide and template selection rules.
- `assets/slides/template_yaml/index.yaml`: machine-readable template lookup.
- `assets/slides/template_yaml/*.yaml`: placeholder and geometry details.
- `assets/slides/template_images/*.png`: full-slide previews for visual reference.
- `scripts/build_maverx_artifacts.py`: deterministic artifact builder.

Read `slide_dictionary.md` before building. Load only the YAML files for
templates you are considering or debugging.

## Workflow

1. Verify the input is a final `lesson_plan.json` with `training` and
   `sessions`.
2. Read `assets/slides/slide_dictionary.md`.
3. Choose the closest Maverx template for each `deck_outline` item:
   - Use `01-deck-title` for the first slide of a session.
   - Use `22-break-time` for `slide_type: "break"`.
   - Use `20-hand-out-slide` for `slide_type: "handout"`.
   - Use `23-debrief` for debrief/consolidation moments.
   - Use content templates by didactic intent, not by visual preference.
4. Source or generate external images when a chosen template needs a more
   relevant image. Store them under the output folder, then replace image
   placeholders carefully while preserving template geometry. If image
   replacement risks breaking the layout, keep the template image and state the
   limitation.
5. Run the builder script:

```bash
uv run python .agents/skills/maverx-presentation-builder/scripts/build_maverx_artifacts.py \
  path/to/lesson_plan.json \
  --template .agents/skills/maverx-presentation-builder/assets/slides/templates.pptx \
  --out-dir path/to/output_dir \
  --clean
```

6. Open the generated PPTX with `python-pptx` to verify it is valid and has the
   expected slide count.
7. Render each PPTX to PDF/PNG using LibreOffice and Poppler when available:

```bash
libreoffice --headless --convert-to pdf --outdir path/to/render_dir path/to/deck.pptx
pdftoppm -png -r 130 path/to/render_dir/deck.pdf path/to/render_dir/slide
```

8. Inspect the PNGs visually. Fix and re-render until satisfied that the deck
   follows the style guide and looks presentation-ready.
9. Return only paths, validation status, and any review notes. Do not paste the
   full lesson plan or document contents into chat.

## Style Rules

- Follow `slide_dictionary.md`; it is authoritative.
- Preserve template logos, footers, social icons, margins, brand colors,
  typography, and image treatments.
- Do not treat template preview PNGs as editable assets; they are references.
- Keep slide text short. Prefer the `key_message` and the strongest
  `suggested_content` items over dumping all lesson-plan text onto a slide.
- Use the lesson-plan `reliability` object in speaker notes so trainers know
  what needs review.
- Every final slide must have trainer-ready speaker notes with:
  `Aim`, `Time`, `Instructions`, `Key discussion points`, `Link to reality`,
  `Debrief & Summary`, and reliability information.
- If no exact template fits, choose the closest match and mention the compromise
  in the final response or artifact manifest.

## Script Notes

The builder script is intentionally conservative. It selects unused source
slides from `templates.pptx`, fills known text placeholders, writes speaker
notes, and creates minimal valid DOCX files without extra Python dependencies.

For unusually large sessions that require more unique slide templates than the
source deck provides, split the session deck, duplicate slides manually with a
presentation-capable tool, or extend the script after testing the duplication
logic on rendered output.

## Done Criteria

- One valid `.pptx` exists per session.
- Required pre/post/handout `.docx` artifacts exist.
- `manifest.json` lists all outputs.
- Rendered PNG inspection has been performed for every deck, unless rendering
  tools are unavailable.
- Any remaining visual compromises are explicitly reported.
