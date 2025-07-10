# GitHub Sentinel

**GitHub Sentinel** is an open-source AI Agent designed for developers and project managers. It automatically fetches, summarizes, and reports the latest updates from your subscribed GitHub repositories on a daily or weekly basis.

## Features

- **Subscription Management**: Easily add, remove, and list repositories to monitor.
- **Automated Update Fetching**: Gathers new commits, issues, pull requests, and releases.
- **AI-Powered Summaries**: Uses a Large Language Model (LLM) to generate concise and insightful reports.
- **Notification System**: Pushes reports to platforms like Slack, Discord, or Email.

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://your-repo-url/github-sentinel.git
    cd github-sentinel
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure:**
    Copy `config.example.yaml` to `config.yaml` and fill in your API keys and settings.
    ```bash
    cp config.example.yaml config.yaml
    ```

4.  **Run the application:**
    ```bash
    # Add a repository
    python -m github_sentinel add-repo https://github.com/owner/repo

    # Run a single check
    python -m github_sentinel run --once

    # Start the scheduler for periodic checks
    python -m github_sentinel run
    ```
