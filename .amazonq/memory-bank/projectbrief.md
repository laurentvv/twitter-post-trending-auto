# Project Brief: GitHub Tweet Bot

## Core Mission
Automated Twitter bot that discovers trending GitHub repositories, generates AI-powered summaries, captures screenshots, and publishes engaging tweets to promote open-source projects.

## Key Requirements
1. **GitHub Integration**: Fetch trending repositories via GitHub API.
2. **AI Summarization**: Use a multi-provider system (Gemini → OpenRouter → Mistral → Ollama) for robust content generation.
3. **AI Quality Control**: Implement an AI-driven validation and correction loop. Generated tweets are validated by a separate AI call for quality and coherence. If issues are found, another AI call attempts to correct them before publication.
4. **Screenshot Automation**: Capture repository pages using Playwright.
5. **Twitter Publishing**: Post tweets with Twitter API v2 (OAuth 1.0a) and a robust Firefox fallback.
6. **Adaptive Scheduling**: Automated posting with an adaptive interval. Starts at 30 minutes and automatically increases to 60, 90, or 120 minutes if rate limits are detected. Active from 09h00 to 01h00.
7. **Modern Architecture**: Async/await, structured logging, and type safety.
8. **Intelligent Fallback**: Use Firefox automation as a backup if the Twitter API fails or is rate-limited. The scheduler can prioritize Firefox based on recent rate limit history.
9. **Data Source Robustness**: Implement multiple fallback strategies (GitHub API, direct scraping, OSS Insight API, and Gitstar Ranking) for discovering trending repositories, ensuring continuous operation.

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
✅ Structured JSON logging for observability
✅ Twitter service with API v2 + intelligent Firefox fallback
✅ Screenshot service with Playwright
✅ AI-powered tweet validation and correction loop
✅ GitHub service (multi-source: API, scraping, OSS Insight API, Gitstar Ranking)
✅ AI service (multi-provider: Gemini, OpenRouter, Mistral, Ollama)
✅ Full integration testing
✅ Adaptive scheduler (30-120 min) running from 09h00-01h00
✅ Firefox fallback instantiated only when needed or prioritized by scheduler

**The bot is now production-ready, robust, and can run indefinitely with automatic fallback and multi-provider AI!**