import torch
from sentence_transformers import CrossEncoder

reranker = None


def get_reranker_model():
    global reranker
    if not reranker:
        reranker = CrossEncoder(
            "BAAI/bge-reranker-v2-m3",
            max_length=256,
            model_kwargs={
                "torch_dtype": torch.float16,
            },
        )

    return reranker
