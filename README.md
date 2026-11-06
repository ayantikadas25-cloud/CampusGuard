# Campus Deadline Guardian 🎓

**An AI-agent-style college notice understanding and task planning prototype.**

## Problem
College students receive notices about exams, scholarships, internships, registrations and events. Important dates and action items can be missed when notices are long or unclear.

## Solution
Campus Deadline Guardian takes pasted notice text and runs it through a small multi-step agent workflow:
1. **Notice Reader Agent** – splits the notice and detects date-like text.
2. **Deadline Analyzer Agent** – parses dates and labels them as urgent, upcoming, later or needing verification.
3. **Task Planner Agent** – extracts action-oriented sentences into a checklist.
4. **Safety/Evidence Agent** – flags missing dates, tasks or contact details.
5. **Memory** – saves analyzed notices locally in `saved_notices.json`.

## Why this is agentic
The system does more than answer a question: it processes an input, passes the extracted information through specialized stages, creates a task plan, checks for missing evidence, and saves the result for later use.

## Features
- Simple browser-based interface using Streamlit
- Works without an API key or paid AI service
- Detects common date formats
- Creates an action checklist
- Highlights potentially urgent deadlines
- Saves notices locally as JSON
- Warns users when information may be incomplete

## Tech stack
- Python
- Streamlit
- Regular expressions
- JSON local storage
- Python `datetime`

## Run locally
1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

6. Paste the sample notice from `sample_notice.txt` and click **Analyze Notice**.

## Demo input
See [`sample_notice.txt`](sample_notice.txt).

## Limitations
- This is a beginner prototype based on transparent rules, not a large language model.
- Date detection supports common written formats; unusual formats may be missed.
- Action extraction uses keywords and may miss implied tasks.
- Users must verify all dates and instructions against the original official notice.
- Data is stored locally; it is not synced across devices.

## Future improvements
- Add PDF/image notice upload and OCR.
- Add Bengali and English notice support.
- Add calendar export and opt-in reminders.
- Add an LLM-based extraction option with evidence snippets.
- Add user accounts and secure cloud storage.

## Team contributions
Update this section with the actual names and contributions of all four team members.

## Responsible use
The app is an assistant, not an official source. Always confirm deadlines and eligibility from the original college notice.
