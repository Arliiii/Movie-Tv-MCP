# Movie Search Project

A comprehensive movie search and recommendation system with three main components: a Movie MCP server, a Mastra-based AI agent, and a mobile application.

## Project Overview

This project provides a complete solution for searching, discovering, and getting detailed information about movies and TV shows:

- **Movie MCP Server**: Backend server providing movie data via TMDb API
- **Mastra Agent**: AI-powered movie assistant for natural language interactions
- **Mobile App**: React Native mobile interface for searching and viewing movie information

## Components

### 1. Movie MCP Server

A Model Context Protocol (MCP) server powered by The Movie Database (TMDb) API.

#### Features
- Movie and TV show search with filtering options
- Detailed movie/TV information (cast, crew, ratings, etc.)
- Trending content discovery
- Genre-based recommendations

#### Installation
```bash
cd mcp
pip install -r requirements.txt
python movie_server.py
```

### 2. Mastra Agent

An AI agent built with the Mastra framework that provides natural language movie assistance.

#### Features
- Natural language movie search
- Personalized recommendations
- Detailed movie information retrieval
- Conversational interface

#### Installation
```bash
cd agent/mcp
npm install
npm run dev
```

### 3. Mobile App

A React Native mobile application for searching and viewing movie information.

#### Features
- User-friendly movie search interface
- Movie details view with images
- Recommendation browsing
- Responsive design

#### Installation
```bash
cd mobile
npm install
npm start
```

## Prerequisites

- Node.js >= 20.9.0
- Python 3.8+
- TMDb API key (configured in .env file)

## License

ISC

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
