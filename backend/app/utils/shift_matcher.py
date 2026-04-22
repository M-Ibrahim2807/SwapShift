from app.utils.validators import canonicalize_shift_name


def is_reciprocal_daily(
    my_current_payload: dict,
    my_wanted_payload: dict,
    other_current_payload: dict,
    other_wanted_payload: dict,
) -> bool:
    def normalize(shift: str | None) -> str | None:
        if not shift:
            return shift
        return canonicalize_shift_name(shift)

    my_wanted = normalize(my_wanted_payload.get("shift"))
    other_wanted = normalize(other_wanted_payload.get("shift"))
    other_current = normalize(other_current_payload.get("shift"))
    my_current = normalize(my_current_payload.get("shift"))

    def is_working(shift: str | None) -> bool:
        return (shift or "").upper() not in ["HOLIDAY", "OFF"]

    # Matching logic:
    # 1. If I want a specific shift (including OFF), other must currently have that shift
    # 2. If I want WORKING, other can have any working shift
    # 3. Same applies for other_wanted checking against my_current
    
    if my_wanted == "WORKING":
        # I want any working shift: other must be working
        current_matches = is_working(other_current)
    else:
        # I want specific shift (including OFF): other must have that exact shift
        current_matches = other_current == my_wanted
    
    if other_wanted == "WORKING":
        # Other wants any working shift: I must be working
        wanted_matches = is_working(my_current)
    else:
        # Other wants specific shift (including OFF): I must have that exact shift
        wanted_matches = my_current == other_wanted

    return current_matches and wanted_matches


def is_reciprocal_weekly(
    my_current_payload: dict,
    my_wanted_payload: dict,
    other_current_payload: dict,
    other_wanted_payload: dict,
) -> bool:
    my_current = my_current_payload.get("days", {})
    my_wanted = my_wanted_payload.get("days", {})
    other_current = other_current_payload.get("days", {})
    other_wanted = other_wanted_payload.get("days", {})

    for day, my_curr_shift in my_current.items():
        if other_wanted.get(day) != my_curr_shift:
            return False
        if other_current.get(day) != my_wanted.get(day):
            return False
    return True
