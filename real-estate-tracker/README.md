# Real Estate Tracker

A small Flask app for tracking real estate listings against a fixed set of
buying criteria:

1. At least 4 bedrooms
2. In a blue chip suburb (editable list under Settings)
3. No more than 3km from the nearest station
4. Door-to-door commute to Flinders St of 75 minutes or less
5. North facing preferred, or otherwise full of light (soft preference, shown
   but doesn't disqualify a listing)
6. At least 2 bathrooms

Each listing is scored against these rules automatically and shown with
pass/fail/unknown chips. The list view can be filtered to only show listings
that meet every must-have criterion.

## Running locally

```bash
cd real-estate-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000. Data is stored in a local SQLite database
at `data/listings.db` (created automatically, git-ignored).

## Running tests

```bash
pip install pytest
pytest tests/
```

## Notes

- Distance to nearest station and commute time to Flinders St are entered
  manually (e.g. read off Google/PTV Journey Planner when reviewing a
  listing) rather than fetched from a live API, so the app has no external
  dependencies or API keys to manage.
- The blue chip suburb list ships with a default set of well-known Melbourne
  suburbs but is fully editable from the Settings page.
