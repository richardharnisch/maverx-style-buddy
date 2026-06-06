#!/usr/bin/env python3
"""Build Maverx PPTX and DOCX artifacts from a lesson_plan.json file."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt


PRIMARY_DARK = RGBColor(0x0D, 0x00, 0x6A)
OFF_WHITE = RGBColor(0xF2, 0xF2, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GREY = RGBColor(0x26, 0x26, 0x26)


TEMPLATE_SOURCE = {
    "01-deck-title": 1,
    "02-process-slide": 2,
    "03-unstructured-three-section-slide": 3,
    "04-agenda": 4,
    "05-text-slide": 5,
    "06-dark-text-slide": 6,
    "07-complex-layout-slide-1": 7,
    "08-complex-layout-slide-2": 8,
    "09-complex-layout-slide-3": 9,
    "10-longer-text-slide": 10,
    "11-tabular-slide": 11,
    "12-itemized-text-boxes": 12,
    "13-four-section-slide": 13,
    "14-dark-section-title-slide": 14,
    "15-extra-process-timetable-slide": 15,
    "16-three-section-slide": 16,
    "17-theory-topic-slides": 17,
    "18-section-title": 18,
    "19-timeline-process-slide": 19,
    "20-hand-out-slide": 20,
    "21-big-question": 21,
    "22-break-time": 22,
    "23-debrief": 23,
}


CONTENT_CANDIDATES = {
    "kick-off": [
        "21-big-question",
        "18-section-title",
        "05-text-slide",
        "06-dark-text-slide",
    ],
    "theory": [
        "17-theory-topic-slides",
        "19-timeline-process-slide",
        "03-unstructured-three-section-slide",
        "16-three-section-slide",
        "05-text-slide",
        "18-section-title",
    ],
    "example": [
        "05-text-slide",
        "03-unstructured-three-section-slide",
        "16-three-section-slide",
        "18-section-title",
        "06-dark-text-slide",
    ],
    "exercise": [
        "10-longer-text-slide",
        "21-big-question",
        "05-text-slide",
        "18-section-title",
        "06-dark-text-slide",
    ],
    "wrap-up": [
        "23-debrief",
        "18-section-title",
        "14-dark-section-title-slide",
        "06-dark-text-slide",
        "03-unstructured-three-section-slide",
        "05-text-slide",
    ],
}


@dataclass(frozen=True)
class PlannedSlide:
    template_id: str
    source_slide_number: int
    item: dict[str, Any]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "maverx-training"


def first_text_shapes(slide) -> list[Any]:
    return [
        shape
        for shape in slide.shapes
        if hasattr(shape, "text_frame") and shape.text_frame is not None
    ]


def iter_text_shapes(container):
    for shape in container.shapes:
        if hasattr(shape, "text_frame") and shape.text_frame is not None:
            yield shape
        if hasattr(shape, "shapes"):
            yield from iter_text_shapes(shape)


def clear_text(shape) -> None:
    if hasattr(shape, "text_frame") and shape.text_frame is not None:
        shape.text_frame.clear()


def clear_unused_text_shapes(slide, keep: set[int]) -> None:
    top_level_shapes = first_text_shapes(slide)
    for index, shape in enumerate(top_level_shapes):
        if index not in keep:
            clear_text(shape)
    top_level_elements = {shape.element for shape in top_level_shapes}
    for shape in iter_text_shapes(slide):
        if shape.element not in top_level_elements:
            clear_text(shape)


def set_text(
    shape,
    paragraphs: str | list[str],
    *,
    font: str = "Raleway",
    size: float = 15,
    color: RGBColor = PRIMARY_DARK,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
) -> None:
    if isinstance(paragraphs, str):
        paragraphs = [paragraphs]
    text_frame = shape.text_frame
    text_frame.clear()
    for index, line in enumerate(paragraphs):
        paragraph = text_frame.paragraphs[0] if index == 0 else text_frame.add_paragraph()
        paragraph.text = line
        paragraph.alignment = align
        paragraph.font.name = font
        paragraph.font.size = Pt(size)
        paragraph.font.bold = bold
        paragraph.font.color.rgb = color
        for run in paragraph.runs:
            run.font.name = font
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color


def set_notes(slide, item: dict[str, Any], session: dict[str, Any]) -> None:
    notes = slide.notes_slide.notes_text_frame
    notes.clear()
    title = item.get("title") or item.get("message") or session["title"]
    reliability = item.get("reliability", {})
    notes.text = (
        f"Aim: {item.get('learning_purpose', 'Support the session flow.')} "
        f"Slide focus: {title}\n\n"
        f"Time: Use the timing from the lesson plan for the "
        f"{item.get('didactic_block', item.get('slide_type', 'slide'))} block.\n\n"
        f"Instructions: Present the key message, connect it to the session "
        f"purpose, and keep the discussion anchored in participant work.\n\n"
        f"Key discussion points: {format_points(item)}\n\n"
        f"Link to reality: Relate this slide to {session['brief_for_trainer']['session_purpose']}\n\n"
        f"Debrief & Summary: {item.get('key_message', title)}\n\n"
        f"Reliability: {reliability.get('score', 'n/a')} "
        f"({reliability.get('review_priority', 'n/a')} review). "
        f"{reliability.get('rationale', '')}"
    )


def format_points(item: dict[str, Any]) -> str:
    if item.get("slide_type") == "content":
        points = item.get("suggested_content", [])
        if points:
            return "; ".join(points[:4])
        return item.get("key_message", "")
    if item.get("slide_type") == "break":
        return f"Break slide; duration {item.get('duration_min')} minutes"
    if item.get("slide_type") == "handout":
        return (
            f"Handout work slide; time budget "
            f"{item.get('time_budget_min')} minutes"
        )
    return ""


def choose_templates(deck_outline: list[dict[str, Any]]) -> list[PlannedSlide]:
    used: set[str] = set()
    planned: list[PlannedSlide] = []
    for item in deck_outline:
        slide_type = item.get("slide_type", "content")
        if item.get("slide_n") == 1:
            template_id = "01-deck-title"
        elif slide_type == "break":
            template_id = "22-break-time"
        elif slide_type == "handout":
            template_id = "20-hand-out-slide"
        elif "debrief" in item.get("title", "").lower():
            template_id = "23-debrief"
        else:
            candidates = CONTENT_CANDIDATES.get(
                item.get("didactic_block", ""), ["05-text-slide"]
            )
            template_id = next(
                (candidate for candidate in candidates if candidate not in used),
                candidates[-1],
            )
        if template_id in used:
            template_id = choose_unused_fallback(used, template_id)
        used.add(template_id)
        planned.append(
            PlannedSlide(
                template_id=template_id,
                source_slide_number=TEMPLATE_SOURCE[template_id],
                item=item,
            )
        )
    return planned


def choose_unused_fallback(used: set[str], preferred: str) -> str:
    fallback_order = [
        preferred,
        "05-text-slide",
        "03-unstructured-three-section-slide",
        "16-three-section-slide",
        "06-dark-text-slide",
        "18-section-title",
        "14-dark-section-title-slide",
        "02-process-slide",
    ]
    for candidate in fallback_order:
        if candidate not in used:
            return candidate
    raise ValueError("This session needs more unique template slides than available.")


def keep_and_order_slides(prs: Presentation, source_slide_numbers: list[int]) -> None:
    all_sld_ids = list(prs.slides._sldIdLst)
    keep_indexes = [number - 1 for number in source_slide_numbers]
    keep_sld_ids = [all_sld_ids[index] for index in keep_indexes]
    for sld_id in all_sld_ids:
        prs.slides._sldIdLst.remove(sld_id)
        if sld_id not in keep_sld_ids:
            prs.part.drop_rel(sld_id.rId)
    for sld_id in keep_sld_ids:
        prs.slides._sldIdLst.append(sld_id)


def fill_slide(slide, planned: PlannedSlide, session: dict[str, Any]) -> None:
    item = planned.item
    template_id = planned.template_id
    slide_type = item.get("slide_type", "content")
    if slide_type == "break":
        fill_break(slide, item)
    elif slide_type == "handout":
        fill_handout(slide, item)
    elif template_id == "01-deck-title":
        fill_title(slide, item, session)
    elif template_id == "04-agenda":
        fill_agenda(slide, session)
    elif template_id == "17-theory-topic-slides":
        fill_theory_opener(slide, item)
    elif template_id == "19-timeline-process-slide":
        fill_timeline(slide, item)
    elif template_id == "23-debrief":
        fill_debrief(slide, item)
    else:
        fill_generic_content(slide, item, template_id)
    set_notes(slide, item, session)


def fill_title(slide, item: dict[str, Any], session: dict[str, Any]) -> None:
    shapes = first_text_shapes(slide)
    set_text(shapes[0], session["title"], font="Space Grotesk", size=36, color=OFF_WHITE, bold=True)
    subtitle = item.get("key_message") or session["brief_for_trainer"]["session_purpose"]
    set_text(shapes[-1], subtitle[:115], font="Space Grotesk", size=22, color=OFF_WHITE)


def fill_agenda(slide, session: dict[str, Any]) -> None:
    shapes = first_text_shapes(slide)
    set_text(shapes[0], "Agenda", font="Space Grotesk", size=33, color=PRIMARY_DARK, bold=True)
    blocks = session["didactic_arc"]
    text_frame = shapes[1].text_frame
    text_frame.clear()
    text_frame.paragraphs[0].text = ""
    for block in blocks:
        paragraph = text_frame.add_paragraph()
        paragraph.text = block["block"].title()
        paragraph.font.name = "Space Grotesk"
        paragraph.font.size = Pt(18.5)
        paragraph.font.color.rgb = PRIMARY_DARK
        paragraph = text_frame.add_paragraph()
        paragraph.text = block["learning_purpose"][:82]
        paragraph.font.name = "Raleway"
        paragraph.font.size = Pt(9.5)
        paragraph.font.color.rgb = PRIMARY_DARK


def fill_theory_opener(slide, item: dict[str, Any]) -> None:
    set_text(
        first_text_shapes(slide)[0],
        item["title"],
        font="Space Grotesk",
        size=32,
        color=PRIMARY_DARK,
        bold=True,
    )


def fill_timeline(slide, item: dict[str, Any]) -> None:
    shapes = first_text_shapes(slide)
    set_text(
        shapes[0],
        item["title"],
        font="Space Grotesk",
        size=33,
        color=PRIMARY_DARK,
        bold=True,
    )
    suggested = item.get("suggested_content", [])
    labels = (suggested + ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"])[:5]
    # Template 19 uses text shapes 1-5 for numbered markers and 6-10 for
    # labels beneath the markers.
    for marker, number in zip(shapes[1:6], ["1", "2", "3", "4", "5"]):
        set_text(
            marker,
            number,
            font="Space Grotesk",
            size=24,
            color=WHITE,
            align=PP_ALIGN.CENTER,
        )
    for label_shape, label in zip(shapes[6:11], labels):
        set_text(
            label_shape,
            shorten(label, 11),
            font="Space Grotesk",
            size=7.5,
            color=DARK_GREY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
    if len(shapes) >= 9:
        set_text(shapes[-3], ["DEFINITION", item["key_message"]], font="Raleway", size=10.5, color=OFF_WHITE)
        set_text(shapes[-2], "Main takeaway", font="Space Grotesk", size=15, color=PRIMARY_DARK, bold=True)
        set_text(shapes[-1], item["learning_purpose"], font="Raleway", size=14, color=PRIMARY_DARK)


def fill_break(slide, item: dict[str, Any]) -> None:
    message = item.get("message", "Break time!")
    duration = item.get("duration_min")
    if re.search(r"\b\d+\s*minutes?\b", message, flags=re.IGNORECASE):
        message = "Break time!"
    set_text(
        first_text_shapes(slide)[0],
        [message, f"{duration} minutes"],
        font="Space Grotesk",
        size=33,
        color=PRIMARY_DARK,
        bold=True,
    )
    paragraphs = first_text_shapes(slide)[0].text_frame.paragraphs
    if len(paragraphs) > 1:
        paragraphs[1].font.size = Pt(18)
        paragraphs[1].font.bold = False


def fill_handout(slide, item: dict[str, Any]) -> None:
    shapes = first_text_shapes(slide)
    set_text(shapes[0], "Handout work", font="Space Grotesk", size=33, color=WHITE, bold=True)
    set_text(
        shapes[1],
        [item.get("message", "Work on the handout."), f"Time budget: {item.get('time_budget_min')} minutes"],
        font="Raleway",
        size=15,
        color=WHITE,
    )


def fill_debrief(slide, item: dict[str, Any]) -> None:
    title = item.get("title", "Debrief")
    size = 29 if len(title) > 34 else 33
    set_text(
        first_text_shapes(slide)[0],
        title,
        font="Space Grotesk",
        size=size,
        color=OFF_WHITE,
        bold=True,
    )


def fill_generic_content(slide, item: dict[str, Any], template_id: str) -> None:
    shapes = first_text_shapes(slide)
    if not shapes:
        return
    dark = template_id in {"06-dark-text-slide", "14-dark-section-title-slide"}
    title_color = OFF_WHITE if dark else PRIMARY_DARK
    body_color = OFF_WHITE if dark else PRIMARY_DARK
    set_text(shapes[0], item["title"], font="Space Grotesk", size=33, color=title_color, bold=True)
    body = [item["key_message"], *item.get("suggested_content", [])[:4]]
    keep = {0}
    for index, (shape, text) in enumerate(zip(shapes[1:], body), start=1):
        set_text(shape, text, font="Raleway", size=15, color=body_color)
        keep.add(index)
    clear_unused_text_shapes(slide, keep)


def shorten(value: str, max_len: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= max_len:
        return value
    words = value.split()
    return words[0][:max_len]


def build_session_deck(
    lesson_plan: dict[str, Any],
    session: dict[str, Any],
    template_path: Path,
    out_dir: Path,
) -> Path:
    planned = choose_templates(session["deck_outline"])
    source_numbers = [slide.source_slide_number for slide in planned]
    prs = Presentation(template_path)
    keep_and_order_slides(prs, source_numbers)
    for slide, planned_slide in zip(prs.slides, planned):
        fill_slide(slide, planned_slide, session)
    output = out_dir / (
        f"{lesson_plan['training']['slug']}-session-"
        f"{session['session_n']:02d}.pptx"
    )
    prs.save(output)
    Presentation(output)
    return output


def docx_escape_lines(lines: list[str]) -> str:
    paragraphs = []
    for line in lines:
        safe = escape(line)
        paragraphs.append(f"<w:p><w:r><w:t>{safe}</w:t></w:r></w:p>")
    return "".join(paragraphs)


def write_docx(path: Path, title: str, sections: list[tuple[str, list[str]]]) -> None:
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    body_lines = [title, ""]
    for heading, lines in sections:
        body_lines.extend([heading, *lines, ""])
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{docx_escape_lines(body_lines)}"
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>'
        "</w:sectPr></w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", content_types)
        package.writestr("_rels/.rels", rels)
        package.writestr("word/document.xml", document)


def build_docs(lesson_plan: dict[str, Any], session: dict[str, Any], out_dir: Path) -> list[Path]:
    slug = lesson_plan["training"]["slug"]
    session_prefix = f"{slug}-session-{session['session_n']:02d}"
    outputs: list[Path] = []
    pre = session["pre_bite"]
    pre_path = out_dir / f"{session_prefix}-pre-bite.docx"
    write_docx(
        pre_path,
        f"Pre-bite: {session['title']}",
        [
            ("Purpose", [pre["purpose"]]),
            ("Time", [f"{pre['time_min']} minutes"]),
            ("Participant task", [pre["participant_task"]]),
            (
                "Resources",
                [
                    f"{resource['title']} - {resource['url_or_reference']} ({resource['why_it_is_included']})"
                    for resource in pre.get("resources", [])
                ],
            ),
        ],
    )
    outputs.append(pre_path)
    post = session["post_bite"]
    post_path = out_dir / f"{session_prefix}-post-bite.docx"
    write_docx(
        post_path,
        f"Post-bite: {session['title']}",
        [
            ("Purpose", [post["purpose"]]),
            ("Time", [f"{post['time_min']} minutes"]),
            ("Participant task", [post["participant_task"]]),
            (
                "Resources",
                [
                    f"{resource['title']} - {resource['url_or_reference']} ({resource['why_it_is_included']})"
                    for resource in post.get("resources", [])
                ],
            ),
        ],
    )
    outputs.append(post_path)
    handout = session.get("handout")
    if handout:
        handout_path = out_dir / f"{session_prefix}-handout.docx"
        lines = [f"Time budget: {handout['time_budget_min']} minutes", handout["purpose"]]
        for activity in handout.get("activities", []):
            lines.append(activity["activity_title"])
            lines.extend(activity["instructions"])
            lines.append(f"Participant output: {activity['participant_output']}")
        write_docx(handout_path, f"Handout: {session['title']}", [("Activity", lines)])
        outputs.append(handout_path)
    return outputs


def validate_lesson_plan(plan: dict[str, Any]) -> None:
    for key in ["training", "sessions"]:
        if key not in plan:
            raise ValueError(f"lesson_plan.json is missing required key: {key}")
    for session in plan["sessions"]:
        for key in ["session_n", "title", "deck_outline", "pre_bite", "post_bite"]:
            if key not in session:
                raise ValueError(f"session is missing required key: {key}")
        if not session["deck_outline"]:
            raise ValueError(f"session {session['session_n']} has no deck_outline")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson_plan", type=Path)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--clean", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = json.loads(args.lesson_plan.read_text(encoding="utf-8"))
    validate_lesson_plan(plan)
    out_dir = args.out_dir or args.lesson_plan.parent / "presentation_artifacts"
    if args.clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "lesson_plan": str(args.lesson_plan),
        "outputs": [],
    }
    for session in plan["sessions"]:
        deck = build_session_deck(plan, session, args.template, out_dir)
        docs = build_docs(plan, session, out_dir)
        manifest["outputs"].append(
            {
                "session_n": session["session_n"],
                "pptx": str(deck),
                "docx": [str(path) for path in docs],
            }
        )
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
