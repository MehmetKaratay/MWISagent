# MWIS Agent TODO

## In Progress
* Catching layer to minimise API/website-scraping calls

* **Genreate the MVP agent!** P2 is complete but we need a new implemenation plan because of the internet crash forcing computer reboot without LLM interaction to save session.



## Next time

## Before deployment
 * Make sure no `/home/karatay` before going live.
 * Final security assessment
 * License headers on all files

## Future

#### Tiding
* `fetch_specific_forecast` uses `../mocks/` instead of `tests/resources/`.
* Specs into subdirs
* Check: docs and specs for everything?
* Anything in Context that could be extracted to a separate file with clean link to keep context window cleaner?

#### Refactoring
* Should `mwis-regions.csv` and its query scripts be moved to mwis-website dir so other skills have access?
* Out of MWIS region in UK should provide distance and direction to nearest MWIS region. If multiple within a set % of each other, then all options should be provided.

#### Features
* Generate the main agent to run on Google Cloud
* Create a front end
   - Interaction with full agent
   - Simple box for ID forecast region (to test features)
   - Simple box for ID forecast date (to test features)

### Low priority
* Spec files for update-boundaries.py (sp?)

## Far future
* Add Met Office Weather Warnings. See DEV-NOTES.md
* cron job to fetch forecast on a schedule. For now it is fetched when first interacted with.

## Draft prompts

### Toekn Spend
Summarise current state of project and archive unnecessary logs. Keep instructions regarding how you interact with me and how the the project environment is set up; in particular remember how you use `pip` and `uv`. Re-read `~/.gemini/GEMINI.md`, load relevant skills, and ask if you have any questions.`

NOTE: This made the agent forget a lot of how we were working together and I had to remind it of our various 'rules'. Better to do that than to hallucinate. I added the second instruction to try to overcome this barrier.

## tmp

User, on live server: What will the weather be like on Ben Nevis today?

Agent: I'm sorry, I don't have a forecast area code for "WH". The available forecast areas are: * **L**ochaber * **P**erthshire * **SN**owdonia * **C**airngorms * **FP**orfar * **DL**och Lomond & The Trossachs * **W**estern Highlands * **E**astern Highlands Please let me know which of these areas you'd like a forecast for. Do you have any follow-up questions? (e.g. higher/lower elevation, specific part of the region, or 'no' to finish)

Note to coding agent: Those areas aren't MWIS regions. The agent should use query_region.sh to find what region is being referred to.

Why did behaviour change so much between local host and live server?

Agent reply from another session: I'm sorry, I cannot find a forecast for the area code "WH". Please check the area codes available in the MWIS forecast, which typically include areas like: * Southern Scotland (SN) * Lake District (LO) * West Highlands (WK) * East Highlands (EH) * Cairngorms (CG) * Southwest Highlands (SW) * Northwest Highlands (NW) Could you please provide a different area code? Do you have any follow-up questions? (e.g. higher/lower elevation, specific part of the region, or 'no' to finish)
