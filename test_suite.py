import pytest
from src.utils.db_utils import db_connection


def test_initial():
    assert 1 == 1


def test_database_connection():
    with db_connection() as conn:
        conn.get_all_approvers()


if __name__ == "__main__":
    pytest.main()
