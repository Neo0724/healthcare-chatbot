from deepeval.synthesizer import Synthesizer
from langchain_openai import ChatOpenAI
from llm.custom_llm import CustomLLM
from deepeval.synthesizer.config import EvolutionConfig, Evolution
from db.get_symptoms_information import get_symptoms_information
from styling_configs.symptom_config import symptom_styling_config

# custom_eval_llm = CustomLLM(
#     model=ChatOpenAI(
#         base_url="http://localhost:1234/v1",
#         model="meta-llama-3.1-8b-instruct",
#         api_key="lm-studio",
#         temperature=0.7,
#         frequency_penalty=0.5,
#         presence_penalty=0.5,
#         max_completion_tokens=6000,
#         extra_body={"repetition_penalty": 1.15, "top_p": 0.9},
#     )
# )

custom_llm = CustomLLM(
    model=ChatOpenAI(
        base_url="http://localhost:1234/v1",
        model="qwen3-14b",
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

def generate_symptom_golden():
    records = get_symptoms_information()

    disease_symptoms = {
        r.data().get("disease_name", ""): r.data().get("symptoms", []) for r in records
    }

    diseases = list(disease_symptoms.keys())
    contexts = [disease_symptoms[d] for d in diseases]

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
        styling_config=symptom_styling_config,
        evolution_config=evolution_config,
    )

    goldens = synthesizer.generate_goldens_from_contexts(
        contexts=contexts,
        max_goldens_per_context=1,
        include_expected_output=False,
        source_files=diseases,
    )

    synthesizer.save_as(
        file_type="csv", directory="./synthetic_data", file_name="symptom_test_set_v3"
    )

if __name__ == "__main__":
    generate_symptom_golden()