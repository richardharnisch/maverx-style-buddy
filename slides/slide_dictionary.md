# Maverx Slide Dictionary

This directory is a reference dictionary for agentic slide workers using
`templates.pptx` as the editable source deck. Use this document to select the
right template slide, understand the Maverx visual system, and populate each
slide without breaking the style.

The image paths listed in each template entry are the canonical preview images
exported from `templates.pptx`. The editable source remains `templates.pptx`.
Machine-readable slide breakdowns live in `template_yaml/`, with
`template_yaml/index.yaml` as the lookup index.

## Worker Workflow

1. Read the YAML breakdown for the available template slide.
2. Match the slide intent to one of the template entries below.
3. Use the matching slide from `templates.pptx` as the editable base.
4. Keep typography, margins, palette, logo placement, footer placement, and
   bottom-right social icons consistent with the template.
5. Create speaker notes for every delivered slide using the required notes
   structure in this document.

## Maverx Style Guidelines

### Typography

- Use Space Grotesk Bold for main slide titles.
- Standard title size: 33 pt.
- Standard subtitle size: 22 pt in Space Grotesk.
- Alternative style title: 33 pt.
- Alternative style subtitle: 25.5 pt, with optional sub-subtitle at 21 pt.
- Use Raleway or Space Grotesk for body copy.
- `templates.pptx` and `instructions.pptx` embed Space Grotesk and Raleway font
  data, but workers should still install or activate Space Grotesk before
  editing/exporting to avoid renderer substitution.
- Standard body copy should be at least 15 pt.
- Main text blocks can be 22-24 pt and bold when the copy is short and clear.
- Subtext should usually be 20 pt or larger, regular weight.
- Dense text slides can use 18 pt, and 14 pt is acceptable only when the slide
  genuinely needs high density.

### Text Rules

- Stay within 3-5 main statements where possible.
- Use no more than 3 sub-bullets under a main statement.
- Do not use bullet symbols for the first or main line of text.
- Use bullet symbols only for supporting subtext.
- Emphasize important words with color, but only sparingly.
- Use empty lines or increased line spacing to create breathing room.
- For short, well-written statements, bold text can work better than bullets.
- Separate statements into distinct text boxes when that gives better layout
  control.
- Avoid slash-heavy wording and unnecessary comma chains.
- For contrast words such as "but" or "or", use a hyphen and italic follow-on
  phrase when it improves readability.
- For sequence words such as "and" or "then", consider splitting the idea into
  separate sub-points.
- Use brackets carefully, especially in subtext, because they add processing
  load.

### Layout And Margins

- Keep titles and subtitles in the established positions unless there is a
  clear layout reason to move them.
- If title or subtitle placement changes, copy the same placement to related
  slides in the section.
- Treat the central content region as the safe area.
- Treat outer bands, corners, and footer/header zones as no-go areas reserved
  for margins, logos, style labels, page details, links, slide numbers, and
  footnotes.
- Use flexible areas around the safe area only when the composition remains
  visually balanced.
- If using asymmetry, make sure the slide still feels stable.
- Equal-importance images should usually receive equal space and equal margins.
- Copy existing elements from another Maverx slide rather than rebuilding them,
  especially icons, compounded icon stories, footer elements, and brand details.

### Color Palette

Use the Maverx palette before introducing any new color.

| Color | Hex | Use |
| --- | --- | --- |
| Primary Dark | `#0D006A` | Titles and body text |
| Dark Purple | `#1A0040` | Cover and section slides |
| Deep Purple | `#3F0576` | Section headers and borders |
| Rose Red | `#EF4453` | Secondary accent |
| Orange | `#F48A28` | CTA and inline highlights |
| Teal | `#00B0F0` | CTA and inline highlights |
| Dark Grey | `#262626` | Captions and footnotes |
| Lavender Tint | `#BCB3FF` | Card backgrounds |
| Rose Tint | `#F7B8C0` | Soft shapes derived from rose |
| Orange Tint | `#FAD0A8` | Soft shapes derived from orange |
| Teal Tint | `#9FE6FF` | Soft shapes derived from teal |
| Off-White | `#F2F2F2` | Background and text on dark backgrounds |
| BG Lavender | `#EDE9FF` | Alternate content background |
| Rose Tint Background | `#FEF0F1` | Soft background derived from rose |
| Orange Background | `#FDEBDB` | Soft background derived from orange |
| Teal Background | `#E7F9FF` | Soft background derived from teal |

