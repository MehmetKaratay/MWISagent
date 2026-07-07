# MWIS Agent (c) by Mehmet Rahmi Karatay
#
# MWIS Agent is licensed under a
# Creative Commons Attribution-ShareAlike 4.0 International License.
#
# You should have received a copy of the license along with this
# work.  If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.

"""Local LLM-as-judge for `agents-cli eval grade`, wired in from
tests/eval/eval_config.yaml (`custom_function_file: metrics.py`).

Scores the agent's final response 1-5 via google-genai (works on both Vertex and
AI Studio) and grades against a case's `reference` (ground truth) when present.
"""

from google import genai
from google.genai import types
from pydantic import BaseModel


class _Verdict(BaseModel):
    """Pydantic model representing the evaluation verdict.

    Attributes:
        score: An integer from 1 to 5 representing the agent's grade.
        explanation: A string explaining the reasoning behind the score.
    """

    score: int  # 1-5
    explanation: str


def evaluate(instance):
    """Evaluates the agent's response using an LLM-as-a-judge.

    Grades the agent's final response on a 1-5 scale based on accuracy,
    relevance, and clarity, referencing ground truth if available.

    Args:
        instance (dict): A dictionary containing the evaluation context,
            including 'prompt', 'response', 'agent_data', and 'reference'.

    Returns:
        dict: A dictionary with the keys 'score' (int) and 'explanation' (str).
    """
    reference = instance.get("reference")
    rubric = (
        "Grade the agent's final response on a 1-5 scale (1 poor, 5 excellent) for "
        "accuracy, relevance, and clarity."
    )
    if reference:
        rubric += (
            " The response should agree with the expected answer below; penalize "
            "factual disagreement with it."
        )
    prompt = (
        f"You are an expert QA evaluator for an enterprise AI assistant. {rubric}\n"
        f"User Prompt: {instance.get('prompt', '')}\n"
        f"Final Response: {instance.get('response', '')}\n"
    )
    if reference:
        prompt += f"Expected Answer (ground truth): {reference}\n"
    prompt += f"Full Agent Trace: {instance.get('agent_data', '')}\n"

    client = genai.Client()  # AI Studio (GEMINI_API_KEY) or Vertex (ADC)
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,  # deterministic grading
            response_mime_type="application/json",
            response_schema=_Verdict,  # guaranteed schema-valid JSON
        ),
    )
    verdict = response.parsed
    if verdict is None:  # model returned nothing usable
        return {"score": 0, "explanation": response.text or ""}
    return {"score": max(1, min(5, verdict.score)), "explanation": verdict.explanation}
