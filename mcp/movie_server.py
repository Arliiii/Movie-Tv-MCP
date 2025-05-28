from fastmcp import FastMCP, Context
import httpx
import os
from typing import Dict, Optional, List
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the MCP server
mcp = FastMCP("MovieTVMCP")

# TMDb API configuration
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/"
API_KEY = os.getenv("TMDB_API_KEY")
READ_ACCESS_TOKEN = os.getenv("TMDB_READ_ACCESS_TOKEN")
INCLUDE_ADULT = os.getenv("INCLUDE_ADULT", "false").lower() == "true"
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en-US")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

# Debug configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# HTTP client with timeout
http_client = httpx.AsyncClient(timeout=API_TIMEOUT)

# Genre cache
_genre_cache = {"movies": [], "tv": []}

async def make_tmdb_request(endpoint: str, params: Dict = None) -> Dict:
    """Make a request to TMDb API with error handling"""
    if not API_KEY:
        return {
            "success": False,
            "error": "TMDb API key not configured. Please set TMDB_API_KEY environment variable.",
            "setup_url": "https://www.themoviedb.org/settings/api"
        }

    if params is None:
        params = {}

    params.update({
        "api_key": API_KEY,
        "language": DEFAULT_LANGUAGE,
        "include_adult": INCLUDE_ADULT
    })

    try:
        url = f"{TMDB_BASE_URL}{endpoint}"
        response = await http_client.get(url, params=params)

        if response.status_code == 401:
            return {
                "success": False,
                "error": "Invalid TMDb API key. Please check your API key configuration.",
                "setup_url": "https://www.themoviedb.org/settings/api"
            }
        elif response.status_code == 404:
            return {
                "success": False,
                "error": "Resource not found. Please check the ID or search parameters."
            }
        elif response.status_code == 422:
            return {
                "success": False,
                "error": "Invalid parameters provided to the API."
            }
        elif response.status_code == 429:
            return {
                "success": False,
                "error": "Rate limit exceeded. Please wait before making more requests.",
                "rate_limit": "40 requests per 10 seconds"
            }
        elif response.status_code >= 500:
            return {
                "success": False,
                "error": "TMDb server error. Please try again later."
            }

        response.raise_for_status()
        data = response.json()
        data["success"] = True
        return data

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": f"Request timeout after {API_TIMEOUT} seconds. Please try again."
        }
    except httpx.RequestError as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

def construct_image_urls(path: Optional[str], image_type: str = "poster") -> Dict[str, Optional[str]]:
    """Construct image URLs for different sizes"""
    if not path:
        return {size: None for size in ["w92", "w154", "w185", "w342", "w500", "w780", "original"]}

    if image_type == "poster":
        sizes = ["w92", "w154", "w185", "w342", "w500", "w780", "original"]
    elif image_type == "backdrop":
        sizes = ["w300", "w780", "w1280", "original"]
    else:  # profile
        sizes = ["w45", "w185", "h632", "original"]

    return {size: f"{TMDB_IMAGE_BASE_URL}{size}{path}" for size in sizes}

async def get_genres() -> Dict[str, List[Dict]]:
    """Get and cache genre lists for movies and TV shows"""
    global _genre_cache

    if not _genre_cache["movies"]:
        movie_genres = await make_tmdb_request("/genre/movie/list")
        if movie_genres.get("success"):
            _genre_cache["movies"] = movie_genres.get("genres", [])

    if not _genre_cache["tv"]:
        tv_genres = await make_tmdb_request("/genre/tv/list")
        if tv_genres.get("success"):
            _genre_cache["tv"] = tv_genres.get("genres", [])

    return _genre_cache

def map_genre_ids_to_names(genre_ids: List[int], content_type: str = "movie") -> List[str]:
    """Convert genre IDs to genre names"""
    genre_map = {genre["id"]: genre["name"] for genre in _genre_cache.get(content_type + "s", [])}
    return [genre_map.get(gid, f"Unknown ({gid})") for gid in genre_ids]

