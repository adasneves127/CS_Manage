import pytest
from src.utils.db_utils import db_connection


def test_initial_user():
    with db_connection() as conn:
        user = conn.get_user_by_seq(1)
    assert user.seq == 1
    assert user.user_name == "~"
    assert user.first_name == "System"
    assert user.last_name == "Account"
    assert user.system_user == 1
    assert user.theme == 0

def test_initial_finance_status():
    with db_connection() as conn:
        statuses = conn.get_all_finance_statuses()
        assert statuses[0][0] == 1
        assert statuses[1][0] == 2
        assert statuses[2][0] == 3
        assert statuses[3][0] == 4
        assert statuses[4][0] == 5
        assert statuses[5][0] == 6
        assert statuses[6][0] == 7

        assert statuses[0][1] == "Closed"
        assert statuses[1][1] == "Paid"
        assert statuses[2][1] == "Open"
        assert statuses[3][1] == "Granted"
        assert statuses[4][1] == "Pending"
        assert statuses[5][1] == "Denied"
        assert statuses[6][1] == "Cancelled"


def test_database_new_status():
    with db_connection() as conn:
        user = conn.get_user_by_seq(1)
        conn.create_finance_status("test_status", user)
        seq = conn.cursor.lastrowid
        stats = conn.get_all_finance_statuses()
        new_stat = stats[seq-1]
        assert new_stat[0] == seq
        assert new_stat[1] == "test_status"
        assert new_stat[2] == "System Account"
        assert new_stat[3] == "System Account"
        assert new_stat[4] == new_stat[5]


def test_database_connection():
    with db_connection() as conn:
        conn.get_all_approvers()


if __name__ == "__main__":
    pytest.main()