Color selection rules:

- On light backgrounds, use hard or darkened colors for highlights.
- On dark backgrounds, use pastel or light tint colors.
- Introduce new colors only by adding or removing brightness from existing
  Maverx colors.
- Use the pipette to match the exact source color before adjusting brightness.
- Use no more than three base colors on a slide unless there is a deliberate
  reason to show complexity.

### Visual Rhythm

- The example slides and assets are inspiration, not rigid templates.
- Be creative with layout, composition, and pacing.
- Not every slide needs the same structure.
- Keep Maverx colors, fonts, logo usage, footer treatment, and overall style
  consistent across the deck.
- Teach theory by introducing the concept, showing an audience-relevant
  example, and applying it in an exercise.
- Multiple concepts may share one exercise if that improves pacing.

### Speaker Notes

Every final slide should include trainer-ready speaker notes with this structure:

- Aim: one clear sentence describing the slide purpose.
- Time: a short timing estimate.
- Instructions: conversational, trainer-ready steps for what to say and do.
- Key discussion points: 3-4 points that must land.
- Link to reality: a concrete story, analogy, or work example.
- Debrief & Summary: one punchy closing line.

## Template Slides

### 01. Deck Title

- Image: `template_images/01-deck-title.png`
- YAML: `template_yaml/01-deck-title.yaml`
- Source slide: `templates.pptx`, slide 1.
- What it does: Opens the deck with the Maverx dark-cover treatment, logo,
  title, subtitle, footer, and social icons.
- How to use it: Replace the title and subtitle only. Keep the dark purple
  background, logo, footer, and bottom-right icons intact.
- When to use it: First slide of a training deck, workshop deck, module deck,
  or major standalone handoff.

### 02. Process Slide

- Image: `template_images/02-process-slide.png`
- YAML: `template_yaml/02-process-slide.yaml`
- Source slide: `templates.pptx`, slide 2.
- What it does: Explains a method or cascade by pairing a definition block with
  a vertical process stack and a guiding question.
- How to use it: Put the core definition on the left, use the right stack for
  stages from strategic to operational, and end with a diagnostic question.
- When to use it: Use for frameworks, maturity ladders, strategic cascades,
  decision flows, and "can you map this for your project?" moments.

### 03. Unstructured Three Section Slide

- Image: `template_images/03-unstructured-three-section-slide.png`
- YAML: `template_yaml/03-unstructured-three-section-slide.yaml`
- Source slide: `templates.pptx`, slide 3.
- What it does: Provides a simple three-part text layout with subtitles,
  bullets, and a wrap-up area.
- How to use it: Assign one idea to each section. Keep each section short, with
  a maximum of 3 supporting points. Use the wrap-up area for takeaways or next
  steps.
- When to use it: Use for lightweight comparison, three-part explanations,
  recap slides, and low-visual theory slides.

### 04. Agenda

- Image: `template_images/04-agenda.png`
- YAML: `template_yaml/04-agenda.yaml`
- Source slide: `templates.pptx`, slide 4.
- What it does: Shows a five-item agenda next to a large image strip.
- How to use it: Replace item labels and descriptions. Keep descriptions brief.
  Use an image that sets the workshop context without competing with the agenda.
- When to use it: Use near the start of a session or module to set pacing and
  expectations.

### 05. Text Slide

- Image: `template_images/05-text-slide.png`
- YAML: `template_yaml/05-text-slide.yaml`
- Source slide: `templates.pptx`, slide 5.
- What it does: Provides a clean, light-background text page with ordered,
  regular, and bulleted text examples.
- How to use it: Use one primary text structure, not all three at once. Keep
  whitespace generous and preserve the blue text hierarchy.
- When to use it: Use for short instructions, definitions, ordered steps,
  simple explanations, or participant prompts.

### 06. Dark Text Slide

- Image: `template_images/06-dark-text-slide.png`
- YAML: `template_yaml/06-dark-text-slide.yaml`
- Source slide: `templates.pptx`, slide 6.
- What it does: Presents text on the Maverx dark background with room for a
  right-side image or visual.
- How to use it: Keep text concise and high contrast. Add an image on the right
  only if it clarifies the concept.
- When to use it: Use for emphasis, transitions, reflective statements, or a
  short message that needs a stronger mood than a light text slide.