def format_movie_result(movie: Dict) -> Dict:
    """Format movie data with image URLs and genre names"""
    return {
        "id": movie.get("id"),
        "title": movie.get("title"),
        "original_title": movie.get("original_title"),
        "overview": movie.get("overview"),
        "release_date": movie.get("release_date"),
        "vote_average": movie.get("vote_average"),
        "vote_count": movie.get("vote_count"),
        "popularity": movie.get("popularity"),
        "adult": movie.get("adult", False),
        "genre_ids": movie.get("genre_ids", []),
        "genres": map_genre_ids_to_names(movie.get("genre_ids", []), "movie"),
        "poster_urls": construct_image_urls(movie.get("poster_path"), "poster"),
        "backdrop_urls": construct_image_urls(movie.get("backdrop_path"), "backdrop"),
        "tmdb_url": f"https://www.themoviedb.org/movie/{movie.get('id')}"
    }

def format_tv_result(show: Dict) -> Dict:
    """Format TV show data with image URLs and genre names"""
    return {
        "id": show.get("id"),
        "name": show.get("name"),
        "original_name": show.get("original_name"),
        "overview": show.get("overview"),
        "first_air_date": show.get("first_air_date"),
        "vote_average": show.get("vote_average"),
        "vote_count": show.get("vote_count"),
        "popularity": show.get("popularity"),
        "origin_country": show.get("origin_country", []),
        "genre_ids": show.get("genre_ids", []),
        "genres": map_genre_ids_to_names(show.get("genre_ids", []), "tv"),
        "poster_urls": construct_image_urls(show.get("poster_path"), "poster"),
        "backdrop_urls": construct_image_urls(show.get("backdrop_path"), "backdrop"),
        "tmdb_url": f"https://www.themoviedb.org/tv/{show.get('id')}"
    }

@mcp.tool()
async def search_movies(ctx: Context, query: str, year: Optional[int] = None, page: int = 1) -> str:
    """
    Search for movies by title with optional year filtering.

    Args:
        query: Movie title to search for (required)
        year: Release year to filter by (optional)
        page: Page number for pagination (default: 1)

    Returns:
        JSON string with movie search results including titles, release dates, overviews, ratings, and image URLs
    """
    # Ensure genres are loaded
    await get_genres()

    params = {
        "query": query,
        "page": page
    }

    if year:
        params["year"] = year

    result = await make_tmdb_request("/search/movie", params)

    if not result.get("success"):
        return json.dumps(result, indent=2)

    if not result.get("results"):
        return json.dumps({
            "success": True,
            "message": f"No movies found for '{query}'" + (f" in {year}" if year else ""),
            "suggestion": "Try different keywords or check spelling",
            "total_results": 0,
            "results": []
        }, indent=2)

    formatted_results = [format_movie_result(movie) for movie in result["results"]]

    return json.dumps({
        "success": True,
        "query": query,
        "year": year,
        "page": page,
        "total_results": result.get("total_results", 0),
        "total_pages": result.get("total_pages", 0),
        "results": formatted_results
    }, indent=2)

@mcp.tool()
async def search_tv_shows(ctx: Context, query: str, first_air_date_year: Optional[int] = None, page: int = 1) -> str:
    """
    Search for TV shows by name with optional year filtering.

    Args:
        query: TV show name to search for (required)
        first_air_date_year: First air date year to filter by (optional)
        page: Page number for pagination (default: 1)

    Returns:
        JSON string with TV show search results including names, air dates, overviews, ratings, and image URLs
    """
    # Ensure genres are loaded
    await get_genres()

    params = {
        "query": query,
        "page": page
    }

    if first_air_date_year:
        params["first_air_date_year"] = first_air_date_year

    result = await make_tmdb_request("/search/tv", params)

    if not result.get("success"):
        return json.dumps(result, indent=2)

    if not result.get("results"):
        return json.dumps({
            "success": True,
            "message": f"No TV shows found for '{query}'" + (f" from {first_air_date_year}" if first_air_date_year else ""),
            "suggestion": "Try different keywords or check spelling",
            "total_results": 0,
            "results": []
        }, indent=2)

    formatted_results = [format_tv_result(show) for show in result["results"]]

    return json.dumps({
        "success": True,
        "query": query,
        "first_air_date_year": first_air_date_year,
        "page": page,
        "total_results": result.get("total_results", 0),
        "total_pages": result.get("total_pages", 0),
        "results": formatted_results
    }, indent=2)

