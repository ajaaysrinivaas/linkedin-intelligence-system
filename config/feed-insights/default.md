# feed_insights

**Name:** Feed Intelligence Brief

**Prompt Template:**
```text
You are writing a feed intelligence brief from a preprocessed feed bundle.
Do not narrate every post. Focus on synthesis, ranking, and actionability.

Feed summary:
{feed_summary}

Top posts:
{top_posts}

Observed signals:
{signals}

Write markdown with:
## Executive Summary
## What Changed
## Key Themes
## Actionable Signals
## People to Watch
## Companies to Watch
## Next Actions
Rules:
- Use only the supplied bundle.
- Compress repetition and surface concrete follow-ups.
- Explain why the feed matters now.
- Avoid copying the feed verbatim.
- Do not turn the brief into a passive report.
```

**Tags:** ["#feed", "#intelligence"]

**Tone:** analytical

**Length:** medium
