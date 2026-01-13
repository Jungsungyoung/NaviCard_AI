import os
import requests
import base64
import time

class ImageGenerator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        # User confirmed model: gemini-2.5-flash-image
        self.model_name = "gemini-2.5-flash-image"

    def generate_image(self, prompt, output_path):
        """
        Generates an image using Gemini API.
        
        Args:
            prompt (str): Description of the image to generate.
            output_path (str): File path to save the generated image.
            
        Returns:
            str: Path to the saved image, or None if failed.
        """
        if not self.api_key:
            print("[ImageGen] No API Key found.")
            return None

        print(f"[ImageGen] Generating image for: {prompt[:50]}...")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        
        # Construct payload for image generation
        # Based on test result, standard generateContent works without special generationConfig
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        try:
            # Simple retry logic for rate limits
            for attempt in range(1, 4):
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 429:
                    print(f"[ImageGen] Rate limit hit. Waiting 60s... (Attempt {attempt})")
                    time.sleep(60)
                    continue
                
                if response.status_code != 200:
                    print(f"[ImageGen] API Error: {response.status_code} - {response.text}")
                    return None
                
                result = response.json()
                
                # Extract image data
                # Structure: candidates[0].content.parts[0].inlineData.data (Base64)
                try:
                    candidates = result.get('candidates', [])
                    if not candidates:
                        print("[ImageGen] No candidates returned.")
                        return None
                        
                    parts = candidates[0].get('content', {}).get('parts', [])
                    img_data = None
                    
                    for part in parts:
                        if 'inlineData' in part:
                            b64_data = part['inlineData']['data']
                            img_data = base64.b64decode(b64_data)
                            break
                    
                    if img_data:
                        # Save to file
                        dirname = os.path.dirname(output_path)
                        if dirname:
                            os.makedirs(dirname, exist_ok=True)
                            
                        with open(output_path, 'wb') as f:
                            f.write(img_data)
                            
                        print(f"[ImageGen] Image saved to {output_path}")
                        return output_path
                    else:
                        print(f"[ImageGen] No inlineData (image) found in any parts.")
                        print(f"[ImageGen] Parts count: {len(parts)}")
                        # print(f"[ImageGen] Full Response Candidates: {candidates}") # Too verbose
                        return None

                except Exception as e:
                    print(f"[ImageGen] Error parsing response: {e}")
                    return None
            
            return None # Failed after retries

        except Exception as e:
            print(f"[ImageGen] Error: {e}")
            return None
