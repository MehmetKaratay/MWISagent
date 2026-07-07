# Kaggle Write Up Context

This Capstone Project for the Kaggle course "AI Agents: Intensive Vibe Coding with Google".

Capstone requirements: https://www.kaggle.com/competitions/vibecoding-agents-capstone-project/overview

The capstone requires submission of:
 1. Link to live project or GitHub public code
 2. Kaggle Report (kaggle-writeup/report/REPORT.md)
 3. Media Gallery (kaggle-writeup/gallery/)
 4. Public Video on YouTube (kaggle-writeup/video/)
 5. README.txt (kaggle-writeup/README.txt)

This context file will be used to generate the Kaggle Report, README.txt and parts of the Public Video including the voiceover.

## Project details
Use this section complemented by your knowledge of the code base to extract information for writing the Kaggle Report and README.md

### Problem

#### Summary
The MWIS website is increasingly old-fashioned, limiting the reach of our life-saving mountain forecasts.

NOTE: The agent does not work as expected, but the code base and videos demostrate what I've learned so I am still publishing it! I will carry on working on it, but the deadline is too close now. I had to do the capstone project while working away for my main job with only mobile internet access. I am not expecting this to affect the judging; I'm simply exmplaining why the project is unfinished and some of the final few commits are potentially shoddy code.

#### Details
 * Impossible to get reliable mountain weather forecasts purely from weather model output as weather models do not have the required resolution.
 * Terrain is models is smoothed and lowered.
 * The models cannot apply deterministic solutions as the air is not forced high enough into the atmosphere and the model does not know about smaller mountain passes the air may be forced through.
 * The current solution is that humans interpreate weather models output and use their knowledge and experience to write reliable mountain forecasts.
 * This output does not come in a format that the public like to interact with this day, namely reading large chunks of text.
 * Many users then rely on 'weather apps' most of which falsly claim to offer mountain forecasts OR they do not fully engage with the forecast details provided by a human.
 * This has a serious safety implication for millioins of outings in teh UK mountains each year.

## Solution

#### Summary
Create an MWIS agent so people can interact with the forecast dynamically and ask probing questions about it. This will be a highly-secure and constrained interaction frontend on the MWIS website which will look at the expert-human written mountain weather foreacst and interpret it for the user.

#### Details
 * Agent knows how to interpret MWIS forecast using SKILLs
 * This allows agent to interpret, compare, add add value to focecasts.
 * Extra functionality will be added over time, eg forecaster's local knowledge, understanding of weather physics to answer user's question etc.; see roadmap.

## Why Agents
 * Solving this problem using weather models is impossible with current super-computers; they simply do not have the power to resolve the resolution we need.
 * Writing deterministic code to modify model output would turn into spagetti code with many different factors that are all interdependent.
 * An Agentic workflow allows the agent to learn the key concepts and dynamically choose the ones to apply using the LLM.
 * This will bridge the gap between deterministic super-computer model output and our expert-human interpreted forecasts.
 * The agent will allow a very interactive session for the user, making them understand and remember the forecast significantly better.
 * In turn, this will improve the mountain goer's plans and safey when out.
 * We will get more people using the MWIS forecasts ans spend time on our website.

## Project journey/history
 * I have never coded with an LLM or AI Agent before. The only internet-ready code I have every published as been javascript, CodeIgnitre php website and WordPress websites.
 * I am comfortable in a variety of programming languages.
 * I am a hobby code, but have always taken tdd, good commit message and security as seriously as I can. I brought this approach over to my agentic coding.
 * I started this project by working an an efficient harness. This is mostly based on my GEMINI.md file open-source skills I discovered while doing the coures.
   - My GEMINI.md files is set up into 8 distinct _Phases_
      0. P0: Project generation
      1. P1: Planning features
      2. P2: Spec generation
      3. P3: Code generation
      4. P4: Debugging
      5. P5: Refactoring
      6. P6: Deployment
      7. P7: Environment setup
   - Each Phase has specific
      * Trigger
      * Goal
      * Rules (Allowed and not allowed)
      * Skills to use
      * A global rule that says to remove from context window when Phase changes
  - The Agent must explicity request permission to change phasse.
  - For the most part this works well. Every now and then the agent forgets, and that's a cue for me to tell it to condese it's context and to reread the rules.
  - In hindsighte a separate PX: Docs would have worked better. This was part of Code genreration but the model kept needing manual prompting.
  - I had all of the definitions in one file. I plan to put each phase in its own file and use GEMINI.md simply as a guide to which files there are the trigger for laoding them.
  * I then thought hard about the architecture, project structure and specificlly the skills I would have to write.
  * I frequently commited to git, trying to keep context relevant and atomic. I did not allow code generation on files which were already modified to make it easy to fix agent mistakes.
    - Almost all my commits were manual so the LLM didn't commit something I wasn't happy with. The LLM suggested well-formatted commit messages using `git-commit-formatter` skill.
  * I started out by writing skills and CONTEXT.md manually, but soon realised telling the agent what I want and then reviewing and eding what it wrote was more efficieint.
  * Once I had the skills I needed, I then worked on security, mostly by adapting the Code Lab tutorials. I also asked the agent what I was missing and what I should consider adding. This made my securty more robust.
    - Precommit linting
    - Semgrep checks (this caught code a few times)
    - A security skills (as suggested in tutorial)
    - Full test suite for security
    - Activly asking agent if security is being met (occasionally the answer as no! with an apology.)
  * I then adapted the Code Labs for creating the backend agent
    - The flow includes nodes that do not do anything for now but will be used in future versions of the agent.
  * While this was happenign I realised I needed to work on the Kaggle Write up and other bits for submission. I did this in parallel to the agent doing its thing.
  * I then worked on the front end.
  * As I was approaching the deadline, the scaffold step broke my `.venv` and on my mobile data I didn't have the download bandwith to set it up agian. I reluctently had to use `git commit --no-verify` after that. This went against my insticnts, but the code in that directory was already verified and did not chagne from this point onwards.







