"""Pass/fail evaluation of a listing against the user's buying criteria."""

MIN_BEDROOMS = 4
MIN_BATHROOMS = 2
MAX_STATION_DISTANCE_M = 3000
MAX_COMMUTE_TO_FLINDERS_MIN = 75

NORTH_ASPECTS = {"N", "NE", "NW"}


def is_north_facing(aspect):
    return bool(aspect) and aspect.strip().upper() in NORTH_ASPECTS


def evaluate(listing, blue_chip_suburbs):
    """Return an ordered dict of criterion -> (passed: bool|None, detail: str).

    passed is None when the listing doesn't have enough data to judge yet.
    """
    suburb = (listing.get("suburb") or "").strip().lower()
    blue_chip_set = {s.strip().lower() for s in blue_chip_suburbs}

    checks = {}

    bedrooms = listing.get("bedrooms")
    checks["bedrooms"] = (
        None if bedrooms is None else bedrooms >= MIN_BEDROOMS,
        f"{bedrooms if bedrooms is not None else '?'} bed (need >= {MIN_BEDROOMS})",
    )

    bathrooms = listing.get("bathrooms")
    checks["bathrooms"] = (
        None if bathrooms is None else bathrooms >= MIN_BATHROOMS,
        f"{bathrooms if bathrooms is not None else '?'} bath (need >= {MIN_BATHROOMS})",
    )

    checks["blue_chip_suburb"] = (
        suburb in blue_chip_set if suburb else None,
        f"{listing.get('suburb') or '?'} "
        + ("(blue chip)" if suburb in blue_chip_set else "(not on blue chip list)"),
    )

    distance = listing.get("distance_to_station_m")
    checks["station_distance"] = (
        None if distance is None else distance <= MAX_STATION_DISTANCE_M,
        (
            f"{distance}m to {listing.get('nearest_station') or 'nearest station'} "
            f"(need <= {MAX_STATION_DISTANCE_M}m)"
            if distance is not None
            else "distance to station unknown"
        ),
    )

    commute = listing.get("commute_to_flinders_min")
    checks["commute_to_flinders"] = (
        None if commute is None else commute <= MAX_COMMUTE_TO_FLINDERS_MIN,
        (
            f"{commute} min door-to-door (need <= {MAX_COMMUTE_TO_FLINDERS_MIN} min)"
            if commute is not None
            else "commute time unknown"
        ),
    )

    north = is_north_facing(listing.get("aspect"))
    full_of_light = bool(listing.get("full_of_light"))
    checks["light"] = (
        north or full_of_light,
        f"aspect={listing.get('aspect') or '?'}, full_of_light={full_of_light}",
    )

    return checks


HARD_CRITERIA = [
    "bedrooms",
    "bathrooms",
    "blue_chip_suburb",
    "station_distance",
    "commute_to_flinders",
]


def qualifies(checks):
    """A listing qualifies only when every hard criterion is known and passed.

    'light' is a soft preference and is intentionally excluded here.
    """
    return all(checks[name][0] is True for name in HARD_CRITERIA)
