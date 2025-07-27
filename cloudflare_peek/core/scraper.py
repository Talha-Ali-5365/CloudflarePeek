"""Web scraping with screenshot fallback for Cloudflare-protected sites."""
import asyncio
import io
import os
import logging
import sys
from typing import Optional

import google.generativeai as genai
from PIL import Image
from playwright.async_api import async_playwright
from langchain_community.document_loaders import WebBaseLoader

from .detector import behind_cloudflare

# Configure logging to show progress by default
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def _run_async(coro):
    """
    Run async function, handling both new and existing event loops.
    This prevents the RuntimeError: asyncio.run() cannot be called from a running event loop.
    """
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        # If we're here, there's already a running loop
        # We need to run the coroutine in a new thread to avoid conflicts
        import concurrent.futures
        import threading
        
        def run_in_thread():
            # Create a new event loop for this thread
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        
        # Run in a separate thread with its own event loop
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()
            
    except RuntimeError:
        # No running event loop, safe to use asyncio.run()
        return asyncio.run(coro)


async def _screenshot_ocr(url: str, api_key: Optional[str] = None, timeout: int = 120000) -> str:
    """
    Take a full-page screenshot and extract text using Gemini OCR.
    
    Args:
        url: The URL to scrape
        api_key: Gemini API key (if not provided, will use GEMINI_API_KEY env var)
        timeout: Page load timeout in milliseconds (default: 120000 = 2 minutes)
        
    Returns:
        Extracted text from the screenshot
        
    Raises:
        ValueError: If no API key is provided
        Exception: If scraping fails
    """
    # Configure Gemini API
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    logger.info("📸 Taking screenshot and extracting content...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        try:
            # Use proper Chromium User-Agent
            ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36")
            
            page = await browser.new_page(user_agent=ua)
            
            # Set default timeout for ALL page operations
            page.set_default_timeout(timeout)
            
            await page.goto(url, timeout=timeout)
            await page.wait_for_load_state("load")  # More reliable than "networkidle"

            # Scroll to bottom to load all content
            prev_height = 0
            while True:
                curr_height = await page.evaluate("document.body.scrollHeight")
                if curr_height == prev_height:
                    break
                    
                prev_height = curr_height
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)

            # Take full-page screenshot
            png_data = await page.screenshot(full_page=True)
            
        finally:
            await browser.close()

    # Process with Gemini
    img = Image.open(io.BytesIO(png_data))
    response = model.generate_content(
        ["Extract all text exactly as it appears on this webpage:", img],
        generation_config={"temperature": 0}
    )
    
    extracted_text = response.text.strip()
    return extracted_text


def _fast_load(url: str) -> str:
    """
    Load webpage content using LangChain WebBaseLoader.
    
    Args:
        url: The URL to load
        
    Returns:
        Extracted text content
    """
    docs = WebBaseLoader([url]).load()
    content = "\n".join(doc.page_content for doc in docs)
    return content


def peek(url: str, api_key: Optional[str] = None, force_ocr: bool = False, timeout: int = 120000) -> str:
    """
    Load webpage content with automatic Cloudflare detection and fallback.
    
    This function first tries fast scraping. If the site is behind Cloudflare 
    or if fast scraping fails, it automatically falls back to OCR extraction.
    
    Args:
        url: The URL to scrape
        api_key: Gemini API key for OCR (optional, uses GEMINI_API_KEY env var if not provided)
        force_ocr: If True, skip fast scraping and go directly to OCR method
        timeout: Page load timeout in milliseconds for OCR method (default: 120000 = 2 minutes)
        
    Returns:
        Extracted text content from the webpage
        
    Raises:
        ValueError: If OCR method is needed but no Gemini API key is available
    """
    logger.info("🎯 Starting CloudflarePeek for: %s", url)
    
    # Check if site is behind Cloudflare or if user wants to force OCR
    if force_ocr:
        logger.info("🔒 Using OCR method (force mode)")
        result = _run_async(_screenshot_ocr(url, api_key, timeout))
        logger.info("✅ Completed! (%d characters extracted)", len(result))
        return result
    
    cf_protected = behind_cloudflare(url)
    if cf_protected:
        logger.info("🛡️ Cloudflare detected - using OCR method")
        result = _run_async(_screenshot_ocr(url, api_key, timeout))
        logger.info("✅ Completed! (%d characters extracted)", len(result))
        return result

    # Try fast scraping first
    try:
        logger.info("⚡ Attempting fast scraping...")
        result = _fast_load(url)
        logger.info("✅ Completed! (%d characters extracted)", len(result))
        return result
    except Exception as e:
        logger.info("⚡ Fast scraping failed - using OCR method")
        result = _run_async(_screenshot_ocr(url, api_key, timeout))
        logger.info("✅ Completed! (%d characters extracted)", len(result))
        return result