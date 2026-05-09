import duckdb
import os

def get_db():
    conn = duckdb.connect("eval_results.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER,
            run_id VARCHAR,
            model VARCHAR,
            question VARCHAR,
            reference_answer VARCHAR,
            model_answer VARCHAR,
            is_correct BOOLEAN,
            similarity_score FLOAT,
            category VARCHAR,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return conn

def save_run(run_id, model, results):
    conn = get_db()
    for i, result in enumerate(results):
        conn.execute("""
            INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, [
            i + 1,
            run_id,
            model,
            result["question"],
            result["reference_answer"],
            result["model_answer"],
            result["is_correct"],
            result["similarity_score"],
            result["category"]
        ])
    conn.close()
    print(f"Saved {len(results)} results to database!")

def get_all_runs():
    conn = get_db()
    result = conn.execute("""
        SELECT run_id, model,
        COUNT(*) as total,
        SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct,
        ROUND(AVG(similarity_score), 3) as avg_similarity,
        MIN(timestamp) as timestamp
        FROM runs
        GROUP BY run_id, model
        ORDER BY timestamp DESC
    """).fetchall()
    conn.close()
    return result