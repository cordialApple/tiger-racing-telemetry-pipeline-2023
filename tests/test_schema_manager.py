from db.schema_manager import split_statements


def test_splits_multiple_statements():
    sql = "CREATE TABLE a (id INT);\nCREATE TABLE b (id INT);"
    assert split_statements(sql) == [
        "CREATE TABLE a (id INT)",
        "CREATE TABLE b (id INT)",
    ]


def test_trailing_semicolon_yields_no_empty_statement():
    assert split_statements("SELECT 1;") == ["SELECT 1"]


def test_comment_lines_are_stripped():
    sql = "-- create the table\nCREATE TABLE a (id INT);\n-- done"
    assert split_statements(sql) == ["CREATE TABLE a (id INT)"]


def test_inline_comment_above_statement_in_same_fragment():
    sql = "-- header\n-- more\nSELECT create_hypertable('x', 'ts');"
    assert split_statements(sql) == ["SELECT create_hypertable('x', 'ts')"]


def test_empty_input():
    assert split_statements("") == []
    assert split_statements("   \n  ;  \n") == []


def test_only_comments():
    assert split_statements("-- nothing here\n-- still nothing") == []
