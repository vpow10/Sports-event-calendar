from datetime import date, time

import pytest

from app import create_app, db
from app.models import Competition, Event, Sport, Stage, Team, Venue


@pytest.fixture
def app():
    app = create_app("config.TestConfig")

    with app.app_context():
        db.create_all()

        sport = Sport(name="Football")
        db.session.add(sport)
        db.session.flush()

        competition = Competition(
            name="Premier League",
            external_id="test-premier-league",
            _sport_id=sport.id,
        )
        db.session.add(competition)

        stage = Stage(
            name="Round 1",
            external_id="test-round-1",
            ordering=1,
        )
        db.session.add(stage)

        venue = Venue(name="Emirates Stadium")
        db.session.add(venue)

        home_team = Team(
            name="Arsenal",
            official_name="Arsenal FC",
            slug="arsenal",
            abbreviation="ARS",
            country_code="ENG",
        )
        db.session.add(home_team)

        away_team = Team(
            name="Chelsea",
            official_name="Chelsea FC",
            slug="chelsea",
            abbreviation="CHE",
            country_code="ENG",
        )
        db.session.add(away_team)

        db.session.flush()

        event = Event(
            season=2025,
            status="scheduled",
            event_date=date(2025, 9, 1),
            event_time_utc=time(18, 30),
            description="Test event",
            _sport_id=sport.id,
            _competition_id=competition.id,
            _stage_id=stage.id,
            _venue_id=venue.id,
            _home_team_id=home_team.id,
            _away_team_id=away_team.id,
            home_goals=None,
            away_goals=None,
            winner=None,
        )
        db.session.add(event)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
