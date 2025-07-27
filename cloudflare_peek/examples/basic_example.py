"""Basic usage example for CloudflarePeek."""

import os
import logging
from cloudflare_peek import peek, behind_cloudflare

def main():
    # Example URLs to test
    test_urls = [
        "https://httpbin.org/html",
        "https://quotes.toscrape.com",
        "https://example.com"
    ]
    
    print("CloudflarePeek Basic Example")
    print("=" * 40)
    
    # Check if Gemini API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not set. OCR fallback won't work.")
        print("   Set it with: export GEMINI_API_KEY='your-key-here'")
        print()
    
    for i, url in enumerate(test_urls):
        print(f"\n📋 Test {i+1}/{len(test_urls)}: {url}")
        print("-" * 60)
        
        try:
            # Example 1: Basic usage with default timeout (2 minutes)
            if i == 0:
                print("🔥 Basic usage (default timeout):")
                content = peek(url)
            
            # Example 2: Custom timeout (30 seconds)
            elif i == 1:
                print("⏱️  Custom timeout (30 seconds):")
                content = peek(url, timeout=30000)
            
            # Example 3: Force OCR mode
            else:
                print("🔒 Force OCR mode:")
                content = peek(url, force_ocr=True, timeout=60000)
            
            content_preview = content[:200].replace('\n', ' ')
            print(f"\n✅ Success! Content preview: {content_preview}...")
            print(f"📊 Total length: {len(content)} characters")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        print("\n" + "=" * 60)

def demo_logging_levels():
    """Demonstrate different logging levels."""
    print("\n🔧 Logging Level Demo")
    print("=" * 40)
    
    # Set to DEBUG to see detailed logs
    logging.getLogger('cloudflare_peek').setLevel(logging.DEBUG)
    
    try:
        # This will show detailed debug information
        content = peek("https://httpbin.org/html", timeout=10000)
        print(f"✅ Retrieved {len(content)} characters with DEBUG logging")
    except Exception as e:
        print(f"❌ Error with DEBUG logging: {e}")

if __name__ == "__main__":
    main()
    
    # Uncomment the line below to see detailed debug logs
    # demo_logging_levels()