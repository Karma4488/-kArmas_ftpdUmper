#!/usr/bin/env python3
"""
Demo script showing kArmas_ftpdUmper HTTP bruteforce capabilities
This demonstrates the features without requiring network access
"""

from http_bruteforce import HTTPBruteForcer
from unittest.mock import Mock, patch

def demo_bypass_techniques():
    """Demonstrate 403 bypass techniques"""
    print("=" * 70)
    print("403 BYPASS TECHNIQUES DEMONSTRATION")
    print("=" * 70)
    
    test_url = "http://example.com/admin"
    
    bruteforcer = HTTPBruteForcer(
        target_url=test_url,
        enable_bypass=True
    )
    
    print(f"\nOriginal URL: {test_url}\n")
    
    print("Bypass Methods:")
    print("-" * 70)
    for technique_name, technique_func in bruteforcer.BYPASS_METHODS.items():
        bypassed_url = technique_func(test_url)
        print(f"  {technique_name:20s} -> {bypassed_url}")
    
    print("\nBypass Headers:")
    print("-" * 70)
    for header in bruteforcer.BYPASS_HEADERS[:5]:  # Show first 5
        header_name = list(header.keys())[0]
        header_value = list(header.values())[0]
        print(f"  {header_name:30s} : {header_value}")
    print(f"  ... and {len(bruteforcer.BYPASS_HEADERS) - 5} more headers")
    
    print("\n")


def demo_http_methods():
    """Demonstrate supported HTTP methods"""
    print("=" * 70)
    print("SUPPORTED HTTP METHODS")
    print("=" * 70)
    
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    print("\nThe following HTTP methods are supported:")
    for method in methods:
        print(f"  ✓ {method}")
    print("\n")


def demo_configuration():
    """Demonstrate configuration options"""
    print("=" * 70)
    print("CONFIGURATION OPTIONS")
    print("=" * 70)
    
    print("\nExample configuration:")
    print("-" * 70)
    
    config = {
        "target_url": "http://example.com/admin",
        "methods": ["GET", "POST"],
        "wordlist": ["admin", "test", "root"],
        "timeout": 10,
        "delay": 0.5,
        "enable_bypass": True,
        "verbose": True,
    }
    
    for key, value in config.items():
        print(f"  {key:20s} : {value}")
    
    print("\n")


def demo_mock_scan():
    """Demonstrate a mock endpoint scan"""
    print("=" * 70)
    print("MOCK ENDPOINT SCAN DEMONSTRATION")
    print("=" * 70)
    
    print("\nSimulating scan of 3 endpoints...")
    print("-" * 70)
    
    # Create mock bruteforcer
    bruteforcer = HTTPBruteForcer(
        target_url="http://example.com",
        wordlist=["admin", "config", "debug"],
        methods=["GET"],
        timeout=5,
        delay=0,
        verbose=False
    )
    
    # Simulate successful scan
    bruteforcer.results["successful"].append({
        "url": "http://example.com/admin",
        "method": "GET",
        "status_code": 200,
        "content_length": 1234
    })
    
    bruteforcer.results["bypassed_403"].append({
        "url": "http://example.com/config",
        "method": "GET",
        "status_code": 200,
        "technique": "apache_dot",
        "content_length": 567
    })
    
    bruteforcer.results["failed"].append({
        "url": "http://example.com/debug",
        "method": "GET",
        "error": "404 Not Found"
    })
    
    # Print summary
    summary = bruteforcer.get_results_summary()
    print(summary)


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "kArmas_ftpdUmper HTTP Bruteforce Demo" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    demo_bypass_techniques()
    demo_http_methods()
    demo_configuration()
    demo_mock_scan()
    
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nFor actual usage, run:")
    print("  python kArmas_ftpdUmper.py --http --url <target> --wordlist wordlist.txt")
    print("\nSee README.md for full documentation and examples.")
    print("\n")


if __name__ == "__main__":
    main()
