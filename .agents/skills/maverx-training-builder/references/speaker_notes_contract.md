# Speaker Notes Contract

Every slide's notes field MUST contain all 5 sections, in this exact order and format. The QA script greps for these markers and fails the build if any are missing.

```
**Aim:** <one sentence — what this slide accomplishes for the learner>
**Time:** <integer> min
**Instructions:**
1. <do this>
2. <then this>
3. <…>
**Reflective question:** <one open question to pose to the room>
**Debrief:** <2–3 sentences summarising what should have landed>
```

Rules:

- `Aim` is one sentence. No bullets.
- `Time` is an integer number of minutes, suffixed with ` min`. The QA script sums these per session and checks against the planned session duration (±5 min tolerance).
- `Instructions` is a numbered list with at least one step.
- `Reflective question` is one sentence ending in `?`.
- `Debrief` is 2–3 sentences (no list).

When the slide is a pure transition (e.g. a section divider), still emit all 5 fields — `Instructions` can be a single step like "1. Pause; click through.", `Reflective question` can be the framing question for the upcoming block.
