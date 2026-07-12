import os
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from deepeval.models import DeepEvalBaseEmbeddingModel

os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = "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"


class CustommMedEmbedEmbedding(DeepEvalBaseEmbeddingModel):
    def __init__(self):
        pass

    def load_model(self):
        return HuggingFaceEmbeddings(model_name="abhinand/MedEmbed-base-v0.1")

    def embed_text(self, text: str) -> List[float]:
        embedding_model = self.load_model()
        return embedding_model.embed_query(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embedding_model = self.load_model()
        return embedding_model.embed_documents(texts)

    async def a_embed_text(self, text: str) -> List[float]:
        embedding_model = self.load_model()
        return await embedding_model.aembed_query(text)

    async def a_embed_texts(self, texts: List[str]) -> List[List[float]]:
        embedding_model = self.load_model()
        return await embedding_model.aembed_documents(texts)

    def get_model_name(self):
        "abhinand/MedEmbed-base-v0.1"
