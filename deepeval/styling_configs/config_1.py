from deepeval.synthesizer.config import StylingConfig

disease_styling_config = StylingConfig(
    task=(
        "Generate a synthetic clinical dataset focusing EXCLUSIVELY on the disease definition, "
        "signs/symptoms, and treatments. You must strictly identify the primary disease "
        "which is always prefixed with '## ' (e.g., '## INFECTIVE ENDOCARDITIS')."
    ),
    scenario=(
        "A rigorous medical data synthesizer extracting data from clinical guidelines. "
        "The context contains a primary disease marked by '## '. The synthesizer MUST ignore "
        "any secondary diseases, complications (e.g., stroke, gangrenous foot), or irrelevant "
        "conditions that are not the primary disease."
    ),
    input_format=(
        "A clear, concise medical query asking about the definition, clinical features, "
        "symptoms, or treatment of the exact disease denoted by '## ' in the context. "
        "Example: 'What is the recommended IV treatment for Infective Endocarditis?'"
    ),
    expected_output_format=(
        "A factual, medically accurate response derived entirely from the provided context. "
        "The answer must only pertain to the disease marked by '## ' and be structured clearly."
    )
)
