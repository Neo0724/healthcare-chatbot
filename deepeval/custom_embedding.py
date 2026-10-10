import os

from deepeval.models import DeepEvalBaseEmbeddingModel
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

os.environ["HF_HOME"] = "D:/hf_cache"
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")


class CustommMedEmbedEmbedding(DeepEvalBaseEmbeddingModel):
    def __init__(self):
        pass

    def load_model(self):
        return HuggingFaceEmbeddings(model_name="abhinand/MedEmbed-base-v0.1")

    def embed_text(self, text: str) -> list[float]:
        embedding_model = self.load_model()
        return embedding_model.embed_query(text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embedding_model = self.load_model()
        return embedding_model.embed_documents(texts)

    async def a_embed_text(self, text: str) -> list[float]:
        embedding_model = self.load_model()
        return await embedding_model.aembed_query(text)

    async def a_embed_texts(self, texts: list[str]) -> list[list[float]]:
        embedding_model = self.load_model()
        return await embedding_model.aembed_documents(texts)

    def get_model_name(self):
        "abhinand/MedEmbed-base-v0.1"
