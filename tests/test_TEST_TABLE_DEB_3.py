"""
Table validation tests for DEB-3 — Development of table and data population procedure

Tests verify the generated table SQL file is correct WITHOUT a live Snowflake connection.

Run with: pytest tests/test_TEST_TABLE_DEB_3.py -v
"""
from pathlib import Path
import re

_ROOT = Path(__file__).resolve().parent.parent
TABLE_SQL_FILE = _ROOT / "src/sql/tables/TEST_TABLE_DEB_3.sql"


def test_table_sql_file_exists():
    """Table SQL file must exist on disk."""
    assert TABLE_SQL_FILE.exists(), f"Table SQL file not found: {TABLE_SQL_FILE}"


def _table_sql():
    return TABLE_SQL_FILE.read_text(encoding="utf-8")


def test_table_ddl_present():
    """AC: Table TEST_TABLE_DEB_3 must be defined in schema RAW."""
    assert "CREATE OR REPLACE TABLE DEV_SECREFTEST_DB.RAW.TEST_TABLE_DEB_3" in _table_sql(), (
        "CREATE TABLE statement for DEV_SECREFTEST_DB.RAW.TEST_TABLE_DEB_3 not found"
    )


def test_all_columns_present():
    """All columns from the ticket schema must appear in the table SQL."""
    sql = _table_sql()
    missing = [col for col in ["ID", "Name", "Amount"] if col not in sql]
    assert not missing, f"Missing columns in table SQL: {missing}"


def test_correct_column_types():
    """Column data types must match the ticket specification."""
    sql = _table_sql()
    assert re.search(r"\bID\s+INT\b", sql), "Column ID INT not found in table SQL"
    assert re.search(r"\bName\s+VARCHAR\b", sql), "Column Name VARCHAR not found in table SQL"
    assert re.search(r"\bAmount\s+FLOAT\b", sql), "Column Amount FLOAT not found in table SQL"


def test_no_unsafe_drop_in_table_sql():
    """Table SQL must not contain DROP without IF EXISTS."""
    unsafe = re.findall(r"\bDROP\s+\w+\s+(?!IF\s+EXISTS\b)", _table_sql(), re.IGNORECASE)
    assert not unsafe, f"Unsafe DROP in table SQL (missing IF EXISTS): {unsafe}"


def test_table_validation_queries_present():
    """Table validation queries must be present as comments."""
    sql = _table_sql()
    assert "DESC TABLE" in sql
    assert "SELECT COUNT(*)" in sql
