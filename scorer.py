from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_score(model_answer, reference_answer):
    embeddings = model.encode([model_answer, reference_answer])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return round(float(score), 3)