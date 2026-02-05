from google import genai
import os

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY isn't set. "
        "Set the environment variable before running."
    )

client = genai.Client(api_key=API_KEY)
modelID = "gemini-3-flash-preview"


def analyze_commit(commit_text):
    try:
        response = client.models.generate_content(
            model=modelID,
            contents=f"""
            Analyze one commit at a time
            Use all available commit data
            Explain what changed in clear, technical language
            Understand how the codebase evolves over time.

            Classify change strictly as:
                Bugfix
                Feature
                Refactor
                Docs

            Determine impact level:
                Low / Medium / High
                Base impact primarily on semantic versioning (X.Y.Z)
                Provide semantic reasoning (“why this change exists”)
                Identify introduced or reinforced patterns

            Link the commit to:
                A feature
                A technical decision
                A maintenance or refactor effort
                Comment on ownership signals when relevant
                Comment on complexity trend (increased, reduced, stabilized)
                Output text only (no JSON, no tables unless textual)

            Commit:
            {commit_text}
            """
        )
        return response.text

    except Exception as e:
        return f'[Error analyzing commit: {e}]'


def answer_question(question, analysis_context):
    prompt = f"""
    You are a senior software engineer AI.

    You already analyzed a Git repository.
    Below is the analysis context.

    --- ANALYSIS CONTEXT ---
    {analysis_context}
    --- END CONTEXT ---

    Now answer the user's question based ONLY on this context.
    If the information is not present, say so clearly.

    User question:
    {question}
    """

    response = client.models.generate_content(
        model=modelID,
        contents=prompt
    )
    return response.text
