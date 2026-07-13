import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from langchain_huggingface import HuggingFaceEmbeddings

from llm.extract_symptoms import extract_symptoms


os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = "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"
os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "1"

embeddings_model = HuggingFaceEmbeddings(model_name="abhinand/MedEmbed-base-v0.1")

query = "I've been feeling really hot lately, sometimes I get dizzy, and it's hard for me to catch my breath when I do anything even mildly active. I don't have a cough or any rash, and I haven't noticed any pain in my joints."

extracted_entities = extract_symptoms(query)

context = [
    "fever",
    "night sweats",
    "weight loss",
    "anorexia",
    "cough",
    "dyspnoea",
    "valvular vegetation",
    "positive blood culture",
    "fever",
    "embolic phenomena",
]

# print(f"Extracted Entities:\n {extracted_entities}")

positive_symptoms = list(extracted_entities.positive_symptoms)
# negative_symptoms = list(extracted_entities.negative_symptoms)

positive_embedding = embeddings_model.embed_query(",".join(positive_symptoms))
context_embedding = embeddings_model.embed_documents(["fever", "night sweats", "weight loss", "anorexia", "cough", "dyspnoea"])

a_2d = np.array(positive_embedding).reshape(1, -1)

# context_embedding is already a 2D list of lists -> shape becomes (num_documents, dimensions)
b_2d = np.array(context_embedding)

similarity = cosine_similarity(a_2d, b_2d)
print(f"Similarity Score: {similarity[0][0]}")
