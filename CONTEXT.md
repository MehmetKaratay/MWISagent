# MWIS Agent

## Note for GEMINI
This document is a draft items with [[double square brackets]] are TBC.

> [!IMPORTANT]
> Before starting any new task, scan the `specs/` directory to identify the relevant feature requirement. Use these specs as the primary source of truth for implementation logic. If a requirement is unclear, ask the user to clarify the spec before proceeding.

## Documentation Responsibility Divide
To avoid context rot, the project's documentation has a strict division of responsibility:
- **`CONTEXT.md`**: Guide the "how" and "why" the agent should work (architectural structure, developer paved roads, integration data-flows, deployment boundaries).
- **`specs/` (Spec Files)**: Explain the "what" to the agent (exact parameter formats, logic schemas, verification requirements, security checks, dependency lists). Do not store implementation specifics or validation details in `CONTEXT.md`.

## Goal
Create an agent that reads MWIS forecasts and interpretation of them for a given date and location. The agent will be used to provide mountain weather information to users on an interactive website.

## MVP
The agent uses its "SKILL Categories" to identify the forecast url, the date, the location, fetch the forecast and present them to the user along with a link to the full forecast. The user interacts with the agent through a front end. Both agent and front end will be hosted on Google Cloud.

Keep as much of the project determistic using python scripts as possible to ensure reliability. LLMs should be used to provide extra information and answers to user questions.

For elements that cannot be provided deterministically the LLM can use its knowledge to provide extra information, but it must make it clear the the LLM can and does make mistakes. The skills should be written so that they can be used by the LLM to provide extra information.

The MVP will include an agent and a front end to provide an interactive experience for the user through a simple web interface which includes:
 * To keep in final product
   - A box to chat with the agent
   - A seperate field that always shows the forecast region and date the forecast is being provided for.
   - Modern, sleek design
 * To be used in development
   - A dialog where a user can input a location and see the direct output of `query_region.py`
   - A dialog where a suser can input a date and see the direct output of `query_date.py`

Security is a high priority. We want to minimise security leaks and make the agent secure against attacks, including prompt injection.

### Architecture

#### Backend
 * FastAPI
 * Python 3.10

#### Frontend
 * Alpine.js

## Future goals
These are mentioned so you can plan ahead for their implementation and design the project architecture accordingly.

* Mountain weather understanding, using extra SKILLS for guidance, so LLM can answer the users questions about, but not limited to:
  - Why the weather is the way it is
  - What the weather will be like higher or lower on the mountain
  - General mountain safety advice based on the weather conditions
* Front end improvements
  - A seperate summary showing the weather forecast the discussion is based on
  - The ability to hover over forecast items to get more detailed information

## SKILL Categories
Skills are dividing into categories to make it easier to identify and use skills.

1. Coding skills
   - These are the skills used to generate the code in the MWIS Agents project folder.
   - These live outside the MWISagent project folder and are mentioned in `~/.gemini/GEMINI.md`
   - They explain code-architeture, writing spec files, clean code, tdd cycle, etc.
2. Security skills
   - These live inside the MWISagent project folder in the `./agents/skills/security` folder.
   - They explain the security policies and practices that should be followed when developing the MWIS Agent.
3. MWIS website
   - These live inside the MWISagent project folder in the `./agents/skills/mwis-website` folder.
   - They explain the structure of the MWIS company and its offerings
   - They do not explain the physics or impact of weather.
4. Weather Physics
   - **No skills in the `./agents/skills/weather-physics` folder currently exist.**
   - These skills will explain the physics of weather.
   - The agent will use this skill to provide a finer grain interpretation of the forecast for a specific location within the forecast region.
   - Will use a mix of deterministic python scripts and LLM understanding.
5. Weather impact
   - **No skills in the `./agents/skills/weather-impact` folder currently exist.**
   - These skills will explain the impact of weather on mountain safety.
   - The agent will use this skill to provide mountain safety advice based on the weather conditions.
   - This will be mostly based on LLM understanding.
6. Local knowledge
   - **No skills in the `./agents/skills/local-knowledge` folder currently exist.**
   - These skills will be used to provide local knowledge about specific mountain areas.
   - The agent will use this skill to provide local knowledge about specific mountain areas to be able to add more value to the forecast.


## Component Inventory
- **Forecast Area Query**: `skills-mwis-website/identify_forecast_area/scripts/query_region.py` (determines region from location name, coords, or grid reference).
- **Date Query**: `skills-mwis-website/identify_outing_date/scripts/query_date.py` (resolves query dates/ranges to MWIS codes).
- **Fetch Specific Forecast URL**: `skills-mwis-website/fetch_specific_forecast/scripts/query_url.py` (resolves region code/name to MWIS URL).
- **Forecast Fetcher**: `skills-mwis-website/fetch_specific_forecast/scripts/parse_forecast.py` (fetches/parses forecast HTML to JSON).


## Security & Input Validation Controls
All inputs, sanitization logic, and prompt isolation schemas are detailed in the [Security Specification](file:///home/karatay/Repositories/weather/MWISagent/specs/security.spec.md).


## Core Paved Roads
1. **Tool Input Validation**: All tool parameters must validate against strict Pydantic schemas.
2. **No Shell Execution**: Never use raw shell execution tools unless approved by `hooks.json`.
3. **Pre-Commit Remediation Loop**: If git commit fails due to pre-commit hook violations (e.g. Semgrep), treat as refactoring, apply fixes, verify with tests, and re-commit.

## Data Flow & Architecture Pipeline
```
[User Input] ──> [Frontend (Alpine.js)] ──> [FastAPI Backend]
                                                    │
                                                    ▼
                                         [LLM Processor /Agent]
                                         - extract region to pass to query_region.py
                                         - extract date to pass to query_date.py
                                                    │
                                                    ▼
                                         [Deterministic Python Scripts]
                                         - query_region.py
                                         - query_date.py
                                         - query_url.py
                                                    │
                                                    ▼
                                          [LLM Processor / Agent]
                                                    │
                                                    ▼
                                              [User Response]
```

## Caching & State
- **Conversation State**: The individual chat conversations will be stateless.
- **Caching Layer**: A backend caching layer will cache fetched forecasts so multiple conversations can refer to the same forecast without re-fetching. Forecasts are fetched once daily at 5:00 PM (after new forecasts are issued).

## Google Cloud Deployment
- **Hosting Service**: Specific GCP hosting services will be finalized later.


## Environment & Tooling Setup
Local linters, custom security scanners (Semgrep), and pre-commit hook policies are detailed in the [Security Specification](file:///home/karatay/Repositories/weather/MWISagent/specs/security.spec.md).

### Local Environment Setup
Instructions on setting up Python versions, repository dependencies, ADK agent installation, and testing commands are detailed in [env_setup.md](file:///home/karatay/Repositories/weather/MWISagent/docs/env_setup.md). For automated evaluation setup, gcloud authentication requirements, and handling API rate limits (such as Free Tier 429 Quota errors), see [evaluation.md](file:///home/karatay/Repositories/weather/MWISagent/docs/evaluation.md#troubleshooting--environment-setup). For local interactive UI testing and automated browser verification protocols, see [playground.md](file:///home/karatay/Repositories/weather/MWISagent/docs/playground.md) and [playground_testing.spec.md](file:///home/karatay/Repositories/weather/MWISagent/specs/playground_testing.spec.md).

> [!NOTE]
> The `GEMINI_API_KEY` is always configured and present in the local `.env` file for this project. It is used for all API interactions, including the ADK evaluation judge.
