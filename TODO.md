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
