import json
from datetime import datetime

from app import create_app, db
from app.models import Competition, Event, Sport, Stage, Team, Venue


def get_or_create_sport(name: str) -> Sport:
    sport = Sport.query.filter_by(name=name).first()
    if sport:
        return sport

    sport = Sport(name=name)
    db.session.add(sport)
    db.session.flush()
    return sport


def get_or_create_competition(
    external_id: str, name: str, sport_id: int
) -> Competition:
    competition = Competition.query.filter_by(external_id=external_id).first()
    if competition:
        return competition

    competition = Competition(
        external_id=external_id,
        name=name,
        _sport_id=sport_id,
    )
    db.session.add(competition)
    db.session.flush()
    return competition


def get_or_create_stage(stage_data: dict | None) -> Stage | None:
    if not stage_data:
        return None

    external_id = stage_data.get("id")
    if not external_id:
        return None

    stage = Stage.query.filter_by(external_id=external_id).first()
    if stage:
        return stage

    stage = Stage(
        external_id=external_id,
        name=stage_data.get("name"),
        ordering=stage_data.get("ordering"),
    )
    db.session.add(stage)
    db.session.flush()
    return stage


def get_or_create_venue(stadium_name: str | None) -> Venue | None:
    if not stadium_name:
        return None

    venue = Venue.query.filter_by(name=stadium_name).first()
    if venue:
        return venue

    venue = Venue(name=stadium_name)
    db.session.add(venue)
    db.session.flush()
    return venue


def get_or_create_team(team_data: dict | None) -> Team | None:
    if not team_data:
        return None

    slug = team_data.get("slug")
    name = team_data.get("name")

    if slug:
        existing_team = Team.query.filter_by(slug=slug).first()
        if existing_team:
            return existing_team

    existing_team = Team.query.filter_by(name=name).first()
    if existing_team:
        return existing_team

    team = Team(
        name=name,
        official_name=team_data.get("officialName"),
        slug=slug,
        abbreviation=team_data.get("abbreviation"),
        country_code=team_data.get("teamCountryCode"),
    )
    db.session.add(team)
    db.session.flush()
    return team


def event_already_exists(
    event_date, event_time, competition_id, home_team_id, away_team_id
) -> bool:
    existing_event = Event.query.filter_by(
        event_date=event_date,
        event_time_utc=event_time,
        _competition_id=competition_id,
        _home_team_id=home_team_id,
        _away_team_id=away_team_id,
    ).first()
    return existing_event is not None


def seed_data():
    with open("data/sample_events.json", "r", encoding="utf-8") as file:
        payload = json.load(file)

    events_data = payload.get("data", [])

    football = get_or_create_sport("Football")

    inserted_count = 0
    skipped_count = 0

    for item in events_data:
        competition = get_or_create_competition(
            external_id=item.get("originCompetitionId"),
            name=item.get("originCompetitionName"),
            sport_id=football.id,
        )

        stage = get_or_create_stage(item.get("stage"))
        venue = get_or_create_venue(item.get("stadium"))
        home_team = get_or_create_team(item.get("homeTeam"))
        away_team = get_or_create_team(item.get("awayTeam"))

        event_date = datetime.strptime(item["dateVenue"], "%Y-%m-%d").date()
        event_time = datetime.strptime(item["timeVenueUTC"], "%H:%M:%S").time()

        result = item.get("result") or {}

        home_team_id = home_team.id if home_team else None
        away_team_id = away_team.id if away_team else None

        if event_already_exists(
            event_date=event_date,
            event_time=event_time,
            competition_id=competition.id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
        ):
            skipped_count += 1
            continue

        event = Event(
            season=item.get("season"),
            status=item.get("status"),
            event_date=event_date,
            event_time_utc=event_time,
            description=(
                f"{competition.name} - {stage.name}" if stage else competition.name
            ),
            _sport_id=football.id,
            _competition_id=competition.id,
            _stage_id=stage.id if stage else None,
            _venue_id=venue.id if venue else None,
            _home_team_id=home_team_id,
            _away_team_id=away_team_id,
            home_goals=result.get("homeGoals"),
            away_goals=result.get("awayGoals"),
            winner=result.get("winner"),
        )

        db.session.add(event)
        inserted_count += 1

    db.session.commit()
    print(
        f"Seeding complete. Inserted: {inserted_count}, Skipped duplicates: {skipped_count}"
    )


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_data()
