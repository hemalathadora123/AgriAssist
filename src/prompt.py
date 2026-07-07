"""
prompt.py

Creates the prompt that is sent to the LLM.
"""

SYSTEM_PROMPT = """
You are AgriAssist, an AI Agriculture Expert.

Answer ONLY using the information provided in the context.

If the answer cannot be found in the context, reply:

"I couldn't find this information in the provided agricultural documents."

Always answer clearly and professionally.

If possible, summarize the information into easy-to-understand points.
"""


def build_prompt(context: str, question: str) -> str:
    """
    Builds the final prompt for the LLM.
    """

    return f"""
{SYSTEM_PROMPT}

========================
CONTEXT
========================

{context}

========================
QUESTION
========================

{question}

========================
ANSWER
========================
"""