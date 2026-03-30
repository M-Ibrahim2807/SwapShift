def is_reciprocal_daily(
    my_current_payload: dict,
    my_wanted_payload: dict,
    other_current_payload: dict,
    other_wanted_payload: dict,
) -> bool:
    my_wanted = my_wanted_payload.get("shift")
    other_wanted = other_wanted_payload.get("shift")
    other_current = other_current_payload.get("shift")
    my_current = my_current_payload.get("shift")

    def is_working(shift: str | None) -> bool:
        return (shift or "").upper() != "HOLIDAY"

    current_matches = (
        is_working(other_current) if my_wanted == "WORKING" else other_current == my_wanted
    )
    wanted_matches = is_working(my_current) if other_wanted == "WORKING" else other_wanted == my_current

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
