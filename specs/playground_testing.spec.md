# Playground Automated Testing Specification

This specification defines the mandatory, deterministic 5-step protocol for launching and testing the ADK Web Playground with automated browser subagents to prevent port collisions, UI hangs, and indefinite timeouts.

```yaml
version: "1.0.0"
category: "environment-testing"
target_app: "app"
server_port: 8080
default_url: "http://127.0.0.1:8080/dev-ui/?app=app"
timeouts:
  watchdog_timer_seconds: 60
  server_startup_seconds: 5
  browser_ui_render_seconds: 10
  browser_response_wait_seconds: 30
```

## Mandatory Execution Protocol

When an agent is tasked with launching or verifying the interactive playground via browser automation, it **MUST** execute the following 5 sequential steps:

### 1. Task Cleanup (Collision Prevention)
- **Rule**: Never attempt to start the playground server without verifying port availability.
- **Action**: Invoke `manage_task` with `Action="list"`. Identify any running background server tasks (e.g., `make playground`, `adk web`, or `agents-cli playground`) and terminate them using `Action="kill"`.

### 2. Server Launch
- **Rule**: Start the server in the background inside the sandboxed virtual environment.
- **Action**: Run `make playground` as a background terminal command (`WaitMsBeforeAsync=5000`).

### 3. Pre-Flight Health Check
- **Rule**: Never launch browser automation against an unverified server endpoint.
- **Action**: Schedule a 5-second pause or inspect task logs/run a silent HTTP check (e.g., `curl -I http://127.0.0.1:8080/dev-ui/?app=app`) to verify the server is returning `200 OK`.

### 4. Watchdog Safety Timer
- **Rule**: Prevent agent hang-ups if the browser subagent freezes or loses connection.
- **Action**: Before invoking the browser tool, schedule a one-shot safety timer using `schedule` with `DurationSeconds=60` and `Prompt="Watchdog timer expired: check browser subagent status or abort"`.

### 5. Browser Subagent Execution with Strict Bailouts
- **Rule**: The prompt sent to `browser_subagent` must contain explicit, non-negotiable timeout thresholds.
- **Required Subagent Instructions**:
  - *Navigation*: Go to `http://127.0.0.1:8080/dev-ui/?app=app`.
  - *UI Render Bailout*: If the chat input box does not render within **10 seconds**, abort immediately and report a UI rendering failure.
  - *Action*: Submit the test query (e.g., `"What is the weather on Ben Nevis."`).
  - *Response Wait Bailout*: Wait at most **30 seconds** for the agent's reply to stream. If no reply appears within 30 seconds, abort the task and return the partial output.
```
