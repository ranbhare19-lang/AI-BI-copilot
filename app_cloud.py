import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import duckdb
import os

load_dotenv()
client = OpenAI()

st.set_page_config(page_title="AI BI Co-Pilot", page_icon="🧭", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800;900&display=swap');
    .stApp { background: #0A0D12; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 3.5rem; max-width: 780px; }
    .hero-title { font-size: 3.6rem; font-weight: 900; letter-spacing: -2px; color: #3FEFB2; margin-bottom: 4px; line-height: 1; }
    .hero-sub { color: #9BA7B2; font-size: 1.3rem; margin-bottom: 14px; font-weight: 400; }
    .badge { display: inline-block; background: rgba(29,158,117,0.12); color: #3FEFB2;
        border: 1px solid rgba(63,239,178,0.3); padding: 6px 16px; border-radius: 20px;
        font-size: 0.9rem; font-weight: 600; margin-bottom: 26px; }
    div[data-testid="stTextInput"] input { background: #12161D; border: 1px solid #263039; border-radius: 12px;
        padding: 16px; font-size: 1.2rem; color: #E6EDF3; }
    div[data-testid="stTextInput"] input:focus { border-color: #1D9E75; box-shadow: 0 0 0 3px rgba(29,158,117,0.18); }
    div[data-testid="stTextInput"] label { font-size: 1.1rem; color: #C9D1D9; }
    .stButton>button { background: #1D9E75; color: white; border: none; border-radius: 10px;
        padding: 0.65rem 2rem; font-weight: 700; font-size: 1.1rem; }
    .stButton>button:hover { background: #17805f; color: white; }
    section[data-testid="stSidebar"] { background: #0C1016; border-right: 1px solid #1A222C; }
    section[data-testid="stSidebar"] .stButton>button { background: #141A22; border: 1px solid #232D38; color: #C9D1D9;
        text-align: left; font-weight: 500; width: 100%; font-size: 1rem; }
    section[data-testid="stSidebar"] .stButton>button:hover { border-color: #1D9E75; color: #3FEFB2; background: #12201A; }
    h3 { color: #E6EDF3 !important; font-weight: 700; font-size: 1.5rem; }
    div[data-testid="stMetricValue"] { color: #3FEFB2; font-size: 3.6rem; font-weight: 900; }
    div[data-testid="stMetricLabel"] { color: #9BA7B2; font-size: 1.2rem; }
    div[data-testid="stMetric"] { background: #12161D; border: 1px solid #1E2530; border-radius: 16px; padding: 24px 28px; }
    .footer { color: #4A5560; font-size: 0.85rem; text-align: center; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

DEMO_EXAMPLES = [
    "How many users are inactive?",
    "Average listening hours by subscription type",
    "Which country has the most users?"
]


def set_question(q):
    st.session_state["question"] = q


def question_to_sql(question, columns):
    prompt = f"""You are a SQL expert. The data is in a table named 'data' with these columns:
{columns}

Write a single DuckDB SQL query that answers the user's question. Use LIMIT not TOP.
Prefer LIKE with wildcards for text matching so partial names still match.
When matching multi-word text, put % between the words (e.g. '%hip%hop%') so hyphens or spaces do not cause a miss.
Return ONLY the SQL query, no explanation, no markdown, no backticks.

User question: {question}
"""
    resp = client.chat.completions.create(
        model="gpt-5.5",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()


def suggest_followups(question, columns):
    prompt = f"""The data has columns: {columns}
Based on the question just asked, suggest exactly 3 short follow-up questions a
business analyst might ask next. Return them as 3 plain lines, no numbering.

Question just asked: {question}
"""
    resp = client.chat.completions.create(
        model="gpt-5.5",
        messages=[{"role": "user", "content": prompt}]
    )
    lines = [l.strip("-• ").strip() for l in resp.choices[0].message.content.strip().split("\n") if l.strip()]
    return lines[:3]


def is_safe_sql(sql):
    lowered = sql.lower().strip()
    forbidden = ["drop", "delete", "update", "insert", "alter", "truncate", "create", "exec", "merge"]
    if not lowered.startswith("select"):
        return False
    return not any(word in lowered for word in forbidden)


def run_sql_csv(sql, df):
    result = duckdb.query_df(df, "data", sql).to_df()
    return list(result.columns), [tuple(r) for r in result.values]


# ---- Sidebar ----
with st.sidebar:
    st.markdown("### 🧭 Settings")
    mode = st.radio("Data source", ["Demo: Spotify data", "Upload your own CSV"])
    if mode == "Demo: Spotify data":
        st.caption("Explore 50,000 Spotify subscription records. Ask anything in plain English.")
        st.divider()
        st.markdown("**Try an example**")
        for ex in DEMO_EXAMPLES:
            st.button(ex, key=f"ex_{ex}", on_click=set_question, args=(ex,))
    else:
        uploaded = st.file_uploader("Upload a CSV", type="csv")
        st.caption("Ask questions about your own data. Nothing is stored.")

# ---- Load the active dataframe ----
df = None
if mode == "Demo: Spotify data":
    if os.path.exists("spotify_demo.csv"):
        df = pd.read_csv("spotify_demo.csv")
else:
    if uploaded is not None:
        df = pd.read_csv(uploaded)

# ---- Main ----
st.markdown('<p class="hero-title">AI BI Co-Pilot</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Ask a business question in plain English. The AI writes the SQL and runs it live against real data.</p>', unsafe_allow_html=True)

if df is not None:
    cols = ", ".join(df.columns)
    st.markdown(f'<span class="badge">● {len(df):,} rows loaded</span>', unsafe_allow_html=True)
    with st.expander("Preview the data"):
        st.dataframe(df.head(), use_container_width=True)
else:
    cols = None
    if mode == "Upload your own CSV":
        st.info("Upload a CSV in the sidebar to begin.")

question = st.text_input("Your question", key="question", placeholder="e.g. How many users are inactive?")

if st.button("Get Answer", key="get_answer_btn"):
    if not question:
        st.warning("Type a question first, or click an example in the sidebar.")
    elif df is None:
        st.warning("Load the demo or upload a CSV first.")
    else:
        with st.spinner("Writing SQL and querying the data..."):
            sql = question_to_sql(question, cols)
            if not is_safe_sql(sql):
                error = "Blocked: only read-only SELECT queries are allowed."
                columns, rows = None, None
            else:
                try:
                    columns, rows = run_sql_csv(sql, df)
                    error = None
                except Exception as e:
                    columns, rows, error = None, None, str(e)

        st.markdown("### Answer")
        if error:
            st.error(f"The query could not run: {error}")
        elif rows is not None and len(rows) == 1 and len(columns) == 1:
            val = rows[0][0]
            col_name = columns[0].lower()
            money_words = ["salary", "amount", "price", "revenue", "cost", "pay", "usd", "income"]
            is_money = any(w in col_name for w in money_words)
            if val is None or (isinstance(val, float) and pd.isna(val)):
                st.metric(columns[0], "No matching data")
            elif isinstance(val, (int, float)):
                st.metric(columns[0], f"${val:,.0f}" if is_money else (f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"))
            else:
                st.metric(columns[0], val)
        elif rows is not None:
            result_df = pd.DataFrame(rows, columns=columns)
            st.dataframe(result_df, use_container_width=True)
            numeric_cols = result_df.select_dtypes(include="number").columns.tolist()
            text_cols = [c for c in result_df.columns if c not in numeric_cols]
            if len(result_df) > 1 and len(numeric_cols) >= 1 and len(text_cols) >= 1:
                chart_df = result_df.set_index(text_cols[0])[numeric_cols]
                chart_type = st.radio("Chart", ["Bar", "Line", "Area"], horizontal=True, key="chart_type")
                if chart_type == "Bar":
                    st.bar_chart(chart_df)
                elif chart_type == "Line":
                    st.line_chart(chart_df)
                else:
                    st.area_chart(chart_df)

        with st.expander("See the SQL the AI wrote"):
            st.code(sql, language="sql")

        if not error:
            st.markdown("**You might also ask:**")
            try:
                for f in suggest_followups(question, cols):
                    st.button(f, key=f"fu_{f}", on_click=set_question, args=(f,))
            except Exception:
                pass

st.markdown('<p class="footer">Built by Charulata Ranbhare · Python · OpenAI · SQL Server · Streamlit</p>', unsafe_allow_html=True)