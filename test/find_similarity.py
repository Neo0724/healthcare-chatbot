from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = "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"


embeddings_model = HuggingFaceEmbeddings(
    model_name="abhinand/MedEmbed-base-v0.1"
)

symptoms = "frequent urination, urgency, burning urination, cloudy urine, foul-smelling urine, lower abdominal pain, fever"
disease = "urinary tract infection"

e1 = np.array(embeddings_model.embed_query(symptoms)).reshape(1, -1)
e2 = np.array(embeddings_model.embed_query(disease)).reshape(1, -1)

score = cosine_similarity(e1, e2)[0][0]

print(score)