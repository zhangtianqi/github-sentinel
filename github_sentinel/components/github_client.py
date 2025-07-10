from github import Github, GithubException
from github_sentinel.components.config_loader import config
from datetime import datetime, timedelta, timezone

class GitHubClient:
    def __init__(self):
        try:
            self.gh = Github(config['github']['token'])
        except Exception as e:
            raise ConnectionError(f"Failed to connect to GitHub. Check your token. Error: {e}")

    def fetch_updates(self, repo_url: str, since: datetime | None) -> dict:
        """Fetch all relevant updates from a repository since a given time."""
        try:
            repo_name = repo_url.replace("https://github.com/", "").strip('/')
            repo = self.gh.get_repo(repo_name)
        except GithubException as e:
            raise ValueError(f"Could not access repository '{repo_name}'. Is the URL correct and token valid? Error: {e.data}")
        
        # If 'since' is None (first run for this repo), fetch updates from the last 24 hours.
        if since is None:
            # First run, create a new aware datetime. This is correct.
            since = datetime.now(timezone.utc) - timedelta(days=1)
        elif since.tzinfo is None:
            # DEFENSIVE CHECK: If the datetime from DB is naive, FIX IT.
            # This is our safety net that catches the error.
            print(f"Warning: Received a naive datetime '{since}' from the database. Assuming it is UTC and making it timezone-aware.")
            since = since.replace(tzinfo=timezone.utc)
            
        updates = {
            "commits": [], "issues": [], "pull_requests": [], "releases": []
        }
        
        # 1. Fetch Commits
        for commit in repo.get_commits(since=since):
            updates["commits"].append({
                "sha": commit.sha,
                "author": commit.commit.author.name,
                "message": commit.commit.message.split('\n')[0],
                "url": commit.html_url
            })
            
        # 2. Fetch Issues and Pull Requests
        for issue in repo.get_issues(since=since, state="all", sort="updated"):
            item = {
                "number": issue.number, "title": issue.title, "user": issue.user.login,
                "state": issue.state, "url": issue.html_url,
                "created_at": issue.created_at, "updated_at": issue.updated_at,
                "closed_at": issue.closed_at
            }
            if issue.pull_request:
                updates["pull_requests"].append(item)
            else:
                updates["issues"].append(item)

        # 3. Fetch Releases
        for release in repo.get_releases():
            if release.published_at and release.published_at > since:
                updates["releases"].append({
                    "tag_name": release.tag_name, "name": release.title,
                    "author": release.author.login, "url": release.html_url
                })
                
        return updates
