
import streamlit as st
import json
import os
import requests
import streamlit.components.v1 as components

# Configure page
st.set_page_config(page_title="NaviCard AI Dashboard", layout="wide")

# Load environment variables (api key)
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

st.title("⚓ NaviCard AI Interactive Brief")

# Layout: Left for Report, Right for Chat
col1, col2 = st.columns([1.2, 1])

# Load Report Data
@st.cache_data
def load_data():
    if os.path.exists("daily_report.json"):
        with open("daily_report.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Load HTML for display
def load_html():
    if os.path.exists("daily_report_debug.html"):
        with open("daily_report_debug.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>No Report Found. Please run main.py first.</h3>"

report_data = load_data()
html_content = load_html()

with col1:
    st.subheader("Daily Report")
    components.html(html_content, height=800, scrolling=True)

with col2:
    st.subheader("🤖 Ask to AI (Naval Expert)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial context system message (invisible to user but used in logic if chat history is built manually)
        # For simplicity, we'll append report context to the latest query or system prompt.

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("이 리포트에 대해 궁금한 점을 물어보세요..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Answer Logic
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Construct Context from Report Data
            context_text = "Here is the content of today's Naval daily report:\n"
            for card in report_data:
                context_text += f"---\nTitle: {card.get('headline_kr', 'No Title')}\n"
                context_text += f"Deep Summary: {card.get('deep_summary_kr', '')}\n"
                context_text += f"Technical Specs: {card.get('technical_specs_kr', '')}\n"
                context_text += f"Strategic Insight: {card.get('strategic_insight_kr', '')}\n"
            
            # Call Gemini API
            if not GEMINI_API_KEY:
                full_response = "Error: GEMINI_API_KEY not found."
                message_placeholder.markdown(full_response)
            else:
                try:
                    # Use gemini-3-flash-preview as requested for high quality QA
                    model_name = "gemini-3-flash-preview"
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent?key={GEMINI_API_KEY}"
                    headers = {'Content-Type': 'application/json'}
                    
                    system_instruction = f"""
                    You are a Senior Naval Systems Engineer. Answer the user's question based strictly on the provided Daily Report context.
                    If the answer is not in the report, use your general knowledge but mention that it's external info.
                    Context:\n{context_text}
                    """
                    
                    data = {
                        "contents": [
                            {"role": "user", "parts": [{"text": system_instruction + "\n\nQuestion: " + prompt}]}
                        ]
                    }
                    
                    # Streaming request
                    response = requests.post(url, headers=headers, json=data, stream=True)
                    
                    if response.status_code != 200:
                        full_response = f"API Error: {response.status_code} - {response.text}"
                        message_placeholder.markdown(full_response)
                    else:
                        # Parse stream
                        for line in response.iter_lines():
                            if line:
                                decoded_line = line.decode('utf-8')
                                if decoded_line.startswith('data: '):
                                    try:
                                        json_line = json.loads(decoded_line[6:])
                                        if 'candidates' in json_line:
                                            chunk = json_line['candidates'][0]['content']['parts'][0]['text']
                                            full_response += chunk
                                            message_placeholder.markdown(full_response + "▌")
                                    except:
                                        pass
                        message_placeholder.markdown(full_response)
                        
                except Exception as e:
                    full_response = f"Error: {e}"
                    message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
