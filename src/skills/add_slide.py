"""Skill: append a slide to an in-progress presentation using a named layout template."""

import logging

from pptx.util import Pt

from src.skills import _store
from src.style_guides.loader import load_slide_templates
from src.style_guides.schema import SlideTemplate, TextArea

log = logging.getLogger(__name__)

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "add_slide",
        "description": (
            "Add a slide to the presentation using a named layout template. "
            "Call list_layouts first to discover valid layout keys and their descriptions. "
            "Slides with image areas will automatically include their default template images. "
            "Use 'image_overrides' to replace a specific image slot with a different image from list_images."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "presentation_id": {"type": "string"},
                "layout": {
                    "type": "string",
                    "description": "Layout key from list_layouts (e.g. 'title_slide_1', 'titeldia_3').",
                },
                "title": {"type": "string", "description": "Text for the title area."},
                "body": {
                    "type": "string",
                    "description": (
                        "Text for the body/subtitle area. "
                        "For two-column layouts, separate left and right with \\n---\\n."
                    ),
                },
                "speaker_notes": {"type": "string"},
                "image_overrides": {
                    "type": "array",
                    "description": (
                        "Optional: override default images. Each item: "
                        "{\"role\": \"background\", \"image_key\": \"img_abc123\"}. "
                        "Get image keys from list_images."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "image_key": {"type": "string"},
                        },
                        "required": ["role", "image_key"],
                    },
                },
            },
            "required": ["presentation_id", "layout"],
        },
    },
}


# ── Layout lookup ──────────────────────────────────────────────────────────────

def _find_pptx_layout(prs, layout_name: str):
    """Search all slide masters for a layout by name."""
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if layout.name == layout_name:
                return layout
    log.warning("Layout '%s' not found in any master; using first available", layout_name)
    return prs.slide_masters[0].slide_layouts[0]


# ── Text box creation ──────────────────────────────────────────────────────────

# MSO auto shape preset name → integer ID used by add_shape()
_PRESET_ID: dict[str, int] = {
    "rect": 1,
    "roundRect": 5,
    "ellipse": 9,
    "diamond": 4,
    "triangle": 7,
    "snip1Rect": 88,
    "snip2SameRect": 89,
    "snipRoundRect": 84,
}


def _hex_to_rgb(hex_color: str):
    from pptx.dml.color import RGBColor
    h = hex_color.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _add_text_box(slide, area: TextArea, text: str) -> None:
    from pptx.enum.text import PP_ALIGN

    _ALIGN_MAP = {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
        "justify": PP_ALIGN.JUSTIFY,
    }

    if area.shape_preset and area.shape_preset in _PRESET_ID:
        shape_id = _PRESET_ID[area.shape_preset]
        shape_obj = slide.shapes.add_shape(shape_id, area.left, area.top, area.width, area.height)
        if area.corner_radius is not None:
            try:
                shape_obj.adjustments[0] = area.corner_radius
            except Exception:
                pass
        if area.bg_color:
            try:
                shape_obj.fill.solid()
                shape_obj.fill.fore_color.rgb = _hex_to_rgb(area.bg_color)
            except Exception:
                pass
        else:
            try:
                shape_obj.fill.background()  # transparent
            except Exception:
                pass
        tf = shape_obj.text_frame
    else:
        box = slide.shapes.add_textbox(area.left, area.top, area.width, area.height)
        tf = box.text_frame

    tf.word_wrap = True
    tf.text = text

    align_val = _ALIGN_MAP.get(area.alignment) if area.alignment else None
    for para in tf.paragraphs:
        if align_val is not None:
            para.alignment = align_val
        for run in para.runs:
            if area.font_name:
                run.font.name = area.font_name
            if area.font_size_pt:
                run.font.size = Pt(area.font_size_pt)
            if area.bold is not None:
                run.font.bold = area.bold
            if area.italic is not None:
                run.font.italic = area.italic
            if area.underline is not None:
                run.font.underline = area.underline
            if area.color:
                try:
                    run.font.color.rgb = _hex_to_rgb(area.color)
                except Exception:
                    pass


