---
name: maverx-training-builder
description: Build a schema-validated Maverx didactic lesson plan JSON file from a training brief. Writes one normalized master JSON file for a single session or multi-session programme, including intake, research-informed didactic arc, deck outline, pre-bites, post-bites, optional handouts, trainer briefs, and per-slide reliability scores. Does not create PPTX, DOCX, visuals, or call external model services.
---

# Maverx Training Builder

This skill turns a training brief into one normalized, schema-validated didactic lesson plan JSON file. The JSON file is the handoff contract for downstream workers such as a PPTX design agent.

The skill focuses exclusively on learning design. It does not generate PowerPoint files, Word documents, visual assets, speaker notes files, or other presentation artifacts. It also does not require external model service configuration.

## When To Trigger

Use this skill when the user asks to:

- build a Maverx training
- design a training programme
- generate a certification track
- create a Lean, Six Sigma, Power BI, AI literacy, or similar training
- create a lesson plan
- make a didactic training plan

## Workflow

### 1. Intake

Load `prompts/system_intake.md` and run the intake conversation.

Ask the required intake questions unless the user already provided a concrete answer:

1. Topic or skill
2. Audience
3. Knowledge level
4. Duration as sessions x minutes per session
5. Primary learning objective
6. Expected participant preparation time before each session
7. Whether handouts or group exercise sheets are wanted
8. If handouts are wanted, the time budget for handout-based work
9. Whether breaks should be included
10. If breaks are wanted, the break time budget per session

For multi-session certification programmes, also gather: certification name, case sector or running context, and tools or tool-agnostic constraints.

Refuse to generate until the intake would validate against `schemas/intake.schema.json`, `completeness_score >= 0.8`, and `vague_fields == []`. If vague, ask one precise follow-up at a time and log it in `follow_ups_asked`.

### 2. Research Autonomously

Before drafting the lesson plan, research autonomously on the internet when current or topic-specific evidence would improve learning outcomes. Prefer authoritative and practical sources:

- primary or official documentation for tools and methods
- reputable educational, professional, government, or academic sources
- recent practitioner guidance when the training topic changes quickly

Record concise research evidence in `research_evidence`. Do not overfit the lesson plan to one article. Use research to improve sequencing, misconceptions, examples, exercises, prerequisites, and reliability scoring.

### 3. Generate The Master JSON File

Produce exactly one JSON object matching `schemas/lesson_plan.schema.json`, then write it to disk as `outputs/<slug>/lesson_plan.json` in the project root (use the `write_lesson_plan` tool). The training can be any length: one 30-minute session, several 60-minute modules, or a full multi-session certification.

Do not paste the JSON into chat. The chat response should only summarize the created file path, validation status, and any issues that require trainer review.

Every session must follow the Maverx didactic model in this exact order:

1. kick-off
2. theory
3. example
4. exercise
5. wrap-up

No exceptions.

Each session must include:

- a didactic deck outline for a downstream PPTX agent
- a pre-bite with prep time and participant task
- a post-bite with follow-up task or reflection
- a trainer brief listing intended skills and learning outcomes
- per-slide reliability scoring so the trainer can review weak or uncertain content

Deck outlines must scale with session duration. For each session, compute `minimum_teach_work_slides = ceil(duration_min / 3)`. The session's `deck_outline` must contain at least that many non-break items. Count `slide_type: "content"` items and `slide_type: "handout"` items toward this minimum; do not count `slide_type: "break"` items. A 60-minute session therefore needs at least 20 non-break deck outline items. Do not reuse a generic 8-slide skeleton for longer sessions. Remember that this is a hard minimum, not a target. Longer sessions can and should have more than `ceil(duration_min / 3)` non-break slides to ensure sufficient depth and variety.

Distribute the deck outline across the five didactic blocks according to their time budgets. A longer theory, example, or exercise block should be split into several focused slide items with distinct learning purposes, not one broad slide. Avoid repeating the same slide pattern in every session; vary titles, examples, checks, misconceptions, prompts, and exercise steps to match the session objective and research evidence.

Each session may include a handout plan with brainstorm questions or exercise prompts, but only if the user requested handouts. When handouts are included, the deck outline must include a `slide_type: "handout"` item during the exercise block. This slide is a placeholder for the predefined handout-work layout; include only the message to show participants and the time budget. The handout slide time budget is part of the exercise block, not extra time outside the didactic arc.

If breaks are included, the deck outline must include one or more `slide_type: "break"` items. A break slide is not a didactic block. It should only state that it is a break and how long the break lasts.

### 4. Verify Before Responding

Validate the final JSON against `schemas/lesson_plan.schema.json` using a JSON Schema validator available in the environment. Then run the bundled dynamic validator:

```bash
uv run --with jsonschema python .agents/skills/maverx-training-builder/scripts/validate_lesson_plan.py \
  .agents/skills/maverx-training-builder/out/<slug>/lesson_plan.json \
  --schema .agents/skills/maverx-training-builder/schemas/lesson_plan.schema.json
```

If a JSON Schema validator is not available, the script still checks dynamic rules such as slide density, didactic order, timing, and reliability fields. If the script reports any issue, fix the JSON before responding.

Set `validation.slide_density_verified` to `true` only after verifying every session meets the slide-density rule.

Also verify:

- every session has the five didactic blocks in the exact required order
- didactic block time budgets plus any break slide durations sum to session duration
- each theory block is reinforced by the example and exercise blocks
- pre-bite time matches the intake expectation
- handout presence matches the intake preference
- break slide presence matches the intake preference
- every deck outline item has a reliability score and rationale
- every session has at least `ceil(duration_min / 3)` non-break deck outline items, with break slides excluded from the count

## Critical Rules

1. The output is a didactic JSON file only.
2. The didactic arc is mandatory: kick-off -> theory -> example -> exercise -> wrap-up.
3. Keep slide-level content conceptual, not visual. Allowed: content slide title, learning purpose, key message, suggested content, break duration, handout message, handout time budget, reliability. Forbidden: layout, template, master slide, colours, fonts, shapes, image placement.
4. Do not use external model service configuration in the skill workflow or output.
5. Refuse vague intake. If the user gave "some people, a few hours, make it good", ask one precise follow-up before generating.
6. The final output must be normalized JSON verified against the schema.
7. Never dump `lesson_plan.json` contents into chat unless the user explicitly asks to inspect the JSON inline.
8. Never create a fixed small deck outline for a long session. Slide count must scale with session duration.
