# Sample Jira Ticket

Use this as a template when creating tickets in your Jira project.
The more structured the ticket, the better the generated SQL output.

---

## Title
Development of Table and Data Population Procedure

## Description

As a data engineer, I need to create a specific table structure and a
corresponding stored procedure in the Snowflake DEV environment to
facilitate testing for AI agents. The procedure must populate the table
with sample data and include metadata tagging for tracking purposes.

### Technical Specifications

| Field | Value |
|-------|-------|
| Role | DEV_SECREF_FR_ENGR_ROLE |
| Database | DEV_SECREFTEST_DB |
| Schema | RAW |
| Table Name | AI_AGENT_TEST_TABLE_2 |
| Procedure Name | P_FILL_AI_AGENT_TEST_TABLE_2 |

### Table Schema

| Column Name | Data Type |
|-------------|-----------|
| ID | INT |
| Name | VARCHAR |
| Amount | FLOAT |

## Acceptance Criteria

- **Object Creation:** Table `AI_AGENT_TEST_TABLE_2` must exist in the specified schema
- **Logic Execution:** Calling `CALL P_FILL_AI_AGENT_TEST_TABLE_2();` must successfully insert exactly 10 rows
- **Observability:** The INSERT statement within the procedure must be identifiable in Snowflake Query History via the tag: `AI_AGENT_POPULATION_PROC`

## Unit Test Plan

Run the following queries to validate the implementation:

```sql
-- Check Table Existence
DESC TABLE AI_AGENT_TEST_TABLE_2;

-- Check Procedure Existence
SHOW PROCEDURES LIKE 'P_FILL_AI_AGENT_TEST_TABLE_2' IN SCHEMA RAW;

-- Verify Row Count
SELECT COUNT(*) FROM AI_AGENT_TEST_TABLE_2;  -- Expected: 10

-- Verify Query Tag in History
SELECT query_id, query_text, query_tag
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_tag = 'AI_AGENT_POPULATION_PROC'
ORDER BY start_time DESC
LIMIT 10;
```
