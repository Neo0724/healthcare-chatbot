from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = None


def get_embedding_model():
    global embedding_model
    if not embedding_model:
        embedding_model = HuggingFaceEmbeddings(
            model_name="abhinand/MedEmbed-base-v0.1"
        )

    return embedding_model
