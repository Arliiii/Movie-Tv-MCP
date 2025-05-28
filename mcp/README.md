# 🎬 Movie & TV MCP Server

A complete Model Context Protocol (MCP) server for movie and TV show data powered by The Movie Database (TMDb) API. This server provides comprehensive search, discovery, and detailed information about movies and TV shows with rich media support.

## ✨ Features

### 🔍 Search & Discovery
- **Movie Search** - Find movies by title with optional year filtering
- **TV Show Search** - Search TV shows by name with air date filtering
- **Trending Content** - Get daily/weekly trending movies and TV shows
- **Smart Discovery** - Find content by genre, year, and custom sorting

### 📊 Rich Data
- **Complete Details** - Cast, crew, genres, ratings, runtime, budget
- **High-Quality Images** - Posters, backdrops, and profile photos in multiple sizes
- **Season Information** - TV show seasons, episodes, and network details
- **Production Data** - Companies, countries, languages, and release info

### 🛠️ Professional Features
- **Error Handling** - Comprehensive error management with helpful messages
- **Rate Limiting** - Respects TMDb's API limits (40 requests per 10 seconds)
- **Image URLs** - Automatic construction of image URLs in multiple sizes
- **Genre Mapping** - Converts genre IDs to human-readable names
- **Multi-language** - Configurable language support

## 🚀 Quick Start

### 1. Get TMDb API Key

1. Visit [TMDb API Settings](https://www.themoviedb.org/settings/api)
2. Create a free account if needed
3. Request an API key (choose "Developer" option)
4. Fill out the application form:
   - Application Name: "Movie MCP Server"
   - Application Type: "Educational/Personal Project"
   - Application Summary: "MCP server for movie and TV data"

### 2. Install Dependencies

```bash
pip install fastmcp httpx
```

### 3. Configure API Key

**Option A: Use the included .env file (Recommended)**
The project includes a `.env` file with your API key already configured. No additional setup needed!

**Option B: Set Environment Variables**

**Windows (Command Prompt):**
```cmd
set TMDB_API_KEY=your_actual_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:TMDB_API_KEY="your_actual_api_key_here"
```

**Mac/Linux:**
```bash
export TMDB_API_KEY="your_actual_api_key_here"
```

### 4. Run the Server

```bash
python movie_server.py
```

## 🛠️ Tools Available

### search_movies
Search for movies by title with optional year filtering.

**Parameters:**
- `query` (required): Movie title to search for
- `year` (optional): Release year to filter by
- `page` (optional): Page number for pagination (default: 1)

**Example:**
```json
{
  "query": "The Matrix",
  "year": 1999
}
```

### search_tv_shows
Search for TV shows by name with optional year filtering.

**Parameters:**
- `query` (required): TV show name to search for
- `first_air_date_year` (optional): First air date year to filter by
- `page` (optional): Page number for pagination (default: 1)

**Example:**
```json
{
  "query": "Breaking Bad"
}
```

### get_movie_details
Get detailed information about a specific movie.

**Parameters:**
- `movie_id` (required): TMDb movie ID

**Example:**
```json
{
  "movie_id": 603
}
```

### get_tv_show_details
Get detailed information about a specific TV show.

**Parameters:**
- `tv_id` (required): TMDb TV show ID

**Example:**
```json
{
  "tv_id": 1396
}
```

### get_trending
Get trending movies or TV shows.

**Parameters:**
- `media_type` (required): "movie" or "tv"
- `time_window` (optional): "day" or "week" (default: "day")

**Example:**
```json
{
  "media_type": "movie",
  "time_window": "week"
}
```

### discover_content
Discover content based on filters.

**Parameters:**
- `content_type` (required): "movie" or "tv"
- `genre_id` (optional): Genre ID to filter by
- `year` (optional): Year to filter by
- `sort_by` (optional): Sort order (default: "popularity.desc")

**Example:**
```json
{
  "content_type": "movie",
  "genre_id": 28,
  "sort_by": "vote_average.desc"
}
```

## 📚 Resources Available

### config://movie-api
Returns API configuration, setup instructions, and current settings.

### data://popular-genres
Returns complete list of movie and TV show genres with IDs and descriptions.

### help://usage-examples
Returns detailed usage examples for all tools with sample requests and responses.

## 🖼️ Image URL Construction

The server automatically constructs image URLs in multiple sizes:

**Base URL:** `https://image.tmdb.org/t/p/`

**Poster Sizes:** w92, w154, w185, w342, w500, w780, original
**Backdrop Sizes:** w300, w780, w1280, original
**Profile Sizes:** w45, w185, h632, original

**Example:**
```
https://image.tmdb.org/t/p/w500/poster_path.jpg
```

## ⚙️ Configuration

### Environment Variables

The server can be configured using environment variables or the included `.env` file:

- `TMDB_API_KEY` (required): Your TMDb API key
- `TMDB_READ_ACCESS_TOKEN` (optional): Your TMDb read access token
- `INCLUDE_ADULT` (optional): Include adult content (default: false)
- `DEFAULT_LANGUAGE` (optional): Default language (default: en-US)
- `API_TIMEOUT` (optional): Request timeout in seconds (default: 10)
- `DEBUG` (optional): Enable debug output (default: false)

### .env File Configuration

The project includes a `.env` file with your API credentials already configured:

```env
TMDB_API_KEY=fdb1a8aa36eefdd57c67c951e1a831e6
TMDB_READ_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiJ9...
INCLUDE_ADULT=false
DEFAULT_LANGUAGE=en-US
API_TIMEOUT=10
DEBUG=false
```

### Popular Sort Options

- `popularity.desc` - Most popular first
- `vote_average.desc` - Highest rated first
- `release_date.desc` - Newest first
- `revenue.desc` - Highest grossing first

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t movie-tv-mcp .

# Run with environment variables
docker run -e TMDB_API_KEY=your_api_key movie-tv-mcp
```

## 🔧 Troubleshooting

### Common Issues

**"Invalid API key" error:**
- Verify your API key at https://www.themoviedb.org/settings/api
- Ensure the environment variable is set correctly

**"Rate limit exceeded" error:**
- Wait 10 seconds between large batches
- TMDb allows 40 requests per 10 seconds

**"No results found" error:**
- Try different keywords or check spelling
- Use broader search criteria

**Images not loading:**
- Check that poster_path is not null
- Verify image URL construction

### Rate Limits

TMDb API limits:
- 40 requests per 10 seconds
- 1,000,000 requests per day

## 📝 Example Responses

### Movie Search Response
```json
{
  "success": true,
  "query": "The Matrix",
  "year": 1999,
  "total_results": 1,
  "results": [
    {
      "id": 603,
      "title": "The Matrix",
      "overview": "Set in the 22nd century...",
      "release_date": "1999-03-30",
      "vote_average": 8.2,
      "genres": ["Action", "Science Fiction"],
      "poster_urls": {
        "w500": "https://image.tmdb.org/t/p/w500/poster.jpg"
      }
    }
  ]
}
```

## 🚀 Smithery Deployment

1. Create a public GitHub repository
2. Upload all files to the repository
3. Connect to Smithery
4. Configure your TMDb API key
5. Deploy and test

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Verify your TMDb API key
3. Review the usage examples
4. Check TMDb API documentation

---

**Created with ❤️ for the MCP community**
