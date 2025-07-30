# Project Brief: GitHub Tweet Bot

## Core Mission
Automated Twitter bot that discovers trending GitHub repositories, generates AI-powered summaries, captures screenshots, and publishes engaging tweets to promote open-source projects.

## Key Requirements
1. **GitHub Integration**: Fetch trending repositories via GitHub API
2. **AI Summarization**: Use multi-provider (Gemini, OpenRouter, Mistral, Ollama) for intelligent content generation
3. **Screenshot Automation**: Capture repository pages with Playwright
4. **Twitter Publishing**: Post tweets with Twitter API v2 (OAuth 1.0a)
5. **Scheduling**: Automated posting every 30 minutes, 09h00–00h00
6. **Modern Architecture**: Async/await, structured logging, type safety
7. **Fallback Firefox**: Selenium automation as backup if API fails or rate limited

## Success Criteria
- Generate engaging tweets that drive GitHub repository discovery
- Maintain 95%+ uptime with robust error handling and fallback
- Process repositories in under 2 minutes per tweet
- Structured JSON logging for observability
- Clean, maintainable, testable codebase

## Technical Constraints
- Python 3.11+ with modern async patterns
- Twitter API v2 with OAuth 1.0a authentication
- Playwright for reliable screenshot capture
- Ollama for local AI processing (no external API costs)
- Pydantic for configuration validation
- Structured logging with JSON output
- Selenium + Firefox for fallback automation

## Current Status
✅ Modern architecture implemented (src/)
✅ Configuration management with Pydantic
✅ Structured logging with JSON output
✅ Twitter service with API v2 + fallback Firefox
✅ Screenshot service with Playwright
✅ GitHub service and AI service multi-provider
✅ Full integration testing
✅ Scheduler toutes les 30 minutes, 09h00–00h00
✅ Fallback Firefox instancié uniquement si nécessaire

**The bot is now production-ready, robust, and can run indefinitely with automatic fallback and multi-provider AI!**