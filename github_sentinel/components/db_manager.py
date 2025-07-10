from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from github_sentinel.models.subscription import Base, Subscription
from github_sentinel.components.config_loader import config
import datetime
from datetime import datetime, timezone # <-- ADD timezone

engine = create_engine(f"sqlite:///{config['database']['path']}")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    return SessionLocal()

def add_subscription(repo_url, schedule):
    session = get_db_session()
    existing = session.query(Subscription).filter_by(repo_url=repo_url).first()
    if existing:
        print(f"Warning: Repository {repo_url} is already subscribed.")
        session.close()
        return
    
    new_sub = Subscription(repo_url=repo_url, schedule=schedule)
    session.add(new_sub)
    session.commit()
    session.close()

def remove_subscription(repo_url):
    session = get_db_session()
    sub = session.query(Subscription).filter_by(repo_url=repo_url).first()
    if sub:
        session.delete(sub)
        session.commit()
        session.close()
        return True
    session.close()
    return False

def get_all_subscriptions():
    session = get_db_session()
    subs = session.query(Subscription).all()
    session.close()
    return subs

def list_subscriptions():
    return get_all_subscriptions()

def update_last_checked(subscription_id):
    session = get_db_session()
    sub = session.query(Subscription).filter_by(id=subscription_id).first()
    if sub:
        # CHANGE: Use an aware datetime here as well
        sub.last_checked_at = datetime.now(timezone.utc) # <-- MODIFIED
        session.commit()
    session.close()

def get_subscription_by_url(repo_url: str) -> Subscription | None:
    """按 URL 查询单个订阅记录。"""
    session = get_db_session()
    sub = session.query(Subscription).filter_by(repo_url=repo_url).first()
    session.close()
    return sub