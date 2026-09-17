from app.schemas import RequestStatus
from app.workflow import can_transition


def test_valid_transition():
    assert can_transition(RequestStatus.NEW, RequestStatus.IN_PROGRESS)


def test_invalid_transition():
    assert not can_transition(RequestStatus.NEW, RequestStatus.CLOSED)
