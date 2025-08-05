# frontend/app.py
import streamlit as st
import requests
import json
import uuid
from src.api_health import check_api_health

API_BASE_URL = "http://localhost:8000"
LLM_URL="http://localhost:11434"

st.set_page_config(
    page_title="🧠 Network Logs Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Network Logs Analyzer Assistant")

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = {}
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.info(f"Session ID: {st.session_state.session_id[:8]}...")

    if check_api_health(API_BASE_URL, "/"):
        st.success("✅ Backend API is running")
    else:
        st.error("❌ Backend API is not available")

    # Ollama health
    if check_api_health(LLM_URL, "/api/tags"):
        st.success("✅ API Ollama is running")
    else:
        st.error("❌ API Ollama is not available")

    if st.button("🔄 New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.session_state.analysis_result = {}
        st.session_state.analysis_complete = False
        st.rerun()

    if st.button("🧹 Clear Chat History"):
        try:
            requests.post(f"{API_BASE_URL}/clear-chat")
            st.session_state.chat_history = []
            st.success("Chat history cleared")
        except:
            st.error("Failed to clear chat")

# --- Section 1: Upload Logs ---
st.subheader("Upload Network Logs in CSV format")
uploaded_file = st.file_uploader("Upload a .csv file", type=['csv'])

if uploaded_file is not None and not st.session_state.analysis_complete:
    with st.spinner("Analyzing uploaded logs..."):
        files = {"file": (uploaded_file.name, uploaded_file, "text/plain")}
        response = requests.post(f"{API_BASE_URL}/upload-logs", files=files)
        if response.status_code == 200:
            st.success("✅ Logs uploaded and analyzed successfully!")
            st.session_state.analysis_complete = True
        else:
            st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")

# --- Section 2: Logs Analysis ---
if st.session_state.analysis_complete:
    st.markdown("---")
    st.subheader("Logs Analysis")
    try:
        response = requests.get(f"{API_BASE_URL}/logs-analysis")
        if response.status_code == 200:
            logs_analysis = response.json().get("logs_analysis", "")
            st.session_state.analysis_result['logs_analysis'] = logs_analysis
            st.markdown(logs_analysis, unsafe_allow_html=True)
        else:
            st.warning("No logs analysis available")
    except:
        st.error("Error fetching logs analysis")

# --- Section 3: Anomaly Detection ---
if st.session_state.analysis_complete:
    st.markdown("---")
    st.subheader("Anomaly Detection")
    try:
        response = requests.get(f"{API_BASE_URL}/anomalies")
        if response.status_code == 200:
            anomalies = response.json().get("anomalies", "")
            st.session_state.analysis_result['anomalies'] = anomalies

            print(f"\n\nAnomalies: {anomalies}\n\n")
            st.warning(anomalies)
        else:
            st.warning("No anomalies detected yet")
    except Exception as e:
        st.error(f"Error fetching anomalies: {e}")

# --- Section 4: Chatbot Interface ---
if st.session_state.analysis_complete:
    st.markdown("---")
    st.header("💬 4. Chat With LogBot")

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])

    if prompt := st.chat_input("Ask something about the network logs"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            try:
                response = requests.post(f"{API_BASE_URL}/chat", json={"message": prompt})
                if response.status_code == 200:
                    bot_reply = response.json().get("response", "")
                    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                else:
                    st.error("Failed to get bot response")
            except:
                st.error("Error during chat with bot")
        st.rerun()
