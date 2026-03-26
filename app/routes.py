from flask import Blueprint, abort, redirect, render_template, url_for
from sqlalchemy.orm import joinedload

from app.models import Event

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return redirect(url_for("main.list_events"))


@main.route("/events")
def list_events():
    events = (
        Event.query.options(
            joinedload(Event.sport),
            joinedload(Event.competition),
            joinedload(Event.stage),
            joinedload(Event.venue),
            joinedload(Event.home_team),
            joinedload(Event.away_team),
        )
        .order_by(Event.event_date.asc(), Event.event_time_utc.asc())
        .all()
    )

    return render_template("events.html", events=events)


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
