import streamlit as st
import requests
import time
import os

st.set_page_config(
    page_title="CodeDoc AI", 
    page_icon="📜", 
    layout="wide"
)


st.markdown("""
    <style>
    @import url('https://rsms.me/inter/inter.css');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background and Sidebar */
    .stApp {
        background-color: #0B0E11;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0D1117;
        border-right: 1px solid #21262d;
    }

    /* Input Field Styling */
    .stTextInput input {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #c9d1d9 !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
    }

    /* Professional Button */
    div.stButton > button {
        background: #0070f3 !important; /* Vercel Blue */
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        background: #0060df !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px 0 rgba(0,118,255,0.39);
    }

    /* Clean Sidebar Buttons */
    .stSidebar [data-testid="stBaseButton-secondary"] {
        background-color: transparent !important;
        border: 1px solid #30363d !important;
        text-align: left !important;
        color: #8b949e !important;
    }
    
    .stSidebar [data-testid="stBaseButton-secondary"]:hover {
        border-color: #58a6ff !important;
        color: #58a6ff !important;
    }

    /* Documentation Container */
    .doc-container {
        background-color: #0D1117;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 40px;
        line-height: 1.6;
        color: #e6edf3;
    }

    /* Title Styling */
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #f0f6fc;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

docs_dir = os.path.join("backend", "generated_docs")

with st.sidebar:
    st.markdown("<h3 style='color: #f0f6fc;'>Workspace</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8b949e; font-size: 0.8rem;'>Select a project to view</p>", unsafe_allow_html=True)
    
    if os.path.exists(docs_dir):
        files = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
        for f in files:
            if st.button(f"● {f.replace('_docs.md', '')}", key=f, use_container_width=True):
                st.session_state['view_file'] = f

st.markdown('<h1 class="hero-title">CodeDoc AI</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #8b949e; margin-bottom: 2rem;'>The intelligent documentation layer for your codebase.</p>", unsafe_allow_html=True)

col1, col2 = st.columns([0.85, 0.15])
with col1:
    repo_url = st.text_input("repo_url", placeholder="Enter GitHub repository URL...", label_visibility="collapsed")
with col2:
    if st.button("Generate", use_container_width=True):
        if repo_url:
            with st.status("Analyzing codebase...", expanded=False) as status:
                try:
                    res = requests.post("http://127.0.0.1:8000/analyze", json={"url": repo_url})
                    if res.status_code == 200:
                        task_id = res.json().get("task_id")
                        while True:
                            status_res = requests.get(f"http://127.0.0.1:8000/status/{task_id}").json()
                            curr = status_res.get("status")
                            if curr in ["SUCCESS", "Completed"]:
                                status.update(label="Analysis complete", state="complete")
                                result_data = status_res.get("result", {})
                                if isinstance(result_data, dict) and "file_saved_at" in result_data:
                                    st.session_state['view_file'] = os.path.basename(result_data["file_saved_at"])
                                time.sleep(0.5)
                                st.rerun()
                                break
                            elif curr == "FAILURE":
                                status.update(label="Analysis failed", state="error")
                                break
                            time.sleep(2)
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("<br>", unsafe_allow_html=True)
selected = st.session_state.get('view_file')

if selected:
    file_path = os.path.join(docs_dir, selected)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                st.markdown(f"<h2 style='font-weight: 600; font-size: 1.5rem;'>{selected.replace('_docs.md', '')}</h2>", unsafe_allow_html=True)
            with c2:
                st.download_button("Export .md", data=content, file_name=selected, use_container_width=True)
            
            st.markdown(f'<div class="doc-container">{content}</div>', unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="text-align: center; margin-top: 5rem; color: #30363d;">
            <p>No project selected. Start by pasting a URL above.</p>
        </div>
    """, unsafe_allow_html=True)