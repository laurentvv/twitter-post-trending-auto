"""Enhanced Scheduler for GitHub Tweet Bot with rate limit management."""
import schedule
import time
import subprocess
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path


class RateLimitManager:
    """Manages rate limit information and scheduling adjustments."""
    
    def __init__(self):
        self.last_rate_limit_time = None
        self.rate_limit_duration = None
        self.consecutive_rate_limits = 0
        self.max_consecutive_limits = 3
    
    def record_rate_limit(self, duration_seconds: int = None):
        """Record a rate limit occurrence."""
        self.last_rate_limit_time = datetime.now()
        self.rate_limit_duration = duration_seconds
        self.consecutive_rate_limits += 1
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Rate limit recorded (#{self.consecutive_rate_limits})")
        
        if duration_seconds:
            next_attempt = datetime.now() + timedelta(seconds=duration_seconds)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Next attempt after: {next_attempt.strftime('%H:%M:%S')}")
    
    def reset_rate_limit_count(self):
        """Reset consecutive rate limit counter on successful run."""
        if self.consecutive_rate_limits > 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Rate limit streak broken after {self.consecutive_rate_limits} attempts")
            self.consecutive_rate_limits = 0
    
    def should_use_firefox_priority(self) -> bool:
        """Determine if Firefox should be prioritized over API."""
        # Use Firefox priority if we've hit rate limits recently
        if self.consecutive_rate_limits >= 2:
            return True
        
        # Use Firefox if last rate limit was within the last hour
        if self.last_rate_limit_time:
            time_since_limit = datetime.now() - self.last_rate_limit_time
            if time_since_limit < timedelta(hours=1):
                return True
        
        return False
    
    def get_adjusted_interval(self) -> int:
        """Get adjusted scheduling interval based on rate limit history."""
        base_interval = 30  # 30 minutes default
        
        if self.consecutive_rate_limits >= 3:
            return 120  # 2 hours if persistent rate limits
        elif self.consecutive_rate_limits >= 2:
            return 90   # 1.5 hours if multiple rate limits
        elif self.consecutive_rate_limits >= 1:
            return 60   # 1 hour if recent rate limit
        
        return base_interval


rate_limit_manager = RateLimitManager()


def run_bot():
    """Execute the GitHub Tweet Bot with enhanced progress display and rate limit handling."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Starting GitHub Tweet Bot...")
    
    # Check if we should prioritize Firefox
    if rate_limit_manager.should_use_firefox_priority():
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🦊 Firefox priority mode enabled due to recent rate limits")
    
    try:
        # Run the bot with real-time output
        process = subprocess.Popen([
            sys.executable, "-m", "src.main"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
           text=True, cwd=Path(__file__).parent, bufsize=1, universal_newlines=True)
        
        rate_limit_detected = False
        rate_limit_duration = None
        
        # Parse and display progress in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                result = parse_and_display_log(output.strip())
                if result and result.get('rate_limit_detected'):
                    rate_limit_detected = True
                    rate_limit_duration = result.get('duration')
        
        # Get final result
        stderr = process.stderr.read()
        
        if process.returncode == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Bot completed successfully")
            rate_limit_manager.reset_rate_limit_count()
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Bot failed:")
            if stderr:
                print(stderr)
            
            # Check if failure was due to rate limiting
            if rate_limit_detected:
                rate_limit_manager.record_rate_limit(rate_limit_duration)
        
        # Handle rate limits detected during execution
        if rate_limit_detected and process.returncode == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Rate limit was handled by Firefox fallback")
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error: {e}")


def parse_and_display_log(log_line):
    """Parse JSON log and display user-friendly progress with rate limit detection."""
    try:
        log_data = json.loads(log_line)
        step = log_data.get('step', '')
        event = log_data.get('event', '')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Enhanced step messages with rate limit awareness
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
            
            # Enhanced API and Firefox tracking
            'main_tweet_post_start': '🐦 Posting main tweet with automatic fallback...',
            'tweet_create_api': f"📡 Trying Twitter API (attempt {log_data.get('attempt', 1)})...",
            'tweet_api_success': f"✅ Tweet posted via API: {log_data.get('tweet_id', 'ID')}",
            'api_rate_limit': f"⚠️ API rate limit hit, switching to Firefox...",
            'firefox_fallback_start': '🦊 Activating Firefox fallback...',
            'firefox_fallback_init': '🔧 Firefox service initialized',
            'tweet_firefox_success': f"✅ Tweet posted via Firefox: {log_data.get('tweet_id', 'ID')}",
            'main_tweet_success': f"✅ Main tweet posted: {log_data.get('tweet_id', 'ID')}",
            
            'reply_tweet_post_start': '💬 Posting reply with automatic fallback...',
            'reply_create_api': f"📡 Trying API reply (attempt {log_data.get('attempt', 1)})...",
            'reply_api_success': f"✅ Reply posted via API: {log_data.get('reply_id', 'ID')}",
            'api_reply_rate_limit': f"⚠️ API reply rate limit, switching to Firefox...",
            'firefox_reply_fallback_start': '🦊 Firefox reply fallback...',
            'reply_firefox_success': f"✅ Reply posted via Firefox: {log_data.get('reply_id', 'ID')}",
            'reply_tweet_success': f"✅ Reply posted: {log_data.get('reply_id', 'ID')}",
            
            'workflow_success': f"🎉 Workflow completed in {log_data.get('duration', 'N/A')} - Tweet: {log_data.get('main_tweet_id', 'N/A')}",
            'firefox_closed': '🔒 Firefox service closed'
        }
        
        # Check for rate limit indicators
        rate_limit_detected = False
        duration = None
        
        error_msg = log_data.get('error', '').lower()
        if any(indicator in error_msg for indicator in ['rate limit exceeded', '429', 'too many requests']):
            rate_limit_detected = True
            # Try to extract duration from error message
            import re
            duration_match = re.search(r'sleeping for (\d+) seconds', error_msg)
            if duration_match:
                duration = int(duration_match.group(1))
        
        # Special handling for rate limit messages
        if 'Rate limit exceeded' in log_line:
            print(f"[{timestamp}] ⏳ Rate limit hit - automatic fallback will handle this...")
            return {'rate_limit_detected': True, 'duration': duration}
        
        # Display progress message
        message = step_messages.get(step, f"ℹ️ {event}" if event else log_line)
        print(f"[{timestamp}] {message}")
        
        return {'rate_limit_detected': rate_limit_detected, 'duration': duration}
        
    except (json.JSONDecodeError, KeyError):
        # Not JSON or missing fields - display as is
        if log_line.strip() and not log_line.startswith('HTTP Request:'):
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] {log_line}")
        return None


def should_run_now():
    """Check if bot should run now (from 09h00 to 00h00 included)."""
    now = datetime.now()
    current_hour = now.hour
    # Autorisé de 9h00 à 23h59 (inclus), donc 9 <= hour < 24
    return 9 <= current_hour < 24


def scheduled_run():
    """Run bot only during active hours with rate limit awareness."""
    if should_run_now():
        run_bot()
        
        # Adjust next run interval based on rate limit history
        new_interval = rate_limit_manager.get_adjusted_interval()
        if new_interval != 30:  # If different from default
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚡ Adjusting interval to {new_interval} minutes due to rate limit history")
            # Clear current jobs and reschedule with new interval
            schedule.clear()
            schedule.every(new_interval).minutes.do(scheduled_run)
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Outside active hours (9h-23h59), skipping...")


def main():
    """Main scheduler loop with adaptive rate limit management."""
    print("🚀 GitHub Tweet Bot Enhanced Scheduler Started")
    print("📅 Schedule: Every 30 minutes (adaptive based on rate limits)")
    print("⏰ Active hours: 09h00 to 00h00 (France time)")
    print("🦊 Firefox fallback: Automatic on rate limits")
    print("🔄 Smart interval adjustment: Enabled")
    print("=" * 60)
    
    # Initial schedule
    initial_interval = rate_limit_manager.get_adjusted_interval()
    schedule.every(initial_interval).minutes.do(scheduled_run)
    
    if initial_interval != 30:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚡ Starting with adjusted interval: {initial_interval} minutes")
    
    # Run once immediately if in active hours
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 Starting initial run...")
    scheduled_run()
    
    # Keep running with status updates
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏰ Scheduler running. Next check in {initial_interval} minutes.")
    
    last_status_time = datetime.now()
    while True:
        schedule.run_pending()
        
        # Status update every hour
        if datetime.now() - last_status_time > timedelta(hours=1):
            current_interval = rate_limit_manager.get_adjusted_interval()
            next_run = None
            for job in schedule.jobs:
                if job.next_run:
                    next_run = job.next_run
                    break
            
            status_msg = f"📊 Status: Interval={current_interval}min"
            if rate_limit_manager.consecutive_rate_limits > 0:
                status_msg += f", Rate limits={rate_limit_manager.consecutive_rate_limits}"
            if next_run:
                status_msg += f", Next run={next_run.strftime('%H:%M')}"
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {status_msg}")
            last_status_time = datetime.now()
        
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🛑 Scheduler stopped by user")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Scheduler error: {e}")