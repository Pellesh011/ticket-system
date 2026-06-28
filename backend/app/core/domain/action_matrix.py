ACTION_MATRIX: dict[tuple[str, str], bool] = {
    ("new", "edit"): True,
    ("new", "delete"): True,
    ("new", "transition"): True,
    ("in_progress", "edit"): True,
    ("in_progress", "delete"): True,
    ("in_progress", "transition"): True,
    ("done", "edit"): False,
    ("done", "delete"): False,
    ("done", "transition"): False,
}

VALID_TRANSITIONS: dict[tuple[str, str], bool] = {
    ("new", "new"): True,
    ("new", "in_progress"): True,
    ("new", "done"): True,
    ("in_progress", "new"): True,
    ("in_progress", "in_progress"): True,
    ("in_progress", "done"): True,
    ("done", "done"): True,
}


def can_perform(state: str, action: str) -> bool:
    return ACTION_MATRIX.get((state, action), False)


def can_transition(from_state: str, to_state: str) -> bool:
    return VALID_TRANSITIONS.get((from_state, to_state), False)


def get_allowed_transitions(state: str) -> list[str]:
    return [to for (fr, to), ok in VALID_TRANSITIONS.items() if fr == state and ok]
