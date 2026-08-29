---
name: generate-image
description: >-
  Use when Daniel asks for an image, diagram, or visual — an exhibit mock-up for
  a drill, a chart to practise reading, or a visual for a note. Also use when a
  drill would be better with a picture than with prose.
disable-model-invocation: false
metadata:
  version: "0.1.0"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: creative
  tags: [image, fal-ai, generation, cost-aware]
  related_skills: [high-yield-drills]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "Daniel directive 2026-08-29 — small skill, Fal.ai tool usage and best practices only"
    house_reference: "nova-field-image-generation (vulcan) — house Fal.ai workflow patterns"
category: creative
---

# Generate Image

## Overview

Image generation through the **`fal-ai` MCP**. Deliberately small: this skill covers tool usage and the handful of practices that prevent waste. It is not a design skill.

⚠️ **The `fal-ai` MCP is not installed on Palladia yet.** Tracked as an open install item. Until it is, say so rather than attempting a call.

## When to Use

Daniel asks for an image or diagram. A drill needs a visual — an exhibit to read, a chart to interpret. A note would land better with a picture.

**Not for:** extracting an existing exhibit from a casebook (that is `casebook-case-extract`), or reading a chart that already exists (that is a vision task, not a generation one).

## Credentials

The key is `FAL_ADMIN_KEY` — Nova Caelum's fleet-wide fal.ai account key, resolved at MCP-connect time by a `headersHelper`, never written into config.

**Never read, echo, log, or write the value.** Reference it by name only. If it is missing, report that the credential is unavailable — never print what you found.

⚠️ **Open trust-boundary question.** `FAL_ADMIN_KEY` currently lives in the Claude-fleet BWS project, while olympus1 authenticates against `novacaelum_olympus`. These are deliberately walled apart. Installing this MCP on Palladia needs that resolved first — the same unresolved issue as the Exa and Browserbase credentials.

## Cost

**fal.ai bills per inference. Every generation spends real money.**

- One image per request unless Daniel asks for variations.
- Never fan out a batch to "see options" without asking first.
- Prefer fixing the prompt over regenerating repeatedly.

Volume is a cost decision, not a free tool call.

## Procedure

1. **Clarify the function first.** What is the image *for* — a drill exhibit, a diagram, an illustration? Function determines aspect ratio and content density. Use `clarify` if it is ambiguous; one question is cheaper than one wasted generation.
2. **Write a specific prompt.** Name the subject, the style, and the composition. Vague prompts produce generic output and a second billed call.
3. **Set aspect ratio by function** — square for icons, landscape for banners and wide exhibits, portrait for full-page.
4. **Generate once.** Read the result properly before deciding anything about it.
5. **Iterate surgically.** For colour, texture, or object swaps, img2img on the closest generation. For layout or composition changes, **go back to the prompt** — img2img handles surface changes well and structural ones badly.
6. **Save into PallaDrive** at the location the request implies, and tell Daniel the path.

Cap at **1–2 img2img passes**. Beyond that, quality drifts and cost climbs — restart from the prompt instead.

## Pitfalls

- Generating before establishing what the image is for.
- Batch fan-out "to see options" — billed per image.
- Using img2img to move things around; it is not good at that.
- Generating a chart for a drill when a real exhibit from a casebook would be better practice.
- Attempting a call before the MCP is installed.

## Verification

Before reporting done: the file exists at the stated path, it is non-empty, and it actually depicts what was asked for — **open it and look**, do not assume from the API response. Report the path and the number of generations spent.
