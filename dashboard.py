import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(page_title="LLM Eval Harness", layout="wide")

st.markdown("""
    <style>
        .main { font-size: 18px; }
        h1 { font-size: 2.5rem !important; }
        h2 { font-size: 1.8rem !important; }
        [data-testid="stMetricValue"] { font-size: 2.5rem !important; }
        [data-testid="stMetricLabel"] { font-size: 1.2rem !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 LLM Evaluation Harness")
st.subheader("Indian History & Geography — Hallucination & Performance Tracker")

conn = duckdb.connect("eval_results.db")

runs_df = conn.execute("""
    SELECT 
        run_id,
        model,
        COUNT(*) as total,
        SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct,
        ROUND(AVG(similarity_score), 3) as avg_similarity,
        ROUND(100.0 * SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct,
        MIN(timestamp) as timestamp
    FROM runs
    GROUP BY run_id, model
    ORDER BY timestamp DESC
""").df()

questions_df = conn.execute("""
    SELECT * FROM runs ORDER BY timestamp DESC
""").df()

conn.close()

st.header("📊 Overall Performance")
col1, col2, col3 = st.columns(3)
if len(runs_df) > 0:
    latest = runs_df.iloc[0]
    col1.metric("Latest Score", f"{int(latest['correct'])}/{int(latest['total'])}")
    col2.metric("Latest Accuracy", f"{latest['accuracy_pct']}%")
    col3.metric("Avg Similarity", str(latest['avg_similarity']))

st.header("📈 Accuracy Over Runs")
if len(runs_df) > 0:
    chart_data = runs_df[['run_id', 'accuracy_pct']].set_index('run_id')
    st.line_chart(chart_data)

st.header("🔵 Similarity Score Over Runs")
if len(runs_df) > 0:
    sim_data = runs_df[['run_id', 'avg_similarity']].set_index('run_id')
    st.line_chart(sim_data)

st.header("📋 All Runs")
if len(runs_df) > 0:
    st.dataframe(runs_df, use_container_width=True)

st.header("🔍 Per Question Drilldown")
if len(questions_df) > 0:
    run_options = questions_df['run_id'].unique().tolist()
    selected_run = st.selectbox("Select a run to inspect:", run_options)
    filtered = questions_df[questions_df['run_id'] == selected_run][[
        'id', 'question', 'reference_answer', 'model_answer', 'is_correct', 'similarity_score', 'category'
    ]]
    st.dataframe(filtered, use_container_width=True)