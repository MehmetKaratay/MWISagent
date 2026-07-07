# MWIS Agent: Interactive Mountain Weather Forecasts

The **MWIS Agent** is an interactive concierge service designed to help users understand complex British mountain weather forecasts. 

## 1. Problem
Traditional weather models are unreliable for mountainous terrain because they rely on smoothed topographical data that misses small mountain passes and local micro-climates. The Mountain Weather Information Service (MWIS) solves this by having expert human meteorologists write highly accurate forecasts. However, these forecasts are published as large chunks of text. Many modern users fail to fully engage with long-form text, instead turning to generic weather apps that falsely claim to offer mountain-specific data. This disconnect has serious safety implications for millions of outings in the UK mountains each year.

## 2. Solution
We built an LLM-powered Concierge Agent to interpret the expert-human written MWIS forecasts. 

Attempting to solve this problem by writing purely deterministic code would result in unmanageable spaghetti logic, given the interdependent variables of weather physics. Instead, the agent uses an agentic workflow: it relies on deterministic Python scripts to accurately fetch the right forecast data, and then uses the LLM to dynamically interpret the text, answer probing questions, and provide interactive safety advice.

## 3. Architecture
The architecture is divided into a secure backend and a lightweight frontend proxy:
- **Backend (Google ADK & Vertex AI)**: The core reasoning agent is built with the Google Agent Development Kit (ADK) and deployed as a remote `ReasoningEngine` on Vertex AI. It uses custom Python skills (`query_region`, `query_date`, `parse_forecast`) to interact with the MWIS API.
- **Frontend (FastAPI & Alpine.js)**: A FastAPI server hosts an Alpine.js web interface. This server acts as a hybrid proxy, routing chat requests securely to the remote Reasoning Engine while also exposing local deterministic scripts for development testing.
- **Caching**: A SQLite database (`mwis_cache.db`) caches fetched forecasts to reduce latency and prevent API rate-limiting.

## 4. Setup Instructions

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/MehmetKaratay/MWISagent.git
   cd MWISagent
   ```
2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
3. Set your `GEMINI_API_KEY` in a `.env` file.
4. Run the local frontend server:
   ```bash
   uv run uvicorn frontend.server:app --host 0.0.0.0 --port 8000 --reload
   ```

### Deploy on Cloud for Development
To deploy the backend agent to Vertex AI Reasoning Engine:
1. Ensure your Google Cloud CLI is authenticated and your project is set.
2. Run the ADK deployment command:
   ```bash
   agents-cli deploy --deployment-target agent_runtime
   ```

### Deploy on Cloud for Production (Cloud Run Frontend)
To set up your own live Cloud Run dashboard:
1. Deploy the containerized frontend to Cloud Run:
   ```bash
   gcloud run deploy mwis-agent-dashboard \
     --source . \
     --command "uv" \
     --args "run,uvicorn,frontend.server:app,--host,0.0.0.0,--port,8080" \
     --region <YOUR_REGION> \
     --allow-unauthenticated \
     --set-env-vars="GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>,AGENT_RUNTIME_ID=<YOUR_REASONING_ENGINE_ID>"
   ```
2. Grant the Cloud Run service account permission to access the Reasoning Engine:
   ```bash
   gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
     --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

## 5. Related Diagrams & Images

### Agent Flow Diagram
![Agent Flow Diagram](/gallery/agent-prototype/agent-flow.png)

*For more screenshots of the frontend interface and development process, see the [Media Gallery](kaggle-writeup/gallery/).*

## 6. Roadmap
The agent currently fetches and interprets the static forecast text. Future versions will include:
- **Weather Physics Skills**: Deterministic scripts mixed with LLM knowledge to explain *why* the weather is behaving a certain way and how it changes at different altitudes.
- **Weather Impact Skills**: Advanced safety advice based on specific weather conditions.
- **Local Knowledge**: Integrating specific geographical knowledge of mountain areas to add localized value to the forecast.
- **Proactive Caching**: Transitioning from a lazy-loaded cache to a scheduled background task (e.g., Cloud Scheduler) to keep forecasts warm.
- **Frontend Enhancements**: Adding hover-over tooltips for forecast items and a dedicated summary panel for the raw forecast discussion.
