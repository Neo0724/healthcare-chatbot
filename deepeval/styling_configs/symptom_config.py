from deepeval.synthesizer.config import StylingConfig

symptom_styling_config = StylingConfig(
    input_format=(
        "A first-person patient message describing how they feel, written the way "
        "a real patient would talk (not clinical terms). The message must include "
        "BOTH: (1) positive symptoms — 2-4 symptoms taken from or paraphrased from "
        "the disease's known symptom list, worded casually (e.g. 'my body feels hot' "
        "instead of 'fever'), and (2) negative symptoms — 1-3 symptoms that are NOT "
        "associated with this disease, explicitly stated as absent (e.g. 'I don't have "
        "frequent urination' or 'no stomach pain'). Vary phrasing, ordering, and how "
        "explicit vs. vague the wording is across examples."
    ),
    expected_output_format=(
        "Not used — we are not generating expected_output for this dataset."
    ),
    task=(
        "Evaluating whether a retrieved disease's symptom list correctly explains "
        "a patient's described positive and negative symptoms (symptom-grounding / "
        "retrieval evaluation for a medical symptom-checker system)."
    ),
    scenario=(
        "Patients self-reporting symptoms in plain, everyday language to a symptom-"
        "checker or triage chatbot, mixing what they do feel with what they explicitly "
        "do not feel, sometimes vaguely and sometimes specifically."
    ),
)

# symptom_styling_config = StylingConfig(
#     input_format=(
#         "A first-person patient statement describing the symptoms found in the "
#         "context, written in plain, everyday language with no medical jargon. "
#         "Clinical terms (e.g. 'dyspnea', 'tachypnea', 'pulmonary crackles') must be "
#         "translated into how a non-medical person would actually describe what "
#         "they are feeling or noticing (e.g. 'I can't catch my breath', 'my chest "
#         "feels tight', 'it feels like something's rattling when I breathe'). "
#         "The input should sound natural and conversational, not like a reworded "
#         "copy of the clinical note, and may include onset, severity in lay terms, "
#         "and a touch of worry or emotion, as a real patient would express to a doctor."
#     ),
#     task=(
#         "Simulating patients describing their symptoms in their own words based on "
#         "a clinical context, for use in evaluating a medical assistant/chatbot."
#     ),
#     scenario=(
#         "A non-medical patient explaining what they are feeling to a doctor or "
#         "nurse, based on an underlying clinical presentation."
#     ),
# )