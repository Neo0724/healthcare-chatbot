import json
import subprocess
import time

from deepeval.models.base_model import DeepEvalBaseLLM
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


class CustomLLM(DeepEvalBaseLLM):
    def __init__(self, model, model_name):
        self.model = model
        self.model_name = model_name
        self.counter = 0

    def _reload_model(self):
        print("Unloading model ...")
        subprocess.run(["lms", "unload", self.get_model_name()])
        time.sleep(5)
        print("Model unloaded successfully!")

        print("Reloading model ...")
        subprocess.run(["lms", "load", self.get_model_name()])
        time.sleep(10)
        print("Model reloaded successfully!")

    def load_model(self):
        return self.model

    def generate(self, prompt: str, schema: BaseModel | None = None) -> str:
        self.counter += 1

        if self.counter % 35 == 0:
            self._reload_model()

        chat_model = self.load_model()

        if schema:
            structured_llm = chat_model.with_structured_output(schema)

            prompt_template = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a strict medical data extraction assistant. Your task is to extract "
                        "information based ONLY on the provided context. Do not extrapolate, infer, "
                        "or use external medical knowledge. If the context states a symptom belongs to "
                        "Condition A, do not attribute it to Condition B, even if they are clinically related.",
                    ),
                    ("user", "{input_prompt}"),
                ]
            )

            chain = prompt_template | structured_llm

            validated_object = chain.invoke({"input_prompt": prompt})

            return validated_object
        else:
            return chat_model.invoke(prompt).content

        # if prompt is not None:
        #     if "json" in prompt:
        #         chat_model = self.load_model().bind(
        #             response_format={"type": "json_schema"}
        #         )
        # return chat_model.invoke(prompt).content

    async def a_generate(self, prompt: str, schema: BaseModel | None = None) -> str:
        self.counter += 1

        if self.counter % 35 == 0:
            self._reload_model()

        chat_model = self.load_model()

        if schema:
            structured_llm = chat_model.with_structured_output(schema)

            prompt_template = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a strict medical data extraction assistant. Your task is to extract "
                        "information based ONLY on the provided context. Do not extrapolate, infer, "
                        "or use external medical knowledge. If the context states a symptom belongs to "
                        "Condition A, do not attribute it to Condition B, even if they are clinically related.",
                    ),
                    ("user", "{input_prompt}"),
                ]
            )

            chain = prompt_template | structured_llm

            validated_object = await chain.ainvoke({"input_prompt": prompt})

            return validated_object
        else:
            return await chain.invoke(prompt).content

    def get_model_name(self):
        return self.model_name
