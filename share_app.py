import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

st.set_page_config(page_title="Centennial Marketing SEO Agent", page_icon="🏆", layout="centered")

st.title("Ultimate Multi-Engine SEO Agent")
st.caption("Powered by the OpenRouter Free Intelligent Routing Engine")

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

def call_openrouter_model(prompt, api_key, generation_num):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost", 
            "X-Title": "SEO Team Agent App"
        }
        
        data = {
            "model": "openrouter/free",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3 + (generation_num * 0.15)
        }
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        try:
            result = response.json()
        except:
            return f"Raw Server Error ({response.status_code}): {response.text}", "Unknown Engine"
            
        if 'choices' in result:
            text_output = result['choices'][0]['message']['content']
            # OpenRouter passes the selected model ID back in the 'model' key!
            model_used = result.get('model', 'OpenRouter Free Choice')
            return text_output, model_used
        elif 'error' in result:
            err_msg = result['error'].get('message', result['error'])
            return f"OpenRouter Rejected Request: {err_msg}", "Error Endpoint"
        else:
            return f"API Structural Error: {result}", "Error Endpoint"
            
    except Exception as e:
        return f"Error calling endpoint: {e}", "Network Offline"

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
                    
                    status_box.info("Querying Free Agent Node 1...")
                    sug_1, model_1 = call_openrouter_model(base_prompt, api_key, 1)
                    st.write(f"✓ Agent 1 Complete ({model_1})")
                    
                    status_box.info("Querying Free Agent Node 2...")
                    sug_2, model_2 = call_openrouter_model(base_prompt, api_key, 2)
                    st.write(f"✓ Agent 2 Complete ({model_2})")
                    
                    status_box.info("Querying Free Agent Node 3...")
                    sug_3, model_3 = call_openrouter_model(base_prompt, api_key, 3)
                    st.write(f"✓ Agent 3 Complete ({model_3})")
                    
                    status_box.info("Querying Free Agent Node 4...")
                    sug_4, model_4 = call_openrouter_model(base_prompt, api_key, 4)
                    st.write(f"✓ Agent 4 Complete ({model_4})")
                    
                    status_box.info("Running AI Judge review...")
                    judge_prompt = f"""
                    You are an expert SEO auditor. Carefully review these 4 generation variations for the same webpage:
                    [VARIATION 1 via {model_1}]: {sug_1}
                    [VARIATION 2 via {model_2}]: {sug_2}
                    [VARIATION 3 via {model_3}]: {sug_3}
                    [VARIATION 4 via {model_4}]: {sug_4}
                    
                    Task: Select or blend the best elements into a final winning set of tags. Output your response exactly like this:
                    
                    🏆 WINNING SELECTION 🏆
                    Meta Title: [Insert Title]
                    Meta Description: [Insert Description]
                    Keywords: [Insert Keywords]
                    
                    ⚖️ JUDGMENT REASONING ⚖️
                    [Explain why this specific selection or combination is superior for SEO ranking]
                    """
                    final_judgment, judge_model = call_openrouter_model(judge_prompt, api_key, 0)
                    
                    status_box.empty()
                    
                    # Update layout strings to show the exact model names
                    final_payload = f"⚖️ JUDGE ENGINE USED: {judge_model}\n\n{final_judgment}\n\n"
                    final_payload += f"===========================================\n"
                    final_payload += f"APPENDIX: INDIVIDUAL AGENT BREAKDOWNS\n"
                    final_payload += f"===========================================\n\n"
                    final_payload += f"[{model_1.upper()} OUTPUT]\n{sug_1}\n\n"
                    final_payload += f"[{model_2.upper()} OUTPUT]\n{sug_2}\n\n"
                    final_payload += f"[{model_3.upper()} OUTPUT]\n{sug_3}\n\n"
                    final_payload += f"[{model_4.upper()} OUTPUT]\n{sug_4}\n"
                    
                    st.subheader("2. Final Winning Recommendation:")
                    st.text_area("Results", value=final_payload, height=450, label_visibility="collapsed")
