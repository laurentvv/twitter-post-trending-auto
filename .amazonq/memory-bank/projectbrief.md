# Project Brief: GitHub Tweet Bot

## Core Mission
Automated Twitter bot that discovers trending GitHub repositories, generates AI-powered summaries, captures screenshots, and publishes engaging tweets to promote open-source projects.

## Key Requirements
1. **GitHub Integration**: Fetch trending repositories via GitHub API
2. **AI Summarization**: Use Ollama (qwen3:14b) for intelligent content generation
3. **Screenshot Automation**: Capture repository pages with Playwright
4. **Twitter Publishing**: Post tweets with Twitter API v2
5. **Scheduling**: Automated posting every 4 hours
6. **Modern Architecture**: Async/await, structured logging, type safety

## Success Criteria
- Generate engaging tweets that drive GitHub repository discovery
- Maintain 95%+ uptime with robust error handling
- Process repositories in under 2 minutes per tweet
- Structured JSON logging for observability
- Clean, maintainable, testable codebase

## Technical Constraints
- Python 3.13+ with modern async patterns
- Twitter API v2 with Bearer Token authentication
- Playwright for reliable screenshot capture
- Ollama for local AI processing (no external API costs)
- Pydantic for configuration validation
- Structured logging with JSON output

## Current Status
✅ Modern architecture implemented (src_v2/)
✅ Configuration management with Pydantic
✅ Structured logging with JSON output
✅ Twitter service with API v2
✅ Screenshot service with Playwright
⚠️ Network connectivity issues during testing
🔄 Need to complete GitHub service and AI service
🔄 Need full integration testing