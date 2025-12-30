import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = """
You are an equity research analyst specializing in forensic accounting.

You are given:
- A time series of forensic alpha values
- Component forensic signals (Beneish, Sloan, Piotroski, Altman)

Your task:
1. Recommend ONE of: LONG, SHORT, or HOLD
2. Provide concise, professional reasoning grounded ONLY in the data
3. Reference trends, not single-year noise
4. Avoid speculation or market price discussion
5. Be cautious and balanced in tone

Output STRICT JSON with exactly these keys:
recommendation
confidence (Low / Medium / High)
reasoning
"""

def ai_alpha_recommendation(alpha_df):
    """
    alpha_df: DataFrame returned by forensic_alpha()
    """

    payload = {
        "model": "llama3",
        "prompt": SYSTEM_PROMPT + "\n\nDATA:\n" + alpha_df.to_json(),
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        raw = response.json().get("response", "")
        start, end = raw.find("{"), raw.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("Invalid AI response")

        return json.loads(raw[start:end + 1])

    except Exception as e:
        return {
            "recommendation": "HOLD",
            "confidence": "Low",
            "reasoning": "AI interpretation unavailable. Recommendation based solely on quantitative forensic alpha."
        }
