---
name: feed-insights
description: "Turn feed activity into actionable intelligence using prompt-based synthesis."
---

# Feed Insights

Use this skill when the user wants a feed digest, market pulse, activity summary, or a signal-rich briefing from LinkedIn posts.

## Workflow

1. Fetch the feed with MCP `get_feed`.
2. Preprocess the feed into a compact input bundle.
3. Build the synthesis prompt from `config/feed-insights/default.md` and the prepared feed bundle.
4. Use an LLM prompt to structure the feed into actionable intelligence.
5. Save the final result as a markdown `feed_insights` brief.
6. Fail immediately if the prompt template or feed source is missing.

## Prompt Contract

The LLM should receive:

- the top posts from the feed
- author and company metadata
- timestamps or recency hints
- repeated themes and keywords if available
- any obvious hiring, launch, partnership, or market signals
- a compact summary of the feed for prompt reuse

The LLM should return markdown with these sections:

- `## Executive Summary`
- `## Key Themes`
- `## Actionable Signals`
- `## People to Watch`
- `## Companies to Watch`
- `## Next Actions`

## Prompt Style

Keep the prompt focused on synthesis, not transcription:

- identify what matters
- compress repeated information
- surface the best follow-up opportunities
- explain why the feed matters now
- avoid copying the full feed verbatim
- use the prompt stored in `config/feed-insights/default.md`

## Output

The output lands in `data/feed_insights/` and is indexed for later reuse.
