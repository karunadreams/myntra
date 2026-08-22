import os
import re
import dotenv
from groq import Groq

dotenv.load_dotenv()

class GroqEngine:
    def __init__(self, api_key=None, model="qwen/qwen3.6-27b"):
        self.api_key = api_key or os.environ.get("groq_api") or os.environ.get("GROQ_API_KEY")
        self.model = model
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing Groq client: {e}")

    def clean_output(self, text):
        if not text:
            return ""
        # Remove <think>...</think> tags if model produces internal thinking
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        return cleaned

    def query(self, system_prompt, user_prompt, max_tokens=1024, temperature=0.3):
        if not self.client:
            return "⚠️ Groq API Key is not configured. Please set `groq_api` in your `.env` file or Streamlit Secrets."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            raw_text = response.choices[0].message.content
            return self.clean_output(raw_text)
        except Exception as e:
            # Fallback to alternative model if available
            try:
                fallback_model = "openai/gpt-oss-120b"
                response = self.client.chat.completions.create(
                    model=fallback_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return self.clean_output(response.choices[0].message.content)
            except Exception as e2:
                return f"⚠️ Error querying Groq API ({self.model}): {e} | Fallback ({fallback_model}): {e2}"

    def generate_rag_answer(self, user_query, evidence_items):
        system_prompt = (
            "You are an expert Senior Growth Product Manager and E-Commerce Discovery Analyst at Myntra. "
            "Your objective is to analyze user feedback at scale, diagnose why wishlist items are not converted to purchases, "
            "and identify actionable non-monetary product opportunities. "
            "Base your answers STRICTLY on the provided verbatim customer reviews and evidence. Do not hallucinate."
        )
        
        context_str = ""
        for i, item in enumerate(evidence_items[:8], 1):
            context_str += f"[{i}] ({item.get('source', 'Unknown')} - {item.get('date', 'N/A')} - Segment: {item.get('segment', 'unidentified')}):\n\"{item.get('raw_text', '')}\"\n\n"
            
        user_prompt = f"""
Customer Evidence Quotes:
{context_str}

User Question: {user_query}

Please provide a structured, executive-ready response containing:
1. **Direct Answer & Discovery Finding**: Synthesize the core pattern emerging from the evidence.
2. **Root Cause Analysis**: Why users behave this way (e.g. sizing doubt, occasion holding, price/fabric comparison).
3. **Quantifiable Signal & Impact**: Note which user segments are most affected.
4. **Actionable Non-Monetary Solution**: Recommend a specific product feature or UX intervention (no discounts).
5. **Key Evidence Quotes**: Cite 2-3 compelling quotes directly from the evidence above.
"""
        return self.query(system_prompt, user_prompt, max_tokens=1000)

    def synthesize_research_question(self, rq_number, rq_title, evidence_items):
        system_prompt = (
            "You are a Principal Product Manager on Myntra's Growth team leading the Wishlist Conversion Initiative. "
            "Synthesize deep customer discovery insights for the specified Research Question using verbatim user feedback. "
            "Strict constraint: Solutions CANNOT offer monetary discounts or promo codes."
        )
        
        context_str = ""
        for i, item in enumerate(evidence_items[:10], 1):
            context_str += f"Quote {i} ({item.get('source')} | {item.get('platform')} | {item.get('segment')}):\n\"{item.get('raw_text')}\"\n\n"
            
        user_prompt = f"""
Research Question #{rq_number}: {rq_title}

Verbatim Customer Reviews & Mentions:
{context_str}

Provide a deep analytical synthesis structured in clean Markdown:
### 1. Executive Summary
Brief 2-3 sentence overview of the discovered truth.

### 2. Behavioral Dynamics & Root Friction
Detail what drives customer hesitation or postponement related to this question.

### 3. Affected Customer Segments
Break down how different personas (e.g. Plus-size, Budget shoppers, Students, Gift buyers) experience this.

### 4. Non-Monetary Product Interventions (Growth Playbook)
Provide 2 concrete product/UX features designed to unblock this specific friction point without discounting.

### 5. Primary Verbatim Evidence
Highlight 3 representative customer quotes verbatim with platform context.
"""
        return self.query(system_prompt, user_prompt, max_tokens=1200)
