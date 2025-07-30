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
    """Check if bot should run now (from 09h00 to 00h00 included, every 30 min)."""
    now = datetime.now()
    current_hour = now.hour
    # Autorisé de 9h00 à 23h59 (inclus), donc 9 <= hour < 24
    return 9 <= current_hour < 24

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
    print("⏰ Active hours: 09h00 to 00h00 (France time)")
    print("=" * 50)
    
    # Run every 30 minutes
    schedule.every(30).minutes.do(scheduled_run)
    
    # Run once immediately if in active hours
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Starting initial run...")
    scheduled_run()
    
    # Keep running
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Scheduler running. Next check every 30 minutes.")
    while True:
        schedule.run_pending()
        # Le planificateur gère le timing, nous avons juste besoin d'une petite pause.
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🛑 Scheduler stopped by user")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Scheduler error: {e}")