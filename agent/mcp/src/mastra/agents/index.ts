import { Agent } from "@mastra/core/agent";
import { MCPClient } from "@mastra/mcp";
import { openai } from "@ai-sdk/openai";

// Use the hardcoded API key and profile from the mcp.json configuration
const apiKey = "58a382f4-573d-4018-b2a7-69ba0a484468";
const profileKey = "noisy-primate-zh17mp";

// Initialize MCP Client with your movie MCP server
const mcp = new MCPClient({
    servers: {
        "moviemcp": {
            command: "cmd",
            args: [
                "/c",
                "npx",
                "-y",
                "@smithery/cli@latest",
                "run",
                "@Arliiii/moviemcp",
                "--key",
                apiKey,
                "--profile",
                profileKey,
            ],
            timeout: 30000, // 30 second timeout
        },
    },
});

// Create agent with access to MCP tools
const movieAgent = new Agent({
    name: "Movie Assistant",
    instructions: `You are a helpful movie assistant that can provide comprehensive movie information and recommendations.

  Your capabilities include:
  - Searching for movies by title, genre, year, or other criteria
  - Getting detailed movie information (plot, cast, ratings, etc.)
  - Providing movie recommendations based on preferences
  - Finding information about actors, directors, and other movie industry professionals
  - Answering questions about movie trivia and facts
  - Helping users discover new movies to watch

  Always use the available movie tools to get the most current and accurate information.
  When providing movie information, be specific and include relevant details like release year, genre, cast, ratings, and plot summaries when available.`,
    model: openai("gpt-3.5-turbo"),
    tools: await mcp.getTools(), // Get all tools from MCP servers
});

export { movieAgent };