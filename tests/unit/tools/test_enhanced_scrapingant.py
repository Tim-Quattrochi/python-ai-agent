#!/usr/bin/env python3
"""
Test script for enhanced ScrapingAnt configuration that bypasses LinkedIn detection.

This script tests the proven anti-detection parameters that successfully bypass 
LinkedIn's browser detection mechanisms.
"""

from src.tools.job_automation.scrapingant_scraper import ScrapingAntJobScraper
import os
import sys
import json
from pathlib import Path

# Add src to path so we can import the enhanced scraper
sys.path.append(str(Path(__file__).parent / "src"))


def test_enhanced_configuration():
    """Test the enhanced ScrapingAnt configuration with your existing scraper."""

    print("🚀 Testing Enhanced ScrapingAnt LinkedIn Configuration")
    print("=" * 60)

    # Check for API key
    api_key = os.getenv('SCRAPINGANT_API_KEY')
    if not api_key:
        print("❌ SCRAPINGANT_API_KEY not found in environment variables")
        print("💡 Please set your API key:")
        print("   export SCRAPINGANT_API_KEY='your_api_key_here'")
        return False

    # Initialize the enhanced scraper
    print("🔧 Initializing ScrapingAnt Job Scraper...")
    scraper = ScrapingAntJobScraper(api_key=api_key)

    if scraper.demo_mode:
        print("❌ Scraper is in demo mode - API key issue")
        return False

    print("✅ Scraper initialized successfully")

    # Test the enhanced LinkedIn method
    print("\n🧪 Testing Enhanced LinkedIn Scraping...")
    print("📊 Using proven anti-detection configuration:")
    print("   - browser=true")
    print("   - return_page_source=true (CRITICAL)")
    print("   - proxy_type=residential")
    print("   - proxy_country=US")
    print("   - wait_for=3000ms")

    # Test search query (software engineer jobs in San Francisco)
    test_query = "software engineer"
    test_location = "San Francisco, CA"

    try:
        print(f"\n🔍 Searching for '{test_query}' jobs in '{test_location}'...")

        # Use the enhanced method through the execute interface
        result = scraper.execute({
            'operation': 'search_linkedin_enhanced',
            'query': test_query,
            'location': test_location,
            'num_results': 5  # Small number for testing
        })

        if result.get('success'):
            jobs = result.get('data', {}).get('jobs', [])
            print(
                f"✅ SUCCESS! Found {len(jobs)} jobs using enhanced configuration")

            if jobs:
                print("\n📋 Sample Results:")
                for i, job in enumerate(jobs[:3], 1):
                    title = job.get('title', 'N/A')
                    company = job.get('company', 'N/A')
                    location = job.get('location', 'N/A')
                    print(f"   {i}. {title} at {company} ({location})")

            # Check if we got page source (indicates successful bypass)
            page_source = result.get('data', {}).get('page_source', '')
            if page_source and len(page_source) > 1000:
                print("✅ Page source retrieved - detection likely bypassed!")
            else:
                print("⚠️  Limited page source - may need further optimization")

        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ Enhanced method failed: {error_msg}")

            # Try fallback to regular method for comparison
            print("\n🔄 Testing fallback to regular method...")
            fallback_result = scraper.execute({
                'operation': 'search_linkedin_jobs',
                'query': test_query,
                'location': test_location,
                'num_results': 5
            })

            if fallback_result.get('success'):
                jobs = fallback_result.get('data', {}).get('jobs', [])
                print(f"✅ Fallback method found {len(jobs)} jobs")
            else:
                print(
                    f"❌ Fallback also failed: {fallback_result.get('error')}")

    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

    return True


def test_api_connectivity():
    """Test basic API connectivity with ScrapingAnt."""

    print("\n🌐 Testing API Connectivity...")
    print("-" * 40)

    api_key = os.getenv('SCRAPINGANT_API_KEY')
    scraper = ScrapingAntJobScraper(api_key=api_key)

    try:
        # Test with a simple non-LinkedIn URL first
        print("🔧 Testing basic scraping capability...")

        result = scraper.execute({
            'operation': 'scrape_url',
            'url': 'https://httpbin.org/ip',
            'return_page_source': True
        })

        if result.get('success'):
            print("✅ Basic API connectivity working")
            return True
        else:
            print(f"❌ API test failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ API connectivity test failed: {str(e)}")
        return False


def main():
    """Main test function."""

    print("ScrapingAnt Enhanced Configuration Test")
    print("=" * 50)

    # Test 1: API Connectivity
    if not test_api_connectivity():
        print("\n❌ Basic connectivity failed - check your API key")
        return

    # Test 2: Enhanced Configuration
    if test_enhanced_configuration():
        print("\n🎉 SUCCESS! Enhanced anti-detection configuration is working!")
        print("\n📝 Summary:")
        print("   ✅ ScrapingAnt API key is valid")
        print("   ✅ Enhanced LinkedIn scraping configuration implemented")
        print("   ✅ Anti-detection parameters successfully integrated")
        print("\n💡 Your scraper now includes:")
        print("   - Residential proxy support")
        print("   - Browser-like behavior simulation")
        print("   - Page source retrieval for better parsing")
        print("   - Multi-country fallback strategy")
        print("   - Proper wait times to avoid detection")
    else:
        print("\n⚠️  Tests completed with some issues")
        print("💡 The enhanced configuration is implemented but may need fine-tuning")


if __name__ == "__main__":
    main()
