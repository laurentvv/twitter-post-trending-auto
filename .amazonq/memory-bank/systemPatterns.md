# System Patterns

## Core Architecture

The GitHub Tweet Bot follows a modular, service-oriented architecture with the following key patterns:

### Service Layer Pattern
- Each core functionality is encapsulated in dedicated services:
  - `GitHubService` for repository discovery and data fetching
  - `AIService` for AI-powered content generation and validation
  - `ScreenshotService` for automated repository screenshots
  - `TwitterService` for Twitter API interactions
  - `FirefoxTwitterService` for Firefox-based fallback automation
  - `HistoryService` for duplicate detection and persistence

### Dependency Injection Pattern
- Services are designed to be loosely coupled with dependency injection
- Configuration is managed through Pydantic settings classes
- Logging uses structlog for structured output

### Retry Pattern
- All services implement retry logic (3x) for robust error handling
- Fallback mechanisms are triggered automatically on failures
- Rate limit handling includes automatic fallback to Firefox

### Fallback Pattern
- Multi-tiered fallback system:
  - **Data sources**: GitHub API → GitHub Scraping → OSS Insight API → Gitstar Ranking
  - **AI providers**: Gemini → OpenRouter → Mistral → Ollama (with 3x retry on each before falling back)
  - **Publishing methods**: Twitter API (2x retry) → Firefox automation

## Key Technical Decisions

### Asynchronous Programming
- Full async/await implementation for I/O bound operations
- Concurrent processing of multiple repositories when possible
- Proper error handling in async contexts

### Configuration Management
- Pydantic-based settings with environment variable support
- Centralized configuration loading and validation
- Type-safe configuration access throughout the application

### Logging Strategy
- Structured JSON logging for observability
- Contextual information in logs (provider used, duration, status)
- Separate log files for different components

### Error Handling
- Comprehensive error handling with specific exception types
- Graceful degradation when services fail
- Detailed error reporting in logs

## Data Flow Patterns

### Repository Discovery Pipeline
1. Multi-source data fetching (API, scraping, etc.)
2. Duplicate detection using HistoryService
3. Repository filtering and validation
4. Content generation via AIService
5. Screenshot capture with ScreenshotService
6. Twitter posting with TwitterService or Firefox fallback

### AI Processing Pipeline
1. **Content Generation**: Generate a summary and key features using the multi-provider AI system.
2. **Tweet Assembly**: Create the main tweet and reply text.
3. **AI Validation**: The complete tweet text is passed to an AI model for a quality check (coherence, grammar, style, length).
4. **AI Correction (if needed)**: If validation fails, the tweets and the validation error are passed to another AI call that attempts to fix the specific issues.
5. **AI Re-Validation**: The corrected tweet is validated again. If it still fails, the bot logs a warning but proceeds with the corrected version to avoid blocking.

## Resource Management

### Robust Browser Automation
- **Lazy Instantiation**: The Firefox driver is instantiated only when needed, conserving resources.
- **Safe Actions**: Implements `_safe_click` and `_safe_send_keys` methods with multiple retries and JavaScript-based fallbacks to handle dynamic and complex web interfaces reliably.
- **Intelligent ID Retrieval**: After posting via browser, it uses a multi-step process to retrieve the new tweet's ID: first by parsing the current URL, and if that fails, by navigating to the user's profile page to find the latest tweet. This is critical for ensuring replies are correctly threaded.
- **Resource Cleanup**: The driver is properly closed using a context manager (`__enter__` and `__exit__`) to ensure no lingering processes.

### Memory Management
- **History Pruning**: The `HistoryService` automatically clears records older than 7 days to keep the history file small and efficient.
- **Efficient Caching**: Uses sets for fast, O(1) lookups when checking if a repository has already been posted.
- **Temporary Files**: Screenshots are stored in a dedicated directory and are not cleaned up automatically, but the filenames are unique.

## Testing Patterns

### Unit Testing
- Service-specific unit tests
- Mock external dependencies where appropriate
- Integration tests for end-to-end workflows

### Fallback Testing
- Dedicated test suites for fallback mechanisms
- Simulated rate limit scenarios
- Multi-provider testing scenarios

## Scheduling Pattern

### Adaptive and Intelligent Scheduler
The bot uses a sophisticated scheduler (`scheduler.py`) that runs the main workflow in a separate process for isolation and stability.

- **Rate Limit Management**: A dedicated `RateLimitManager` class tracks the history of rate limit errors.
- **Progressive Backoff**: The scheduling interval is dynamically adjusted. It starts at 30 minutes and automatically increases to 60, 90, and finally 120 minutes upon detecting consecutive rate limit failures. The interval resets to 30 minutes after a successful run.
- **Proactive Fallback Prioritization**: Based on recent failures, the scheduler can decide to prioritize using the Firefox fallback from the start, rather than waiting for the API to fail during the workflow.
- **Active Hours**: The scheduler only runs the bot during a predefined time window (09h00 to 01h00 France time) to maximize audience engagement and respect API usage patterns.
- **Live Monitoring**: The scheduler provides detailed, user-friendly status updates in the console by parsing the JSON logs from the main bot process in real-time, offering excellent observability.
```

amazonq\memory-bank\techContext.md
