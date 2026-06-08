import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

st.set_page_config(page_title="Centennial Marketing SEO Agent", page_icon="🏆", layout="centered")

st.title("Ultimate Multi-Engine SEO Agent")
st.caption("Powered by Gemini, ChatGPT, Grok, and Copilot (Free Endpoints)")

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
        
        try:
            result = response.json()
        except:
            return f"Raw Server Error ({response.status_code}): {response.text}"
            
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        elif 'error' in result:
            err_msg = result['error'].get('message', result['error'])
            return f"OpenRouter Rejected Request: {err_msg}"
        else:
            return f"API Structural Error: {result}"
            
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
    
    user_key = st.text_input("Paste Your OpenRouter API Key Here:", type="password", placeholder="sk-or-v1-...")
    if user_key:
        st.session_state["OR_KEY"] = user_key
        st.success("API Key loaded into session securely!")

with tab_main:
    st.subheader("1. Paste Your Target Webpage URL:")
    url_input = st.text_input("Target URL", placeholder="e.g., www.example.com/services", label_visibility="collapsed")
    
    if st.button("Run 4-Engine Agent Pipeline", type="primary", use_container_width=True):
        
        # --- HARDCODED TESTING FALLBACK ---
        # If the text box keeps resetting, paste your sk-or-v1-... key between the quotes below:
        TEST_KEY = "" 
        
        api_key = TEST_KEY if TEST_KEY else st.session_state.get("OR_KEY", "")
        
        if not api_key:
            st.error("⚠️ SETUP REQUIRED: Please add your OpenRouter API Key in the Settings tab first!")
        elif not url_input:
            st.warning("Please enter a web address first.")
        else:
            with st.spinner("Executing agents..."):
                status_box = st.empty()
                status_box.info("Scraping webpage text content...")
                page_text = fetch_webpage_text(url_input)
                
                if "Error fetching" in page_text:
                    st.error(page_text)
                else:
                    base_prompt = f"Analyze this text and output an optimized Meta Title, Meta Description, and Keywords for SEO:\n\n{page_text}"
                    
                    status_box.info("Querying Gemini, ChatGPT, Grok, and Copilot simultaneously...")
                    sug_gemini = call_openrouter_model("google/gemini-2-flash-thinking-exp:free", base_prompt, api_key)
                    st.write("✓ Gemini Complete")
                    
                    sug_chatgpt = call_openrouter_model("openai/gpt-4o-mini-privacy:free", base_prompt, api_key)
                    st.write("✓ ChatGPT Complete")
                    
                    sug_grok = call_openrouter_model("x-ai/grok-2-1212:free", base_prompt, api_key)
                    st.write("✓ Grok Complete")
                    
                    sug_copilot = call_openrouter_model("microsoft/phi-3-medium-128k-instruct:free", base_prompt, api_key)
                    st.write("✓ Copilot Complete")
                    
                    status_box.info("Running AI Judge review...")
                    judge_prompt = f"""
                    You are an expert SEO auditor. Carefully review these options:
                    [GEMINI]: {sug_gemini}
                    [CHATGPT]: {sug_chatgpt}
                    [GROK]: {sug_grok}
                    [COPILOT]: {sug_copilot}
                    
                    Output the absolute best combined Meta Title, Description, and Keywords based on your review.
                    """
                    final_judgment = call_openrouter_model("google/gemini-2-flash-thinking-exp:free", judge_prompt, api_key)
                    
                    status_box.empty()
                    
                    final_payload = f"{final_judgment}\n\n"
                    final_payload += f"===========================================\n"
                    final_payload += f"APPENDIX: INDIVIDUAL MODEL BREAKDOWNS\n"
                    final_payload += f"===========================================\n\n"
                    final_payload += f"[RAW GEMINI OUTPUT]\n{sug_gemini}\n\n"
                    final_payload += f"[RAW CHATGPT OUTPUT]\n{sug_chatgpt}\n\n"
                    final_payload += f"[RAW GROK OUTPUT]\n{sug_grok}\n\n"
                    final_payload += f"[RAW COPILOT OUTPUT]\n{sug_copilot}\n"
                    
                    st.subheader("2. Final Winning Recommendation:")
                    st.text_area("Results", value=final_payload, height=450, label_visibility="collapsed")
