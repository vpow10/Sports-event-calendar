from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import func, or_
from sqlalchemy.orm import aliased, joinedload

from app import db
from app.forms import EventForm
from app.models import Competition, Event, Sport, Stage, Team, Venue

main = Blueprint("main", __name__)


def normalize_text(value):
    if value is None:
        return None

    cleaned = value.strip()
    return cleaned if cleaned else None


def get_or_create_sport(name):
    normalized_name = normalize_text(name)
    if not normalized_name:
        return None

    sport = Sport.query.filter(
        func.lower(Sport.name) == normalized_name.lower()
    ).first()
    if sport:
        return sport

    sport = Sport(name=normalized_name)
    db.session.add(sport)
    db.session.flush()
    return sport


def get_or_create_competition(name, sport_id):
    normalized_name = normalize_text(name)
    if not normalized_name:
        return None

    competition = Competition.query.filter(
        func.lower(Competition.name) == normalized_name.lower(),
        Competition._sport_id == sport_id,
    ).first()

    if competition:
        return competition

    external_id = f"manual-{normalized_name.lower().replace(' ', '-')}-{sport_id}"

    competition = Competition(
        name=normalized_name,
        external_id=external_id,
        _sport_id=sport_id,
    )
    db.session.add(competition)
    db.session.flush()
    return competition


def get_or_create_stage(name):
    normalized_name = normalize_text(name)
    if not normalized_name:
        return None

    stage = Stage.query.filter(
        func.lower(Stage.name) == normalized_name.lower()
    ).first()
    if stage:
        return stage

    external_id = f"manual-{normalized_name.lower().replace(' ', '-')}"

    stage = Stage(
        name=normalized_name,
        external_id=external_id,
        ordering=None,
    )
    db.session.add(stage)
    db.session.flush()
    return stage


def get_or_create_venue(name):
    normalized_name = normalize_text(name)
    if not normalized_name:
        return None

    venue = Venue.query.filter(
        func.lower(Venue.name) == normalized_name.lower()
    ).first()
    if venue:
        return venue

    venue = Venue(name=normalized_name)
    db.session.add(venue)
    db.session.flush()
    return venue


def get_or_create_team(name):
    normalized_name = normalize_text(name)
    if not normalized_name:
        return None

    team = Team.query.filter(func.lower(Team.name) == normalized_name.lower()).first()
    if team:
        return team

    slug = normalized_name.lower().replace(" ", "-")

    existing_slug_team = Team.query.filter_by(slug=slug).first()
    if existing_slug_team:
        return existing_slug_team

    team = Team(
        name=normalized_name,
        official_name=normalized_name,
        slug=slug,
        abbreviation=None,
        country_code=None,
    )
    db.session.add(team)
    db.session.flush()
    return team


@main.route("/")
def home():
    return redirect(url_for("main.list_events"))


@main.route("/events")
def list_events():
    sport_filter = request.args.get("sport", "").strip()
    status_filter = request.args.get("status", "").strip()
    search_query = request.args.get("q", "").strip()

    home_team_alias = aliased(Team)
    away_team_alias = aliased(Team)

    query = Event.query.options(
        joinedload(Event.sport),
        joinedload(Event.competition),
        joinedload(Event.stage),
        joinedload(Event.venue),
        joinedload(Event.home_team),
        joinedload(Event.away_team),
    )

    if sport_filter:
        query = query.join(Event.sport).filter(
            func.lower(Sport.name) == sport_filter.lower()
        )

    if status_filter:
        query = query.filter(func.lower(Event.status) == status_filter.lower())

    if search_query:
        search_term = f"%{search_query.lower()}%"
        query = (
            query.join(Event.competition)
            .outerjoin(home_team_alias, Event._home_team_id == home_team_alias.id)
            .outerjoin(away_team_alias, Event._away_team_id == away_team_alias.id)
            .filter(
                or_(
                    func.lower(Competition.name).like(search_term),
                    func.lower(home_team_alias.name).like(search_term),
                    func.lower(away_team_alias.name).like(search_term),
                )
            )
        )

    events = (
        query.distinct()
        .order_by(Event.event_date.asc(), Event.event_time_utc.asc())
        .all()
    )

    sports = Sport.query.order_by(Sport.name.asc()).all()
    available_statuses = ["scheduled", "played", "cancelled", "postponed"]

    return render_template(
        "events.html",
        events=events,
        sports=sports,
        available_statuses=available_statuses,
        selected_sport=sport_filter,
        selected_status=status_filter,
        search_query=search_query,
    )


@main.route("/events/<int:event_id>")
def event_detail(event_id):
    event = (
        Event.query.options(
            joinedload(Event.sport),
            joinedload(Event.competition),
            joinedload(Event.stage),
            joinedload(Event.venue),
            joinedload(Event.home_team),
            joinedload(Event.away_team),
        )
        .filter_by(id=event_id)
        .first()
    )

    if event is None:
        abort(404)

    return render_template("event_detail.html", event=event)


@main.route("/events/new", methods=["GET", "POST"])
def create_event():
    form = EventForm()

    if form.validate_on_submit():
        sport = get_or_create_sport(form.sport_name.data)
        competition = get_or_create_competition(form.competition_name.data, sport.id)
        stage = get_or_create_stage(form.stage_name.data)
        venue = get_or_create_venue(form.venue_name.data)
        home_team = get_or_create_team(form.home_team_name.data)
        away_team = get_or_create_team(form.away_team_name.data)

        event = Event(
            season=form.season.data,
            status=form.status.data,
            event_date=form.event_date.data,
            event_time_utc=form.event_time_utc.data,
            description=normalize_text(form.description.data),
            _sport_id=sport.id,
            _competition_id=competition.id,
            _stage_id=stage.id if stage else None,
            _venue_id=venue.id if venue else None,
            _home_team_id=home_team.id if home_team else None,
            _away_team_id=away_team.id if away_team else None,
            home_goals=form.home_goals.data,
            away_goals=form.away_goals.data,
            winner=normalize_text(form.winner.data),
        )

        db.session.add(event)
        db.session.commit()

        flash("Event created successfully.", "success")
        return redirect(url_for("main.event_detail", event_id=event.id))

    return render_template("add_event.html", form=form)
