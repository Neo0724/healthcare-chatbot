import os

import pandas as pd
from deepeval import evaluate
from deepeval.evaluate import AsyncConfig, DisplayConfig
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from llm.custom_llm import CustomLLM

load_dotenv()

os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "1"
os.environ["DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE"] = "600"

TEST_SET_FILE = "./synthetic_data/test_set_combined_2_populated_modified.csv"

custom_llm = CustomLLM(
    model=ChatOpenAI(
        base_url=os.getenv("LLM_URL"),
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("API_KEY"),
        temperature=0.2,
        frequency_penalty=1.0,
        presence_penalty=0.6,
        max_completion_tokens=5000,
        extra_body={
            "repetition_penalty": 1.15,
            "top_p": 0.85,
            "top_k": 20,
            "min_p": 0.05,
        },
    ),
    model_name=os.getenv("LLM_MODEL"),
)


# 2. Load your synthetic CSV dataset
df = pd.read_csv(TEST_SET_FILE)

# Look at your CSV columns to map them precisely. DeepEval needs a list of LLMTestCase objects
test_cases = []

print("⏳ Gathering actual outputs from your live RAG system...")
for index, row in df.iterrows():
    # if index > 5:
    #     continue
    # if index <= 20:
    # Fetch data points from your CSV structure safely
    # print(f"Processing test set no: **{index + 1}**")
    # print(f"Given input: {row['input']}")
    user_query = row["input"]
    ground_truth = row["expected_output"]
    retrieved_context = str(row["retrieved_context"]).split("\n[context_seperator]\n")
    actual_output = row["actual_output"]

    # Wrap everything cleanly into an Evaluation Test Case
    test_case = LLMTestCase(
        input=user_query,
        actual_output=actual_output,
        expected_output=ground_truth,
        retrieval_context=retrieved_context,
    )
    test_cases.append(test_case)

# # 3. Create the DeepEval Dataset container object
# eval_dataset = EvaluationDataset()

# Initialize your evaluation metrics using your local model configuration
faithfulness = FaithfulnessMetric(
    threshold=0.5, model=custom_llm, truths_extraction_limit=50
)
relevancy = AnswerRelevancyMetric(threshold=0.5, model=custom_llm)
contextual_recall = ContextualRecallMetric(threshold=0.5, model=custom_llm)
contextual_precision = ContextualPrecisionMetric(threshold=0.5, model=custom_llm)

print("🚀 Starting local Evaluation using your local model...")
# Run the evaluation sequentially to protect your local GPU constraints
evaluate(
    test_cases=test_cases,
    # metrics=[faithfulness],
    metrics=[contextual_precision, contextual_recall],
    async_config=AsyncConfig(run_async=False, max_concurrent=1, throttle_value=5),
    display_config=DisplayConfig(results_folder="./results/", verbose_mode=False),
)
