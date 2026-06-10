import io
import os
import subprocess
import sys
from huggingface_hub import InferenceClient # type: ignore
# The OpenAI prompt is defined inside the Generate My Roadmap button logic, as a multiline f-string named 'prompt'.
# To modify the prompt, scroll to the section with 'if generate:' and edit the f-string assigned to 'prompt'.

# If launched via `python file.py`, immediately hand off to Streamlit
# before any Streamlit API calls run in bare mode.
if __name__ == "__main__" and os.environ.get("STREAMLIT_LAUNCHED") != "1":
    env = os.environ.copy()
    env["STREAMLIT_LAUNCHED"] = "1"
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__), "--server.headless", "false"],
        check=True,
        env=env,
    )
    sys.exit(0)

import streamlit as st

HF_MODEL = os.getenv("HF_MODEL", "microsoft/Phi-3-mini-4k-instruct")
FALLBACK_MODELS = [
    "meta-llama/Llama-3.1-8B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
]


def get_hf_token() -> str:
    def _safe_secret_get(key: str) -> str:
        try:
            return st.secrets.get(key, "")
        except Exception:
            return ""

    token = os.getenv("HF_TOKEN", "")
    if not token:
        token = _safe_secret_get("HF_TOKEN")
    if not token:
        token = _safe_secret_get("HF_API_TOKEN")
    if not token:
        token = os.getenv("HF_API_TOKEN", "")
    if not token:
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    return token


@st.cache_resource
def get_inference_client(token: str) -> InferenceClient:
    return InferenceClient(api_key=token)


def _candidate_models() -> list[str]:
    models = [HF_MODEL] + FALLBACK_MODELS
    deduped = []
    for model in models:
        if model and model not in deduped:
            deduped.append(model)
    return deduped


def call_hf_inference(prompt: str, token: str) -> str:
    client = get_inference_client(token)
    last_error = None

    for model_name in _candidate_models():
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                stream=False,
            )

            if completion and completion.choices and completion.choices[0].message:
                content = completion.choices[0].message.content
                if isinstance(content, str) and content.strip():
                    return content.strip()

            last_error = ValueError(f"Unexpected response format for model '{model_name}'.")
        except Exception as e:
            msg = str(e)
            last_error = e
            if "model_not_supported" in msg or "not supported by any provider" in msg:
                continue
            raise

    raise ValueError(
        "No supported model was available for your enabled providers. "
        "Set HF_MODEL in secrets/env to a model available in your HF account/providers. "
        f"Tried: {', '.join(_candidate_models())}. Last error: {last_error}"
    )

