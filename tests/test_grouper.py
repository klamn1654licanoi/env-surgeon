import pytest
from env_surgeon.parser import EnvFile, EnvEntry
from env_surgeon.grouper import group_env_file, _prefix


def _make_env(*pairs) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs]
    return EnvFile(path="test.env", entries=entries)


def test_prefix_simple():
    assert _prefix("DB_HOST") == "DB"


def test_prefix_no_underscore():
    assert _prefix("HOSTNAME") is None


def test_prefix_leading_underscore():
    assert _prefix("_PRIVATE") is None


def test_group_basic():
    env = _make_env(("DB_HOST", "localhost"), ("DB_PORT", "5432"), ("APP_NAME", "x"))
    result = group_env_file(env)
    assert "DB" in result.groups
    assert "APP" in result.groups
    assert len(result.groups["DB"]) == 2
    assert result.is_clean()


def test_ungrouped_no_prefix():
    env = _make_env(("HOSTNAME", "localhost"), ("DB_HOST", "db"))
    result = group_env_file(env)
    assert len(result.ungrouped) == 1
    assert result.ungrouped[0].key == "HOSTNAME"
    assert not result.is_clean()


def test_filter_by_prefixes():
    env = _make_env(("DB_HOST", "db"), ("AWS_KEY", "k"), ("APP_NAME", "n"))
    result = group_env_file(env, prefixes=["DB", "AWS"])
    assert "APP" not in result.groups
    assert len(result.ungrouped) == 1


def test_comment_entry_goes_to_ungrouped():
    entry = EnvEntry(key=None, value=None, raw="# comment")
    env = EnvFile(path="t.env", entries=[entry])
    result = group_env_file(env)
    assert len(result.ungrouped) == 1


def test_group_names_sorted():
    env = _make_env(("Z_A", "1"), ("A_B", "2"), ("M_C", "3"))
    result = group_env_file(env)
    assert result.group_names() == ["A", "M", "Z"]
