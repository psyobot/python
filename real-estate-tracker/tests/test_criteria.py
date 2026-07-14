import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import criteria

BLUE_CHIP = ["Toorak", "Kew"]


def base_listing(**overrides):
    listing = {
        "suburb": "Toorak",
        "bedrooms": 4,
        "bathrooms": 2,
        "distance_to_station_m": 1500,
        "nearest_station": "Toorak",
        "commute_to_flinders_min": 40,
        "aspect": "N",
        "full_of_light": False,
    }
    listing.update(overrides)
    return listing


def test_fully_qualifying_listing_passes():
    checks = criteria.evaluate(base_listing(), BLUE_CHIP)
    assert criteria.qualifies(checks)
    assert checks["light"][0] is True


def test_too_few_bedrooms_fails():
    checks = criteria.evaluate(base_listing(bedrooms=3), BLUE_CHIP)
    assert checks["bedrooms"][0] is False
    assert not criteria.qualifies(checks)


def test_non_blue_chip_suburb_fails():
    checks = criteria.evaluate(base_listing(suburb="Dandenong"), BLUE_CHIP)
    assert checks["blue_chip_suburb"][0] is False
    assert not criteria.qualifies(checks)


def test_station_distance_over_limit_fails():
    checks = criteria.evaluate(base_listing(distance_to_station_m=3500), BLUE_CHIP)
    assert checks["station_distance"][0] is False
    assert not criteria.qualifies(checks)


def test_commute_over_limit_fails():
    checks = criteria.evaluate(base_listing(commute_to_flinders_min=90), BLUE_CHIP)
    assert checks["commute_to_flinders"][0] is False
    assert not criteria.qualifies(checks)


def test_light_is_soft_and_does_not_block_qualification():
    checks = criteria.evaluate(base_listing(aspect="S", full_of_light=False), BLUE_CHIP)
    assert checks["light"][0] is False
    assert criteria.qualifies(checks)


def test_full_of_light_satisfies_light_even_without_north_aspect():
    checks = criteria.evaluate(base_listing(aspect="S", full_of_light=True), BLUE_CHIP)
    assert checks["light"][0] is True


def test_missing_data_is_unknown_not_failing():
    checks = criteria.evaluate(base_listing(bedrooms=None), BLUE_CHIP)
    assert checks["bedrooms"][0] is None
    assert not criteria.qualifies(checks)