# Set normal text font size to 16px (black), header color to blue (bold), and make spacing very tight
st.markdown(
    """
    <style>
    .stMarkdown p {
        font-size: 16px !important;
        color: #222 !important;
        font-weight: normal !important;
        margin-top: 0.05em !important;
        margin-bottom: 0.05em !important;
        line-height: 1.15 !important;
        padding: 0 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #2563eb !important;
        font-weight: bold !important;
        margin-top: 0.2em !important;
        margin-bottom: 0.1em !important;
        padding: 0 !important;
    }
    .stMarkdown > div, .stMarkdown > * {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding: 0 !important;
    }

    /* Keep all left sidebar content readable */
    section[data-testid='stSidebar'],
    section[data-testid='stSidebar'] * {
        font-size: 20px !important;
    }

    /* Explicit widget text targets inside sidebar */
    section[data-testid='stSidebar'] .stSelectbox label,
    section[data-testid='stSidebar'] .stDateInput label,
    section[data-testid='stSidebar'] .stFileUploader label,
    section[data-testid='stSidebar'] .stCheckbox label,
    section[data-testid='stSidebar'] .stTextInput label,
    section[data-testid='stSidebar'] .stSelectbox,
    section[data-testid='stSidebar'] .stFileUploader,
    section[data-testid='stSidebar'] .stDateInput,
    section[data-testid='stSidebar'] input,
    section[data-testid='stSidebar'] textarea,
    section[data-testid='stSidebar'] button,
    section[data-testid='stSidebar'] small,
    section[data-testid='stSidebar'] p,
    section[data-testid='stSidebar'] span,
    section[data-testid='stSidebar'] [data-baseweb='select'] div,
    section[data-testid='stSidebar'] [data-testid='stMarkdownContainer'] p {
        font-size: 20px !important;
    }

    /* Hide uploader size-limit helper text (e.g., 200MB limit line) */
    [data-testid='stFileUploaderDropzoneInstructions'] > div:nth-child(2),
    [data-testid='stFileUploaderDropzoneInstructions'] small {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
from datetime import datetime, timedelta
import datetime as dt
import re

# --- FIELD AND FOCUS AREA DEFINITIONS ---
fields = [
    "Business Analyst",
    "Marketing Specialist",
    "Human Resources Coordinator",
    "Financial Analyst",
    "Software Engineer",
    "AI Engineer",
    "Machine Learning Engineer",
    "Data Analyst",
    "Cybersecurity Specialist",
    "IT Support Specialist",
    "Project Management",
    "IT Director",
    "Executive Team Lead",
    "HR Manager",
    "Data Scientist", 
    "Product Manager" 
       ]

# --- Progressive Step-by-Step Sidebar ---

def generate_roadmap(missing_skills, fast_track=False):
    pass

fields_with_blank = ["-- Select Field --"] + fields + ["Other"]

role_selection = st.sidebar.selectbox("Step 1: Select Your Target Role", fields_with_blank, key="step1_field")

if role_selection == "Other":
    custom_role = st.sidebar.text_input(
        label="Enter your custom target role",
        key="custom_target_role",
        placeholder="Type your custom role and press Enter"
    )
    effective_field = custom_role
    step1_done = bool(custom_role.strip())
else:
    effective_field = role_selection
    step1_done = effective_field.strip() and effective_field != "-- Select Field --" and effective_field != "Other"

 # Removed sidebar debug info
 # (Debug print removed)

resume_text = ""
step2_done = False
if step1_done:
    st.sidebar.markdown("**Step 2: Upload Resume (PDF, DOCX, or TXT)**")
    uploaded_resume = st.sidebar.file_uploader(
        "Upload your resume (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        key="step2_resume"
    )
    if uploaded_resume is not None:
        if uploaded_resume.type == "application/pdf":
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_resume)
                resume_text = " ".join(page.extract_text() or "" for page in pdf_reader.pages)
            except Exception as e:
                st.sidebar.error(f"Could not read PDF: {e}")
        elif uploaded_resume.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                import docx
                doc = docx.Document(uploaded_resume)
                resume_text = " ".join([para.text for para in doc.paragraphs])
            except Exception as e:
                resume_text = uploaded_resume.read().decode("utf-8", errors="ignore")
        step2_done = True



# Step 3: Timeline Start Date (button only after user selects a date)
timeline_start_date = None
step3_done = False
if step1_done and step2_done:
    st.sidebar.markdown("**Step 3: Select a Roadmap Timeline Start Date**")
    today = datetime.today().date()
    # Use session state to track if user has interacted with the date input
    if 'timeline_date_selected' not in st.session_state:
        st.session_state['timeline_date_selected'] = False

    # Reset date-interaction state when role/resume context changes.
    resume_file = st.session_state.get("step2_resume")
    resume_name = getattr(resume_file, "name", "") if resume_file is not None else ""
    timeline_context_signature = f"{effective_field}|{resume_name}"
    if st.session_state.get("timeline_context_signature") != timeline_context_signature:
        st.session_state["timeline_context_signature"] = timeline_context_signature
        st.session_state['timeline_date_selected'] = False
        st.session_state['fast_track'] = False
        st.session_state['fast_track_mode'] = False

    def on_date_change():
        st.session_state['timeline_date_selected'] = True

    timeline_start_date = st.sidebar.date_input(
        label="Timeline Start Date",
        key="timeline_start_date",
        value=today,
        on_change=on_date_change
    )
    # Only show the button after user has interacted with the date picker
    if st.session_state['timeline_date_selected']:
        step3_done = True

    if step3_done:
        fast_track = st.sidebar.checkbox("Select Fast Track", key="fast_track_mode")
        st.session_state['fast_track'] = fast_track
    else:
        fast_track = False
        st.session_state['fast_track'] = False
else:
    fast_track = False
    st.session_state['fast_track'] = False

skillset = ""

step4_done = False
if step1_done and step2_done and step3_done:
    step4_done = True

career_path = None
pace = 5

# Roadmap generation is only triggered by button


# --- AI & LOGIC PLACEHOLDER FUNCTIONS ---
def skills_gap_analysis(current_skills, target_tools):
    # Improved gap analysis: allow partial matches, ignore extra spaces, case-insensitive
    current = [s.strip().lower() for s in current_skills.split(",") if s.strip()]
    target = [t.strip().lower() for t in target_tools.split(",") if t.strip()]
    if not target:
        return 0, []
    matched = set()
    for t in target:
        for c in current:
            if t in c or c in t:
                matched.add(t)
                break
    match_pct = int(100 * len(matched) / len(target)) if target else 0
    missing = [t for t in target if t not in matched]
    return match_pct, missing

def generate_roadmap(missing_skills, pace, fast_track=False):
    # Simulate a roadmap as a list of milestones/sprints
    sprints = []
    start_date = datetime.today()
    sprint_length = 7 if fast_track else 14  # days per sprint
    for i, skill in enumerate(missing_skills):
        sprint = {
            "Task": f"Learn {skill.title()}",
            "Start": (start_date + timedelta(days=i * sprint_length)).strftime("%Y-%m-%d"),
            "Finish": (start_date + timedelta(days=(i + 1) * sprint_length)).strftime("%Y-%m-%d"),
            "Resource": "Learning Sprint"
        }
        sprints.append(sprint)
    # Add a final milestone
    if sprints:
        sprints.append({
            "Task": "Capstone/Project/Certification",
            "Start": sprints[-1]["Finish"],
            "Finish": (datetime.strptime(sprints[-1]["Finish"], "%Y-%m-%d") + timedelta(days=sprint_length)).strftime("%Y-%m-%d"),
            "Resource": "Milestone"
        })
    return sprints

generate = False
# --- OUTPUT SECTION ---

if generate:
    pass

# --- STYLING ---
st.markdown(
    """
   <style>
    .stApp {background-color: #f8fafc;}
    section[data-testid='stSidebar'] {
        background-color: #f1f5f9;
        min-width: 400px !important;
        max-width: 450px !important;
        border: 2px solid #2563eb !important;
        border-radius: 12px !important;
        box-shadow: 0 0 0 2px #2563eb33 !important;
    }
    input, textarea, .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div {
        border: 2px solid #2563eb !important;
        border-radius: 8px !important;
        box-shadow: 0 0 0 1.5px #2563eb33 !important;
    }
    .stButton>button {
        font-weight: 700;
        font-size: 22px !important;
        border: 2px solid #2563eb !important;
        padding: 0.55rem 1.25rem !important;
    }

    /* Streamlit button label is nested; force larger visible text */
    .stButton > button p,
    .stButton > button span {
        font-size: 30px !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
    }

    /* Word download button styling and spacing */
    .stDownloadButton {
        margin-top: 48px !important; /* ~0.5 inch */
    }
    .stDownloadButton > button {
        background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: 1px solid #1e40af !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        letter-spacing: 0.2px !important;
        border-radius: 10px !important;
        min-height: 52px !important;
        padding: 0.75rem 1.2rem !important;
        box-shadow: 0 8px 16px rgba(29, 78, 216, 0.24) !important;
        transition: transform 120ms ease, box-shadow 120ms ease, background-color 120ms ease !important;
    }
    .stDownloadButton > button p,
    .stDownloadButton > button span {
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
    }
    div.stDownloadButton > button,
    div.stDownloadButton > button *,
    div.stDownloadButton > button p,
    div.stDownloadButton > button span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(180deg, #1d4ed8 0%, #1e3a8a 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 10px 20px rgba(30, 58, 138, 0.28) !important;
        transform: translateY(-1px) !important;
    }
    .stDownloadButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 6px 12px rgba(30, 58, 138, 0.24) !important;
    }
    .metric-square, .stMetric {background: #fff !important; border: 2px solid #2563eb !important; border-radius: 8px !important;}

    /* SMART table styling */
    #smart-table table {
        font-family: 'Arial', Times, serif;
        font-size: 12pt;
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 2em;
    }
    #smart-table th, #smart-table td {
        border: 1px solid #444;
        border-style: solid !important;
        padding: 8px 12px;
        text-align: left;
    }
    #smart-table tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    #smart-table th {
        background-color: #e0e7ef;
        font-weight: bold;
    }

    /* FIX: Add spacing before/after numbered sections */
    p, li {
        margin-bottom: 0.75em !important;
    }

    /* Output section headers only (keep body text normal) */
    .block-container [data-testid='stMarkdownContainer'] p > strong:first-child,
    .block-container [data-testid='stMarkdownContainer'] li > strong:first-child,
    .block-container [data-testid='stMarkdownContainer'] li p > strong:first-child {
        color: #2563eb !important;
        font-size: 1.15em !important;
        font-weight: 700 !important;
    }

    .block-container [data-testid='stMarkdownContainer'] p,
    .block-container [data-testid='stMarkdownContainer'] li {
        color: #222 !important;
        font-weight: 400 !important;
    }
  </style>
    """,
    unsafe_allow_html=True
)

if step1_done and step2_done and step3_done:
    _left_spacer, _generate_col, _right_spacer = st.columns([1, 2.6, 1])
    with _generate_col:
        generate = st.button("Generate My Roadmap", use_container_width=True, key="generate_roadmap_btn")
    if generate:
        # Do NOT clear session_state here!
        with st.spinner("Generating your roadmap..."):
            st.markdown("---")
            st.header(f"Your Career Roadmap for {effective_field}")
            # Use persistent values from session_state
            fast_track = st.session_state.get('fast_track', False)
            match_pct = st.session_state.get('match_pct', 0)
            missing_count = st.session_state.get('missing_count', 0)
            salary_value = st.session_state.get('salary_value', 'Unavailable')
            trend_value = st.session_state.get('trend_value', 'Unavailable')
            # Optionally, retrieve missing_skills if you want to show them

            prompt = f"""
                       Target Role: {effective_field}
            Skills: {skillset}
            Focus Areas: {career_path}
            Past Experience (from Resume): {resume_text if resume_text else 'N/A'}
            Start Date: {timeline_start_date}

            Please generate a clear, step-by-step career roadmap for the user with the following sections:

