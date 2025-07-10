from apscheduler.schedulers.blocking import BlockingScheduler
from github_sentinel.core.processor import run_once

def start_scheduler():
    """Initializes and starts the task scheduler."""
    scheduler = BlockingScheduler(timezone="UTC")
    
    # This is a simple schedule. Can be enhanced to read schedules from the DB.
    scheduler.add_job(run_once, 'interval', hours=24, id='daily_check') 
    
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")
