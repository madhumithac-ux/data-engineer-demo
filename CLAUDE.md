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
1. jira-reader    → reads ticket via Jira MCP, extracts requirements
2. code-generator → writes SQL + pytest file using built-in Write tool
3. test-runner    → runs pytest locally, blocks pipeline if any test fails
4. pr-creator     → git commit + push, open draft PR via GitHub MCP
                    + comment PR link, transition status, assign ticket on Jira

## Output files per ticket
- src/sql/tables/<EXACT_TABLE_NAME>.sql         — Snowflake CREATE OR REPLACE TABLE
- src/sql/procedures/<EXACT_PROCEDURE_NAME>.sql — Snowflake stored procedure
- tests/test_<EXACT_TABLE_NAME>.py              — pytest validation (no DB needed)

## Conventions
- Branch:  feature/<TICKET-ID>
- Commit:  [TICKET-ID] <ticket title>
- Always draft PRs — never merge automatically
- Never push directly to main
- Never overwrite existing files without confirmation

## MCP servers required
- jira   — read tickets, post comments
- github — open draft PR, comment, list pull requests

## Config
All settings in .claude/config/defaults.json (gitignored).
Copy defaults.template.json and fill in your values.
