
import os
import google.generativeai as genai
import json
import time
import requests

class NewsSummarizer:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("[Summarizer] Warning: GEMINI_API_KEY not found.")
        # User requested gemini-3-flash-preview for deep insights
        self.model_name = "gemini-3-flash-preview"

    def summarize(self, article_text, source_name):
        """
        Analyzes the article using Gemini 3 Flash to provide deep technical summary and strategic insights.
        """
        if not self.api_key:
            return None

        prompt_text = f"""
        You are a Senior Naval Systems Engineer and Strategy Analyst specialing in Ship Control Systems, Autonomous Vessels (USV), and Propulsion.
        
        Your task is to analyze the provided naval defense news article and generate a professional intelligence brief.
        The reader is an expert in M&S (Modeling & Simulation) and Ship Control.

        **Source**: {source_name}
        **Article**:
        {article_text[:15000]}

        **Analysis Requirements**:
        1. **Headline (Korean)**: Professional and concise (max 50 chars).
        2. **Deep Summary (Korean)**: Do NOT just summarize the text. Extract meaningful technical details, specifications, and operational concepts. The user should not need to read the original article to understand the core technical value. Focus on Control Systems / USV / Platform details if present. (**Very Important**: Must be detailed and specific).
        3. **Technical Specs (Korean)**: Extract key numbers, dimensions, speeds, sensor types, engine details, or control system names. Present as bullet points key-value pairs if possible.
        4. **Strategic Insight (Korean)**: Analyze this news from the perspective of "Ship Control System R&D" or "Future Naval Warfare M&S". How does this affect future simulation requirements? What is the trend in autonomy or platform management?
        5. **Image Prompt (English)**: A vivid, cinematic description of the subject (USV, Control Room, Ship) for a high-end AI image generator. Focus on lighting, atmosphere, and technical realism.

        **Output Format**:
        Return ONLY a valid JSON object with these keys:
        - "headline_kr"
        - "deep_summary_kr" (Note: changed from technical_fact to hold the long summary)
        - "technical_specs_kr"
        - "strategic_insight_kr"
        - "image_prompt"
        """
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }

        for attempt in range(3):
            try:
                print(f"[*] Asking Gemini ({self.model_name}) to summarize via REST (Attempt {attempt+1})...")
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 429:
                    print(f"[Summarizer] Rate limit hit. Waiting 60 seconds...")
                    time.sleep(60)
                    continue

                if response.status_code != 200:
                    print(f"[Summarizer] API Error: {response.status_code} - {response.text}")
                    return None
                    
                result_json = response.json()
                # Parse response structure
                try:
                    text_content = result_json['candidates'][0]['content']['parts'][0]['text']
                    parsed = json.loads(text_content)
                    if isinstance(parsed, list):
                        if len(parsed) > 0:
                            return parsed[0]
                        else:
                            return None # Empty list
                    return parsed
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    print(f"[Summarizer] Failed to parse API response: {e}")
                    print(f"[Summarizer] Raw response: {result_json}")
                    return None

            except Exception as e:
                print(f"[Summarizer] Error generating summary: {e}")
                return None
        return None

if __name__ == "__main__":
    # Test stub
    summ = NewsSummarizer()
    print("Summarizer initialized.")
