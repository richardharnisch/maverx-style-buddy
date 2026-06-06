# Presentation Creation Guidelines

Follow these rules on every presentation. They are non-negotiable defaults.

---

## 1. Workflow Order

Always execute in this exact sequence — no skipping, no reordering:

1. `create_presentation` — with the correct style guide name.
2. `list_layouts` — read every entry. Keys and availability vary per style guide and **must be discovered at runtime**.
3. `list_images` — call this if photos or icons would improve the deck (recommended for most decks).
4. `add_slide` — one call per slide.
5. `export_pptx` — saves the finished file.

---

## 2. Layout Selection

**Vary layouts across the deck.** Repetition looks lazy and wastes the template library.

- A 4–6 slide deck → at least 3 different layouts.
- A 7–10 slide deck → at least 4–5 different layouts.
- A 10+ slide deck → at least 6 different layouts.

Match each layout to its purpose:

| Slide purpose | Layout type to choose |
|---|---|
| Opening / cover | Photo-background or branded cover layout |
| Section divider / chapter break | Title-only or decorative accent layout |
| Standard informational content | Title + body layout |
| Comparing two things or ideas | Two-column layout |
| High-impact statement or quote | Large-type title-only layout |
| Multi-point or data-heavy content | Layout with multiple body areas |
| Closing / call to action | Cover-style or clean title-only |

Read each layout's `description` field before choosing it. Look for:
- **Background tone**: dark backgrounds need light text — don't bury content.
- **Photo areas**: if a layout has a photo area, provide a relevant image via `image_overrides` or accept the default.
- **Structural fit**: a two-column layout used for a single point wastes half the slide.

---

## 3. Text Box Roles — One Job Each

Every text area in a template has a declared `role`. **Each role carries different information.** Never copy the same text into two different roles.

| Role | Purpose | Limits |
|---|---|---|
| `title` | The slide's headline — what this slide is about | 3–7 words, no trailing punctuation |
| `subtitle` | A complementary hook, date, or framing line — **not** a restatement of the title | ≤ 12 words |
| `body` | Supporting detail: bullet points or short paragraphs that **add to** the title | 3–6 bullets or 2–3 short paragraphs |
| `left_column` / `right_column` | Parallel content split across two areas | Equal length; each self-contained |
| `caption` | A brief label for a visual element | ≤ 5 words |

**Common mistakes to avoid:**
- Writing the title as a sentence and then repeating it in the body.
- Using the subtitle as a longer version of the title.
- Putting a full paragraph in the `caption` role.
- Leaving `right_column` empty while `left_column` is dense.

---

## 4. White Space and Brevity

Visual breathing room is part of the design — it is not empty space to be filled. When in doubt, write less.

**Per-role word budgets:**

- `title`: 3–7 words. Punchy noun phrase or active verb phrase.
- `subtitle`: 6–12 words. One line.
- `body`: Each bullet point ≤ 15 words. Each paragraph ≤ 3 sentences.
- `caption`: 1–5 words.
- `left_column` / `right_column`: same rules as body, applied independently to each column.

**If you have too much content for one slide:** split it across two slides rather than cramming it in. A slide that is half-full is more readable than a slide that is overflowing.

---

## 5. Content Flow Across the Deck

Each slide must introduce **new** information. Never copy text verbatim from one slide to another.

Structure the deck as:

1. **Opening slide** — title + subtitle hook only. No detailed content yet.
2. **Content slides** — one main idea per slide, progressing from overview to detail.
3. **Section dividers** (if needed) — title only. Let them breathe; they signal transitions, not information.
4. **Closing slide** — call to action, next steps, or summary. Keep it minimal.

Don't front-load all detail on the first content slide. Audiences read decks progressively — reward attention with a logical flow.

---

## 6. Two-Column Layouts

Pass the body argument using the `---` separator to split left and right content:

```
Left column heading or intro

• First left point
• Second left point
• Third left point
---
Right column heading or intro

• First right point
• Second right point
• Third right point
```

Rules for two-column slides:
- Both columns must be **parallel in structure** — either both use bullets, or both use prose. Don't mix.
- Keep both columns **balanced in length** — a long left column and an empty right column looks broken.
- Each column must be **self-contained** — readable on its own without requiring the other column for context.
- Use two-column layouts for genuine comparisons or parallel content — not as a way to squeeze more text onto one slide.

---

## 7. Images

- Call `list_images` before deciding on `image_overrides` — you need to know what is available.
- Match the image tone to the slide content: a technical diagram is out of place on a warm closing slide.
- **Do not override branded or decorative images** (icons, logos, accent graphics) unless you have a clearly better alternative. They were chosen to match the brand.
- When a layout has a photo area and no better image fits, leave the template's default image in place.
- When overriding: use the exact `image_key` returned by `list_images`.

---

## 8. Speaker Notes

Add speaker notes to elaborate on content that didn't fit on the slide. They are optional for title-only or section-divider slides, but recommended for any slide with complex information.

Good speaker notes:
- Explain the *why* behind a bullet point, not just the bullet point again.
- Anticipate audience questions.
- Include any numbers or details that were cut for brevity.
