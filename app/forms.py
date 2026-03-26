from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class EventForm(FlaskForm):
    season = IntegerField(
        "Season",
        validators=[DataRequired(), NumberRange(min=1900, max=3000)],
    )

    status = SelectField(
        "Status",
        choices=[
            ("scheduled", "Scheduled"),
            ("played", "Played"),
            ("cancelled", "Cancelled"),
            ("postponed", "Postponed"),
        ],
        validators=[DataRequired()],
    )

    event_date = DateField(
        "Event Date",
        format="%Y-%m-%d",
        validators=[DataRequired()],
    )

    event_time_utc = TimeField(
        "Event Time (UTC)",
        format="%H:%M",
        validators=[DataRequired()],
    )

    sport_name = StringField(
        "Sport",
        validators=[DataRequired(), Length(max=100)],
    )

    competition_name = StringField(
        "Competition",
        validators=[DataRequired(), Length(max=150)],
    )

    stage_name = StringField(
        "Stage",
        validators=[Optional(), Length(max=100)],
    )

    venue_name = StringField(
        "Venue",
        validators=[Optional(), Length(max=150)],
    )

    home_team_name = StringField(
        "Home Team",
        validators=[Optional(), Length(max=150)],
    )

    away_team_name = StringField(
        "Away Team",
        validators=[Optional(), Length(max=150)],
    )

    home_goals = IntegerField(
        "Home Goals",
        validators=[Optional(), NumberRange(min=0)],
    )

    away_goals = IntegerField(
        "Away Goals",
        validators=[Optional(), NumberRange(min=0)],
    )

    winner = StringField(
        "Winner",
        validators=[Optional(), Length(max=150)],
    )

    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=1000)],
    )

    submit = SubmitField("Create Event")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        home_team = (self.home_team_name.data or "").strip().lower()
        away_team = (self.away_team_name.data or "").strip().lower()

        if home_team and away_team and home_team == away_team:
            self.away_team_name.errors.append(
                "Home team and away team must be different."
            )
            return False

        return True
