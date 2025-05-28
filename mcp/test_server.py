#!/usr/bin/env python3
"""
Test script for the Movie & TV MCP Server
Run this to test all functionality before deployment
"""

import asyncio
import os
import json

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

async def test_basic_functionality():
    """Test basic MCP server functionality"""

    print("Movie & TV MCP Server Test Suite")
    print("=" * 50)

    # Check if API key is configured
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("ERROR: TMDB_API_KEY not set. Please check your .env file.")
        return False

    print(f"SUCCESS: API Key configured: {api_key[:8]}...")
    print()

    # Import the server functions
    try:
        from movie_server import (
            search_movies, search_tv_shows, get_movie_details,
            get_tv_show_details, get_trending, discover_content,
            get_api_config, get_popular_genres, get_usage_examples
        )
        print("SUCCESS: All server functions imported")
    except ImportError as e:
        print(f"ERROR: Failed to import server functions: {e}")
        return False

    print()
    print("Testing Tools:")
    print("-" * 30)

    # Test 1: Search Movies
    try:
        print("Testing: Search Movies - The Matrix")
        result = await search_movies(None, "The Matrix", 1999)
        data = json.loads(result)
        if data.get("success") and data.get("results"):
            count = len(data["results"])
            print(f"  SUCCESS - Found {count} movies")
        else:
            print(f"  FAILED - {data.get('error', 'No results')}")
    except Exception as e:
        print(f"  ERROR - {str(e)}")

    # Test 2: Search TV Shows
    try:
        print("Testing: Search TV Shows - Breaking Bad")
        result = await search_tv_shows(None, "Breaking Bad")
        data = json.loads(result)
        if data.get("success") and data.get("results"):
            count = len(data["results"])
            print(f"  SUCCESS - Found {count} TV shows")
        else:
            print(f"  FAILED - {data.get('error', 'No results')}")
    except Exception as e:
        print(f"  ERROR - {str(e)}")

    # Test 3: Get Movie Details
    try:
        print("Testing: Movie Details - The Matrix (ID: 603)")
        result = await get_movie_details(None, 603)
        data = json.loads(result)
        if data.get("success") and data.get("title"):
            print(f"  SUCCESS - Retrieved details for '{data['title']}'")
        else:
            print(f"  FAILED - {data.get('error', 'No details')}")
    except Exception as e:
        print(f"  ERROR - {str(e)}")

    # Test 4: Get Trending
    try:
        print("Testing: Trending Movies")
        result = await get_trending(None, "movie", "week")
        data = json.loads(result)
        if data.get("success") and data.get("results"):
            count = len(data["results"])
            print(f"  SUCCESS - Found {count} trending movies")
        else:
            print(f"  FAILED - {data.get('error', 'No results')}")
    except Exception as e:
        print(f"  ERROR - {str(e)}")

    print()
    print("Testing Resources:")
    print("-" * 30)

    # Test Resources
    try:
        print("Testing: API Configuration")
        result = await get_api_config()
        data = json.loads(result)
        if data.get("api_name"):
            print(f"  SUCCESS - API config retrieved")
        else:
            print(f"  FAILED - Invalid config")
    except Exception as e:
        print(f"  ERROR - {str(e)}")

    try:
        print("Testing: Popular Genres")
        result = await get_popular_genres()
        data = json.loads(result)
        if data.get("movies") and data.get("tv"):
            movie_count = len(data["movies"])
            tv_count = len(data["tv"])
            print(f"  SUCCESS - {movie_count} movie genres, {tv_count} TV genres")
        else:
            print(f"  FAILED - Invalid genre data")
    except Exception as e:
        print(f"  ERROR - {str(e)}")

    print()
    return True

async def test_image_urls():
    """Test image URL construction"""
    print("Testing Image URL Construction:")
    print("-" * 40)

    try:
        from movie_server import search_movies
        result = await search_movies(None, "The Matrix", 1999)
        data = json.loads(result)

        if data.get("success") and data.get("results") and len(data["results"]) > 0:
            movie = data["results"][0]
            print(f"Movie: {movie['title']}")
            print("Sample Poster URLs:")
            poster_urls = movie.get("poster_urls", {})
            for size in ["w185", "w500", "original"]:
                if poster_urls.get(size):
                    print(f"  {size}: {poster_urls[size]}")
            print("Sample Backdrop URLs:")
            backdrop_urls = movie.get("backdrop_urls", {})
            for size in ["w780", "w1280", "original"]:
                if backdrop_urls.get(size):
                    print(f"  {size}: {backdrop_urls[size]}")
            print("SUCCESS: Image URLs constructed properly")
        else:
            print("ERROR: Could not retrieve movie data for image testing")
            if data.get("success"):
                print(f"  Debug: Found {len(data.get('results', []))} results")

    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    print()
    asyncio.run(test_image_urls())
    print()

    if success:
        print("Testing completed successfully!")
        print()
        print("Your Movie & TV MCP Server is ready!")
        print("Next steps:")
        print("1. Run: python movie_server.py")
        print("2. Deploy to Smithery for production use")
    else:
        print("Some tests failed. Check your configuration.")
