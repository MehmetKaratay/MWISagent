# Mountain Weather Information Service User Agents
**Explore British mountain weather forecasts interactively**

**Project Links:**
- GitHub Repository: [https://github.com/MehmetKaratay/MWISagent](https://github.com/MehmetKaratay/MWISagent)
- Live Agent Dashboard: [https://mwis-agent-dashboard-124959983474.europe-west2.run.app/](https://mwis-agent-dashboard-124959983474.europe-west2.run.app/)
- MWIS Website: [https://mwis.org.uk/](https://mwis.org.uk/)

**Track:** Concierge

## 1. Pitch
The Mountain Weather Information Service (MWIS) produces highly accurate, human-interpreted forecasts that are vital for the safety of millions of outings in the UK mountains each year. Traditional weather models rely on smoothed terrain data, completely missing micro-climates, smaller mountain passes, and the complex physics of air being forced over peaks. Therefore, expert human meteorologists are required to interpret the models and write reliable mountain forecasts.

However, the current MWIS output relies on users reading large chunks of text—a format that many people today struggle to fully engage with. As a result, many mountain goers rely on generic 'weather apps' that falsely claim to offer mountain forecasts, leading to serious safety implications.

Our solution is a Concierge Agent that bridges this gap. By building an interactive frontend connected to a reasoning agent, users can dynamically ask probing questions about the forecast. The agent interprets the expert-written MWIS forecasts using a set of deterministic Python skills, combined with the LLM's natural language understanding, to provide highly customized, interactive safety advice. This ensures that users truly understand the conditions before they head into the mountains.

## 2. Implementation
The project began by building a suite of highly deterministic Python scripts designed to accurately query the MWIS API for specific regions, outing dates, and forecast URLs. Rather than trusting the LLM to guess the forecast parameters, the agent strictly uses these deterministic tools to fetch the exact forecast data.

Once the data is retrieved, the LLM processes it and handles the natural language interaction with the user. To reduce latency, we implemented a SQLite caching layer that stores fetched forecasts, preventing redundant API calls to MWIS.

### Architecture
The backend is built using the Google Agent Development Kit (ADK) and deployed to a remote **Vertex AI Reasoning Engine**.

The frontend is a lightweight Alpine.js web application served by a FastAPI proxy. Deployed as a containerized service on **Google Cloud Run**, this proxy intercepts chat messages from the user interface and securely routes them to the remote Reasoning Engine using the `google-cloud-aiplatform` SDK. This hybrid approach ensures the frontend remains secure, responsive, and decoupled from the heavy agentic reasoning backend.

## 3. Concepts I'm Demonstrating

- **Agent System**: Utilizing the Google ADK to orchestrate complex LLM workflows. The agent dynamically chooses when to trigger specific Python skills (e.g., `query_date`, `query_region`) to fetch the correct data before responding to the user.
- **Antigravity**: Leveraging a strict, 8-phase `GEMINI.md` workflow for the IDE agent. This ensured the AI only wrote code after planning, generating specs, and adhering to strict rules.
- **Security**: Integrating pre-commit hooks, Semgrep code scanning, and an `OAuthJWTValidationMiddleware` to enforce Google OAuth JWT validation on Agent-to-Agent (A2A) endpoints.
- **Deployability**: Containerizing the frontend and backend with Docker, using `uv` for lightning-fast dependency management, and deploying to Google Cloud Run and Vertex AI.
- **Skills**: Developing modular, deterministic Python skills that the agent invokes to interact with external APIs safely.

## 4. Project Journey
I am a hobbyist coder who is comfortable in a variety of programming languages, but this was my very first time coding with an LLM or building an AI Agent. My previous internet-ready code was mostly JavaScript, CodeIgniter, and WordPress.

I approached this project with a strong emphasis on discipline. I created a strict harness by writing a custom `GEMINI.md` file from scratch, alongside open-source skills I discovered during the course. This broke the development process into 8 distinct Phases (P0 to P7). The IDE agent was required to explicitly request permission before changing phases, ensuring atomic, manual git commits and preventing the LLM from making unauthorized sweeping changes.

I adopted a Test-Driven Development (TDD) approach, wrote my skills and `CONTEXT.md` iteratively, and heavily utilized the Code Lab tutorials to implement security features like Semgrep and OAuth validation.

There were challenges along the way—such as the scaffold step breaking my `.venv` while I was working remotely on mobile data, forcing me to rely on `git commit --no-verify` near the deadline. However, this disciplined, agentic coding journey taught me how to effectively harness LLMs to build secure, deployable, and highly interactive applications.
