
import os
import sys
import time
from datetime import datetime
import json
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# Import modules
from feed_parser import collect_news
from summarizer import NewsSummarizer
from image_generator import ImageGenerator
from mailer import send_email

# Load environment variables
load_dotenv()

def main():
    print("=== NaviCard AI System Started ===")
    
    # 1. Collect News
    raw_articles = collect_news()
    if not raw_articles:
        print("[!] No news found. Exiting.")
        return

    # 2. AI Processing (Summarize + Image)
    summarizer = NewsSummarizer()
    image_gen = ImageGenerator()
    
    cards = []
    
    # Process max 5 articles to save time/cost during dev/test
    # In production, maybe limit to top 10 relevant ones
    for article in raw_articles[:5]: 
        print(f"[-] Processing: {article['title']}")
        
        # A. Summarize
        summary_data = summarizer.summarize(f"{article['title']}\n{article['summary']}", article['source'])
        
        if not summary_data:
            print("   -> Failed to summarize. Skipping.")
            continue
            
        # Add metadata
        summary_data['source'] = article['source']
        summary_data['original_link'] = article['link']
        
        # B. Generate Image
        # If image prompt exists in summary, use it. Otherwise use title.
        image_prompt = summary_data.get('image_prompt', summary_data['headline_kr'])
        
        # Create a local filename
        safe_title = "".join(x for x in article['title'] if x.isalnum())[:20]
        image_path = f"images/{safe_title}.png"
        
        # Ensure images dir exists
        os.makedirs("images", exist_ok=True)
        
        generated_image = image_gen.generate_image(image_prompt, image_path)
        
        # For email, we might need a hosted URL or CID attachment.
        # For serverless without storage, we have a challenge.
        # Option 1: Base64 embed (increases email size, might be blocked).
        # Option 2: Upload to temporary storage (GitHub Artifacts? Not accessible in email easily).
        # Option 3: Use the NanoBanana URL directly if public?
        # For this PoC, let's assume valid URL or use a placeholder if file based.
        # If ImageGenerator returns a local path, we can't easily embed unless we use CID.
        # Let's simplify: If Mock, return a Placeholder URL.
        
        if generated_image:
             if generated_image.startswith("http"):
                 summary_data['image_url'] = generated_image
             else:
                 # It's a local path. Since the report is in root and images in images/, 
                 # and generated_image comes as "images/foo.png" (from output_path arg)
                 # We can use it directly.
                 # Normalize slashes for HTML
                 summary_data['image_url'] = generated_image.replace("\\", "/")
        else:
             # Fallback or local file logic (omitted for serverless simplicity)
             # Use a generic placeholder for now 
             summary_data['image_url'] = "https://via.placeholder.com/600x300?text=Naval+Technology"

        cards.append(summary_data)
        
        print("    [Rate Limit] Sleeping 10s...")
        time.sleep(10)

    if not cards:
        print("[!] No cards generated. Exiting.")
        return

    # 3. Generate HTML
    env = Environment(loader=FileSystemLoader('src/templates'))
    template = env.get_template('email_template.html')
    
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    html_output = template.render(cards=cards, date_str=date_str)
    
    # Save locally for debug
    with open("daily_report_debug.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    # Save structured data for Dashboard
    print(f"[*] Saving {len(cards)} cards to daily_report.json...")
    with open("daily_report.json", "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=4)
    print("[*] JSON saved.")
        
    # 4. Send Email
    subject = f"[NaviCard AI] {datetime.now().strftime('%Y-%m-%d')} Naval Tech Brief"
    send_email(subject, html_output)

    print("=== NaviCard AI System Finished ===")

if __name__ == "__main__":
    main()
