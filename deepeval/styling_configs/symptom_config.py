from deepeval.synthesizer.config import StylingConfig

# symptom_styling_config = StylingConfig(
#     input_format=(
#         "A first-person patient message describing how they feel, written the way "
#         "a real patient would talk (not clinical terms). The message must include "
#         "BOTH: (1) positive symptoms — 2-4 symptoms taken from or paraphrased from "
#         "the disease's known symptom list, worded casually (e.g. 'my body feels hot' "
#         "instead of 'fever'), and (2) negative symptoms — 1-3 symptoms that are NOT "
#         "associated with this disease, explicitly stated as absent (e.g. 'I don't have "
#         "frequent urination' or 'no stomach pain'). Vary phrasing, ordering, and how "
#         "explicit vs. vague the wording is across examples."
#     ),
#     expected_output_format=(
#         "Not used — we are not generating expected_output for this dataset."
#     ),
#     task=(
#         "Evaluating whether a retrieved disease's symptom list correctly explains "
#         "a patient's described positive and negative symptoms (symptom-grounding / "
#         "retrieval evaluation for a medical symptom-checker system)."
#     ),
#     scenario=(
#         "Patients self-reporting symptoms in plain, everyday language to a symptom-"
#         "checker or triage chatbot, mixing what they do feel with what they explicitly "
#         "do not feel, sometimes vaguely and sometimes specifically."
#     ),
# )

symptom_styling_config = StylingConfig(
    input_format=(
        "A realistic first-person message from a patient (or parent if appropriate) "
        "describing their symptoms to a doctor or symptom-checker chatbot. "
        "Write exactly as an ordinary person would speak in everyday language. "
        "Avoid medical jargon, disease names, diagnoses, or technical clinical terms. "
        "Include 2-4 symptoms that naturally reflect the disease, expressed in casual "
        "language (e.g., 'I feel really hot', 'my joints ache', 'I get out of breath "
        "walking upstairs'). Also include 1-3 symptoms that are explicitly absent, "
        "using natural expressions such as 'I don't have a cough', 'I'm not throwing "
        "up', or 'I haven't noticed any rash'. The message should sound spontaneous, "
        "not like a checklist, and should not list every symptom."
        "Never phrase the message as a question about symptoms, mechanisms, or diagnoses (e.g., do not write 'How does X relate to Y' or 'What condition presents with...'). "
        "The message must be a first-person statement describing what the patient is experiencing."
        "Never mention a named disease, syndrome, or anatomical/pathological term (e.g., 'infective endocarditis', 'coarctation of the aorta') anywhere in the message, even in passing."
        "The patient never asks the chatbot to explain a relationship between symptoms and a condition — they only report what they feel."
    ),
    expected_output_format=(
        "Not used — we are not generating expected_output for this dataset."
    ),
    task=(
        "Generate natural patient symptom descriptions for evaluating a symptom-based "
        "disease retrieval system."
    ),
    scenario=(
        "The patient is seeking preliminary advice from an online symptom-checker "
        "before visiting a healthcare professional. They describe only what they can "
        "personally notice or experience. They do not know the diagnosis, do not use "
        "medical terminology unless it is commonly used by the public, and never ask "
        "about a specific disease or mention one by name."
    ),
)