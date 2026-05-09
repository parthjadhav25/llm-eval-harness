import requests
import json
import os 
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv
from database import save_run, get_all_runs
from scorer import semantic_score

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
MODEL = sys.argv[1] if len(sys.argv) > 1 else "llama-3.3-70b-versatile"

def ask_llm(question):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": question}
            ]
        }
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]

def check_answer(model_answer, reference_answer):
    model_lower = model_answer.lower()
    reference_lower = reference_answer.lower()
    if reference_lower in model_lower:
        return True
    if model_lower in reference_lower:
        return True
    for word in reference_lower.split():
        if len(word) > 4 and word in model_lower:
            return True
    score = semantic_score(model_answer, reference_answer)
    if score >= 0.5:
        return True
    return False

with open("test_cases.json") as f:
    test_cases = json.load(f)

run_id = str(uuid.uuid4())[:8]
print(f"Starting run {run_id} with model {MODEL}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 50)

correct = 0
total = len(test_cases)
results = []

for test in test_cases:
    print(f"Q{test['id']}: {test['question']}")
    model_answer = ask_llm(test['question'])
    is_correct = check_answer(model_answer, test['reference_answer'])
    sim_score = semantic_score(model_answer, test["reference_answer"])
    if is_correct:
        correct += 1
        print(f"✓ CORRECT — Model said: {model_answer[:80]}...")
    else:
        print(f"✗ WRONG — Expected: {test['reference_answer']}")
        print(f"  Model said: {model_answer[:80]}...")
    print(f"   Similarity score: {sim_score}")
    print()
    results.append({
        "question": test["question"],
        "reference_answer": test["reference_answer"],
        "model_answer": model_answer,
        "is_correct": is_correct,
        "similarity_score": sim_score,
        "category": test["category"]
    })

print("-" * 50)
print(f"FINAL SCORE: {correct}/{total} correct")
save_run(run_id, MODEL, results)

print("\nAll previous runs:")
for run in get_all_runs():
    print(f"Run {run[0]} | Model: {run[1]} | Score: {run[3]}/{run[2]} | Avg Similarity: {run[4]} | Time: {run[5]}")