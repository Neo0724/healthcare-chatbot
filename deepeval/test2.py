import os

from transformers import pipeline

os.environ["HF_HOME"] = "C:/hf_cache"
os.environ["HF_TOKEN"] = "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"

pipe = pipeline(
    "token-classification",
    model="Clinical-AI-Apollo/Medical-NER",
    aggregation_strategy="simple",
)
result = pipe(
    "I have headache, and feel very dizzy when moving head around. When moving head around, I felt like the walls are moving which makes me want to vomit"
)

print(result)
