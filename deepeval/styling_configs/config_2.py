from deepeval.synthesizer.config import StylingConfig

disease_styling_config = StylingConfig(
    task=(
        "Generate simple, single-fact factual recall questions about ONE disease at a time, "
        "focusing EXCLUSIVELY on that disease's definition, signs/symptoms, or treatment. "
        "The primary disease is always prefixed with '## ' (e.g., '## INFECTIVE ENDOCARDITIS'). "
        "Each question must be answerable by extracting a single contiguous block of text "
        "from ONE of the three relationships (Definition, Symptoms, or Treatment) belonging "
        "to that one disease node — never by combining, comparing, or reasoning across "
        "multiple diseases or multiple relationships."
    ),
    scenario=(
        "A rigorous medical data synthesizer extracting single, direct lookup facts from "
        "clinical guidelines, for a simple retrieval system that answers one disease, one "
        "relationship (Definition OR Symptoms OR Treatment), at a time. The context contains "
        "a primary disease marked by '## '. The synthesizer MUST ignore any secondary "
        "diseases, complications, subtypes, or related conditions mentioned in passing. "
        "The synthesizer MUST NOT generate comparative, differential, or 'distinguish "
        "between X and Y' questions, even if two related conditions both appear as headers "
        "in the source text. Each question targets exactly one disease and exactly one "
        "category of information."
    ),
    input_format=(
        "A short, direct lookup question asking about the definition, symptoms, OR treatment "
        "of the exact single disease denoted by '## ' in the context — never asking to "
        "compare, differentiate, or contrast it with another disease or subtype. "
        "Good examples: 'What is the definition of Infective Endocarditis?', "
        "'What are the symptoms of Infective Endocarditis?', "
        "'What is the recommended IV treatment for Infective Endocarditis?'. "
        "Bad examples to AVOID generating: 'What distinguishes X from Y?', "
        "'Compare the treatment of X and Y', 'How does X differ from Y?'."
    ),
    expected_output_format=(
        "A short, factual answer derived entirely from ONE relationship (Definition, "
        "Symptoms, or Treatment) of the single disease marked by '## ' in the context. "
        "The answer must be a direct, single-topic extraction — not a comparison, not a "
        "synthesis across multiple diseases, and not spanning more than one relationship "
        "type in the same answer."
    ),
)
