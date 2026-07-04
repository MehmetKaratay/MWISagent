# MWIS Agent TODO

## Next time
 * Create MWIS forecast structure reference
 * Improve get_current_forecast skills definition (perhaps)
    - Rename to parse_current_forecast
 * Create CONTEXT.md to explain the overall goal, so agent knows int include scope for interpreting weather features and their impact.
    - Add note to say that we will be fetching forecast from website but in future we may access db directly. The code should be designed to make this swap trivial.
 * Python script to fetch MWIS forecast. Output goes to LLM.




## Future
* Generate the main agent to run on Google Cloud
* Create a front end
   - Interaction with full agent
   - Simple box for ID forecast region (to test features)
   - Simple box for ID forecast date (to test features)



## Draft prompts

### forecast_source → fetch_forecast

change forecast_sources to be fetch_forecast. Use the url provided by [get_forecast_url.py](file;file:///home/karatay/Repositories/learning/ai/MWISagent/skills-mwis-website/forecast_source/scripts/get_forecast_url.py) to fetch the live MWIS forecast. Create a copy of what you receive to use for tests as the live forecast will keep changing.

The forecast you fetch will contain three forecast days and an outlook. Each day will contain, in order:
 - UK Summary (first day only)
 - Region Summary (first day only)
 - Wind headline
 - Wind details (may be empty)
 - Rain headline
 - Rain deatils (may be empty)
 - Cloud headline
 - Cloud details
** THIS SHOULD BE IN A SKILL AS REFERENCE **


The result of this forecast will be passed to the LLM. Output the forecast as an LLM, paying special attention to divide the forecast by date (YYYY-MM-DD) and ("outlook").
