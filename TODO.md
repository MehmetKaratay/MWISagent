# MWIS Agent TODO

## Next time
 * Improve serve_forecast_to_user skills definition (perhaps)
    - Work on spec for the full agent
    - Work on forecast_information.md so agent has better understanding of forecast.

 * Carry on with CONTEXT.md to explain the overall goal, so agent knows int include scope for interpreting weather features and their impact.
    - Add note to say that we will be fetching forecast from website but in future we may access db directly. The code should be designed to make this swap trivial.
    - Work on Security rules in particular




## Future
* Refactor python scripts to send data directly instead of through command line (if this is more efficient for LLM)
* Generate the main agent to run on Google Cloud
* Check how we did security on Kaggle course
* Create a front end
   - Interaction with full agent
   - Simple box for ID forecast region (to test features)
   - Simple box for ID forecast date (to test features)

## Far future
* Add Met Office Weather Warnings. See DEV-NOTES.md

## Draft prompts
