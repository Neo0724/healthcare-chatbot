from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser  # Added
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
import json, time, subprocess


# 1. Define the Pydantic Schema
class RelationshipSchema(BaseModel):
    relationship: Literal["Symptoms", "Treatment", "Definition"] = Field(
        description="The category of the medical text snippet"
    )

# 2. Initialize the Parser
parser = PydanticOutputParser(pydantic_object=RelationshipSchema)

# 3. Setup LLM
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="qwen3.5-4b",
    temperature=0,
)

# 4. Create Prompt Template using format_instructions
prompt_template = """
You are a medical classifier. 
Classify the text into one of these three categories:
- Definition: Explains what the disease is, its origin, or its biological nature.
- Symptoms: Lists physical signs, clinical criteria, or what the patient experiences.
- Treatment: Lists medications, procedures, or management steps.

{format_instructions}

Text to analyze:
{text}

Metadatas related to the text
{header}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["text", "header"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

structured_llm = llm.with_structured_output(RelationshipSchema)

classifier_chain = prompt | structured_llm

def restart_llm_model():
    subprocess.run(["lms", "unload", "qwen3.5-4b"])
    subprocess.run(["lms", "load", "qwen3.5-4b"])

def classify_chunks(chunk):

    # --- Execution ---
    result: RelationshipSchema = "Definition"
    try:
        # The result is now an object, not a string
        parsed_result = classifier_chain.invoke(
            {"text": chunk.page_content, "header": json.dumps(chunk.metadata, ensure_ascii=False)}
        )

        result = parsed_result.relationship
        return result

    except Exception as e:
        print(e)
        return result

# --- 2. Main Execution Flow ---
def run_pipeline():
    start_time = time.perf_counter()

    # 1. Load and Split
    try:
        with open(
            "./doctor-cleaned.md", "r", encoding="utf-8"
        ) as f:
            markdown_file = f.read()

        headers_to_split_on = [("#", "Disease Category"), ("##", "Disease Name"), ("###", "H3")]
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )

        split_docs = header_splitter.split_text(markdown_file)

        with open("./relationship.md", "a", encoding="utf-8") as w:
            for i, doc in enumerate(split_docs):
                if i % 10 == 0:
                    restart_llm_model()

                if "H3" in doc.metadata and doc.metadata["H3"] == "Further Reading":
                    continue

                if not doc.page_content or len(doc.page_content.strip()) == 0:
                    continue

                w.write(f"### Chunk {i + 1}\n")
                w.write(f"**Content:**\n```\n{doc.page_content}\n```\n\n")
                w.write(f"**Relationship:** `{classify_chunks(doc)}`\n\n")
                w.write(f"**Metadata**:\n```{doc.metadata}```\n\n")
                w.write("---\n")

        end_time = time.perf_counter()

        execution_time = end_time - start_time
        print(f"Execution time: {execution_time:.6f} seconds")

    except FileNotFoundError:
        print("File not found")


if __name__ == "__main__":
    run_pipeline()
