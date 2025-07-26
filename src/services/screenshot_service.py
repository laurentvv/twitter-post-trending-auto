"""Modern screenshot service using Playwright."""
import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page

from ..core.config import settings
from ..core.logger import logger, log_step


class ScreenshotService:
    """Modern screenshot service with Playwright."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.screenshots_dir = Path(settings.screenshots_dir)
        self.screenshots_dir.mkdir(exist_ok=True)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    async def start(self) -> None:
        """Start the browser."""
        if self.browser:
            return
            
        logger.info("Starting Playwright browser", **log_step("browser_start"))
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ]
        )
        
        logger.info("Browser started successfully", **log_step("browser_ready"))
    
    async def stop(self) -> None:
        """Stop the browser."""
        if self.browser:
            logger.info("Stopping browser", **log_step("browser_stop"))
            await self.browser.close()
            await self.playwright.stop()
            self.browser = None
    
    async def capture_repository(self, url: str, filename: str) -> str:
        """
        Capture screenshot of GitHub repository (with 3 retry attempts).
        
        Args:
            url: Repository URL
            filename: Output filename
            
        Returns:
            Path to saved screenshot
        """
        if not self.browser:
            await self.start()
        
        filepath = self.screenshots_dir / filename
        
        for attempt in range(3):
            try:
                logger.info(
                    "Starting screenshot capture",
                    **log_step("screenshot_start", url=url, filename=filename, attempt=attempt+1)
                )
                
                # Create new page with optimized settings
                page = await self.browser.new_page(
                    viewport={"width": 1200, "height": 800},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                
                # Navigate with timeout
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=settings.screenshot_timeout * 1000
                )
                
                # Wait for GitHub README to load and position properly
                try:
                    await page.wait_for_selector("article", timeout=10000)
                    
                    # Hide file browser and focus on README
                    await page.evaluate("""
                        // Hide multiple file tree selectors
                        const selectors = [
                            '[data-testid="repos-file-tree-container"]',
                            '.react-directory-filename-column',
                            '.js-navigation-container',
                            '[aria-labelledby="folders-and-files"]',
                            '.Box-sc-g0xbh4-0.fSWWem'
                        ];
                        
                        selectors.forEach(selector => {
                            const elements = document.querySelectorAll(selector);
                            elements.forEach(el => el.style.display = 'none');
                        });
                        
                        // Hide header
                        const header = document.querySelector('header');
                        if (header) header.style.display = 'none';
                        
                        // Wait a bit then position at README top
                        setTimeout(() => {
                            const readme = document.querySelector('#readme');
                            if (readme) {
                                // Get README position and scroll well above it
                                const rect = readme.getBoundingClientRect();
                                const scrollTop = window.pageYOffset + rect.top - 200;
                                window.scrollTo(0, Math.max(0, scrollTop));
                            } else {
                                window.scrollTo(0, 400);
                            }
                        }, 500);
                    """)
                    await asyncio.sleep(4)
                    await asyncio.sleep(3)
                except:
                    await page.evaluate("window.scrollTo(0, 600)")
                    await asyncio.sleep(2)
                
                # Take screenshot
                await page.screenshot(
                    path=str(filepath),
                    full_page=False,
                    clip={"x": 0, "y": 0, "width": 1000, "height": 600}
                )
                
                await page.close()
                
                logger.info(
                    "Screenshot captured successfully",
                    **log_step("screenshot_success", filepath=str(filepath), attempt=attempt+1)
                )
                
                return str(filepath)
                
            except Exception as e:
                logger.warning(
                    f"Screenshot attempt {attempt+1} failed",
                    **log_step("screenshot_retry", error=str(e), attempt=attempt+1)
                )
                if attempt == 2:  # Last attempt
                    logger.error(
                        "Screenshot capture failed after 3 attempts",
                        **log_step("screenshot_error", error=str(e), url=url)
                    )
                    raise
    
    async def capture_multiple(self, urls_and_filenames: list[tuple[str, str]]) -> list[str]:
        """
        Capture multiple screenshots efficiently.
        
        Args:
            urls_and_filenames: List of (url, filename) tuples
            
        Returns:
            List of screenshot paths
        """
        if not self.browser:
            await self.start()
        
        tasks = [
            self.capture_repository(url, filename)
            for url, filename in urls_and_filenames
        ]
        
        return await asyncio.gather(*tasks, return_exceptions=True)


# Convenience function for single screenshot
async def capture_screenshot(url: str, filename: str) -> str:
    """Capture a single screenshot."""
    async with ScreenshotService() as service:
        return await service.capture_repository(url, filename)