@mcp.tool()
async def get_movie_details(ctx: Context, movie_id: int) -> str:
    """
    Get detailed information about a specific movie including cast, crew, and production details.

    Args:
        movie_id: TMDb movie ID (required)

    Returns:
        JSON string with complete movie information including cast, crew, genres, runtime, budget, revenue
    """
    # Ensure genres are loaded
    await get_genres()

    # Get movie details with additional data
    result = await make_tmdb_request(f"/movie/{movie_id}", {"append_to_response": "credits,production_companies,production_countries,spoken_languages"})

    if not result.get("success"):
        return json.dumps(result, indent=2)

    # Format cast (top 10)
    cast = []
    if result.get("credits", {}).get("cast"):
        for actor in result["credits"]["cast"][:10]:
            cast.append({
                "id": actor.get("id"),
                "name": actor.get("name"),
                "character": actor.get("character"),
                "profile_urls": construct_image_urls(actor.get("profile_path"), "profile"),
                "order": actor.get("order")
            })

    # Format crew (key roles)
    crew = {"directors": [], "writers": [], "producers": []}
    if result.get("credits", {}).get("crew"):
        for person in result["credits"]["crew"]:
            job = person.get("job", "").lower()
            crew_member = {
                "id": person.get("id"),
                "name": person.get("name"),
                "job": person.get("job"),
                "profile_urls": construct_image_urls(person.get("profile_path"), "profile")
            }

            if "director" in job:
                crew["directors"].append(crew_member)
            elif any(role in job for role in ["writer", "screenplay", "story"]):
                crew["writers"].append(crew_member)
            elif "producer" in job:
                crew["producers"].append(crew_member)

    # Format genres
    genres = [{"id": g.get("id"), "name": g.get("name")} for g in result.get("genres", [])]

    # Format production companies
    production_companies = [{"id": pc.get("id"), "name": pc.get("name"), "origin_country": pc.get("origin_country")}
                           for pc in result.get("production_companies", [])]

    formatted_result = {
        "success": True,
        "id": result.get("id"),
        "title": result.get("title"),
        "original_title": result.get("original_title"),
        "tagline": result.get("tagline"),
        "overview": result.get("overview"),
        "release_date": result.get("release_date"),
        "runtime": result.get("runtime"),
        "status": result.get("status"),
        "vote_average": result.get("vote_average"),
        "vote_count": result.get("vote_count"),
        "popularity": result.get("popularity"),
        "budget": result.get("budget"),
        "revenue": result.get("revenue"),
        "adult": result.get("adult", False),
        "genres": genres,
        "production_companies": production_companies,
        "production_countries": [pc.get("name") for pc in result.get("production_countries", [])],
        "spoken_languages": [sl.get("english_name") for sl in result.get("spoken_languages", [])],
        "poster_urls": construct_image_urls(result.get("poster_path"), "poster"),
        "backdrop_urls": construct_image_urls(result.get("backdrop_path"), "backdrop"),
        "cast": cast,
        "crew": crew,
        "tmdb_url": f"https://www.themoviedb.org/movie/{movie_id}",
        "imdb_id": result.get("imdb_id")
    }

    return json.dumps(formatted_result, indent=2)

