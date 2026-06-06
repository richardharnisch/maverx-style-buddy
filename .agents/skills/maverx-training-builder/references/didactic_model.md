# Maverx Didactic Model

Every training, every session, every block follows this arc. No exceptions.

| Block | Purpose | Typical slides |
|-------|---------|----------------|
| **Kick-off** | Set learning goals, introduce agenda, set tone | Cover, About this session, Agenda, Timetable, (Mentimeter recap for session ≥ 2) |
| **Theory** | Core concepts explained for the audience | 3–6 theory slides per topic; use Theory/Topic templates |
| **Example** | Concrete, recognizable illustration of the theory | 1–2 example slides per major theory block |
| **Exercise** | Active application — individual, pair, or group work | Exercise brief slide + step/handout slide + Debrief slide |
| **Wrap-up** | Key takeaways, link to practice, next steps | "What stays", "What's next", Resources, Closer |

## Timing distribution (default heuristic — LLM may adjust)

For a 2-hour (120-min) session:

| Block | Share | Minutes |
|-------|-------|---------|
| Kick-off | 10% | ~12 |
| Theory | 35% | ~42 |
| Example | 10% | ~12 |
| Exercise | 30% | ~36 |
| Wrap-up | 10% | ~12 |
| Buffer / break | 5% | ~6 |

Sum of `notes.time` across all slides in a session **must** equal session duration (±5 min). QA checks this.

## Theory ↔ Exercise matching rule

Every Theory block must be followed (within the same session) by at least one Example slide and at least one Exercise slide that drills the same concept. The session planner is prompted to emit an `exercise_target` field on every Theory slide and verify the Exercise block references it.

## Mentimeter recap (sessions ≥ 2)

First slide after the cover is a Mentimeter recap of the previous session's post-bite. Generated as a styled slide + companion `mentimeter_questions.md` file.

## Pre-bite / Post-bite

- **Pre-bite** ships before the session: reading, install instructions, or one reflection question.
- **Post-bite** ships after the session: reflection questions, an assignment, or further reading.
- For Tier 3, **post-bite of session N must reference the artefact pre-bite of session N+1 expects**. The track planner emits this handshake explicitly.
