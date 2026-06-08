import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# Set up clean page config
st.set_page_config(page_title="Centennial Marketing SEO Agent", page_icon="🏆", layout="centered")

st.title("Ultimate Multi-Engine SEO Agent")
st.caption("Powered by Gemini, ChatGPT, Grok, and Copilot")

# --- CORE AGENT LOGIC ---
def fetch_webpage_text(url):
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text(separator=' ', strip=True)[:4000]
    except Exception as e:
        return f"Error fetching webpage: {e}"

def call_openrouter_model(model_name, prompt, api_key):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost", 
            "X-Title": "SEO Team Agent App"
        }
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=data, timeout=15)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Error calling {model_name}: {e}"

# --- APP TABS ---
tab_main, tab_settings = st.tabs(["Run Multi-AI Agent", "App Setup & Settings"])

with tab_settings:
    st.subheader("Application Setup Instructions")
    st.markdown(
        """
        **How to configure this application for your team:**
        1. Click the button below to go to OpenRouter.ai.
        2. Create a free account or log in.
        3. Generate an API Key, copy it, paste it below, and hit enter.
        """
    )
    st.link_button("🔗 Create Free OpenRouter Key", "https://openrouter.ai/keys")
    
    # Store the API key safely in the web browser session memory
    user_key = st.text_input("Paste Your OpenRouter API Key Below:", type="password", placeholder="sk-or-v1-...")
    if user_key:
        st.session_state["OR_KEY"] = user_key
        st.success("API Key loaded into session securely!")

with tab_main:
    st.subheader("1. Paste Your Target Webpage URL:")
    url_input = st.text_input("", placeholder="e.g., www.example.com/services", label_visibility="collapsed")
    
    if st.button("Run 4-Engine Agent Pipeline", type="primary", use_container_width=True):
        if "OR_KEY" not in st.session_state or not st.session_state["OR_KEY"]:
            st.error("⚠️ SETUP REQUIRED: Please go to the 'App Setup & Settings' tab and add your OpenRouter API Key first!")
        elif not url_input:
            st.warning("Please enter a web address first.")
        else:
            with st.spinner("Executing agents..."):
                api_key = st.session_state["OR_KEY"]
                
                # Progress logging updates live on screen
                status_box = st.empty()
                status_box.info("Scraping webpage text content...")
                page_text = fetch_webpage_text(url_input)
                
                if "Error fetching" in page_text:
                    st.error(page_text)
                else:
                    base_prompt = f"Analyze this text and output an optimized Meta Title, Meta Description, and Keywords for SEO:\n\n{page_text}"
                    
                    status_box.info("Querying Gemini, ChatGPT, Grok, and Copilot simultaneously...")
                    sug_gemini = call_openrouter_model("google/gemini-2.5-flash:free", base_prompt, api_key)
                    sug_chatgpt = call_openrouter_model("openai/gpt-4o-mini:free", base_prompt, api_key)
                    sug_grok = call_openrouter_model("x-ai/grok-2-mini:free", base_prompt, api_key)
                    sug_copilot = call_openrouter_model("microsoft/phi-4:free", base_prompt, api_key)
                    
                    status_box.info("Running AI Judge review and generating winner consensus...")
                    judge_prompt = f"""
                    You are an expert SEO auditor. Carefully review these four sets of suggestions generated for the same webpage:
                    [GEMINI]: {sug_gemini}
                    [CHATGPT]: {sug_chatgpt}
                    [GROK]: {sug_grok}
                    [COPILOT]: {sug_copilot}
                    
                    Task: Select or blend the best elements into a final winning set of tags. Output your response exactly like this:
                    
                    🏆 WINNING SELECTION 🏆
                    Meta Title: [Insert Title]
                    Meta Description: [Insert Description]
                    Keywords: [Insert Keywords]
                    
                    ⚖️ JUDGMENT REASONING ⚖️
                    [Explain why this specific selection or combination is superior for SEO ranking]
                    """
                    final_judgment = call_openrouter_model("google/gemini-2.5-flash:free", judge_prompt, api_key)
                    
                    status_box.empty() # clear status
                    
                    # Final Compilation string
                    final_payload = f"{final_judgment}\n\n"
                    final_payload += f"===========================================\n"
                    final_payload += f"APPENDIX: INDIVIDUAL MODEL BREAKDOWNS\n"
                    final_payload += f"===========================================\n\n"
                    final_payload += f"[RAW GEMINI OUTPUT]\n{sug_gemini}\n\n"
                    final_payload += f"[RAW CHATGPT OUTPUT]\n{sug_chatgpt}\n\n"
                    final_payload += f"[RAW GROK OUTPUT]\n{sug_grok}\n\n"
                    final_payload += f"[RAW COPILOT OUTPUT]\n{sug_copilot}\n"
                    
                    st.subheader("2. Final Winning Recommendation:")
                    # Streamlit text area features a built-in copy button natively in the upper right corner!
                    st.text_area("", value=final_payload, height=450, label_visibility="collapsed")