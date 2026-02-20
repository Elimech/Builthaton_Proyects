from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def answer_question(G, question):
    MODEL_ID = "gemini-flash-lite-latest"
    context = ""
    for u, v, data in G.edges(data=True):
        context += f"{u} --({data.get('label', '')})-> {v}\n"

    prompt = f"""
    Based on this graph, answer the question concisely:
    {context}  
    Question: {question}
    """

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text if response.text else "No response."
    except Exception as e:
        return f"Error in the analysis: {e}"