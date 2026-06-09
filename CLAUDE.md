# Data Engineer Agent Demo

## What this project does
An autonomous AI agent that reads a Jira ticket, generates Snowflake SQL
(CREATE TABLE + stored procedure), writes pytest validation tests, then
opens a GitHub draft PR and comments the PR link back on the Jira ticket.

No database connection required. All tests run locally against the
generated SQL file as plain text.

## How to trigger the agent
```
$data-engineer TICKET-ID
```
Example: `$data-engineer DE-42`

## Agent pipeline
1. jira-reader   → reads ticket via Jira MCP, extracts requirements
2. code-generator → writes SQL + pytest file via Filesystem MCP
3. pr-creator    → branch + commit + draft PR via GitHub MCP
                   + comment PR link on Jira ticket

## Output files per ticket
- src/sql/<ticket_id>_<object_name>.sql   — Snowflake DDL + DML
- tests/test_<ticket_id>_<object_name>.py — pytest validation (no DB needed)

## Conventions
- Branch:  feature/<TICKET-ID>
- Commit:  [TICKET-ID] <ticket title>
- Always draft PRs — never merge automatically
- Never push directly to main
- Never overwrite existing files without confirmation

## MCP servers required
- jira       — read tickets, post comments
- filesystem — write generated files to src/sql/ and tests/
- github     — create branch, commit files, open draft PR

## Config
All settings in .claude/config/defaults.json (gitignored).
Copy defaults.template.json and fill in your values.
