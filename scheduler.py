"""Scheduler for GitHub Tweet Bot - runs every 30 minutes during active hours."""
import schedule
import time
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

def run_bot():
    """Execute the GitHub Tweet Bot with progress display."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Starting GitHub Tweet Bot...")
    
    try:
        # Run the bot with real-time output
        process = subprocess.Popen([
            sys.executable, "-m", "src.main"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
           text=True, cwd=Path(__file__).parent, bufsize=1, universal_newlines=True)
        
        # Parse and display progress in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                parse_and_display_log(output.strip())
        
        # Get final result
        stderr = process.stderr.read()
        
        if process.returncode == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Bot completed successfully")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Bot failed:")
            if stderr:
                print(stderr)
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error: {e}")

def parse_and_display_log(log_line):
    """Parse JSON log and display user-friendly progress."""
    try:
        import json
        log_data = json.loads(log_line)
        step = log_data.get('step', '')
        event = log_data.get('event', '')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Map steps to user-friendly messages
        step_messages = {
            'workflow_start': '🔄 Starting workflow...',
            'github_fetch': f"📡 Fetching {log_data.get('limit', 20)} trending repos (attempt {log_data.get('attempt', 1)})...",
            'github_success': f"✅ Found {log_data.get('count', 0)} trending repositories",
            'step_1_success': f"🎯 Selected: {log_data.get('repo_name', 'repo')}",
            'screenshot_start': f"📸 Capturing screenshot (attempt {log_data.get('attempt', 1)})...",
            'screenshot_success': '✅ Screenshot captured',
            'readme_fetch': f"📖 Fetching README (attempt {log_data.get('attempt', 1)})...",
            'readme_success': f"✅ README loaded ({log_data.get('length', 0)} chars)",
            'ai_summarize': '🤖 Generating AI summary...',
            'ai_summary_success': f"✅ Summary generated ({log_data.get('summary_length', 0)} chars)",
            'ai_features': '🔍 Extracting key features...',
            'ai_features_success': f"✅ Features extracted ({log_data.get('count', 0)} items)",
            'tweets_ready': f"📝 Tweets ready (main: {log_data.get('main_length', 0)}, reply: {log_data.get('reply_length', 0)} chars)",
            'tweet_validation_start': '🤖 Validating tweet content...',
            'tweet_validation_success': f"✅ Tweet validation passed ({log_data.get('provider', 'AI')})",
            'tweet_validation_failed': f"⚠️ Tweet validation warning: {log_data.get('reason', 'Unknown')}",
            'tweets_validated': f"✅ Tweets validated (status: {log_data.get('validation_status', 'unknown')})",
            'tweet_correction_start': '🔧 Attempting AI correction...',
            'tweet_correction_success': f"✅ Tweet corrected by AI ({log_data.get('provider', 'AI')})",
            'tweet_correction_failed': '⚠️ AI correction failed, using original',
            'tweet_revalidation_start': '🔄 Re-validating corrected tweets...',
            'tweet_revalidation_success': f"✅ Corrected tweets validated ({log_data.get('provider', 'AI')})",
            'tweet_revalidation_warning': f"⚠️ Corrected tweets still have issues: {log_data.get('reason', 'Unknown')}",
            'tweet_create': f"🐦 Creating tweet (attempt {log_data.get('attempt', 1)})...",
            'media_upload_success': '📎 Image uploaded successfully',
            'tweet_success': f"✅ Tweet posted: {log_data.get('tweet_id', 'ID')}",
            'reply_create': f"💬 Creating reply (attempt {log_data.get('attempt', 1)})...",
            'reply_success': f"✅ Reply posted: {log_data.get('reply_id', 'ID')}",
            'workflow_success': f"🎉 Workflow completed in {log_data.get('duration', 'N/A')} - Tweet: {log_data.get('main_tweet_id', 'N/A')}"
        }
        
        # Display rate limit info
        if 'Rate limit exceeded' in log_line:
            print(f"[{timestamp}] ⏳ Rate limit hit - waiting...")
            return
        
        # Display progress message
        message = step_messages.get(step, f"ℹ️ {event}" if event else log_line)
        print(f"[{timestamp}] {message}")
        
    except (json.JSONDecodeError, KeyError):
        # Not JSON or missing fields - display as is
        if log_line.strip() and not log_line.startswith('HTTP Request:'):
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] {log_line}")

def should_run_now():
    """Check if bot should run now (9h00-21h00 France time for 4 tweets max)."""
    now = datetime.now()
    current_hour = now.hour
    
    # DEBUG: Always run for testing (comment out for production)
    # return True
    
    # Active hours: 9h00 to 21h00 (France timezone) = 4 slots × 4h = 4 tweets/day max
    # Créneaux: 9h, 13h, 17h, 21h
    if current_hour in [9, 13, 17, 21]:
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
    print("📅 Schedule: Every 4 hours")
    print("⏰ Active hours: 9h, 13h, 17h, 21h (France time)")
    print("📊 Max tweets/day: 4 (ultra-safe for 17/24h limit)")
    print("=" * 50)
    
    # Check every hour for active slots
    schedule.every().hour.do(scheduled_run)
    
    # Run once immediately if in active hours
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Starting initial run...")
    scheduled_run()
    
    # Keep running
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Scheduler running, checking every minute...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
        
        # Show status every 30 minutes
        if datetime.now().minute % 30 == 0:
            current_hour = datetime.now().hour
            
            # Calculate next active slot
            active_hours = [9, 13, 17, 21]
            next_active = None
            for hour in active_hours:
                if hour > current_hour:
                    next_active = hour
                    break
            if not next_active:
                next_active = active_hours[0] + 24  # Tomorrow 9h
            
            hours_until_next = next_active - current_hour
            
            if should_run_now():
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💓 Active slot - Running bot now!")
                run_bot()
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 😴 Outside active slots (9h,13h,17h,21h) - Next in {hours_until_next}h")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🛑 Scheduler stopped by user")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Scheduler error: {e}")