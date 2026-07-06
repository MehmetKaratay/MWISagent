# Local Testing via Playground

To interactively chat with the agent and observe its decision-making flow in real-time, you can use the ADK 2.0 Web Playground.

## Launching the Playground

From the root directory of the repository, run:
```bash
make playground
```

This will automatically load the `.env` variables (such as your `GEMINI_API_KEY`) and launch a local web server.

## Using the UI

1. Open your web browser and navigate to the local address output by the command (by default, it binds to `http://localhost:8080`).
2. You will see a chat interface. Type your query (e.g., "What is the weather on Ben Nevis.") into the input box and hit send.
3. **Observing the Flow**: The playground interface streams the agent's thought process. You can click on the expandable tool call logs to see exactly what parameters the agent passed to the skills (such as `check_forecast_issued`) and the raw JSON data the skill returned to the agent before it formulated its final response to you.

---

## Automated Browser Testing
When verifying UI changes or executing interactive tests with automated browser agents, always adhere to the 5-step collision and timeout prevention protocol defined in [specs/playground_testing.spec.md](file:///home/karatay/Repositories/weather/MWISagent/specs/playground_testing.spec.md). This ensures clean background task cleanup, pre-flight server checks, watchdog timers, and strict browser subagent timeout bailouts.
