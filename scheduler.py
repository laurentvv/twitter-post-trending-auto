"""Scheduler for GitHub Tweet Bot - runs every 30 minutes during active hours."""
import schedule
import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_bot():
    """Execute the GitHub Tweet Bot."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting GitHub Tweet Bot...")
    
    try:
        # Run the bot
        result = subprocess.run([
            sys.executable, "-m", "src.main"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Bot executed successfully")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Bot failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error: {e}")

def should_run_now():
    """Check if bot should run now (8h00-23h30 France time)."""
    now = datetime.now()
    current_hour = now.hour
    
    # Active hours: 8h00 to 23h30 (France timezone)
    if 8 <= current_hour <= 23:
        return True
    return False

def scheduled_run():
    """Run bot only during active hours."""
    if should_run_now():
        run_bot()
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Outside active hours (8h-23h30), skipping...")

def main():
    """Main scheduler loop."""
    print("🚀 GitHub Tweet Bot Scheduler Started")
    print("📅 Schedule: Every 30 minutes")
    print("⏰ Active hours: 8h00 - 23h30 (France time)")
    print("📊 Max tweets/month: 500 (≈16/day)")
    print("=" * 50)
    
    # Schedule every 30 minutes
    schedule.every(30).minutes.do(scheduled_run)
    
    # Run once immediately if in active hours
    scheduled_run()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🛑 Scheduler stopped by user")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Scheduler error: {e}")