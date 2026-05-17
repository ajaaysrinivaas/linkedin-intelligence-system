---
name: content-draft
description: "Build a curated draft from a raw post idea."
---

# Content Draft

Use this skill when the user wants a LinkedIn post draft, rewrite, or thought-leadership post.

## Workflow

1. Read `data/posts/raw/*.md`.
2. Apply the selected template from `config/content-draft/`.
3. Build a curated markdown draft artifact.
4. Fail immediately if the raw idea file or template file is missing.

Keep the template generic unless the raw idea explicitly requires a domain-specific frame. Do not assume healthcare, medtech, or any other sector by default.
Do not fall back to another template name or infer a different source file.

If a final body is already available, pass it with `--body` to store the curated draft directly.
