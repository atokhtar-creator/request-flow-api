from app.schemas import RequestStatus

ALLOWED_TRANSITIONS = {
    RequestStatus.NEW: {
        RequestStatus.IN_PROGRESS,
        RequestStatus.CANCELLED,
    },
    RequestStatus.IN_PROGRESS: {
        RequestStatus.RESOLVED,
        RequestStatus.CANCELLED,
    },
    RequestStatus.RESOLVED: {
        RequestStatus.CLOSED,
        RequestStatus.IN_PROGRESS,
    },
    RequestStatus.CLOSED: set(),
    RequestStatus.CANCELLED: set(),
}


def can_transition(old: RequestStatus, new: RequestStatus) -> bool:
    return new in ALLOWED_TRANSITIONS[old]
