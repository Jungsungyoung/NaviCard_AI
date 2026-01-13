
import os
import sys
from dotenv import load_dotenv

def check_setup():
    print("Checking environment setup...")
    
    # Check .env
    if not os.path.exists('.env'):
        print("[!] .env file not found.")
        return
    
    load_dotenv()
    
    required_keys = [
        "GEMINI_API_KEY",
        "EMAIL_USER", 
        "EMAIL_PASSWORD",
        "RECIPIENT_EMAILS"
    ]
    
    missing = []
    defaults = []
    
    for key in required_keys:
        val = os.getenv(key)
        if not val:
            missing.append(key)
        elif "your_" in val and "here" in val: # Simple check for default values
             defaults.append(key)
             
    if missing:
        print(f"[!] Missing environment variables: {', '.join(missing)}")
    if defaults:
        print(f"[!] Default values detected (need updates): {', '.join(defaults)}")
        
    if not missing and not defaults:
        print("[OK] .env configuration looks valid (keys present).")

    # Check dependencies
    try:
        import google.generativeai
        import feedparser
        import bs4
        import requests
        import jinja2
        import dotenv
        import dateutil
        print("[OK] All dependencies appear to be installed.")
    except ImportError as e:
        print(f"[!] Missing dependency: {e.name}. Please run pip install.")

if __name__ == "__main__":
    check_setup()
