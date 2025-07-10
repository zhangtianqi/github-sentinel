import typer
from typing_extensions import Annotated
from github_sentinel.core.processor import run_once
from github_sentinel.core.scheduler import start_scheduler
from github_sentinel.components.db_manager import add_subscription, list_subscriptions, remove_subscription

app = typer.Typer()

@app.command()
def run(once: Annotated[bool, typer.Option("--once", help="Run the check a single time and exit.")] = False):
    """
    Starts GitHub Sentinel.
    By default, it runs in scheduler mode to perform periodic checks.
    """
    if once:
        print("Running a single check for all subscribed repositories...")
        run_once()
        print("Single run finished.")
    else:
        print("Starting the scheduler for periodic checks...")
        start_scheduler()

@app.command()
def add_repo(repo_url: str, schedule: str = "daily"):
    """Adds a new repository to the subscription list."""
    add_subscription(repo_url, schedule)
    print(f"Repository {repo_url} added with a '{schedule}' schedule.")

@app.command()
def remove_repo(repo_url: str):
    """Removes a repository from the subscription list."""
    if remove_subscription(repo_url):
        print(f"Repository {repo_url} has been removed.")
    else:
        print(f"Repository {repo_url} not found in subscriptions.")


@app.command()
def list_repos():
    """Lists all subscribed repositories."""
    subscriptions = list_subscriptions()
    if not subscriptions:
        print("No repositories subscribed yet. Use 'add-repo' to add one.")
        return
        
    print("Subscribed Repositories:")
    for sub in subscriptions:
        last_checked = sub.last_checked_at.strftime('%Y-%m-%d %H:%M:%S UTC') if sub.last_checked_at else "Never"
        print(f"- {sub.repo_url} (Schedule: {sub.schedule}, Last Checked: {last_checked})")

if __name__ == "__main__":
    app()
