import os
from dotenv import load_dotenv
from deepeval.synthesizer import Synthesizer
from langchain_openai import ChatOpenAI
from langchain_text_splitters import MarkdownHeaderTextSplitter
from llm.custom_llm import CustomLLM
from custom_embedding import CustommMedEmbedEmbedding
from deepeval.synthesizer.config import EvolutionConfig, Evolution
from styling_configs.config_3 import disease_styling_config
from utils.context_cleaner import clean_context_chunk

load_dotenv()

# custom_eval_llm = CustomLLM(
#     model=ChatOpenAI(
#         base_url=os.getenv("LLM_URL"),
#         model="meta-llama-3.1-8b-instruct",
#         api_key="lm-studio",
#         temperature=0.7,
#         frequency_penalty=0.5,
#         presence_penalty=0.5,
#         max_completion_tokens=6000,
#         extra_body={"repetition_penalty": 1.15, "top_p": 0.9},
#     )
# )

MD_FILE_NAME = "./malawi-stg-cleaned-short.md"


custom_llm = CustomLLM(
    model=ChatOpenAI(
        base_url=os.getenv("LLM_URL"),
        model=os.getenv("LLM_MODEL"),
        api_key="lm-studio",
        temperature=0.2,
        frequency_penalty=1.0,
        presence_penalty=0.6,
        max_completion_tokens=5000,
        extra_body={
            "repetition_penalty": 1.15,
            "top_p": 0.95,
            "top_k": 20,
            "min_p": 0.0,
        },
    ),
    model_name="qwen3-14b",
)

custom_embedding_model = CustommMedEmbedEmbedding()

with open(MD_FILE_NAME, "r", encoding="utf-8") as f:
    markdown_text = f.read()

# 3. Define which headers to track and split by
headers_to_split_on = [
    # ("#", "Disease Category"),
    ("##", "Disease Name"),
    ("###", "Subsection"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on, strip_headers=False
)

contexts_dict = {}

md_header_splits = markdown_splitter.split_text(markdown_text)

for d in md_header_splits:
    disease_name = d.metadata.get("Disease Name")

    if not disease_name:
        continue

    if disease_name not in contexts_dict:
        contexts_dict[disease_name] = []

    contexts_dict[disease_name].append(clean_context_chunk((d.page_content)))

evolution_config = EvolutionConfig(
    evolutions={
        Evolution.REASONING: 0,
        Evolution.MULTICONTEXT: 0,
        Evolution.COMPARATIVE: 0,  # explicitly kill comparative generation
        Evolution.HYPOTHETICAL: 0,
        Evolution.IN_BREADTH: 0,
        Evolution.CONCRETIZING: 1,  # keep simple, concrete rephrasing only
    },
    num_evolutions=1,
)

synthesizer = Synthesizer(
    model=custom_llm,
    max_concurrent=1,
    styling_config=disease_styling_config,
    evolution_config=evolution_config,
)

goldens = synthesizer.generate_goldens_from_contexts(
    contexts=list(contexts_dict.values()), max_goldens_per_context=2
)

synthesizer.save_as(
    file_type="csv", directory="./synthetic_data", file_name="test_set_8"
)
