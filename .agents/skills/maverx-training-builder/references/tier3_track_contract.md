# Tier 3 Track Contract

A Tier 3 deliverable is a multi-session certification programme with a coherent narrative thread across **all** sessions.

## Required at track level

1. **Backbone**: a named methodology that structures the whole track. Default: DMAIC (8 sessions; Define ×1, Measure ×2, Analyse ×2, Improve ×2, Control ×1) — but the planner may propose another backbone if the topic warrants it. The chosen backbone is recorded in `track_plan.backbone`.
2. **Fictional case**: one company, one problem, one dataset spec. Every session draws on this case. The planner emits:
   - `case.company` — name, sector, size, geography
   - `case.problem_statement`
   - `case.dataset_spec` — tables/columns/realistic ranges so an exercise can synthesise data
   - `case.protagonists` — 2–4 named characters with roles
3. **Per-session contract**: each session has
   - `objective` (one sentence)
   - `depends_on` (list of prior session numbers — Expert content presupposes earlier ones)
   - `case_advance` — what the protagonists *do* with the case this session
   - `post_bite_artefact` — what learners produce after this session
   - `next_session_pre_bite_expects` — name of the artefact the next session's pre-bite references (must equal session N's `post_bite_artefact`)
4. **Track overview document** (`track_overview.docx`): red thread, timing, learning objectives per session, case summary.

## N → N+1 handshake (hard QA check)

For every consecutive pair (N, N+1):

```
track_plan.sessions[N].post_bite_artefact == track_plan.sessions[N+1].next_session_pre_bite_expects_from_prior
```

If this equality fails, `qa_deck.py` reports a `narrative_break` error and the orchestrator re-prompts the planner to fix the pair.

## Difficulty scaling

If the track is structured as Essentials → Advanced → Expert (Tier 2 style nested inside Tier 3), the planner must annotate each session with `level` ∈ {essentials, advanced, expert} and assert (in `dependencies`) that no Advanced session is reachable before its Essentials prerequisites.

## Case handout per session

Every session ships a `case_handout.docx` with three parts:

1. **The case so far** — recap, including the post-bite artefact from the prior session.
2. **Today's situation** — new data, new constraints, new ask.
3. **Working space** — model reference sheet + blank tables/prompts for the learner to fill in.
