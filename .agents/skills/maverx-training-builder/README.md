# Maverx Training Builder

An agentic skill that turns a training brief into one normalized, schema-validated Maverx didactic lesson plan JSON file.

The JSON file is intended for downstream agentic workers, especially a PPTX design agent. This skill does not create slides, decks, Word documents, visual assets, or files from a command-line workflow.

## Output

One file at `out/<slug>/lesson_plan.json`, containing one JSON object matching `schemas/lesson_plan.schema.json`.

The agent should not paste the JSON into chat. The chat response should report the file path, validation status, and any review issues.

The master JSON contains:

- validated intake summary
- autonomous research evidence used for didactic choices
- programme-level learning outcomes
- one or more sessions
- the required Maverx didactic arc for every session
- a didactic deck outline for each session
- pre-bite and post-bite plans
- optional handout plans
- trainer-facing skills and learning outcomes
- per-slide reliability indicators

## How It Works

1. **Intake**: use `prompts/system_intake.md` and validate against `schemas/intake.schema.json`.
2. **Research**: browse autonomously when current or topic-specific evidence improves didactic quality.
3. **Lesson planning**: create one master JSON file matching `schemas/lesson_plan.schema.json`.
4. **Validation**: verify schema compliance and the required didactic arc before responding.

## Required Didactic Arc

Every session must follow this order:

1. kick-off
2. theory
3. example
4. exercise
5. wrap-up

No exceptions.

## Non-Goals

This skill does not:

- generate `.pptx`
- generate `.docx`
- choose visual layouts
- reference slide masters or templates
- call external model services
- require external model service configuration
- expose a command-line interface

## Files

- `SKILL.md`: agent-facing workflow
- `prompts/system_intake.md`: intake gate
- `prompts/system_lesson_plan.md`: normalized JSON drafting contract
- `schemas/intake.schema.json`: intake validation
- `schemas/lesson_plan.schema.json`: final output validation
- `references/didactic_model.md`: Maverx didactic model
- `references/qa_checklist.md`: manual validation checklist

## Validation

The final response should state whether JSON Schema validation was completed. If validation fails, fix the JSON before returning it.

Recommended local validation, when a JSON file exists:

```bash
uv run python -m jsonschema -i .agents/skills/maverx-training-builder/out/<slug>/lesson_plan.json .agents/skills/maverx-training-builder/schemas/lesson_plan.schema.json
```
