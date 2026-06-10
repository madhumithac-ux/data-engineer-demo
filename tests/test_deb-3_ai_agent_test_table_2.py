
"""
Validation tests for DEB-3 — Development of table and data population procedure

Tests verify generated SQL files are correct WITHOUT a live Snowflake connection.

Acceptance criteria from the Jira ticket:
1. Table AI_AGENT_TEST_TABLE_2 must exist in schema RAW of database DEV_SECREFTEST_DB
2. Calling CALL P_FILL_AI_AGENT_TEST_TABLE_2(); must successfully insert exactly 10 rows
3. The INSERT statement must be identifiable via query tag AI_AGENT_POPULATION_PROC
4. No DROP statements without IF EXISTS guard
5. Procedure must use EXECUTE AS CALLER

Run with: pytest tests/test_deb-3_ai_agent_test_table_2.py -v
"""
from pathlib import Path
import re

TABLE_SQL_FILE = Path("src/sql/tables/deb-3_ai_agent_test_table_2.sql")
PROCEDURE_SQL_FILE = Path("src/sql/procedures/deb-3_p_fill_ai_agent_test_table_2.sql")


def test_table_sql_file_exists():
    """Table SQL file must exist on disk."""
    assert TABLE_SQL_FILE.exists(), f"Table SQL file not found: {TABLE_SQL_FILE}"


def test_procedure_sql_file_exists():
    """Procedure SQL file must exist on disk."""
    assert PROCEDURE_SQL_FILE.exists(), f"Procedure SQL file not found: {PROCEDURE_SQL_FILE}"


def _table_sql():
    return TABLE_SQL_FILE.read_text(encoding="utf-8")


def _proc_sql():
    return PROCEDURE_SQL_FILE.read_text(encoding="utf-8")


def test_table_ddl_present():
    """AC: Table AI_AGENT_TEST_TABLE_2 must be defined in schema RAW."""
    assert "CREATE OR REPLACE TABLE RAW.AI_AGENT_TEST_TABLE_2" in _table_sql(), (
        "CREATE TABLE statement for RAW.AI_AGENT_TEST_TABLE_2 not found"
    )


def test_procedure_ddl_present():
    """AC: Procedure P_FILL_AI_AGENT_TEST_TABLE_2 must exist."""
    assert "CREATE OR REPLACE PROCEDURE RAW.P_FILL_AI_AGENT_TEST_TABLE_2" in _proc_sql(), (
        "CREATE PROCEDURE statement for P_FILL_AI_AGENT_TEST_TABLE_2 not found"
    )


def test_all_columns_present():
    """All columns from the ticket schema must appear in the table SQL."""
    sql = _table_sql()
    missing = [col for col in ["ID", "Name", "Amount"] if col not in sql]
    assert not missing, f"Missing columns in table SQL: {missing}"


def test_correct_column_types():
    """Column data types must match the ticket specification."""
    sql = _table_sql()
    assert "ID" in sql and "INT" in sql, "Column ID with type INT not found in table SQL"
    assert "Name" in sql and "VARCHAR(255)" in sql, "Column Name with type VARCHAR(255) not found in table SQL"
    assert "Amount" in sql and "FLOAT" in sql, "Column Amount with type FLOAT not found in table SQL"


def test_exactly_10_rows_inserted():
    """AC: Procedure must insert exactly 10 rows."""
    rows = re.findall(r"\(\s*\d+\s*,", _proc_sql())
    assert len(rows) == 10, (
        f"Expected 10 INSERT rows, found {len(rows)}. "
        f"Check VALUES block in {PROCEDURE_SQL_FILE}"
    )


def test_query_tag_present():
    """AC: INSERT must be tagged with AI_AGENT_POPULATION_PROC for observability."""
    assert "AI_AGENT_POPULATION_PROC" in _proc_sql(), (
        "Query tag AI_AGENT_POPULATION_PROC not found in procedure SQL"
    )


def test_query_tag_is_set_and_cleared():
    """Query tag must be set before INSERT and cleared after."""
    sql = _proc_sql()
    assert "ALTER SESSION SET QUERY_TAG = ''AI_AGENT_POPULATION_PROC''" in sql, \
        "QUERY_TAG not set before INSERT"
    assert "ALTER SESSION SET QUERY_TAG = ''''" in sql, \
        "QUERY_TAG not cleared after INSERT"


def test_execute_as_caller_present():
    """AC: Procedure must use EXECUTE AS CALLER."""
    assert "EXECUTE AS CALLER" in _proc_sql(), (
        "EXECUTE AS CALLER not found in procedure SQL"
    )


def test_no_unsafe_drop_in_table_sql():
    """Table SQL must not contain DROP without IF EXISTS."""
    unsafe = re.findall(r"\bDROP\s+\w+\s+(?!IF\s+EXISTS\b)", _table_sql(), re.IGNORECASE)
    assert not unsafe, f"Unsafe DROP in table SQL (missing IF EXISTS): {unsafe}"


def test_no_unsafe_drop_in_procedure_sql():
    """Procedure SQL must not contain DROP without IF EXISTS."""
    unsafe = re.findall(r"\bDROP\s+\w+\s+(?!IF\s+EXISTS\b)", _proc_sql(), re.IGNORECASE)
    assert not unsafe, f"Unsafe DROP in procedure SQL (missing IF EXISTS): {unsafe}"


def test_table_validation_queries_present():
    """Table validation queries must be present as comments."""
    sql = _table_sql()
    assert "DESC TABLE" in sql
    assert "SELECT COUNT(*)" in sql


def test_procedure_validation_queries_present():
    """Procedure validation queries must be present as comments."""
    sql = _proc_sql()
    assert "SHOW PROCEDURES" in sql
    assert "QUERY_HISTORY" in sql
