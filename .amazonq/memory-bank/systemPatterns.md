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
  - Data sources: API → Scraping → LibHunt → Gitstar Ranking
  - AI providers: Gemini → OpenRouter → Mistral → Ollama
  - Publishing methods: Twitter API → Firefox automation

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
1. Try primary provider (Gemini)
2. Fallback to secondary providers if needed
3. Validation and correction using AI
4. Error handling and retry logic

## Resource Management

### Browser Automation
- Firefox driver instantiated only when needed (lazy loading)
- Proper resource cleanup in all service lifecycle methods
- Headless mode support for production environments

### Memory Management
- Efficient data structures for repository caching
- Automatic cleanup of temporary files
- Persistent storage for history tracking

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

### Adaptive Scheduler
- Fixed interval execution (30 minutes)
- Time-based filtering (09h00–01h00 France time)
- Dynamic adjustment based on rate limit feedback
- Status reporting and next-run calculation
```

amazonq\memory-bank\techContext.md
