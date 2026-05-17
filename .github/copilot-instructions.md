# Copilot Instructions - LinkedIn Intelligence Agent

This repo is workflow-first. The useful surface area is:

- [`Tools.md`](../Tools.md) for MCP tool definitions
- [`.github/skills/`](./skills) for the merged skill workflows
- [`config/`](../config) for watchlists and templates
- [`data/`](../data) for generated dossiers, feed insights, and drafts
- [`lifecycle.py`](../lifecycle.py) for startup archival

## Operating Rules

- Keep MCP calls sequential.
- Use the broadest merged skill that matches the user intent.
- Save output under `data/`.
- Treat stale docs and deleted paths as non-authoritative.
- Require an explicit workspace root and explicit source/config inputs.
- Do not assume repo-root discovery or filename inference.
- If a required config file or source file is missing, fail immediately instead of guessing.

## Automatic Routing

Route to the following skills by intent:

### Research and intelligence

Use `/dossier-gather` when the user wants any of the following:

- people search
- profile overview
- company research
- company deep dive
- job search
- job details
- market intelligence
- relationship mapping
- “tell me about X”
- “find X at Y”
- “should I reach out to X”

Use this skill for:

- `search_people`
- `get_person_profile`
- `search_companies`
- `get_company_profile`
- `get_company_posts`
- `get_company_employees`
- `search_jobs`
- `get_job_details`

### Outreach and inbox

Use `/outreach` when the user wants any of the following:

- prepare a message
- send a message
- connect with a person
- read inbox
- search conversations
- review outreach context

Use this skill for:

- `get_inbox`
- `get_conversation`
- `search_conversations`
- `send_message`
- `connect_with_person`

### Feed Insights

Use `/feed-insights` when the user wants:

- a feed digest
- market pulse
- activity summary
- actionable intelligence from feed posts

Use this skill for:

- `get_feed`

The skill should preprocess the feed, build the prompt from `config/feed-insights/default.md`, then use prompt-based synthesis to produce a markdown intelligence brief. Do not treat the feed as a report dump.

### Content

Use `/content-draft` when the user wants:

- draft a LinkedIn post
- rewrite raw ideas
- generate a thought-leadership post

## Notes

- The Python layer is intentionally small; there is no separate `src/skills` implementation.
- The repository’s job is to direct and store research, not to orchestrate a large app runtime.
