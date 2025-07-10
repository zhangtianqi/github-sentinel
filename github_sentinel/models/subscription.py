# github_sentinel/models/subscription.py

# CHANGE: Import TypeDecorator
from sqlalchemy import Column, Integer, String, DateTime, TypeDecorator
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone


# NEW: Define a custom type to handle timezones with SQLite
class AwareDateTime(TypeDecorator):
    """
    A custom SQLAlchemy type that ensures datetimes are always timezone-aware (UTC).
    This is necessary for SQLite, which doesn't natively support timezone-aware datetimes.
    """
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> str | None:
        # On the way in (to the DB), if it's aware, convert to naive UTC
        if value is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return None

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        # On the way out (from the DB), if it's not None, assume it's UTC and make it aware
        if value is not None:
            return value.replace(tzinfo=timezone.utc)
        return None


Base = declarative_base()


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    repo_url = Column(String, unique=True, nullable=False, index=True)
    schedule = Column(String, default="daily", nullable=False)
    # CHANGE: Use our new AwareDateTime type
    created_at = Column(AwareDateTime, default=lambda: datetime.now(timezone.utc))
    last_checked_at = Column(AwareDateTime, nullable=True)

    def __repr__(self):
        return f"<Subscription(repo='{self.repo_url}', schedule='{self.schedule}')>"