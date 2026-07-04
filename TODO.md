# MWIS Agent TODO

## Next time
 * Create MWIS forecast structure reference
 * Improve serve_forecast_to_user skills definition (perhaps)
    - Rename to parse_current_forecast
 * Create CONTEXT.md to explain the overall goal, so agent knows int include scope for interpreting weather features and their impact.
    - Add note to say that we will be fetching forecast from website but in future we may access db directly. The code should be designed to make this swap trivial.
 * Python script to fetch MWIS forecast. Output goes to LLM.
 * Resent AGENTS.md file




## Future
* Refactor python scripts to send data directly instead of through command line (if this is more efficient for LLM)
* Generate the main agent to run on Google Cloud
* Create a front end
   - Interaction with full agent
   - Simple box for ID forecast region (to test features)
   - Simple box for ID forecast date (to test features)



## Draft prompts
