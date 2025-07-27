"""Test script to verify event loop compatibility."""

import asyncio
from cloudflare_peek import peek


async def test_in_async_context():
    """Test that peek() works even when called from within an async function."""
    print("🧪 Testing CloudflarePeek in async context...")
    
    # This would normally fail with "RuntimeError: asyncio.run() cannot be called from a running event loop"
    # But our implementation handles it automatically
    result = peek("https://httpbin.org/html")
    
    print(f"✅ Success! Extracted {len(result)} characters from async context")
    return result


def test_in_sync_context():
    """Test that peek() works in normal synchronous context."""
    print("🧪 Testing CloudflarePeek in sync context...")
    
    result = peek("https://httpbin.org/html")
    
    print(f"✅ Success! Extracted {len(result)} characters from sync context")
    return result


async def main():
    """Run both tests to demonstrate compatibility."""
    print("CloudflarePeek Event Loop Compatibility Test")
    print("=" * 50)
    
    # Test 1: Sync context (normal usage)
    test_in_sync_context()
    
    print("\n" + "-" * 50 + "\n")
    
    # Test 2: Async context (problematic for most libraries)
    await test_in_async_context()
    
    print("\n🎉 All tests passed! CloudflarePeek works in both contexts.")


if __name__ == "__main__":
    # Test sync context first
    print("Testing sync context (standalone):")
    test_in_sync_context()
    
    print("\n" + "=" * 50 + "\n")
    
    # Test async context
    print("Testing both contexts with asyncio.run():")
    asyncio.run(main())