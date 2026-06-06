# QA Checklist

## Intake

- [ ] Intake validates against `schemas/intake.schema.json`.
- [ ] Completeness score is at least 0.8.
- [ ] `vague_fields` is empty.
- [ ] Preparation time expectation is captured.
- [ ] Handout preference is captured.
- [ ] If handouts are requested, handout time budget is captured.

## Research

- [ ] Topic-specific research was performed when useful.
- [ ] Sources are relevant to learning outcomes.
- [ ] Sources are summarized rather than copied.
- [ ] Research is used to improve sequencing, misconceptions, examples, exercises, or reliability scoring.

## Lesson Plan JSON

- [ ] Output validates against `schemas/lesson_plan.schema.json`.
- [ ] There is exactly one master JSON object for the training.
- [ ] The JSON object is written to `out/<slug>/lesson_plan.json`.
- [ ] The JSON object is not pasted into chat unless explicitly requested.
- [ ] No PPTX, DOCX, visual asset, slide master, template, layout, colour, font, or external service instruction appears in the output.

## Didactic Arc

- [ ] Every session contains the five blocks in exact order: kick-off, theory, example, exercise, wrap-up.
- [ ] Block time budgets sum to the session duration.
- [ ] Theory is reinforced by the example and exercise.
- [ ] Exercise creates active application and a clear participant output.
- [ ] Wrap-up connects to post-bite and, where relevant, the next session.

## Session Requirements

- [ ] Every session has a didactic deck outline.
- [ ] Every session has a pre-bite.
- [ ] Every session has a post-bite.
- [ ] Every session has a trainer brief with intended skills and learning outcomes.
- [ ] Optional handouts match the user's preference and time budget.

## Reliability

- [ ] Every deck outline item has a reliability score from 0 to 1.
- [ ] Every reliability score has a rationale.
- [ ] Review priority is one of low, medium, or high.
- [ ] Scores below 0.75 are easy for the trainer to identify and review.