# ── Role → content mapping ────────────────────────────────────────────────────

def _build_role_map(title: str, body: str) -> dict[str, str]:
    left, _, right = body.partition("\n---\n")
    return {
        "title": title,
        "subtitle": body,
        "body": body,
        "left_column": left.strip(),
        "right_column": right.strip() if right else "",
        "caption": "",  # captions are decorative; skip if no explicit content
    }


# ── Image placement ───────────────────────────────────────────────────────────

def _place_images(slide, template, guide, image_overrides: list[dict]) -> list[str]:
    """Add image shapes to slide from template image areas. Returns list of placed roles."""
    if not template.image_areas:
        return []

    from src.style_guides.loader import PROJECT_ROOT

    layouts_dir = PROJECT_ROOT / guide.layouts_dir if guide.layouts_dir else None
    if not layouts_dir:
        return []
    images_dir = layouts_dir / "images"

    override_map = {o["role"]: o["image_key"] for o in (image_overrides or [])}
    placed = []

    for ia in template.image_areas:
        image_key = override_map.get(ia.role, ia.image_key)
        if not image_key:
            continue
        # Find the image file (any extension)
        matches = list(images_dir.glob(f"{image_key}.*")) if images_dir.exists() else []
        img_path = next((m for m in matches if m.suffix != ".yaml"), None)
        if not img_path:
            log.warning("Image file not found for key '%s'", image_key)
            continue
        try:
            slide.shapes.add_picture(str(img_path), ia.left, ia.top, ia.width, ia.height)
            placed.append(ia.role)
            log.debug("Placed image role='%s' key='%s'", ia.role, image_key)
        except Exception as e:
            log.warning("Could not place image '%s': %s", image_key, e)

    return placed


# ── execute ────────────────────────────────────────────────────────────────────

def execute(
    presentation_id: str,
    layout: str,
    title: str = "",
    body: str = "",
    speaker_notes: str = "",
    image_overrides: list | None = None,
) -> dict:
    log.debug("add_slide: prs=%s layout=%s", presentation_id, layout)
    prs, guide, _ = _store.get(presentation_id)

    # Load the YAML template for this layout key
    templates = load_slide_templates(guide)
    template = templates.get(layout)
    if template is None:
        available = list(templates.keys())
        log.warning("Unknown layout '%s'. Available: %s", layout, available)
        return {
            "error": f"Layout '{layout}' not found.",
            "available_layouts": available,
            "hint": "Call list_layouts to see all valid keys.",
        }

    # Add slide with the correct PowerPoint layout (for background graphics)
    pptx_layout = _find_pptx_layout(prs, template.layout_name)
    slide = prs.slides.add_slide(pptx_layout)
    log.debug("Added slide with PPTX layout: '%s'", pptx_layout.name)

    # Place images from template catalog
    placed_images = _place_images(slide, template, guide, image_overrides or [])

    # Fill text areas using exact geometry from the template YAML
    role_map = _build_role_map(title, body)
    filled = []
    for area in template.text_areas:
        content = role_map.get(area.role, "")
        if not content:
            log.debug("Skipping area role='%s' (no content provided)", area.role)
            continue
        _add_text_box(slide, area, content)
        log.debug("Filled area role='%s' text='%s'", area.role, content[:60])
        filled.append(area.role)

    if speaker_notes:
        slide.notes_slide.notes_text_frame.text = speaker_notes

    slide_index = len(prs.slides) - 1
    log.info(
        "Slide %d added: layout='%s' filled=%s images=%s prs=%s",
        slide_index, layout, filled, placed_images, presentation_id,
    )
    return {
        "slide_index": slide_index,
        "layout": layout,
        "filled_areas": filled,
        "placed_images": placed_images,
    }
