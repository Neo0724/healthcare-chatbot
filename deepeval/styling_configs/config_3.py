from deepeval.synthesizer.config import StylingConfig

disease_styling_config = StylingConfig(
    task=(
        "Generate simple, single-fact factual recall questions about ONE disease at a time, "
        "focusing EXCLUSIVELY on that disease's definition, signs/symptoms, or treatment. "
        "The primary disease name is the EXACT LITERAL STRING that immediately follows '## ' "
        "in the context (e.g., '## ACUTE LEFT VENTRICULAR FAILURE' -> disease name is "
        "'ACUTE LEFT VENTRICULAR FAILURE'). You must copy this string verbatim into the "
        "question. NEVER substitute a synonym, a related pathological process, or a "
        "condition mentioned inside the definition/description text as the disease name — "
        "e.g. if the CLINICAL DESCRIPTION says 'Pulmonary edema due to left ventricular "
        "failure' under the header '## ACUTE LEFT VENTRICULAR FAILURE', the disease name is "
        "'ACUTE LEFT VENTRICULAR FAILURE', NOT 'pulmonary edema', even though 'pulmonary "
        "edema' appears first and reads like a diagnosis. Each question must be answerable "
        "by extracting a single contiguous block of text from ONE of the three relationships "
        "(Definition, Symptoms, or Treatment) belonging to that one disease node."
    ),
    scenario=(
        "A rigorous medical data synthesizer extracting single, direct lookup facts from "
        "clinical guidelines. The context contains a primary disease marked by '## ', and "
        "the disease name is exactly the text following that marker — never a term found "
        "later in the body text, even if that term appears earlier, more prominently, or "
        "more clinically specific than the header itself. The synthesizer MUST ignore any "
        "secondary diseases, complications, subtypes, underlying mechanisms, or related "
        "conditions mentioned in passing within the body text when naming the disease in "
        "the question. The synthesizer MUST NOT generate comparative or differential "
        "questions."
    ),
    input_format=(
        "A short, direct lookup question asking about the definition, symptoms, OR treatment "
        "of the exact single disease denoted by '## ' in the context, using that header's "
        "literal text as the disease name — never a term borrowed from the body text below "
        "it. Good example: context header '## ACUTE LEFT VENTRICULAR FAILURE' with body text "
        "mentioning 'pulmonary edema' -> question is 'What are the clinical features of "
        "Acute Left Ventricular Failure?', NOT 'What are the clinical features of pulmonary "
        "edema?'. Bad examples to AVOID: 'What distinguishes X from Y?', 'Compare X and Y', "
        "and using any disease name not taken verbatim from the '## ' header."
    ),
    expected_output_format=(
        "A short, factual answer derived entirely from ONE relationship (Definition, "
        "Symptoms, or Treatment) of the single disease marked by '## ' in the context, using "
        "that disease's exact header name — not a synonym found in the body text."
    ),
)
