import { Mastra } from "@mastra/core/mastra";
import { createLogger } from "@mastra/core/logger";
import { LibSQLStore } from "@mastra/libsql";
import { movieAgent } from "./agents/index";

export const mastra = new Mastra({
    agents: { movieAgent },
    storage: new LibSQLStore({
        // stores telemetry, evals, ... into memory storage, if it needs to persist, change to file:../mastra.db
        url: ":memory:",
    }),
    logger: createLogger({
        name: "Mastra",
        level: "info",
    }),
});