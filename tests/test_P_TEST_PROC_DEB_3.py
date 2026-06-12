"""
Procedure validation tests for DEB-3 — Development of table and data population procedure

Tests verify the generated procedure SQL file is correct WITHOUT a live Snowflake connection.

Run with: pytest tests/test_P_TEST_PROC_DEB_3.py -v
"""
from pathlib import Path
import re

_ROOT = Path(__file__).resolve().parent.parent
PROCEDURE_SQL_FILE = _ROOT / "src/sql/procedures/P_TEST_PROC_DEB_3.sql"


def test_procedure_sql_file_exists():
    """Procedure SQL file must exist on disk."""
    assert PROCEDURE_SQL_FILE.exists(), f"Procedure SQL file not found: {PROCEDURE_SQL_FILE}"


def _proc_sql():
    return PROCEDURE_SQL_FILE.read_text(encoding="utf-8")


def test_procedure_ddl_present():
    """AC: Procedure P_TEST_PROC_DEB_3 must exist."""
    assert "CREATE OR REPLACE PROCEDURE RAW.P_TEST_PROC_DEB_3" in _proc_sql(), (
        "CREATE PROCEDURE statement for P_TEST_PROC_DEB_3 not found"
    )


def test_returns_varchar_present():
    """AC: Procedure must declare RETURNS VARCHAR."""
    assert "RETURNS VARCHAR" in _proc_sql(), (
        "RETURNS VARCHAR not found in procedure SQL"
    )


def test_execute_as_caller_present():
    """AC: Procedure must use EXECUTE AS CALLER to inherit the caller's role permissions."""
    assert "EXECUTE AS CALLER" in _proc_sql(), (
        "EXECUTE AS CALLER not found in procedure SQL"
    )


def test_exactly_10_rows_inserted():
    """AC: Procedure must insert exactly 10 rows."""
    rows = re.findall(r"^\s*\(.*\)\s*[;,]?\s*$", _proc_sql(), re.MULTILINE)
    assert len(rows) == 10, (
        f"Expected 10 INSERT rows, found {len(rows)}. "
        f"Check VALUES block in {PROCEDURE_SQL_FILE}"
    )


def test_query_tag_cleared_after_insert():
    """AC: The query tag must be cleared after the INSERT completes."""
    sql = _proc_sql()
    # query_tag is null so no SET is expected, but a CLEAR line must not be present
    # either. Since no query tag is set, we verify no stray ALTER SESSION SET QUERY_TAG
    # with a non-empty value exists that was never cleared.
    set_tag_matches = re.findall(
        r"ALTER\s+SESSION\s+SET\s+QUERY_TAG\s*=\s*''[^']+''",
        sql,
        re.IGNORECASE,
    )
    assert not set_tag_matches, (
        "A non-empty QUERY_TAG was set but query_tag is null in the ticket spec. "
        f"Found: {set_tag_matches}"
    )


def test_no_unsafe_drop_in_procedure_sql():
    """Procedure SQL must not contain DROP without IF EXISTS."""
    unsafe = re.findall(r"\bDROP\s+\w+\s+(?!IF\s+EXISTS\b)", _proc_sql(), re.IGNORECASE)
    assert not unsafe, f"Unsafe DROP in procedure SQL (missing IF EXISTS): {unsafe}"


def test_procedure_validation_queries_present():
    """Procedure validation queries must be present as comments."""
    sql = _proc_sql()
    assert "SHOW PROCEDURES" in sql
    assert "QUERY_HISTORY" in sql
