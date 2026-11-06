import json
import re
from datetime import datetime, date
from pathlib import Path

import streamlit as st

DATA_FILE = Path("saved_notices.json")

# -----------------------------
# Agent 1: Notice Reader
# -----------------------------
def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [part.strip(" •-\t") for part in parts if part.strip(" •-\t")]

def extract_dates(text):
    """Find common date formats in a notice. Returns unique date strings."""
    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{1,2}\s+(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{4}\b",
        r"\b(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2},?\s+\d{4}\b",
    ]
    found = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    # Keep order while removing duplicates
    return list(dict.fromkeys(found))

# -----------------------------
# Agent 2: Deadline Analyzer
# -----------------------------
def parse_date(date_text):
    formats = [
        "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
        "%d %B %Y", "%d %b %Y", "%B %d %Y", "%B %d, %Y",
        "%b %d %Y", "%b %d, %Y"
    ]
    cleaned = date_text.replace(",", "")
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            pass
    return None

def analyze_deadlines(date_strings):
    results = []
    today = date.today()
    for item in date_strings:
        parsed = parse_date(item)
        if parsed:
            days_left = (parsed - today).days
            if days_left < 0:
                status = "Date may have passed"
            elif days_left <= 3:
                status = "Urgent"
            elif days_left <= 7:
                status = "Upcoming"
            else:
                status = "Later"
            results.append({
                "date_text": item,
                "date": parsed.isoformat(),
                "days_left": days_left,
                "status": status
            })
        else:
            results.append({
                "date_text": item,
                "date": None,
                "days_left": None,
                "status": "Please verify date"
            })
    return results

# -----------------------------
# Agent 3: Task Planner
# -----------------------------
ACTION_WORDS = [
    "submit", "apply", "register", "upload", "download", "pay",
    "attend", "bring", "visit", "complete", "fill", "verify",
    "collect", "contact", "send", "renew"
]

def create_tasks(text):
    tasks = []
    for sentence in split_sentences(text):
        lower = sentence.lower()
        if any(word in lower for word in ACTION_WORDS):
            tasks.append({
                "task": sentence,
                "done": False
            })
    return tasks

# -----------------------------
# Agent 4: Safety / Evidence Checker
# -----------------------------
def check_notice(text, dates, tasks):
    warnings = []
    if len(text.strip()) < 30:
        warnings.append("The notice is very short. Add the complete notice for better analysis.")
    if not dates:
        warnings.append("No clear calendar date was detected. Please check the notice manually.")
    if not tasks:
        warnings.append("No action item was detected. Read the notice carefully and add tasks manually.")
    if re.search(r"\b(contact|office|department|helpdesk)\b", text, re.IGNORECASE) is None:
        warnings.append("No contact/helpdesk detail was detected. Verify where to ask questions.")
    return warnings

def load_saved():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []

def save_record(record):
    records = load_saved()
    records.insert(0, record)
    DATA_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

# -----------------------------
# Streamlit application
# -----------------------------
st.set_page_config(page_title="Campus Deadline Guardian", page_icon="🎓", layout="wide")

st.title("🎓 Campus Deadline Guardian")
st.caption("A student-focused notice reader that turns college notices into deadlines and action checklists.")

with st.sidebar:
    st.header("How it works")
    st.write("1. Paste a college notice.")
    st.write("2. Reader Agent finds dates.")
    st.write("3. Deadline Agent checks urgency.")
    st.write("4. Planner Agent creates tasks.")
    st.write("5. Safety Agent flags missing details.")
    st.info("Prototype note: this version uses transparent Python rules and works without paid APIs.")

tab1, tab2 = st.tabs(["Analyze a Notice", "Saved Notices"])

with tab1:
    notice_title = st.text_input("Notice title", placeholder="Example: Scholarship Application Notice")
    notice_text = st.text_area(
        "Paste the complete notice here",
        height=230,
        placeholder="Paste your college notice, including dates, instructions and contact details..."
    )

    if st.button("Analyze Notice", type="primary"):
        if not notice_text.strip():
            st.warning("Please paste a notice first.")
        else:
            dates = extract_dates(notice_text)
            deadlines = analyze_deadlines(dates)
            tasks = create_tasks(notice_text)
            warnings = check_notice(notice_text, dates, tasks)

            record = {
                "title": notice_title.strip() or "Untitled Notice",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "deadlines": deadlines,
                "tasks": tasks,
                "warnings": warnings,
                "notice_text": notice_text
            }
            st.session_state["latest_record"] = record

    record = st.session_state.get("latest_record")
    if record:
        st.divider()
        st.subheader("Analysis Result")
        st.write(f"**Notice:** {record['title']}")

        left, right = st.columns(2)
        with left:
            st.markdown("### 📅 Detected deadlines")
            if record["deadlines"]:
                for item in record["deadlines"]:
                    st.write(f"**{item['date_text']}** — {item['status']}")
                    if item["days_left"] is not None:
                        st.caption(f"{item['days_left']} day(s) from today")
            else:
                st.write("No date found.")

        with right:
            st.markdown("### ✅ Action checklist")
            if record["tasks"]:
                for i, item in enumerate(record["tasks"]):
                    st.checkbox(item["task"], key=f"task_{i}")
            else:
                st.write("No action items found.")

        st.markdown("### ⚠️ Things to verify")
        if record["warnings"]:
            for warning in record["warnings"]:
                st.warning(warning)
        else:
            st.success("No obvious missing details detected. Still verify the original notice.")

        if st.button("Save this notice"):
            save_record(record)
            st.success("Notice saved on this device.")

with tab2:
    st.subheader("Your saved notices")
    saved = load_saved()
    if not saved:
        st.info("No saved notices yet. Analyze and save a notice first.")
    else:
        for index, item in enumerate(saved):
            with st.expander(f"{item.get('title', 'Untitled Notice')} — {item.get('created_at', '')}"):
                st.write("**Deadlines**")
                if item.get("deadlines"):
                    for deadline in item["deadlines"]:
                        st.write(f"- {deadline['date_text']}: {deadline['status']}")
                else:
                    st.write("No dates detected.")
                st.write("**Tasks**")
                for task in item.get("tasks", []):
                    st.write(f"- {task['task']}")
                st.write("**Original notice**")
                st.text(item.get("notice_text", ""))