### 07. Complex Layout Slide 1

- Image: `template_images/07-complex-layout-slide-1.png`
- YAML: `template_yaml/07-complex-layout-slide-1.yaml`
- Source slide: `templates.pptx`, slide 7.
- What it does: Organizes a decision topic with input categories, structured
  examples, practical questions, and a key takeaway.
- How to use it: Keep the upper row for categories or constraints, the middle
  for evidence/examples, and the bottom row for decision support and takeaway.
- When to use it: Use for risk classification, data-sensitivity guidance,
  decision heuristics, and any concept that needs both examples and rules.

### 08. Complex Layout Slide 2

- Image: `template_images/08-complex-layout-slide-2.png`
- YAML: `template_yaml/08-complex-layout-slide-2.yaml`
- Source slide: `templates.pptx`, slide 8.
- What it does: Compares risk levels in stacked bands with a strong caution and
  decision heuristic at the bottom.
- How to use it: Use the top rows for escalating or contrasting categories.
  Reserve the bottom blocks for the practical warning and "what to do" rule.
- When to use it: Use for policy nuance, risk awareness, governance guidance,
  or cases where "safe" depends on context.

### 09. Complex Layout Slide 3

- Image: `template_images/09-complex-layout-slide-3.png`
- YAML: `template_yaml/09-complex-layout-slide-3.yaml`
- Source slide: `templates.pptx`, slide 9.
- What it does: Introduces an automation or process concept with three example
  cards, then lands the human role and key takeaway.
- How to use it: Put the concept statement under the title, use the cards for
  representative examples, and use the bottom bands for role shift and summary.
- When to use it: Use for automation opportunities, AI use cases, process
  redesign, and "what changes in your role?" explanations.

### 10. Longer Text Slide

- Image: `template_images/10-longer-text-slide.png`
- YAML: `template_yaml/10-longer-text-slide.yaml`
- Source slide: `templates.pptx`, slide 10.
- What it does: Holds dense workshop instructions with numbered sections and
  timing/process detail.
- How to use it: Use only when the audience needs detailed task instructions on
  screen. Break content into numbered blocks and bold the action cues.
- When to use it: Use for breakout-room instructions, multi-step exercises,
  participant assignments, or handoff instructions.

### 11. Tabular Slide

- Image: `template_images/11-tabular-slide.png`
- YAML: `template_yaml/11-tabular-slide.yaml`
- Source slide: `templates.pptx`, slide 11.
- What it does: Gives a trainer-facing timetable with module blocks, activity
  descriptions, notes, and timing.
- How to use it: Populate rows with modules and activities. Use the colored
  timing tags to make pacing scannable. Keep text trainer-oriented.
- When to use it: Use as a facilitator reference, run-of-show, session design
  overview, or internal prep slide.

### 12. Itemized Text Boxes

- Image: `template_images/12-itemized-text-boxes.png`
- YAML: `template_yaml/12-itemized-text-boxes.yaml`
- Source slide: `templates.pptx`, slide 12.
- What it does: Presents five numbered capabilities or outcomes as discrete
  cards with short explanatory text.
- How to use it: Give each card a one-word action label, one short title, and
  one concise explanation. Keep the final wide card for the broadest or
  integrative capability.
- When to use it: Use for learning outcomes, principles, capabilities,
  maturity dimensions, or a memorable five-part model.

### 13. Four Section Slide

- Image: `template_images/13-four-section-slide.png`
- YAML: `template_yaml/13-four-section-slide.yaml`
- Source slide: `templates.pptx`, slide 13.
- What it does: Splits content into four quadrants with colored headers and
  light card backgrounds.
- How to use it: Use one clear category per quadrant. Keep each quadrant to a
  compact paragraph or 3-4 bullets. Preserve the colored header logic.
- When to use it: Use for audience definition, learning objectives, target
  group, good-to-know notes, course setup, or balanced four-part summaries.

### 14. Dark Section Title Slide

- Image: `template_images/14-dark-section-title-slide.png`
- YAML: `template_yaml/14-dark-section-title-slide.yaml`
- Source slide: `templates.pptx`, slide 14.
- What it does: Creates a clean dark divider slide with minimal text.
- How to use it: Add a short section title only. Do not overload it with body
  copy.
- When to use it: Use for major chapter breaks, module transitions, or moments
  where the audience needs a reset.

