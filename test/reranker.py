from sentence_transformers import CrossEncoder

model = CrossEncoder("Qwen/Qwen3-Reranker-4B")

query = "I've been really itchy all over my body, and I've been getting chills and vomiting. My fever is really high, and I've been sweating a lot. I also have a headache, and I feel nauseous. My muscles are really sore."
documents = [
    "Acute and chronic malaria is characterized by paroxysms of fever, chills, sweats, fatigue, anemia, splenomegaly, and in severe cases by cerebral symptoms such as coma, convulsions, hyperpyrexia, hemolysis, oliguria, anuria, pulmonary edema, and macroscopic hemoglobinuria",
    "Bacteremia accompanied by systemic inflammatory response criteria including fever, tachycardia, tachypnea, or abnormal white blood cell count with immature bands",
]

pairs = [(query, doc) for doc in documents]
scores = model.predict(pairs)
print(scores)
# [  6.4375 -4.375 ]

rankings = model.rank(query, documents)
print(rankings)
# [{'corpus_id': 0, 'score': 6.4375}, {'corpus_id': 1, 'score': -14.375}]
