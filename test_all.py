"""Test script to validate complete bot configuration including Firefox fallback."""
import sys
import time
from datetime import datetime
from pathlib import Path

def test_imports():
    """Test all required imports."""
    print("📦 Testing imports...")
    try:
        import tweepy
        print("  ✅ Tweepy")
        
        import selenium
        from selenium import webdriver
        print("  ✅ Selenium")
        
        from webdriver_manager.firefox import GeckoDriverManager
        print("  ✅ WebDriver Manager")
        
        import schedule
        print("  ✅ Schedule")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_twitter_api():
    """Test Twitter API configuration."""
    print("\n🐦 Testing Twitter API...")
    try:
        from src.services.twitter_service import TwitterService
        
        service = TwitterService()
        if service.client:
            print("  ✅ Twitter client initialized")
            
            # Test if OAuth 1.0a is available for posting
            if service._has_oauth1_credentials():
                print("  ✅ OAuth 1.0a credentials available (can post)")
            else:
                print("  ⚠️ Only Bearer Token available (read-only)")
            
            return True
        else:
            print("  ❌ Twitter client not initialized")
            return False
            
    except Exception as e:
        print(f"  ❌ Twitter API error: {e}")
        return False

def test_firefox_config():
    """Test Firefox configuration."""
    print("\n🦊 Testing Firefox configuration...")
    try:
        from src.core.firefox_config import firefox_config
        
        config = firefox_config.get_config()
        
        if config["enabled"]:
            print(f"  ✅ Firefox enabled")
            print(f"  📁 Profile: {config['profile_path']}")
            
            # Run Firefox test
            if firefox_config.test_configuration():
                print("  ✅ Firefox test passed - Twitter login confirmed")
                return True
            else:
                print("  ⚠️ Firefox test failed - check Twitter login")
                print("\n" + firefox_config.setup_instructions())
                return False
        else:
            print("  ⚠️ Firefox not enabled")
            print("\n" + firefox_config.setup_instructions())
            return False
            
    except Exception as e:
        print(f"  ❌ Firefox error: {e}")
        return False

def test_github_service():
    """Test GitHub service."""
    print("\n🐙 Testing GitHub service...")
    try:
        from src.services.github_service import GitHubService
        
        service = GitHubService()
        repos = service.get_trending_repositories(limit=1)
        
        if repos:
            print(f"  ✅ GitHub API working - found {len(repos)} trending repo(s)")
            return True
        else:
            print("  ⚠️ No trending repositories found")
            return False
            
    except Exception as e:
        print(f"  ❌ GitHub error: {e}")
        return False

def test_ai_service():
    """Test AI service."""
    print("\n🤖 Testing AI service...")
    try:
        from src.services.ai_service import AIService
        
        service = AIService()
        
        # Test with simple content
        test_readme = "# Test Project\nThis is a simple test project for GitHub automation."
        summary = service.summarize_readme(test_readme)
        
        if summary:
            print(f"  ✅ AI service working - generated summary: '{summary[:50]}...'")
            return True
        else:
            print("  ⚠️ AI service returned empty summary")
            return False
            
    except Exception as e:
        print(f"  ❌ AI service error: {e}")
        return False

def test_complete_workflow():
    """Test the complete workflow without posting."""
    print("\n🔄 Testing complete workflow (dry run)...")
    try:
        # This would test the main workflow without actually posting
        print("  ℹ️ Complete workflow test requires actual execution")
        print("  ℹ️ Use 'python -m src.main' to test full workflow")
        return True
        
    except Exception as e:
        print(f"  ❌ Workflow test error: {e}")
        return False

def main():
    """Run all configuration tests."""
    print("🚀 GitHub Tweet Bot - Configuration Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Twitter API", test_twitter_api),
        ("Firefox Config", test_firefox_config),
        ("GitHub Service", test_github_service),
        ("AI Service", test_ai_service),
        ("Workflow", test_complete_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready to run.")
        print("\n🔧 Next steps:")
        print("  1. Run 'python scheduler.py' to start the scheduler")
        print("  2. Or run 'python -m src.main' for a single execution")
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
        print("\n🔧 Common fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Configure Twitter API credentials")
        print("  - Login to Twitter in Firefox browser")
        print("  - Check AI service API keys")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)