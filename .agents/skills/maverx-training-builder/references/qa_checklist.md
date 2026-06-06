# Submission Checklist

The QA script (`qa_deck.py`) checks each item below automatically where possible. Items marked **human** require a trainer to glance at the rendered PDFs.

## Editability

- [ ] Every `.pptx` opens cleanly in desktop PowerPoint (no repair prompt). *(human)*
- [ ] All slide content is real text or real tables, never images of text. *(auto: scans for text in placeholders, flags slides with zero text frames)*
- [ ] Titles, bullets, and tables can be edited. *(auto: every slide has ≥1 editable text frame; tables are `pptx.Table`)*

## House style compliance

- [ ] Master layouts are referenced — not redrawn. *(auto: every emitted slide's XML originated from cloning a master slide; no programmatically-added shapes)*
- [ ] Footer (`maverx.nl` + social icons) present on every content slide. *(auto: searches for `maverx.nl` text run in each slide)*
- [ ] Fonts used are Space Grotesk / Raleway / Calibri (master fallback). *(auto: scans run fonts; flags any other font)*
- [ ] Colours fall within the approved palette (see `house_style.md`). *(auto: scans solid fills/run colours; flags hexes that aren't in the palette ±tint range)*

## Didactic arc

- [ ] Each session contains, in order: Kick-off → Theory → Example → Exercise → Wrap-up. *(auto: scans slide `role`s in session_plan.json)*
- [ ] Every Theory slide has at least one matching Exercise slide in the same session. *(auto: `exercise_target` linkage)*
- [ ] Session timing (sum of `notes.time`) equals planned session duration ±5 min. *(auto)*

## Speaker notes

- [ ] All 5 fields present on every slide: Aim, Time, Instructions, Reflective question, Debrief. *(auto: regex on notes text)*

## Companion documents

- [ ] `pre_bite.docx` exists per session.
- [ ] `post_bite.docx` exists per session.
- [ ] `case_handout.docx` exists per session.
- [ ] `track_overview.docx` exists at track level.

## Track narrative (Tier 3)

- [ ] For every consecutive session pair: `post_bite_artefact[N] == next_session_pre_bite_expects_from_prior[N+1]`. *(auto)*
- [ ] Every session's `case_advance` references the same `case.company` and `case.protagonists`. *(auto)*

## Intake

- [ ] All 5 required questions answered.
- [ ] Vague answers triggered at least one follow-up before generation. *(auto: intake log contains ≥1 follow-up if completeness_score < 0.8)*
