import pytest
from click.testing import CliRunner
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from devlog.cli import cli
from devlog.db import Base


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def in_memory_db():
    """Swap the real DB for an in-memory SQLite DB on every test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    with patch("devlog.commands.start.get_session", return_value=TestSession()), \
         patch("devlog.commands.stop.get_session", return_value=TestSession()), \
         patch("devlog.commands.tag.get_session", return_value=TestSession()), \
         patch("devlog.commands.list_sessions.get_session", return_value=TestSession()):
        yield


def test_start_session(runner):
    result = runner.invoke(cli, ["start", "building auth"])
    assert result.exit_code == 0
    assert "Started" in result.output


def test_stop_with_no_active_session(runner):
    result = runner.invoke(cli, ["stop"])
    assert result.exit_code == 0
    assert "No active session" in result.output


def test_list_empty(runner):
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No sessions found" in result.output
