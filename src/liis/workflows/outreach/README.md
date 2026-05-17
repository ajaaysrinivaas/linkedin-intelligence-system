# outreach

Helpers for preparing outreach briefs and structured message data.

This package handles target loading, lookup, and message preparation for outreach workflows.

## Modules

- `targets.py`:
  - `OutreachTarget`: simple dataclass for name, username, and role.
  - `load_targets()`: loads a YAML people list and converts it into `OutreachTarget` objects.
  - `find_target()`: finds a target by username, name, or slugified name.
  - `prepare_message()`: builds a structured outbound message payload with confirmation metadata.
- `workflow.py`:
  - `build_outreach_brief()`: saves the prepared outreach payload, indexes the outreach record, and returns a saved file path.
