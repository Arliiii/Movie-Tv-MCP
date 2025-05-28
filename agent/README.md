# Movie MCP - Mastra Project

A Mastra-based project for building AI agents and workflows with movie information capabilities.

## Description

This project uses the Mastra framework to create and manage AI agents with movie-related capabilities, including movie search, recommendations, and detailed information retrieval.

## Prerequisites

- Node.js >= 20.9.0
- npm or yarn

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd mastra
```

2. Install dependencies:
```bash
cd mcp
npm install
```

## Usage

### Development
```bash
npm run dev
```

### Build
```bash
npm run build
```

## Project Structure

```
mcp/
├── src/
│   └── Mastra/
│       ├── agents/
│       │   └── index.ts
│       └── index.ts
├── package.json
└── README.md
```

## Dependencies

- **@mastra/core**: Core Mastra framework
- **@mastra/libsql**: LibSQL integration for Mastra
- **@mastra/memory**: Memory management for Mastra
- **@ai-sdk/openai**: OpenAI integration
- **zod**: TypeScript-first schema validation

## License

ISC

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
