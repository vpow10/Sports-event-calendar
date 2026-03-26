from app.models import Competition, Event, Sport, Team


def test_events_page_loads(client):
    response = client.get("/events")

    assert response.status_code == 200
    assert b"Sports Events" in response.data
    assert b"Arsenal" in response.data
    assert b"Chelsea" in response.data


def test_event_detail_page_loads(client):
    response = client.get("/events/1")

    assert response.status_code == 200
    assert b"Arsenal" in response.data
    assert b"Chelsea" in response.data
    assert b"Premier League" in response.data


def test_event_detail_404_for_missing_event(client):
    response = client.get("/events/9999")

    assert response.status_code == 404


def test_new_event_page_loads(client):
    response = client.get("/events/new")

    assert response.status_code == 200
    assert b"Add New Event" in response.data


def test_create_event_post_creates_new_entities_and_event(client, app):
    response = client.post(
        "/events/new",
        data={
            "season": 2026,
            "status": "scheduled",
            "event_date": "2026-01-15",
            "event_time_utc": "20:45",
            "sport_name": "Basketball",
            "competition_name": "EuroLeague",
            "stage_name": "Quarterfinal",
            "venue_name": "OAKA Arena",
            "home_team_name": "Panathinaikos",
            "away_team_name": "Real Madrid",
            "home_goals": "",
            "away_goals": "",
            "winner": "",
            "description": "Created in test",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Event created successfully." in response.data
    assert b"Panathinaikos" in response.data
    assert b"Real Madrid" in response.data
    assert b"EuroLeague" in response.data

    with app.app_context():
        assert Sport.query.filter_by(name="Basketball").first() is not None
        assert Competition.query.filter_by(name="EuroLeague").first() is not None
        assert Team.query.filter_by(name="Panathinaikos").first() is not None
        assert Team.query.filter_by(name="Real Madrid").first() is not None
        assert Event.query.filter_by(description="Created in test").first() is not None


def test_create_event_rejects_same_home_and_away_team(client):
    response = client.post(
        "/events/new",
        data={
            "season": 2026,
            "status": "scheduled",
            "event_date": "2026-01-15",
            "event_time_utc": "20:45",
            "sport_name": "Football",
            "competition_name": "Premier League",
            "stage_name": "Round 2",
            "venue_name": "Emirates Stadium",
            "home_team_name": "Arsenal",
            "away_team_name": "Arsenal",
            "home_goals": "",
            "away_goals": "",
            "winner": "",
            "description": "Invalid test event",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Home team and away team must be different." in response.data


def test_filter_events_by_sport(client):
    response = client.get("/events?sport=Football")

    assert response.status_code == 200
    assert b"Arsenal" in response.data
    assert b"Chelsea" in response.data


def test_filter_events_by_status(client):
    response = client.get("/events?status=scheduled")

    assert response.status_code == 200
    assert b"Arsenal" in response.data
    assert b"Chelsea" in response.data


def test_search_events_by_team_name(client):
    response = client.get("/events?q=Arsenal")

    assert response.status_code == 200
    assert b"Arsenal" in response.data


def test_search_events_by_competition_name(client):
    response = client.get("/events?q=Premier")

    assert response.status_code == 200
    assert b"Premier League" in response.data
