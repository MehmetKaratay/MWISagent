# Development Notes

This file is to record reserach for on how to implement features in future. This file will go into more detail than TODO.md but the items mentioned here will ideally be summarised in TODO.md.

## Met Office Weather Warnings

Consider creating (or finding) a MCP server.

Extra research suggests that the answer below may not give access to weather warnigns, only forecasts. If that's the case I may need to create my own MCP server wrapper for the Met Office API, which is free for low-level use. With local memory (if that's a thing) we could check for weather warnings once per hour and remember the results for all future calls.

### Chats
Gemini chat here: https://gemini.google.com/app/ae76611113686a54

### AI Research
You can access official Met Office weather forecasts and severe weather warnings for the UK using AI via Model Context Protocol (MCP) servers provided by developers kaihendry and MCPBundles.

These servers—such as uk-weather-mcp-via-skill  or the unified UK Environmental Intelligence server —allow your AI agent to query specific locations for data. While the base Met Office Weather DataHub tool focuses on standard hourly and 7-day spot forecasts, severe impacts and flood hazards are usually handled in tandem with the Environment Agency Flood Monitoring MCP Server.

**How to Configure and Run**

1. **API Keys**: You will need to obtain a free or paid API key from the Met Office Weather DataHub to unlock forecast querying.Setup: Add the MCPBundles server URL (e.g., https://mcp.mcpbundles.com/bundle/met-office) to your MCP client configuration (such as Claude Desktop, Cursor, or VS Code) .Alternatively: Deploy the Python-based kaihendry/uk-weather-mcp-via-skill via stdio, ensuring you set the MET_OFFICE_API_KEY environment variable in your configuration.Execution: Once connected, prompt your AI assistant using latitude/longitude or placenames .Understanding Warning SeveritiesWhen the server fetches UK warnings, the Met Office categorizes them into three distinct severity levels:Yellow: Be aware of a range of weather situations; read the content to determine how it impacts you.Amber: Increased likelihood of severe impacts (disruptions to travel, potential risk to life/property).Red: Dangerous weather expected with risk to life and widespread property damage; take action immediately.Further Exploration: Additional Environmental and Meteorological AI ToolsAccess the UK Weather MCP Server by kaihendry directly to view its code and automated Github actions testing suite .View the [Environment Agency Flood Monitoring MCP Server] listing to cross-reference UK flood alerts with standard weather forecasts.Explore community implementations and add-on skills via the Met Office Weather DataHub & Skill landing page.If you can tell me the specific location or postcode you want to track, I can help you set up the correct latitude and longitude query strings for the MCP client.
