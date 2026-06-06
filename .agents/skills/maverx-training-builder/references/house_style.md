# Maverx House Style (distilled from the supplied Style Guide deck)

This file is the single source of truth for visual rules. The builder reads it; QA validates against it.

## Palette (exact hex)

| Role | Hex | Use |
|------|-----|-----|
| Primary Dark | `#0D006A` | Titles, body text |
| Dark Purple | `#1A0040` | Cover & section slides |
| Deep Purple | `#3F0576` | Section headers, borders |
| Rose Red (accent) | `#EF4453` | Secondary accent |
| Orange (CTA) | `#F48A28` | CTA, inline highlights |
| Teal (CTA) | `#00B0F0` | CTA, inline highlights |
| Dark Grey | `#262626` | Captions, footnotes |
| Lavender Tint | `#BCB3FF` | Card backgrounds |
| Rose Tint | `#F7B8C0` | Derived from Rose |
| Orange Tint | `#FAD0A8` | Derived from Orange |
| Teal Tint | `#9FE6FF` | Derived from Teal |
| Off-White | `#F2F2F2` | Background / text on dark |
| BG Lavender | `#EDE9FF` | Alt content background |
| Rose BG | `#FEF0F1` | Soft shapes |
| Orange BG | `#FDEBDB` | Soft shapes |
| Teal BG | `#E7F9FF` | Soft shapes |

**Color rules**

- Lighter background → darker highlights. Pastels only on dark backgrounds.
- Never more than 3 base colors per slide.
- New colors only by brightening/darkening existing ones (use the pipet).

## Typography

| Element | Font | Size |
|---------|------|------|
| Title | Space Grotesk Bold | 33 pt |
| Subtitle | Space Grotesk | 22 pt |
| Sub-subtitle | Space Grotesk | 21 pt |
| Body | Raleway *or* Space Grotesk | 15 pt+ |
| Bulleted sub-text | Raleway | 20 pt+ regular (18 pt acceptable on dense slides) |

- Never start the first line of a paragraph with `•`. Bullets only on sub-items.
- Indent sub-items with one Tab.

## Copy rules

- Avoid `/` and `,` where possible. Prefer "left or right" or "left & right" over "left/right".
- Emphasise important words by colouring them (Rose / Orange / Teal), not bold-only.
- Use empty lines or larger line spacing between points instead of dense paragraphs.

## Layout discipline

- Respect the master's Safe / Flexible / No-go zones — do not place content in No-go bands.
- Don't move the title or subtitle. If you must, propagate the new placement to **every** slide in the deck.
- Footer on every content slide: `maverx.nl` + social icons (these live on the master layouts; do not remove).
- Copying an existing styled element from the master is always preferred over drawing a new one — this is why the builder clones template slides instead of building layouts from scratch.

## Section dividers

The didactic blocks each get a full-bleed purple divider from the master:

- Pre-training / Kick-off → master slide 18
- Theory & Topic → master slide 21
- Exercise → master slide 30
- Wrap-up & Next Steps → master slide 34

(See `assets/template_catalog.json` for the full role → slide-index mapping.)