### 15. Extra Process/Timetable Slide

- Image: `template_images/15-extra-process-timetable-slide.png`
- YAML: `template_yaml/15-extra-process-timetable-slide.yaml`
- Source slide: `templates.pptx`, slide 15.
- What it does: Shows a five-step session journey with connected numbered
  markers and a column for each stage.
- How to use it: Put the high-level sequence in the numbered markers. Use the
  columns for stage labels, purpose, and short content notes.
- When to use it: Use for workshop agendas, learning journeys, project phases,
  onboarding flows, or timetable-overview slides.

### 16. Three Section Slide

- Image: `template_images/16-three-section-slide.png`
- YAML: `template_yaml/16-three-section-slide.yaml`
- Source slide: `templates.pptx`, slide 16.
- What it does: Provides three equal colored vertical cards for parallel
  sections.
- How to use it: Use one label and one short text block per card. Keep the
  three items parallel in grammar and importance.
- When to use it: Use for three lenses, three options, three examples, three
  principles, or a simple compare-and-contrast set.

### 17. Theory / Topic Slides

- Image: `template_images/17-theory-topic-slides.png`
- YAML: `template_yaml/17-theory-topic-slides.yaml`
- Source slide: `templates.pptx`, slide 17.
- What it does: Opens a theory or topic section with a large title and angled
  image treatment.
- How to use it: Replace the numbered section title. Keep the image treatment
  as the main visual anchor.
- When to use it: Use at the start of an educational content block, especially
  before multiple explanatory slides.

### 18. Section Title

- Image: `template_images/18-section-title.png`
- YAML: `template_yaml/18-section-title.yaml`
- Source slide: `templates.pptx`, slide 18.
- What it does: Provides a lighter section divider with the same angled image
  language as the theory slide.
- How to use it: Use a short title and preserve the large open white space.
- When to use it: Use for softer transitions, subsection openers, or moments
  where a full dark divider would feel too heavy.

### 19. Timeline/Process Slide

- Image: `template_images/19-timeline-process-slide.png`
- YAML: `template_yaml/19-timeline-process-slide.yaml`
- Source slide: `templates.pptx`, slide 19.
- What it does: Explains a concept through a definition bar, horizontal
  timeline, and main takeaway.
- How to use it: Put the formal definition at the top, map the process steps
  left to right, and place the memorable takeaway beneath.
- When to use it: Use for customer journeys, process stages, moments of truth,
  lifecycle flows, and stepwise diagnostics.

### 20. Hand-Out Slide

- Image: `template_images/20-hand-out-slide.png`
- YAML: `template_yaml/20-hand-out-slide.yaml`
- Source slide: `templates.pptx`, slide 20.
- What it does: Frames a handout or practical assignment with a dark text panel
  over an image-heavy background.
- How to use it: Keep the title and instructions in the left panel. Use the
  right image to show the work context, artifact, or tool.
- When to use it: Use before a handout, worksheet, individual reflection,
  exercise brief, or participant action.

### 21. Big Question

- Image: `template_images/21-big-question.png`
- YAML: `template_yaml/21-big-question.yaml`
- Source slide: `templates.pptx`, slide 21.
- What it does: Poses a central question using a large illustration and minimal
  text.
- How to use it: Replace the title with the question or prompt. Keep the slide
  visually sparse so participants focus on the question.
- When to use it: Use for reflection prompts, discussion starters, checks for
  understanding, or provocative transitions.

### 22. Break time!

- Image: `template_images/22-break-time.png`
- YAML: `template_yaml/22-break-time.yaml`
- Source slide: `templates.pptx`, slide 22.
- What it does: Announces a break with a strong image and colorful Maverx shape
  overlays.
- How to use it: Keep the break title short. Add return time only if needed and
  place it where it does not fight the image.
- When to use it: Use for scheduled breaks or energy resets between modules.

### 23. Debrief

- Image: `template_images/23-debrief.png`
- YAML: `template_yaml/23-debrief.yaml`
- Source slide: `templates.pptx`, slide 23.
- What it does: Sets up a debrief or reflection moment with a dark overlay and
  live-session photo treatment.
- How to use it: Use the title for the debrief topic. Follow with spoken or
  written questions rather than filling the slide with text.
- When to use it: Use after demos, exercises, simulations, group work, or any
  activity that needs consolidation into learning.
