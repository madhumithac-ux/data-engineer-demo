"""
Validation tests for DE-42 — Development of Table and Data Population Procedure

These tests verify the generated SQL file is correct WITHOUT
needing a live Snowflake database connection.

Each test maps to one acceptance criterion from the Jira ticket:
1. Table AI_AGENT_TEST_TABLE_2 must exist in schema RAW
2. CALL P_FILL_AI_AGENT_TEST_TABLE_2() must insert exactly 10 rows
3. INSERT must be tagged with AI_AGENT_POPULATION_PROC in query history

Run with: pytest tests/test_de42_ai_agent_test_table_2.py -v
"""
from pathlib import Path
import re

# Path to the generated SQL file being validated
SQL_FILE = Path("src/sql/de42_ai_agent_test_table_2.sql")


def test_sql_file_was_generated():
    """SQL file must exist on disk."""
    assert SQL_FILE.exists(), (
        f"SQL file not found: {SQL_FILE}\n"
        "Run the data-engineer agent first."
    )


def _sql():
    """Helper — read SQL file content once."""
    return SQL_FILE.read_text(encoding="utf-8")


def test_table_ddl_present():
    """AC: Table AI_AGENT_TEST_TABLE_2 must exist in schema RAW."""
    assert "CREATE OR REPLACE TABLE RAW.AI_AGENT_TEST_TABLE_2" in _sql(), (
        "CREATE TABLE statement for RAW.AI_AGENT_TEST_TABLE_2 not found in SQL file"
    )


def test_procedure_ddl_present():
    """AC: Procedure P_FILL_AI_AGENT_TEST_TABLE_2 must exist."""
    assert "CREATE OR REPLACE PROCEDURE RAW.P_FILL_AI_AGENT_TEST_TABLE_2" in _sql(), (
        "CREATE PROCEDURE statement not found in SQL file"
    )


def test_all_columns_present():
    """All columns from the ticket schema must appear in the SQL."""
    sql = _sql()
    missing = []
    for col in ["ID", "Name", "Amount"]:
        if col not in sql:
            missing.append(col)
    assert not missing, f"Missing columns in SQL: {missing}"


def test_correct_column_types():
    """Column data types must match the ticket specification."""
    sql = _sql()
    assert "INT" in sql,     "Column ID should be INT"
    assert "VARCHAR" in sql, "Column Name should be VARCHAR"
    assert "FLOAT" in sql,   "Column Amount should be FLOAT"


def test_exactly_10_rows_inserted():
    """AC: Procedure must insert exactly 10 rows."""
    rows = re.findall(r"\(\s*\d+\s*,", sql := _sql())
    assert len(rows) == 10, (
        f"Expected 10 INSERT rows, found {len(rows)}.\n"
        f"Check the VALUES block in {SQL_FILE}"
    )


def test_query_tag_present():
    """AC: INSERT must be identifiable by query tag AI_AGENT_POPULATION_PROC."""
    assert "AI_AGENT_POPULATION_PROC" in _sql(), (
        "Query tag AI_AGENT_POPULATION_PROC not found in SQL file.\n"
        "The procedure must set QUERY_TAG for observability."
    )


def test_query_tag_is_set_and_cleared():
    """Query tag must be set before INSERT and cleared after."""
    sql = _sql()
    assert "QUERY_TAG = ''AI_AGENT_POPULATION_PROC''" in sql, \
        "QUERY_TAG not set before INSERT"
    assert "QUERY_TAG = ''''" in sql, \
        "QUERY_TAG not cleared after INSERT"


def test_no_unsafe_drop_statements():
    """SQL must not contain DROP without IF EXISTS (safety check)."""
    unsafe = re.findall(
        r"\bDROP\s+\w+\s+(?!IF\s+EXISTS\b)",
        _sql(),
        re.IGNORECASE
    )
    assert not unsafe, (
        f"Unsafe DROP statement found (missing IF EXISTS): {unsafe}\n"
        "Always use DROP ... IF EXISTS for safety."
    )


def test_validation_queries_are_commented():
    """Validation queries must be present as comments for manual Snowflake use."""
    sql = _sql()
    assert "DESC TABLE" in sql,       "Table existence check comment missing"
    assert "SHOW PROCEDURES" in sql,   "Procedure existence check comment missing"
    assert "SELECT COUNT(*)" in sql,   "Row count validation comment missing"
    assert "QUERY_HISTORY" in sql,     "Query history check comment missing"
