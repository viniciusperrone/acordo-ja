import pytest

from datetime import datetime


@pytest.fixture
def mock_datetime(monkeypatch):

    class MockDateTime:
        @staticmethod
        def utcnow():
            return datetime(2024, 2, 15, 10, 30, 0)

        @staticmethod
        def now():
            return datetime(2024, 2, 15, 10, 30, 0)

    monkeypatch.setattr("datetime.datetime", MockDateTime)

    return MockDateTime
