from github_sentinel.components.db_manager import get_all_subscriptions, update_last_checked
from github_sentinel.components.github_client import GitHubClient
from github_sentinel.components.summarizer import get_summarizer
from github_sentinel.components.notifiers import dispatch_notification

def process_subscription(subscription):
    """
    Processes a single repository subscription.
    Fetches updates, generates a summary, and sends notifications.
    """
    print(f"Processing {subscription.repo_url}...")
    
    # 1. Initialize components
    client = GitHubClient()
    summarizer = get_summarizer() # 使用工厂函数
    
    # 2. Fetch updates since the last check
    updates = client.fetch_updates(subscription.repo_url, since=subscription.last_checked_at)
    
    # Check if there's anything to report
    if not any(updates.values()):
        print(f"No new updates for {subscription.repo_url}.")
        update_last_checked(subscription.id) # Still update the timestamp
        return

    # 3. Use AI to generate a summary report
    print(f"Generating AI summary for {subscription.repo_url}...")
    report = summarizer.summarize(repo_url=subscription.repo_url, updates=updates)
    
    # 4. Dispatch the report to configured notifiers
    print(f"Sending notification for {subscription.repo_url}...")
    print(f"report: {report}")
    dispatch_notification(report)
    
    # 5. Update the 'last_checked_at' timestamp in the database
    # update_last_checked(subscription.id)
    print(f"Finished processing {subscription.repo_url}.")


def run_once():
    """Runs the complete check-and-report process for all subscriptions."""
    subscriptions = get_all_subscriptions()
    if not subscriptions:
        print("No subscriptions found. Exiting.")
        return

    for sub in subscriptions:
        try:
            process_subscription(sub)
        except Exception as e:
            print(f"ERROR: Failed to process {sub.repo_url}. Reason: {e}")


from github_sentinel.components.db_manager import get_subscription_by_url # <-- 新增导入

def check_single_repo(repo_url: str):
    """
    按需立即检查单个仓库。
    """
    subscription = get_subscription_by_url(repo_url)
    if not subscription:
        print(f"ERROR: Repository '{repo_url}' is not subscribed. Use 'add' command first.")
        return

    try:
        # 复用已有的处理逻辑
        process_subscription(subscription)
    except Exception as e:
        print(f"ERROR: Failed to process {subscription.repo_url}. Reason: {e}")