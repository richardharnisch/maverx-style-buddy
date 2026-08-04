# QA Checklist

## Intake

- [ ] Intake validates against `schemas/intake.schema.json`.
- [ ] Completeness score is at least 0.8.
- [ ] `vague_fields` is empty.
- [ ] Preparation time expectation is captured.
- [ ] Handout preference is captured.
- [ ] If handouts are requested, handout time budget is captured.
- [ ] Break preference is captured.
- [ ] If breaks are requested, break time budget is captured.

## Research

- [ ] Topic-specific research was performed when useful.
- [ ] Sources are relevant to learning outcomes.
- [ ] Sources are summarized rather than copied.
- [ ] Research is used to improve sequencing, misconceptions, examples, exercises, or reliability scoring.

## Lesson Plan JSON

- [ ] Output validates against `schemas/lesson_plan.schema.json`.
- [ ] `scripts/validate_lesson_plan.py` passes for schema checks and dynamic checks.
- [ ] There is exactly one master JSON object for the training.
- [ ] The JSON object is written to `out/<slug>/lesson_plan.json`.
- [ ] The JSON object is not pasted into chat unless explicitly requested.
- [ ] No PPTX, DOCX, visual asset, slide master, template, layout, colour, font, or external service instruction appears in the output.

## Didactic Arc

- [ ] Every session contains the five blocks in exact order: kick-off, theory, example, exercise, wrap-up.
- [ ] If breaks are not included, didactic block time budgets sum to the session duration.
- [ ] If breaks are included, didactic block time plus break slide time sums to the session duration.
- [ ] Theory is reinforced by the example and exercise.
- [ ] Exercise creates active application and a clear participant output.
- [ ] Wrap-up connects to post-bite and, where relevant, the next session.

## Session Requirements

- [ ] Every session has a didactic deck outline.
- [ ] Every session has at least `ceil(duration_min / 3)` non-break deck outline items.
- [ ] Break slides are excluded from the slide-density count.
- [ ] Long theory, example, and exercise blocks are split into multiple focused deck outline items rather than one generic slide.
- [ ] Multi-session programmes do not repeat the same 8-slide structure across sessions.
- [ ] Every session has a pre-bite.
- [ ] Every session has a post-bite.
- [ ] Every session has a trainer brief with intended skills and learning outcomes.
- [ ] Optional handouts match the user's preference and time budget.
- [ ] If handouts are included, the deck outline includes a `slide_type: "handout"` item with a participant-facing message and time budget inside the exercise block.
- [ ] If breaks are included, the deck outline includes a `slide_type: "break"` item with break duration.

## Reliability

- [ ] Every deck outline item has a reliability score from 0 to 1.
- [ ] Every reliability score has a rationale.
- [ ] Review priority is one of low, medium, or high.
- [ ] Scores below 0.75 are easy for the trainer to identify and review.
