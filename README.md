# Accessible Assessment Reader + AI Rubric Review

Educational prototype using fictional student writing only. Not approved for actual student records or classroom deployment.

## Deploy on Render (Python web service)

- Connect your private GitHub repository to Render.
- Runtime: Python
- Build command: `python -m compileall -q app.py`
- Start command: `python app.py`
- Set environment variable `OPENAI_API_KEY` in Render dashboard, never in GitHub.
- Optional: `OPENAI_MODEL=gpt-4o-mini`.
- Render supplies `PORT` automatically.

## Local test (optional)

`OPENAI_API_KEY=... python app.py` then open http://localhost:8000.

## Important limitations

The web page is publicly reachable if deployed, and this version has **no teacher authentication, student codes, save/resume, or server-side access controls**. The teacher rubric and review button are visible to anyone with the URL. Do not use with real students, share with a class, or send real student work to the API. The current web interface uses browser text-to-speech. V2 includes a two-step LLM process but must still be tested against the V1 samples.

The server only serves the web page, not its Python source. API keys are read from server-side environment variables.

## Refined V2 comparison
The workflow dropdown now includes **V2 refined**, which uses strengthened evidence gathering and rubric-specific safeguards. Original V1 and initial V2 remain available unchanged for before-and-after comparisons. Test with fictional responses only. Results are provisional and require teacher review; prompt refinements do not guarantee accuracy.
