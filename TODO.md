# MWIS Agent TODO

## In Progress
* Catching layer to minimise API/website-scraping calls

## Next time
 * Improve serve_forecast_to_user skills definition (perhaps)
    - Work on spec for the full agent
    - Work on forecast_information.md so agent has better understanding of forecast.

## Future

* Generate the main agent to run on Google Cloud
* Check how we did security on Kaggle course
* Create a front end
   - Interaction with full agent
   - Simple box for ID forecast region (to test features)
   - Simple box for ID forecast date (to test features)

### Low priority
* Spec files for update-boundaries.py (sp?)

## Far future
* Add Met Office Weather Warnings. See DEV-NOTES.md

## Draft prompts

### Toekn Spend
Summarise current state of project and archive unnecessary logs. Re-read `~/.gemini/GEMINI.md`, load relevant skills, and ask if you have any questions.`

NOTE: This made the agent forget a lot of how we were working together and I had to remind it of our various 'rules'. Better to do that than to hallucinate. I added the second instruction to try to overcome this barrier.
