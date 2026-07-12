# MWIS Agent TODO

## In Progress


## Next time


## Future

### Tiding
 * `fetch_specific_forecast` uses `../mocks/` instead of `tests/resources/`.
 * Specs into subdirs
 * Check: docs and specs for everything?
 * Anything in Context that could be extracted to a separate file with clean link to keep context  window cleaner?
 * Tidy up local GEMINI.md so it plays nicely with global GEMINI.md
 * Fix depreciation warning that occurs during `make cloud-deploy`
 * `make cloud-deploy` updates the deploy timestamp (possibly by calling helper script)
 * `curl -X POST` as automatic deployment check of live agent

### Agent

 * Format output (Already markdown, but include line breaks in fronts of sections)
 * Short paragraphs for easy reading
 * Summarise the forecast, then give more detail if asked.
 * Focus (mostly) on the variable asked for (eg temp, wind, but briefly mention others)
 * Compare skills (as skill?)
 * Abovid that blanket question! (Do you want a forecast for a specific location, or a comparison of up to 5 regions (e.g., 'Scottish areas')?
 * Any more questions at end, as separate chat msg. Only after a pause to let user ask other qs first.
 * London: result should be "That is not MWIS regions. The nearest region/s is/are: XXXX. Would you like a forecast for one of these?"

#### Human interaction
 * Which day is better?
 * Where should I go in Scotland?
 * Where will I see more sunshine? (Know to load cloud & sunshine fields and anaylise)
 * Give me summary of the weather over Ben Nevis.
 * How cloudy will Ben Nevis be tomorrow?

### Skills
 * If database cannot id a name, check local csv file to see if its there.

### Refactoring
 * Should `mwis-regions.csv` and its query scripts be moved to mwis-website dir so other skills have access?
 * Out of MWIS region in UK should provide distance and direction to nearest MWIS region. If multiple within a set % of each other, then all options should be provided.


### Low priority
 * Spec files for update-boundaries.py (sp?)

## Far future
 * Add Met Office Weather Warnings. See DEV-NOTES.md
 * cron job to fetch forecast on a schedule. For now it is fetched when first interacted with.
 * fuzzy names to allow for mis-spellings. Agent should return "Did you mean X in WH region?"

## Draft prompts

### Token Spend
Summarise current state of project and archive unnecessary logs. Keep instructions regarding how you interact with me and how the the project environment is set up; in particular remember how you use `pip` and `uv`. Re-read `~/.gemini/GEMINI.md`, load relevant skills, and ask if you have any questions.`

NOTE: This made the agent forget a lot of how we were working together and I had to remind it of our various 'rules'. Better to do that than to hallucinate. I added the second instruction to try to overcome this barrier.