1. Vision Statement: One or two sentences summarizing the user's career vision. 
2. Market Trends & Summary Metrics: Always present this section as a Markdown table with the following columns:

| Metric | Details |
|--------|---------|
| Estimated Salary Range (US) | [AI-generated value, e.g., $120,000–$180,000 (median, varies by region and company)] |
| Demand Trend | [AI-generated value, e.g., High and growing demand—AI/ML Engineer is one of the fastest-growing roles in tech, with continuing talent shortages.] |
| Skill Match | [AI-generated value, e.g., 60–70% (Strong foundation in cloud, DevOps, and Python; moderate exposure to AI/ML.)] |

Use this format for every response, and do not use HTML or lists for the Market Trends & Summary Metrics section—only a Markdown table as shown above.
3. Transferable Skills & Gaps: Always present this section as a Markdown table with the following two columns:

| Transferable Skills | Skill Gaps |
|---------------------|------------|

Each row should pair a transferable skill with a skill gap if possible. Use this format for every response, and do not use HTML or lists for the Transferable Skills & Gaps section—only a Markdown table as shown above.
4. SMART Goals Table: Always present this section as a Markdown table with the following columns, in this exact order and format:

| Specific Goal | Measurable Outcome | Achievable? | Relevant? | Time-bound | Milestone Description |

