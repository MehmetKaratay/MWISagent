# MWIS Agent

## Note for GEMINI
This document is a draft items with [[double square brackets]] are TBC.

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

The MVP should use only skills from the `skills-mwis-website` folder and the Coding Skills. This means: 
  * Read the skills in `skills-mwis-website` folder
  * Read the `CONTEXT.md` file
  * Read the `~/.gemini/GEMINI.md` file
  * Identify what needs to be done to create the MVP
  * Implement the MVP using the tdd cycle and clean code principles, etc. 

### Architecture

#### Backend
 * FastAPI
 * Python 3.10

#### Frontend
 * Alpine.js

## Future goals
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
   - **Does not currently exist.**
   - These live inside the MWISagent project folder in the `secure-skills` folder and are mentioned in `secure-skills/SKILL.md`
3. Core skills — MWIS website
   - These live inside the MWISagent project folder in the `MWISagent/skills-mwis-website` folder.
   - They explain the structure of the MWIS company and its offerings
   - They do not explain the physics or impact of weather.
4. Core skills — Weather interpretation
   - **Does not currently exist.**
   - These skills will explain the physics of weather.
   - The agent will use this skill to provide a finer grain interpretation of the forecast for a specific location within the forecast region.
   - Will use a mix of deterministic python scripts and LLM understanding.
5. Core skills — Weather impact
   - **Does not currently exist.**
   - These skills will explain the impact of weather on mountain safety.
   - The agent will use this skill to provide mountain safety advice based on the weather conditions.
   - This will be mostly based on LLM understanding.

## Component Inventory
- **Forecast Area Query**: `skills-mwis-website/identify_forecast_area/scripts/query_region.py` (determines region from location name, coords, or grid reference).
- **Date Query**: `skills-mwis-website/identify_outing_date/scripts/query_date.py` (resolves query dates/ranges to MWIS codes).
- **Fetch Specific Forecast URL**: `skills-mwis-website/fetch_specific_forecast/scripts/query_url.py` (resolves region code/name to MWIS URL).
- **Forecast Fetcher**: [[Provide script name/path if exists, e.g., fetch_mwis_forecast.py]]

## Security & Input Validation Controls
- **Input Filtering**: [[Explain input validation strategy, e.g., Pydantic schemas, character length limits, regex filtering]]
- **Prompt Injection Mitigations**: [[Explain prompt injection strategy, e.g. strict system instructions, separation of user input from instructions, sanitization]]

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

## Google Cloud Deployment
- **Hosting Service**: [[Specify GCP hosting, e.g., Cloud Run for backend, Cloud Storage for frontend static files]]
- **Authentication / IAM**: [[Specify backend authentication or access rules if needed]]

