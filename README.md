# CloudflarePeek 🔍
### Made by Talha Ali

A powerful Python utility that can scrape **any website**—even those protected by Cloudflare. When traditional scraping fails, CloudflarePeek automatically falls back to taking a full-page screenshot and extracting text using Google's Gemini OCR.

## ✨ Features

- **🛡️ Cloudflare Detection**: Automatically detects Cloudflare-protected sites
- **📸 Screenshot Fallback**: Takes full-page screenshots when traditional scraping fails  
- **🤖 AI-Powered OCR**: Uses Google Gemini to extract clean text from screenshots
- **⚡ Smart Switching**: Tries fast scraping first, falls back to OCR only when needed
- **🔄 Auto-scrolling**: Scrolls pages to bottom to capture all content
- **🎯 Zero Config**: Works out of the box with minimal setup
- **⚙️ Event Loop Safe**: Automatically handles asyncio conflicts in Jupyter/existing loops

## 🚀 Installation

### From GitHub
```bash
# Install in development mode
pip install -e git+https://github.com/Talha-Ali-5365/CloudflarePeek.git#egg=cloudflare-peek

# Or clone and install locally
git clone https://github.com/Talha-Ali-5365/CloudflarePeek.git
cd CloudflarePeek
pip install -e .
```

### Additional Setup

1. **Install Playwright browsers** (required for screenshot functionality):
```bash
playwright install
```

2. **Get a Gemini API key** (required for OCR):
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Set it as an environment variable:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

## 📖 Quick Start

### Basic Usage

```python
from cloudflare_peek import peek

# Scrape any website - automatically handles Cloudflare
text = peek("https://example.com")
print(text)
```

### Advanced Usage

```python
from cloudflare_peek import peek, behind_cloudflare

# Check if a site is behind Cloudflare
if behind_cloudflare("https://example.com"):
    print("Site is protected by Cloudflare")

# Force OCR method (useful for dynamic content)
text = peek("https://example.com", force_ocr=True)

# Use with custom API key and timeout (5 minutes)
text = peek("https://example.com", api_key="your-gemini-key", timeout=300000)
```

### CLI Usage

CloudflarePeek also comes with a powerful command-line interface.

**Scrape a website:**
```bash
cloudflare-peek scrape https://example.com
```

**Check if a site is behind Cloudflare:**
```bash
cloudflare-peek check-cloudflare https://example.com
```

**Save content to a file:**
```bash
cloudflare-peek scrape https://example.com -o content.txt
```

**Advanced options:**
```bash
# Force OCR, run in non-headless mode, and set a 60s timeout
cloudflare-peek scrape https://example.com --force-ocr --no-headless --timeout 60

# See all commands and options
cloudflare-peek --help
cloudflare-peek scrape --help
```

### Environment Variables

```bash
# Required for OCR functionality
export GEMINI_API_KEY="your-gemini-api-key"
```

### ⏱️ Timeout Configuration

CloudflarePeek uses a default timeout of **2 minutes (120,000ms)** for page loading during OCR extraction. You can customize this:

```python
# Quick timeout (30 seconds) for fast sites
text = peek("https://example.com", timeout=30000)

# Extended timeout (5 minutes) for slow/complex sites  
text = peek("https://example.com", timeout=300000)

# Very long timeout (10 minutes) for extremely slow sites
text = peek("https://example.com", timeout=600000)
```

### 📋 Progress Logging

CloudflarePeek provides detailed progress information during scraping:

```python
import logging
from cloudflare_peek import peek

# Enable detailed debug logging to see all steps
logging.getLogger('cloudflare_peek').setLevel(logging.DEBUG)

# You'll see progress like:
# 🎯 Starting CloudflarePeek for: https://example.com
# 🔍 Checking if https://example.com is behind Cloudflare...
# 🚀 No Cloudflare detected - attempting fast scraping...
# ✅ Fast scraping successful! (1234 characters extracted)

text = peek("https://example.com")
```

### 🔧 Event Loop Compatibility

CloudflarePeek automatically handles asyncio event loop conflicts, so it works seamlessly in:

- **Jupyter Notebooks** ✅
- **IPython environments** ✅ 
- **Web frameworks** (FastAPI, Django, etc.) ✅
- **Standalone scripts** ✅

No need for `nest_asyncio.apply()` or other workarounds - it's all handled internally!

## 🛠️ API Reference

### `peek(url, api_key=None, force_ocr=False, timeout=120000)`

The main function that intelligently chooses between fast scraping and OCR extraction.

**Parameters:**
- `url` (str): The URL to scrape
- `api_key` (str, optional): Gemini API key (uses `GEMINI_API_KEY` env var if not provided)  
- `force_ocr` (bool): Skip fast scraping and use OCR method directly
- `timeout` (int): Page load timeout in milliseconds for OCR method (default: 120000 = 2 minutes)

**Returns:** Extracted text content as string

### `behind_cloudflare(url)`

Check if a website is protected by Cloudflare.

**Parameters:**
- `url` (str): The URL to check

**Returns:** `True` if behind Cloudflare, `False` otherwise


## 📝 Examples

### Example 1: Basic Website Scraping
```python
from cloudflare_peek import peek

# Works with any website
websites = [
    "https://httpbin.org/html",
    "https://quotes.toscrape.com",
    "https://scrapethissite.com"
]

for url in websites:
    content = peek(url)
    print(f"Content from {url}:")
    print(content[:200] + "...")
    print("-" * 50)
```

### Example 2: Batch Processing URLs
```python
import asyncio
from cloudflare_peek import peek

async def scrape_multiple(urls):
    results = {}
    for url in urls:
        try:
            content = peek(url)
            results[url] = content
            print(f"✅ Successfully scraped {url}")
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")
            results[url] = None
    return results

urls = ["https://example1.com", "https://example2.com"]
results = asyncio.run(scrape_multiple(urls))
```

### Example 3: Error Handling
```python
from cloudflare_peek import peek

def safe_scrape(url):
    try:
        return peek(url)
    except ValueError as e:
        if "API key" in str(e):
            print("❌ Gemini API key not found. Please set GEMINI_API_KEY environment variable.")
        return None
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return None

content = safe_scrape("https://example.com")
if content:
    print("Scraping successful!")
```

## 🔧 Development

### Setting up for Development

```bash
# Clone the repository
git clone https://github.com/your-username/CloudflarePeek.git
cd CloudflarePeek

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Set up your API key
export GEMINI_API_KEY="your-key-here"
```

### Running Tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=cloudflare_peek
```

### Code Formatting

```bash
# Format code
black cloudflare_peek/

# Check types
mypy cloudflare_peek/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. The author is not responsible for any misuse or damage caused by this tool.

This tool is intended for legitimate web scraping purposes only. Always respect websites' robots.txt files and terms of service. Be mindful of rate limiting and don't overload servers with requests.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for browser automation
- [Google Gemini](https://ai.google.dev/) for OCR capabilities  
- [LangChain](https://python.langchain.com/) for traditional web scraping
- The open source community for inspiration and support