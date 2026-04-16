import pytest
from click.testing import CliRunner
from env_surgeon.cli_group import group_command


@pytest.fixture()
def runner():
    return CliRunner()


def _write(tmp_path, content: str):
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_group_exits_0(runner, tmp_path):
    f = _write(tmp_path, "DB_HOST=localhost\nDB_PORT=5432\n")
    res = runner.invoke(group_command, [f])
    assert res.exit_code == 0


def test_group_shows_prefix_header(runner, tmp_path):
    f = _write(tmp_path, "DB_HOST=localhost\nDB_PORT=5432\n")
    res = runner.invoke(group_command, [f])
    assert "[DB]" in res.output


def test_group_filter_prefix(runner, tmp_path):
    f = _write(tmp_path, "DB_HOST=db\nAWS_KEY=k\nAPP_NAME=n\n")
    res = runner.invoke(group_command, [f, "--prefix", "DB"])
    assert "[DB]" in res.output
    assert "[AWS]" not in res.output


def test_group_ungrouped_hidden_by_default(runner, tmp_path):
    f = _write(tmp_path, "DB_HOST=db\nHOSTNAME=host\n")
    res = runner.invoke(group_command, [f])
    assert "ungrouped" not in res.output


def test_group_show_ungrouped_flag(runner, tmp_path):
    f = _write(tmp_path, "DB_HOST=db\nHOSTNAME=host\n")
    res = runner.invoke(group_command, [f, "--show-ungrouped"])
    assert "ungrouped" in res.output
    assert "HOSTNAME" in res.output


def test_group_custom_sep(runner, tmp_path):
    f = _write(tmp_path, "DB.HOST=db\nDB.PORT=5432\n")
    res = runner.invoke(group_command, [f, "--sep", "."])
    assert "[DB]" in res.output
