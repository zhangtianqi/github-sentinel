# github_sentinel/interactive.py

import time
from apscheduler.schedulers.background import BackgroundScheduler
from github_sentinel.core.processor import run_once, check_single_repo
from github_sentinel.components.db_manager import add_subscription, list_subscriptions, remove_subscription


def print_help():
    """打印帮助菜单"""
    print("\n--- GitHub Sentinel Interactive CLI ---")
    print("Available Commands:")
    print("  add <repo_url>       - Subscribe to a new repository (e.g., add https://github.com/owner/repo)")
    print("  remove <repo_url>    - Unsubscribe from a repository")
    print("  list                 - List all subscribed repositories")
    print("  check <repo_url>     - Trigger an immediate check for a specific repository")
    print("  checkall             - Trigger an immediate check for ALL subscribed repositories")
    print("  help                 - Show this help menu")
    print("  exit                 - Quit the application")
    print("---------------------------------------")


def interactive_session():
    """启动交互式会话和后台调度器"""
    # 1. 初始化并启动后台调度器
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(run_once, 'interval', hours=24, id='daily_check')
    scheduler.start()
    print("✅ Background scheduler started. It will check all repos every 24 hours.")

    print_help()

    try:
        while True:
            # 2. 创建主循环，等待用户输入
            user_input = input("\nsentinel> ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:]

            # 3. 解析并执行命令
            if command == "exit":
                break
            elif command == "help":
                print_help()
            elif command == "add" and len(args) == 1:
                repo_url = args[0]
                add_subscription(repo_url, "daily")
                print(f"👍 Repository {repo_url} added to subscriptions.")
            elif command == "remove" and len(args) == 1:
                repo_url = args[0]
                if remove_subscription(repo_url):
                    print(f"🗑️ Repository {repo_url} removed.")
                else:
                    print(f"❓ Repository {repo_url} not found.")
            elif command == "list":
                subs = list_subscriptions()
                if not subs:
                    print("No repositories subscribed yet.")
                else:
                    print("\n--- Subscribed Repositories ---")
                    for sub in subs:
                        last_checked = sub.last_checked_at.strftime(
                            '%Y-%m-%d %H:%M') if sub.last_checked_at else "Never"
                        print(f"- {sub.repo_url} (Last checked: {last_checked})")
            elif command == "check" and len(args) == 1:
                repo_url = args[0]
                print(f"⚡ Triggering immediate check for {repo_url}...")
                check_single_repo(repo_url)
            elif command == "checkall":
                print("⚡ Triggering immediate check for ALL repositories...")
                run_once()
            else:
                print(f"❌ Unknown command or incorrect arguments: '{user_input}'")
                print_help()

    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
    finally:
        # 4. 优雅地关闭调度器
        print("Shutting down background scheduler...")
        scheduler.shutdown()
        print("Goodbye!")


if __name__ == "__main__":
    interactive_session()