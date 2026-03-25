from app import db


class Sport(db.Model):
    __tablename__ = "sports"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    competitions = db.relationship("Competition", back_populates="sport", lazy=True)
    events = db.relationship("Event", back_populates="sport", lazy=True)

    def __repr__(self):
        return f"<Sport {self.name}>"


class Competition(db.Model):
    __tablename__ = "competitions"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)

    _sport_id = db.Column(db.Integer, db.ForeignKey("sports.id"), nullable=False)

    sport = db.relationship("Sport", back_populates="competitions")
    events = db.relationship("Event", back_populates="competition", lazy=True)

    def __repr__(self):
        return f"<Competition {self.name}>"


class Stage(db.Model):
    __tablename__ = "stages"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    ordering = db.Column(db.Integer, nullable=True)

    events = db.relationship("Event", back_populates="stage", lazy=True)

    def __repr__(self):
        return f"<Stage {self.name}>"


class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    events = db.relationship("Event", back_populates="venue", lazy=True)

    def __repr__(self):
        return f"<Venue {self.name}>"


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    official_name = db.Column(db.String(200), nullable=True)
    slug = db.Column(db.String(150), unique=True, nullable=True)
    abbreviation = db.Column(db.String(20), nullable=True)
    country_code = db.Column(db.String(10), nullable=True)

    home_events = db.relationship(
        "Event",
        foreign_keys="Event._home_team_id",
        back_populates="home_team",
        lazy=True,
    )

    away_events = db.relationship(
        "Event",
        foreign_keys="Event._away_team_id",
        back_populates="away_team",
        lazy=True,
    )

    def __repr__(self):
        return f"<Team {self.name}>"


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_time_utc = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text, nullable=True)

    _sport_id = db.Column(db.Integer, db.ForeignKey("sports.id"), nullable=False)
    _competition_id = db.Column(
        db.Integer, db.ForeignKey("competitions.id"), nullable=False
    )
    _stage_id = db.Column(db.Integer, db.ForeignKey("stages.id"), nullable=True)
    _venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=True)
    _home_team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=True)
    _away_team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=True)

    home_goals = db.Column(db.Integer, nullable=True)
    away_goals = db.Column(db.Integer, nullable=True)
    winner = db.Column(db.String(150), nullable=True)

    sport = db.relationship("Sport", back_populates="events")
    competition = db.relationship("Competition", back_populates="events")
    stage = db.relationship("Stage", back_populates="events")
    venue = db.relationship("Venue", back_populates="events")

    home_team = db.relationship(
        "Team",
        foreign_keys=[_home_team_id],
        back_populates="home_events",
    )

    away_team = db.relationship(
        "Team",
        foreign_keys=[_away_team_id],
        back_populates="away_events",
    )

    def __repr__(self):
        home_name = self.home_team.name if self.home_team else "TBD"
        away_name = self.away_team.name if self.away_team else "TBD"
        return f"<Event {home_name} vs {away_name} on {self.event_date}>"