@mcp.tool()
async def get_tv_show_details(ctx: Context, tv_id: int) -> str:
    """
    Get detailed information about a specific TV show including cast, seasons, and network details.

    Args:
        tv_id: TMDb TV show ID (required)

    Returns:
        JSON string with complete TV show information including cast, seasons, networks, creators
    """
    # Ensure genres are loaded
    await get_genres()

    # Get TV show details with additional data
    result = await make_tmdb_request(f"/tv/{tv_id}", {"append_to_response": "credits,content_ratings"})

    if not result.get("success"):
        return json.dumps(result, indent=2)

    # Format cast (main cast)
    cast = []
    if result.get("credits", {}).get("cast"):
        for actor in result["credits"]["cast"][:15]:
            cast.append({
                "id": actor.get("id"),
                "name": actor.get("name"),
                "character": actor.get("character"),
                "profile_urls": construct_image_urls(actor.get("profile_path"), "profile"),
                "order": actor.get("order")
            })

    # Format creators
    creators = []
    if result.get("created_by"):
        for creator in result["created_by"]:
            creators.append({
                "id": creator.get("id"),
                "name": creator.get("name"),
                "profile_urls": construct_image_urls(creator.get("profile_path"), "profile")
            })

    # Format seasons
    seasons = []
    if result.get("seasons"):
        for season in result["seasons"]:
            seasons.append({
                "id": season.get("id"),
                "season_number": season.get("season_number"),
                "name": season.get("name"),
                "overview": season.get("overview"),
                "episode_count": season.get("episode_count"),
                "air_date": season.get("air_date"),
                "poster_urls": construct_image_urls(season.get("poster_path"), "poster")
            })

    # Format networks
    networks = [{"id": n.get("id"), "name": n.get("name"), "origin_country": n.get("origin_country")}
               for n in result.get("networks", [])]

    # Format genres
    genres = [{"id": g.get("id"), "name": g.get("name")} for g in result.get("genres", [])]

    formatted_result = {
        "success": True,
        "id": result.get("id"),
        "name": result.get("name"),
        "original_name": result.get("original_name"),
        "tagline": result.get("tagline"),
        "overview": result.get("overview"),
        "first_air_date": result.get("first_air_date"),
        "last_air_date": result.get("last_air_date"),
        "status": result.get("status"),
        "type": result.get("type"),
        "vote_average": result.get("vote_average"),
        "vote_count": result.get("vote_count"),
        "popularity": result.get("popularity"),
        "number_of_seasons": result.get("number_of_seasons"),
        "number_of_episodes": result.get("number_of_episodes"),
        "episode_run_time": result.get("episode_run_time", []),
        "in_production": result.get("in_production"),
        "origin_country": result.get("origin_country", []),
        "original_language": result.get("original_language"),
        "genres": genres,
        "networks": networks,
        "production_companies": [{"id": pc.get("id"), "name": pc.get("name")} for pc in result.get("production_companies", [])],
        "poster_urls": construct_image_urls(result.get("poster_path"), "poster"),
        "backdrop_urls": construct_image_urls(result.get("backdrop_path"), "backdrop"),
        "cast": cast,
        "creators": creators,
        "seasons": seasons,
        "tmdb_url": f"https://www.themoviedb.org/tv/{tv_id}"
    }

    return json.dumps(formatted_result, indent=2)

@mcp.tool()
async def get_trending(ctx: Context, media_type: str, time_window: str = "day") -> str:
    """
    Get trending movies or TV shows.

    Args:
        media_type: Type of media - "movie" or "tv" (required)
        time_window: Time window - "day" or "week" (default: "day")

    Returns:
        JSON string with trending content including popularity scores and rankings
    """
    # Ensure genres are loaded
    await get_genres()

    if media_type not in ["movie", "tv"]:
        return json.dumps({
            "success": False,
            "error": "Invalid media_type. Must be 'movie' or 'tv'."
        }, indent=2)

    if time_window not in ["day", "week"]:
        return json.dumps({
            "success": False,
            "error": "Invalid time_window. Must be 'day' or 'week'."
        }, indent=2)

    result = await make_tmdb_request(f"/trending/{media_type}/{time_window}")

    if not result.get("success"):
        return json.dumps(result, indent=2)

    if not result.get("results"):
        return json.dumps({
            "success": True,
            "message": f"No trending {media_type} found for {time_window}",
            "total_results": 0,
            "results": []
        }, indent=2)

    if media_type == "movie":
        formatted_results = [format_movie_result(item) for item in result["results"]]
    else:
        formatted_results = [format_tv_result(item) for item in result["results"]]

    return json.dumps({
        "success": True,
        "media_type": media_type,
        "time_window": time_window,
        "total_results": result.get("total_results", 0),
        "results": formatted_results
    }, indent=2)

@mcp.tool()
async def discover_content(ctx: Context, content_type: str, genre_id: Optional[int] = None,
                          year: Optional[int] = None, sort_by: str = "popularity.desc") -> str:
    """
    Discover movies or TV shows based on filters.

    Args:
        content_type: Type of content - "movie" or "tv" (required)
        genre_id: Genre ID to filter by (optional)
        year: Year to filter by (optional) - release year for movies, first air date year for TV
        sort_by: Sort order (default: "popularity.desc")

    Returns:
        JSON string with curated content based on filters
    """
    # Ensure genres are loaded
    await get_genres()

    if content_type not in ["movie", "tv"]:
        return json.dumps({
            "success": False,
            "error": "Invalid content_type. Must be 'movie' or 'tv'."
        }, indent=2)

    params = {
        "sort_by": sort_by
    }

    if genre_id:
        params["with_genres"] = genre_id

    if year:
        if content_type == "movie":
            params["year"] = year
        else:
            params["first_air_date_year"] = year

    result = await make_tmdb_request(f"/discover/{content_type}", params)

    if not result.get("success"):
        return json.dumps(result, indent=2)

    if not result.get("results"):
        return json.dumps({
            "success": True,
            "message": f"No {content_type} found with the specified filters",
            "filters": {"genre_id": genre_id, "year": year, "sort_by": sort_by},
            "total_results": 0,
            "results": []
        }, indent=2)

    if content_type == "movie":
        formatted_results = [format_movie_result(item) for item in result["results"]]
    else:
        formatted_results = [format_tv_result(item) for item in result["results"]]

    return json.dumps({
        "success": True,
        "content_type": content_type,
        "filters": {"genre_id": genre_id, "year": year, "sort_by": sort_by},
        "total_results": result.get("total_results", 0),
        "total_pages": result.get("total_pages", 0),
        "results": formatted_results
    }, indent=2)

