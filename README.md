**Here's the updated version with the warning moved to the top and strengthened:**

```markdown
# LinkedIn Intelligence System

> An agent-first workspace that turns LinkedIn research into structured intelligence artifacts — directly inside VS Code.

---

## ⚠️ Important Warning

**Use at your own risk.**

This system uses a real browser session via a LinkedIn MCP server. While it does not use undocumented APIs or aggressive scraping techniques, **LinkedIn strictly prohibits automation** in their Terms of Service.

- By using this repository, **you take full responsibility** for how the MCP server and AI agents are used.
- There is always a **risk of account warning or permanent ban**, even with moderate usage.
- No users have reported bans so far with responsible usage, but this cannot be guaranteed.
- Always use the system thoughtfully and limit automation volume.

**Proceed only if you accept these risks.**

---

## Overview

**LinkedIn Intelligence System** combines a real LinkedIn MCP server with GitHub Copilot skills to automate profile research, market intelligence, and outreach workflows.

Instead of manual work, you collaborate with AI inside VS Code using natural language and predefined skills. The system retrieves live data, normalizes it, and produces clean, reusable markdown artifacts.

### Sample Output
**[Satya Nadella – Intelligence Dossier](data/dossiers/active/people/satya_nadella-microsoft.md)**

---

## Core Skills

Trigger these skills directly in GitHub Copilot Chat:

| Skill              | Purpose |
|--------------------|-------|
| `/dossier-gather`  | Deep research on people, companies, or jobs → structured dossier |
| `/feed-insights`   | Turn your LinkedIn home feed into actionable intelligence |
| `/outreach`        | Craft personalized connection messages and track conversations |
| `/content-draft`   | Turn raw ideas into polished, persona-optimized LinkedIn posts |

**Example prompt:**
> "Use `/dossier-gather` to research the CEO of Microsoft and save the artifact."

---

## Setup & Installation

### Prerequisites
- VS Code with **GitHub Copilot Chat** enabled
- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended)

### 1. Configure the LinkedIn MCP Server (Required)

```bash
uvx linkedin-scraper-mcp@latest --login
```

Authenticate with LinkedIn when prompted, then configure the MCP server in your VS Code settings (`mcp.json`).

### 2. Clone & Install (Optional)

```bash
git clone https://github.com/ajaaysrinivaas/linkedin-intelligence-system.git
cd linkedin-intelligence-system
uv sync --dev
```

---

## Project Structure

```
.
├── .github/skills/          # Copilot skill definitions
├── config/                  # Watchlists & prompt templates
├── data/                    # Generated artifacts (git-ignored)
├── src/liis/                # Python utilities
└── mcp.json.example
```

---

## License

MIT License © 2026 Ajaay Srinivaas R.  
See [LICENSE](LICENSE) for details.
