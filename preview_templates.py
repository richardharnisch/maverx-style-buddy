"""Generate a single PPTX with one slide per template, filled with Lorem Ipsum."""

import sys
sys.path.insert(0, ".")

LOREM_SHORT = "Lorem ipsum dolor sit amet"
LOREM_TITLE = "Lorem Ipsum Dolor Sit Amet"
LOREM_BODY = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n\n"
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris "
    "nisi ut aliquip ex ea commodo consequat."
)
LOREM_COLUMN = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
    "• Sed do eiusmod tempor\n"
    "• Incididunt ut labore\n"
    "• Dolore magna aliqua"
)


def filler_for(template):
    roles = {area.role for area in template.text_areas}
    has_columns = "left_column" in roles or "right_column" in roles

    title = LOREM_TITLE if "title" in roles else ""
    if has_columns:
        body = f"{LOREM_COLUMN}\n---\n{LOREM_COLUMN}"
    elif "body" in roles or "subtitle" in roles:
        body = LOREM_BODY
    else:
        body = ""
    return title, body


def main():
    guide = load_style_guide("updated_maverx")
    templates = load_slide_templates(guide)

    if not templates:
        print("No templates found — check style_guides/maverx/")
        return

    result = create_presentation.execute(title="Template Preview", style_guide="maverx")
    pid = result["presentation_id"]
    print(f"Created presentation {pid} ({len(templates)} templates)")

    for key, template in templates.items():
        title, body = filler_for(template)
        add_slide.execute(
            presentation_id=pid,
            layout=key,
            title=title,
            body=body,
            speaker_notes=f"Template: {key}\n{template.description or ''}",
        )
        print(f"  + {key}")

    out = export_pptx.execute(presentation_id=pid, filename="template_preview")
    print(f"\nSaved → {out['path']}  ({out['slides']} slides)")


if __name__ == "__main__":
    main()
