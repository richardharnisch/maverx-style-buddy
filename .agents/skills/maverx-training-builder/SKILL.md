---
name: maverx-training-builder
description: Build a schema-validated Maverx didactic lesson plan JSON from a training brief. Produces one normalized master JSON for a single session or multi-session programme, including intake, research-informed didactic arc, deck outline, pre-bites, post-bites, optional handouts, trainer briefs, and per-slide reliability scores. Does not create PPTX, DOCX, visuals, or call external model services.
---

# Maverx Training Builder

This skill turns a training brief into one normalized, schema-validated didactic lesson plan JSON. The JSON is the handoff contract for downstream workers such as a PPTX design agent.

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

For multi-session certification programmes, also gather: certification name, case sector or running context, language, and tools or tool-agnostic constraints.

Refuse to generate until the intake would validate against `schemas/intake.schema.json`, `completeness_score >= 0.8`, and `vague_fields == []`. If vague, ask one precise follow-up at a time and log it in `follow_ups_asked`.

### 2. Research Autonomously

Before drafting the lesson plan, research autonomously on the internet when current or topic-specific evidence would improve learning outcomes. Prefer authoritative and practical sources:

- primary or official documentation for tools and methods
- reputable educational, professional, government, or academic sources
- recent practitioner guidance when the training topic changes quickly

Record concise research evidence in `research_evidence`. Do not overfit the lesson plan to one article. Use research to improve sequencing, misconceptions, examples, exercises, prerequisites, and reliability scoring.

### 3. Generate The Master JSON

Produce exactly one JSON object matching `schemas/lesson_plan.schema.json`. The training can be any length: one 30-minute session, several 60-minute modules, or a full multi-session certification.

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

Each session may include a handout plan with brainstorm questions or exercise prompts, but only if the user requested handouts.

### 4. Verify Before Responding

Validate the final JSON against `schemas/lesson_plan.schema.json` using a JSON Schema validator available in the environment. If a validator is not available, perform a manual field-by-field check against the schema and say that validation was manual.

Also verify:

- every session has the five didactic blocks in the exact required order
- block time budgets sum to session duration
- each theory block is reinforced by the example and exercise blocks
- pre-bite time matches the intake expectation
- handout presence matches the intake preference
- every deck outline item has a reliability score and rationale
- no slide visual, layout, master, PPTX, DOCX, or external service instructions are present

## Critical Rules

1. The output is didactic JSON only.
2. The didactic arc is mandatory: kick-off -> theory -> example -> exercise -> wrap-up.
3. Keep slide-level content conceptual, not visual. Allowed: slide title, learning purpose, key message, suggested content, interaction, reliability. Forbidden: layout, template, master slide, colours, fonts, shapes, image placement.
4. Do not use external model service configuration in the skill workflow or output.
5. Refuse vague intake. If the user gave "some people, a few hours, make it good", ask one precise follow-up before generating.
6. The final output must be normalized JSON verified against the schema.