Each row should be a concrete SMART goal. For the Time-bound column, always include both the Start and Finish date for each goal, using the Start Date selected by the user as the starting point and calculating the Finish date based on the goal's duration. Use this format for every response, and do not use HTML or lists for the SMART table—only a Markdown table as shown above.

5. Certifications: List any certifications required for the target role.

6. Recommended Resources: Always present this section as a Markdown table with the following four columns:

| Resource Type | Name/Title | Description | Link/Example |
|--------------|------------|-------------|--------------|
7. Final Advice: One or two sentences of final advice or encouragement for the user. 

Each row should be a single resource, book, community, or piece of advice, with a brief description and a link or example if available. Use this format for every response, and do not use HTML or lists for the Recommended Resources section—only a Markdown table as shown above.
{''.join([chr(10), '8. Fast Track Insights: The user has selected Fast Track mode. Reduce ALL goal timeline durations in the SMART Goals Table by 30% (e.g., a 10-week goal becomes 7 weeks). Then add a new section titled "Fast Track Insights" with 5 to 7 concise bullet points of actionable strategies the user can use to accelerate their career transition—such as intensive bootcamps, networking shortcuts, high-impact certifications, portfolio projects, or mentorship opportunities specific to the target role.']) if fast_track else ''}
            """
            # Hugging Face API call
            try:
                hf_token = get_hf_token()
                if not hf_token:
                    st.error("Missing Hugging Face token. Add HF_TOKEN (preferred) or HF_API_TOKEN to environment variables/secrets.")
                    st.stop()

                roadmap_md = call_hf_inference(prompt, hf_token)
                st.session_state['roadmap_md'] = roadmap_md
            except Exception as e:
                st.error(f"Hugging Face API error: {e}")

# --- Display and Download Roadmap if available ---
if 'roadmap_md' in st.session_state:
    roadmap_md = st.session_state['roadmap_md']
    import re
    import plotly.express as px
    import pandas as pd
    from dateutil.relativedelta import relativedelta

    # Extract Milestones table from markdown
    milestone_table = None
    milestone_pattern = re.compile(r"(?s)\n5\. Milestones:.*?\n((\|.*?\|\n)+)")
    match = milestone_pattern.search(roadmap_md)
    if match:
        milestone_table = match.group(1)
    milestones = []
    if milestone_table:
        lines = [line.strip() for line in milestone_table.split('\n') if line.strip() and line.strip().startswith('|')]
        if len(lines) > 2:
            headers = [h.strip() for h in lines[0].strip('|').split('|')]
            for row in lines[2:]:
                cols = [c.strip() for c in row.strip('|').split('|')]
                if len(cols) == len(headers):
                    milestones.append(dict(zip(headers, cols)))

    # Compute Start and Finish Dates for each milestone and overwrite Proposed Timeline
    if milestones and 'Proposed Timeline' in milestones[0]:
        base_date = None
        if 'timeline_start_date' in st.session_state:
            base_date = st.session_state['timeline_start_date']
        elif 'timeline_start_date' in locals():
            base_date = timeline_start_date
        else:
            base_date = pd.Timestamp.today().date()
        current_date = pd.to_datetime(base_date)
        for m in milestones:
            m['Start Date'] = current_date.strftime('%Y-%m-%d')
            duration = m['Proposed Timeline'].lower()
            if 'week' in duration:
                num = int(re.search(r'(\d+)', duration).group(1)) if re.search(r'(\d+)', duration) else 1
                finish = current_date + pd.Timedelta(weeks=num)
            elif 'month' in duration:
                num = int(re.search(r'(\d+)', duration).group(1)) if re.search(r'(\d+)', duration) else 1
                finish = current_date + relativedelta(months=num)
            elif 'day' in duration:
                num = int(re.search(r'(\d+)', duration).group(1)) if re.search(r'(\d+)', duration) else 1
                finish = current_date + pd.Timedelta(days=num)
            else:
                finish = current_date + pd.Timedelta(weeks=2)
            m['Finish Date'] = finish.strftime('%Y-%m-%d')
            m['Proposed Timeline'] = m['Start Date'] + ' to ' + m['Finish Date']
            current_date = finish
        df = pd.DataFrame(milestones)
        # Save for Word export
        st.session_state['milestone_table_df'] = df[['Milestone', 'Proposed Timeline']]

        # --- Overwrite the Milestones table in the markdown with the new one ---
        # Rebuild the markdown table with updated Proposed Timeline
        milestone_headers = list(df.columns)
        # Only keep the original columns (not Start/Finish Date)
        orig_headers = [h for h in headers if h in df.columns]
        table_md = '| ' + ' | '.join(orig_headers) + ' |\n'
        table_md += '| ' + ' | '.join(['---'] * len(orig_headers)) + ' |\n'
        for _, row in df.iterrows():
            table_md += '| ' + ' | '.join(str(row[h]) for h in orig_headers) + ' |\n'

        # Replace the old milestone table in roadmap_md with the new one
        roadmap_md = re.sub(r"(?s)(\n5\. Milestones:.*?\n)(\|.*?\|\n)+", r"\1" + table_md, roadmap_md)

    # Remove the entire '5. Milestones' section (header, table, and any text) from the markdown before rendering
    # This will remove everything from the '5. Milestones:' header up to the next numbered section (e.g., '6. Certifications')
    roadmap_md_clean = re.sub(r"(?s)\n5\. Milestones:.*?(?=\n\d+\.)", "\n", roadmap_md)
    # Remove extra blank lines for tighter spacing
    roadmap_md_clean = re.sub(r"\n{3,}", "\n\n", roadmap_md_clean)

    def normalize_section_headers(md_text: str) -> str:
        header_titles = [
            "Vision Statement",
            "Market Trends & Summary Metrics",
            "Transferable Skills & Gaps",
            "SMART Goals Table",
            "Certifications",
            "Recommended Resources",
            "Final Advice",
            "Fast Track Insights",
        ]
        title_pattern = "|".join(re.escape(title) for title in header_titles)
        header_re = re.compile(
            rf'^\s*(\*\*)?(\d+)\.\s*({title_pattern})(\*\*)?\s*[:\-]?\s*(.*)\s*$',
            re.IGNORECASE,
        )

        normalized_lines = []
        for line in md_text.split("\n"):
            match = header_re.match(line)
            if not match:
                normalized_lines.append(line)
                continue

            num = match.group(2)
            title = match.group(3)
            trailing = (match.group(5) or "").strip()
            normalized_lines.append(f"**{num}. {title}**")
            if trailing:
                normalized_lines.append(trailing)

        return "\n".join(normalized_lines)

    roadmap_md_display = normalize_section_headers(roadmap_md_clean)
    # Remove duplicate AI-provided top title/subtitle if present.
    roadmap_md_display = re.sub(
        r"(?im)^\s{0,3}(?:#{1,6}\s*)?(?:your\s+)?career\s+roadmap\s+for\s+[^\n]+\n+",
        "",
        roadmap_md_display,
        count=1,
    )
    # Split inline bullet markers into separate lines for clean markdown lists.
    roadmap_md_display = re.sub(r"\s+•\s+", "\n• ", roadmap_md_display)
    st.markdown(roadmap_md_display)

    # --- Replace with a professional milestone table and Gantt chart ---
    if milestones and 'Start Date' in milestones[0] and 'Finish Date' in milestones[0]:
        st.markdown('## Milestone Timeline (Gantt Chart)')
        try:
            fig = px.timeline(
                df,
                x_start='Start Date',
                x_end='Finish Date',
                y='Milestone Description' if 'Milestone Description' in df.columns else 'Milestone',
                color='Milestone',
                title="Milestone Timeline (Start to Finish)"
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info(f"Could not render timeline chart: {e}")
        st.markdown('### Milestones Table (with Date Ranges)')
        st.dataframe(df[[col for col in ['Milestone', 'Milestone Description', 'Proposed Timeline', 'Resources/Notes'] if col in df.columns]])
    # --- Download Buttons with Markdown Formatting ---
    import docx
    from io import BytesIO
    import markdown2 # type: ignore
    from bs4 import BeautifulSoup # type: ignore

    # Download as Word Doc (convert Markdown to rich text)
    import datetime
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    def roadmap_markdown_to_docx(md_text, target_role=None):
        from docx.shared import Pt, RGBColor
        doc = docx.Document()
        section = doc.sections[0]
        # Set document to landscape
        section.orientation = docx.enum.section.WD_ORIENTATION.LANDSCAPE
        new_width, new_height = section.page_width, section.page_height
        section.page_width = new_height
        section.page_height = new_width
        html = markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables", "smarty-pants"])
        soup = BeautifulSoup(html, "html.parser")
        doc_title = None
        for element in soup.children:
            if element.name == 'h1' and not doc_title:
                doc_title = element.get_text()
                break
        if not doc_title:
            doc_title = "Career Roadmap"
        if target_role:
            doc_title = f"{doc_title} — {target_role}"
        # Title
        title = doc.add_paragraph()
        run = title.add_run(doc_title)
        run.bold = True
        run.font.size = Pt(32)
        run.font.name = "Arial"
        title.alignment = 0
        title.paragraph_format.space_after = Pt(0)
        title.paragraph_format.space_before = Pt(0)
        numbered_section_pattern = re.compile(r"^(\d+)\. ")
        plain_section_pattern = re.compile(
            r"^(Vision Statement|Market Trends\s*&\s*Summary Metrics|Transferable Skills\s*&\s*Gaps|"
            r"SMART Goals Table|Certifications|Recommended Resources|Final Advice|"
            r"Fast Track Insights(?:\s*\(.*\))?)$",
            re.IGNORECASE,
        )
        for element in soup.children:
            text = element.get_text().strip() if hasattr(element, "get_text") else ""
            # Handle markdown like: <p><strong>7. Final Advice</strong> body...</p>
            # so only the header stays blue/bold and body remains normal text.
            if element.name == "p":
                strong_tag = element.find("strong")
                if strong_tag:
                    strong_text = strong_tag.get_text().strip()
                    if numbered_section_pattern.match(strong_text):
                        p = doc.add_paragraph()
                        run = p.add_run(strong_text)
                        run.font.name = "Arial"
                        run.font.size = Pt(18)
                        run.font.color.rgb = RGBColor(47,117,181)
                        run.bold = True
                        p.paragraph_format.space_before = Pt(24)
                        p.paragraph_format.space_after = Pt(6)
                        p.paragraph_format.line_spacing = 1.0

                        body_parts = []
                        for child in element.contents:
                            if child == strong_tag:
                                continue
                            child_text = child.get_text(" ", strip=True) if hasattr(child, "get_text") else str(child)
                            if child_text and child_text.strip():
                                body_parts.append(child_text.strip())
                        body_text = " ".join(body_parts).strip()
                        if body_text:
                            body_p = doc.add_paragraph(body_text)
                            for run in body_p.runs:
                                run.font.name = "Arial"
                                run.font.size = Pt(16)
                                run.font.color.rgb = RGBColor(0,0,0)
                                run.bold = False
                            body_p.paragraph_format.space_before = Pt(0)
                            body_p.paragraph_format.space_after = Pt(0)
                            body_p.paragraph_format.line_spacing = 1.15
                        continue
            # Numbered section headers (blue, bold, larger, with extra space before)
            if numbered_section_pattern.match(text):
                p = doc.add_paragraph()
                run = p.add_run(text)
                run.font.name = "Arial"
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(47,117,181)  # Blue
                run.bold = True
                p.paragraph_format.space_before = Pt(24)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.0
                continue

            # Non-numbered section headers (some model outputs omit numbering)
            if plain_section_pattern.match(text):
                p = doc.add_paragraph()
                run = p.add_run(text)
                run.font.name = "Arial"
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(47,117,181)
                run.bold = True
                p.paragraph_format.space_before = Pt(20)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.0
                continue

            # H2
            if element.name == "h2":
                p = doc.add_paragraph()
                run = p.add_run(text)
                run.font.name = "Arial"
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(47,117,181)
                run.bold = True
                p.paragraph_format.space_before = Pt(20)
                p.paragraph_format.space_after = Pt(6)
                continue
            # H3
            if element.name == "h3":
                p = doc.add_paragraph()
                run = p.add_run(text)
                run.font.name = "Arial"
                run.font.size = Pt(13)
                run.font.color.rgb = RGBColor(0,0,0)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(12)
                continue
            # Lists (bulleted/numbered items in black, normal weight)
            if element.name in ["ul", "ol"]:
                style = "List Bullet" if element.name == "ul" else "List Number"
                for li in element.find_all("li"):
                    p = doc.add_paragraph(li.get_text(), style=style)
                    for run in p.runs:
                        run.font.name = "Arial"
                        run.font.size = Pt(16)
                        run.font.color.rgb = RGBColor(0,0,0)  # Ensure black text
                        run.bold = False
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(4)
                    p.paragraph_format.line_spacing = 1.0
                continue
            # Tables
            if element.name == "table":
                rows = element.find_all("tr")
                if rows:
                    cols = rows[0].find_all(["td", "th"])
                    table = doc.add_table(rows=len(rows), cols=len(cols))
                    table.style = "Table Grid"
                    for i, row in enumerate(rows):
                        cells = row.find_all(["td", "th"])
                        for j, cell in enumerate(cells):
                            cell_obj = table.cell(i, j)
                            cell_obj.text = cell.get_text()
                            for run in cell_obj.paragraphs[0].runs:
                                run.font.name = "Arial"
                                run.font.size = Pt(16)
                                run.font.color.rgb = RGBColor(0,0,0)
                            if i == 0:
                                for run in cell_obj.paragraphs[0].runs:
                                    run.bold = True
                    continue
            # Normal paragraphs (not numbered section headers, not bold, not blue)
            if text:
                if numbered_section_pattern.match(text):
                    continue
                # Treat bold paragraphs starting with dash as bullet points
                if text.strip().startswith('- '):
                    p = doc.add_paragraph(text.strip()[2:], style='List Bullet')
                    for run in p.runs:
                        run.font.name = "Arial"
                        run.font.size = Pt(16)
                        run.font.color.rgb = RGBColor(0,0,0)  # Ensure black text
                        run.bold = False
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(4)
                    p.paragraph_format.line_spacing = 1.15
                else:
                    p = doc.add_paragraph(text)
                    for run in p.runs:
                        run.font.name = "Arial"
                        run.font.size = Pt(16)
                        run.font.color.rgb = RGBColor(0,0,0)
                        run.bold = False
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(6)
                    p.paragraph_format.line_spacing = 1.15
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        return buf

    # Export the same normalized content shown on screen so DOCX matches app output.
    docx_buf = roadmap_markdown_to_docx(roadmap_md_display, effective_field)
    st.download_button(
        label="Download Roadmap as Word Document",
        data=docx_buf,
        file_name=f"career_roadmap_{today_str}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


