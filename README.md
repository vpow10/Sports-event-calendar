# Sports Event Calendar

## Overview
This project is a Flask + PostgreSQL web application for managing and displaying sports events.

It is being built as part of the Sportradar Coding Academy backend coding exercise. The application supports:
- database modeling for sports events
- event storage in a relational database
- backend functionality to add and retrieve events
- frontend pages to display event data

## Project Structure
```
sports-event-calendar/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── templates/
│   └── static/
├── migrations/
├── data/
├── docs/
├── tests/
├── seed.py
├── config.py
└── run.py
```
## Tech Stack
- Python
- Flask
- PostgreSQL
- SQLAlchemy
- Flask-Migrate
- Jinja2 templates
- pytest

## Current Features

- Display all sports events from the database
- View a single event in detail
- Efficient event retrieval using SQLAlchemy eager loading
- Navigation bar with placeholder links
- Basic styling for readability
- Create new events using a web form
- Validate required fields and prevent duplicate home/away team selection
- Save new events to PostgreSQL and redirect to the event detail page
- Filter events by sport
- Filter events by status
- Search events by team name or competition


### Query Efficiency

The event list and event detail views use eager loading for related entities such as teams, competition, stage, venue, and sport. This avoids repeated database queries when rendering templates.

### Filtering

The event list supports query-parameter-based filtering. Filters are applied at the database query level rather than in Python after loading all records, which keeps retrieval efficient.

## Assumptions

- The provided sample data does not include a direct sport field, so all imported events are assigned to the "Football" sport category.
- Some fields in the dataset (e.g., stadium, result, teams) can be null, so the schema allows nullable relationships where appropriate.

## Database Design

The database is structured around the `events` table, which stores each sports match together with date, time, season, status, and score information.

Supporting entities are normalized into separate tables:
- `sports` stores sport categories
- `competitions` stores tournament information
- `teams` stores home and away team data
- `stages` stores tournament round information such as "Round of 16" or "Final"
- `venues` stores stadium information when available

The `events` table references these entities through foreign keys:
- `_sport_id`
- `_competition_id`
- `_stage_id`
- `_venue_id`
- `_home_team_id`
- `_away_team_id`

This design reduces duplication and keeps the schema easy to query efficiently for event list and detail pages.

ERD diagram of the database design (from docs/erd.png):
![ERD Diagram](docs/erd.png)

## Design Decisions

- The database schema is normalized to reduce duplication and improve data consistency.
- Related entities (sports, competitions, teams, venues, stages) are stored in separate tables and linked via foreign keys.
- The event creation form accepts free-text input and automatically creates related entities if they do not exist. This improves usability while preserving normalization.
- SQLAlchemy eager loading (`joinedload`) is used to avoid N+1 query problems when rendering event lists and detail views.
- Filtering is implemented at the database query level to ensure scalability and efficiency.

## Setup

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```
4. Create a PostgreSQL database named `sports_calendar`
5. Create a `.env` file based on `.env.example` and set your database credentials
6. Run database migrations:

```bash
flask db upgrade
```
7. Start the application:

```bash
flask run
```

## Sample Data

The project includes a seed script that imports sample sports event data from a JSON file into PostgreSQL.

The imported dataset includes:
- season
- status
- event date and UTC time
- competition
- stage
- home and away team data
- optional stadium information
- optional result data

### Run the seed script

```bash
python seed.py
```
Assumption: the provided sample data does not explicitly include a sport field, so imported sample records are assigned to the `Football` sport category based on the competition context.

## Usage

### Create a new event

Open `/events/new` in the browser and submit the form to create a new database record.

### Event Creation

The event creation form accepts free-text input for related entities such as sport, competition, teams, stage, and venue.

When a submitted value already exists, the application reuses the existing database row. When it does not exist, the application creates the related record automatically and then stores the new event using foreign-key references.

## Future Improvements

- Add pagination for large datasets
- Add editing and deletion of events
- Improve validation (e.g., derive winner automatically from score)
- Add API endpoints for programmatic access
- Improve filtering with date ranges and advanced search