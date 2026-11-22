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

The web page is publicly reachable if deployed. The Student View includes a demonstration practice code and browser-based local saving of student responses, but these features do not provide secure authentication or server-side access controls. The Teacher View does not require authentication. The teacher rubric and review button are visible to anyone with the URL. Do not use with real students, share with a class, or send real student work to the API. The current web interface uses browser text-to-speech. V2 was compared with V1 using selected fictional test cases; results were mixed and remain provisional.

The server only serves the web page, not its Python source. API keys are read from server-side environment variables.

## Refined V2 comparison
The workflow dropdown now includes **V2 refined**, which uses strengthened evidence gathering and rubric-specific safeguards. Original V1 and initial V2 remain available unchanged for before-and-after comparisons. Test with fictional responses only. Results are provisional and require teacher review; prompt refinements do not guarantee accuracy.


## Separate-interface demonstration
`/` selects a view; `/student.html` contains a student-only writing preview; `/teacher.html` retains the original three teacher rubric review workflows. These are separate presentations only, not authenticated roles. The Student View saves responses locally in the browser but does not automatically submit them to the teacher or AI service. The `/api/review` endpoint is still publicly reachable and can incur API charges: do not distribute this public demo to students. Use only fictional data. The Student View includes a demonstration practice code and browser-based response saving, but secure authentication, server-side draft storage, neural TTS, and assessment uploads are not implemented.