# Resources
@mcp.resource("config://movie-api")
async def get_api_config() -> str:
    """Get API configuration and setup information"""
    config = {
        "api_name": "TMDb (The Movie Database)",
        "api_version": "3",
        "base_url": TMDB_BASE_URL,
        "image_base_url": TMDB_IMAGE_BASE_URL,
        "documentation": "https://developers.themoviedb.org/3",
        "rate_limits": {
            "requests_per_10_seconds": 40,
            "daily_limit": 1000000
        },
        "image_sizes": {
            "poster": ["w92", "w154", "w185", "w342", "w500", "w780", "original"],
            "backdrop": ["w300", "w780", "w1280", "original"],
            "profile": ["w45", "w185", "h632", "original"]
        },
        "setup_instructions": {
            "1": "Visit https://www.themoviedb.org/settings/api",
            "2": "Create a free account if you don't have one",
            "3": "Request an API key (choose Developer option)",
            "4": "Set the TMDB_API_KEY environment variable",
            "5": "Optionally configure INCLUDE_ADULT, DEFAULT_LANGUAGE, and API_TIMEOUT"
        },
        "environment_variables": {
            "TMDB_API_KEY": "Your TMDb API key (required)",
            "INCLUDE_ADULT": "Include adult content (default: false)",
            "DEFAULT_LANGUAGE": "Default language (default: en-US)",
            "API_TIMEOUT": "Request timeout in seconds (default: 10)"
        },
        "current_config": {
            "api_key_configured": bool(API_KEY),
            "include_adult": INCLUDE_ADULT,
            "default_language": DEFAULT_LANGUAGE,
            "api_timeout": API_TIMEOUT
        }
    }

    return json.dumps(config, indent=2)

@mcp.resource("data://popular-genres")
async def get_popular_genres() -> str:
    """Get list of movie and TV show genres with IDs"""
    genres = await get_genres()

    # Add popular genre information
    popular_movie_genres = [28, 12, 16, 35, 80, 99, 18, 10751, 14, 36, 27, 10402, 9648, 10749, 878, 10770, 53, 10752, 37]
    popular_tv_genres = [10759, 16, 35, 80, 99, 18, 10751, 14, 10762, 9648, 10763, 10764, 10765, 10766, 10767, 10768]

    result = {
        "movies": genres.get("movies", []),
        "tv": genres.get("tv", []),
        "popular_movie_genre_ids": popular_movie_genres,
        "popular_tv_genre_ids": popular_tv_genres,
        "genre_descriptions": {
            "28": "Action - High-energy films with physical stunts and chases",
            "12": "Adventure - Journey and exploration themed movies",
            "16": "Animation - Animated films and shows",
            "35": "Comedy - Humorous content designed to entertain",
            "80": "Crime - Stories involving criminal activities",
            "18": "Drama - Character-driven stories with emotional depth",
            "14": "Fantasy - Magical and supernatural elements",
            "27": "Horror - Scary and suspenseful content",
            "878": "Science Fiction - Futuristic and technological themes",
            "53": "Thriller - Suspenseful and tension-filled stories"
        }
    }

    return json.dumps(result, indent=2)

