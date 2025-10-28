"""NFL Database Models

Minimal models to support AI prediction system.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Player(Base):
    """NFL Player"""
    __tablename__ = "players"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    player_position = Column(String)  # QB, RB, WR, TE, etc.
    team_id = Column(String)
    jersey_number = Column(Integer)
    status = Column(String, default="ACTIVE")  # ACTIVE, INACTIVE, INJURED, etc.

    # External IDs for API syncing
    espn_id = Column(String, unique=True, index=True)
    sleeper_id = Column(String, unique=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    game_stats = relationship("PlayerGameStats", back_populates="player")


class Team(Base):
    """NFL Team"""
    __tablename__ = "teams"

    id = Column(String, primary_key=True)  # Team abbreviation (e.g., "KC", "BUF")
    name = Column(String, nullable=False)
    city = Column(String)
    conference = Column(String)  # AFC or NFC
    division = Column(String)


class Game(Base):
    """NFL Game"""
    __tablename__ = "games"

    id = Column(String, primary_key=True)
    season = Column(Integer, nullable=False, index=True)
    week = Column(Integer, nullable=False, index=True)
    game_date = Column(Date, index=True)
    game_time = Column(DateTime)

    # Teams
    home_team_id = Column(String, ForeignKey("teams.id"))
    away_team_id = Column(String, ForeignKey("teams.id"))
    opponent_team_id = Column(String)  # For reference

    # Scores
    home_score = Column(Integer)
    away_score = Column(Integer)
    is_completed = Column(Boolean, default=False)

    # Weather
    weather_description = Column(String)
    temperature = Column(Float)
    wind_speed = Column(Float)
    is_dome = Column(Boolean, default=False)

    # Vegas Lines
    vegas_line = Column(Float)  # Spread
    over_under = Column(Float)  # Total points

    # External IDs
    espn_id = Column(String, unique=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlayerGameStats(Base):
    """Player statistics for a single game"""
    __tablename__ = "player_game_stats"

    id = Column(String, primary_key=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False, index=True)
    game_id = Column(String, ForeignKey("games.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    week = Column(Integer, nullable=False)

    # Snap counts
    snap_count = Column(Integer)
    snap_percentage = Column(Float)

    # Passing stats
    passing_completions = Column(Integer)
    passing_attempts = Column(Integer)
    passing_yards = Column(Integer)
    passing_touchdowns = Column(Integer)
    passing_long = Column(Integer)
    interceptions = Column(Integer)

    # Rushing stats
    rushing_attempts = Column(Integer)
    rushing_yards = Column(Integer)
    rushing_touchdowns = Column(Integer)
    rushing_long = Column(Integer)

    # Receiving stats
    receiving_targets = Column(Integer)
    receiving_receptions = Column(Integer)
    receiving_yards = Column(Integer)
    receiving_touchdowns = Column(Integer)
    receiving_long = Column(Integer)

    # Fantasy
    fantasy_points = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="game_stats")


class PrizePicksProjection(Base):
    """PrizePicks prop projection"""
    __tablename__ = "prizepicks_projections"

    id = Column(String, primary_key=True)
    player_name = Column(String, nullable=False, index=True)
    stat_type = Column(String, nullable=False)  # receiving_yards, rushing_yards, etc.
    line_score = Column(Float, nullable=False)  # The over/under line
    league = Column(String, default="NFL")
    game_time = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)

    # External IDs
    external_id = Column(String, unique=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeamDefensiveStats(Base):
    """Team defensive statistics vs positions"""
    __tablename__ = "team_defensive_stats"

    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    season = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)  # 0 for season average

    # What position are we measuring defense against?
    defensive_position = Column(String, nullable=False)  # QB, RB, WR, TE

    # Rankings
    rank_vs_position = Column(Integer)  # 1-32 rank
    avg_points_allowed = Column(Float)

    # Additional stats
    games_played = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class PlayerInjury(Base):
    """Player injury status"""
    __tablename__ = "player_injuries"

    id = Column(String, primary_key=True)
    player_id = Column(String, ForeignKey("players.id"), nullable=False, index=True)

    # Injury details
    injury_status = Column(String)  # QUESTIONABLE, OUT, IR, etc.
    injury_type = Column(String)  # Ankle, Hamstring, etc.
    description = Column(Text)

    # Timeline
    injured_date = Column(Date)
    expected_return = Column(Date)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Prediction(Base):
    """AI prediction records"""
    __tablename__ = "predictions"

    id = Column(String, primary_key=True)
    prop_id = Column(String, ForeignKey("prizepicks_projections.id"))
    player_id = Column(String, ForeignKey("players.id"), index=True)

    # Player/Game context
    player_name = Column(String, nullable=False, index=True)
    player_position = Column(String, index=True)
    team = Column(String)
    opponent = Column(String)
    week = Column(Integer, index=True)
    season = Column(Integer, default=2025)
    game_time = Column(DateTime, index=True)

    # Prop details
    stat_type = Column(String, nullable=False, index=True)
    line_score = Column(Float, nullable=False)

    # Prediction details
    prediction = Column(String, nullable=False)  # OVER or UNDER
    confidence = Column(Integer, nullable=False, index=True)  # 0-100
    projected_value = Column(Float, nullable=False)
    edge = Column(Float)  # projected_value - line_score
    reasoning = Column(Text)
    key_factors = Column(Text)  # JSON array
    risk_factors = Column(Text)  # JSON array
    comparable_game = Column(String)

    # Model info
    model_version = Column(String)
    similar_situations_count = Column(Integer)

    # Status
    is_active = Column(Boolean, default=True, index=True)  # For showing in opportunities feed
    is_archived = Column(Boolean, default=False)

    # Actual outcome (filled in after game)
    actual_value = Column(Float)
    was_correct = Column(Boolean)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