@mcp.resource("help://usage-examples")
async def get_usage_examples() -> str:
    """Get complete usage examples for all tools"""
    examples = {
        "search_movies": {
            "description": "Search for movies by title with optional year filtering",
            "examples": [
                {
                    "request": {"query": "The Matrix", "year": 1999},
                    "description": "Search for The Matrix from 1999"
                },
                {
                    "request": {"query": "Avengers", "page": 2},
                    "description": "Search for Avengers movies, page 2"
                }
            ]
        },
        "search_tv_shows": {
            "description": "Search for TV shows by name with optional year filtering",
            "examples": [
                {
                    "request": {"query": "Breaking Bad"},
                    "description": "Search for Breaking Bad TV show"
                },
                {
                    "request": {"query": "Game of Thrones", "first_air_date_year": 2011},
                    "description": "Search for Game of Thrones from 2011"
                }
            ]
        },
        "get_movie_details": {
            "description": "Get detailed information about a specific movie",
            "examples": [
                {
                    "request": {"movie_id": 603},
                    "description": "Get details for The Matrix (ID: 603)"
                },
                {
                    "request": {"movie_id": 550},
                    "description": "Get details for Fight Club (ID: 550)"
                }
            ]
        },
        "get_tv_show_details": {
            "description": "Get detailed information about a specific TV show",
            "examples": [
                {
                    "request": {"tv_id": 1396},
                    "description": "Get details for Breaking Bad (ID: 1396)"
                },
                {
                    "request": {"tv_id": 1399},
                    "description": "Get details for Game of Thrones (ID: 1399)"
                }
            ]
        },
        "get_trending": {
            "description": "Get trending movies or TV shows",
            "examples": [
                {
                    "request": {"media_type": "movie", "time_window": "week"},
                    "description": "Get trending movies this week"
                },
                {
                    "request": {"media_type": "tv", "time_window": "day"},
                    "description": "Get trending TV shows today"
                }
            ]
        },
        "discover_content": {
            "description": "Discover content based on filters",
            "examples": [
                {
                    "request": {"content_type": "movie", "genre_id": 28, "sort_by": "vote_average.desc"},
                    "description": "Discover top-rated action movies"
                },
                {
                    "request": {"content_type": "tv", "year": 2023, "sort_by": "popularity.desc"},
                    "description": "Discover popular TV shows from 2023"
                }
            ]
        },
        "common_sort_options": [
            "popularity.desc", "popularity.asc",
            "vote_average.desc", "vote_average.asc",
            "release_date.desc", "release_date.asc",
            "revenue.desc", "revenue.asc"
        ],
        "troubleshooting": {
            "no_results": "Try different keywords, check spelling, or broaden search criteria",
            "invalid_api_key": "Verify your TMDb API key at https://www.themoviedb.org/settings/api",
            "rate_limit": "Wait 10 seconds between large batches (40 requests per 10 seconds)",
            "missing_images": "Some content may not have poster or backdrop images available",
            "timeout_errors": "Increase API_TIMEOUT environment variable if requests are timing out"
        }
    }

    return json.dumps(examples, indent=2)

# Test cases for development
"""
Test cases:
search_movies("The Matrix", 1999)
search_tv_shows("Breaking Bad")
get_movie_details(603)  # The Matrix ID
get_tv_show_details(1396)  # Breaking Bad ID
get_trending("movie", "week")
discover_content("movie", genre_id=28, sort_by="vote_average.desc")
"""

if __name__ == "__main__":
    # Minimal startup for STDIO compatibility
    import sys

    # Debug information (only if DEBUG is enabled)
    if DEBUG:
        print("🎬 Movie & TV MCP Server Starting...", file=sys.stderr)
        print(f"   .env file loaded: {os.path.exists('.env')}", file=sys.stderr)
        print(f"   API key configured: {bool(API_KEY)}", file=sys.stderr)
        print(f"   Read token configured: {bool(READ_ACCESS_TOKEN)}", file=sys.stderr)
        print(f"   Language: {DEFAULT_LANGUAGE}", file=sys.stderr)
        print(f"   Include adult: {INCLUDE_ADULT}", file=sys.stderr)
        print(f"   Timeout: {API_TIMEOUT}s", file=sys.stderr)

    # Check API key on startup
    if not API_KEY:
        print("Warning: TMDB_API_KEY environment variable not set", file=sys.stderr)
        print("Check your .env file or set the environment variable", file=sys.stderr)
        print("Get your API key from: https://www.themoviedb.org/settings/api", file=sys.stderr)

    try:
        mcp.run()
    except KeyboardInterrupt:
        print("Server stopped", file=sys.stderr)
    finally:
        # Clean shutdown
        asyncio.run(http_client.aclose())