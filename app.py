import streamlit as st
import requests
import pandas as pd
import time

API_URL = "http://localhost:8000"

try:
    from src.utils.config import settings
    raw_model = settings.LLM_MODEL
    # Capitalize nicely e.g., llama3.2 -> Llama 3.2
    LLM_MODEL = raw_model.replace("3.2", " 3.2").title() if "3.2" in raw_model else raw_model.title()
except Exception:
    import os
    raw_model = os.getenv("LLM_MODEL", "llama3.2")
    LLM_MODEL = raw_model.replace("3.2", " 3.2").title() if "3.2" in raw_model else raw_model.title()

st.set_page_config(page_title="Support Ticket AI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CUSTOM CSS FOR PREMIUM UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Core fonts and styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Elegant app background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
        color: #1e293b;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    /* Modern Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a;
        font-weight: 700 !important;
    }
    
    /* Metric Cards Styles */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
        width: 100%;
    }
    @media (max-width: 1200px) {
        .metrics-container {
            grid-template-columns: repeat(3, 1fr);
        }
    }
    @media (max-width: 768px) {
        .metrics-container {
            grid-template-columns: repeat(1, 1fr);
        }
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 16px;
        padding: 1.25rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 4px 15px -3px rgba(15, 23, 42, 0.05), 0 2px 6px -2px rgba(15, 23, 42, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px -5px rgba(15, 23, 42, 0.08), 0 6px 12px -3px rgba(15, 23, 42, 0.04);
    }
    
    .card-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    .card-content {
        display: flex;
        flex-direction: column;
    }
    .card-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .card-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    
    /* Hover effects for individual cards with theme accents */
    .card-total:hover {
        border-color: rgba(37, 99, 235, 0.4);
        background: rgba(239, 246, 255, 0.45);
    }
    .card-open:hover {
        border-color: rgba(245, 158, 11, 0.4);
        background: rgba(254, 243, 199, 0.45);
    }
    .card-resolved:hover {
        border-color: rgba(16, 185, 129, 0.4);
        background: rgba(209, 250, 229, 0.45);
    }
    .card-escalated:hover {
        border-color: rgba(139, 92, 246, 0.4);
        background: rgba(245, 243, 255, 0.45);
    }
    .card-critical:hover {
        border-color: rgba(239, 68, 68, 0.4);
        background: rgba(254, 242, 242, 0.45);
    }
    
    /* Icon color styling */
    .blue-gradient {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        color: #2563eb;
    }
    .orange-gradient {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        color: #d97706;
    }
    .green-gradient {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        color: #059669;
    }
    .purple-gradient {
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
        color: #7c3aed;
    }
    .red-gradient {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        color: #dc2626;
    }
    
    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 2px solid rgba(226, 232, 240, 0.5);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: rgba(255, 255, 255, 0.4);
        border-radius: 12px 12px 0 0;
        border: 1px solid rgba(226, 232, 240, 0.6);
        border-bottom: none;
        color: #64748b;
        padding: 0 24px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0f172a;
        background-color: rgba(255, 255, 255, 0.8);
        border-color: rgba(99, 102, 241, 0.2);
    }
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #4f46e5 !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        border-bottom: 3px solid #4f46e5 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.15);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.3);
        border-color: transparent;
        color: white;
    }
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: white;
        border: 1px solid rgba(226, 232, 240, 0.8);
        color: #1e293b;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
    }
    
    /* Dataframe view */
    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05);
        background: white;
    }
    
    /* Chat message overrides */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        backdrop-filter: blur(10px);
    }
    .stChatMessage[data-testid="stChatMessage-user"] {
        background-color: rgba(99, 102, 241, 0.05);
        border-color: rgba(99, 102, 241, 0.15);
    }
    
    /* Custom divider */
    hr {
        border-color: rgba(226, 232, 240, 0.8);
    }
    
    /* Metadata Container in Chat */
    .metadata-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px dashed rgba(226, 232, 240, 0.8);
    }
    .metadata-section {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
    }
    .metadata-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
        font-weight: 600;
    }
    .metadata-value {
        font-size: 0.95rem;
        color: #0f172a;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)
# --- END CUSTOM CSS ---

# --- DATA PREPARATION ---
try:
    df = pd.read_csv("support_tickets.csv")
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    data_loaded = True
except Exception as e:
    df = pd.DataFrame()
    data_loaded = False
    st.error(f"Error loading support tickets dataset: {e}")

# Title Block
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 800; margin: 0; padding-bottom: 0.5rem; letter-spacing: -0.5px;">✨ Customer Support Ticket AI</h1>
    <h3 style="color: #475569; font-weight: 500; font-size: 1.25rem; margin: 0 0 0.5rem 0;">Next-Gen Intelligence for Support Operations</h3>
    <p style="color: #64748b; font-size: 1rem; margin: 0;">Unlock deep insights from your support tickets using natural language and automated anomaly detection.</p>
</div>
""", unsafe_allow_html=True)

# Dynamic Dashboard Metric Cards
if data_loaded:
    total_tickets = len(df)
    open_tickets = len(df[df['status'] == 'Open']) if 'status' in df.columns else 0
    resolved_tickets = len(df[df['status'] == 'Resolved']) if 'status' in df.columns else 0
    escalated_tickets = len(df[df['status'] == 'Escalated']) if 'status' in df.columns else 0
    critical_tickets = len(df[df['priority'] == 'Critical']) if 'priority' in df.columns else 0
else:
    total_tickets, open_tickets, resolved_tickets, escalated_tickets, critical_tickets = 0, 0, 0, 0, 0

st.markdown(f"""
<div class="metrics-container">
    <div class="metric-card card-total">
        <div class="card-icon blue-gradient">🎫</div>
        <div class="card-content">
            <span class="card-label">Total Tickets</span>
            <span class="card-val">{total_tickets:,}</span>
        </div>
    </div>
    <div class="metric-card card-open">
        <div class="card-icon orange-gradient">⏳</div>
        <div class="card-content">
            <span class="card-label">Open</span>
            <span class="card-val">{open_tickets:,}</span>
        </div>
    </div>
    <div class="metric-card card-resolved">
        <div class="card-icon green-gradient">✅</div>
        <div class="card-content">
            <span class="card-label">Resolved</span>
            <span class="card-val">{resolved_tickets:,}</span>
        </div>
    </div>
    <div class="metric-card card-escalated">
        <div class="card-icon purple-gradient">⚠️</div>
        <div class="card-content">
            <span class="card-label">Escalated</span>
            <span class="card-val">{escalated_tickets:,}</span>
        </div>
    </div>
    <div class="metric-card card-critical">
        <div class="card-icon red-gradient">🚨</div>
        <div class="card-content">
            <span class="card-label">Critical</span>
            <span class="card-val">{critical_tickets:,}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# System Status in Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    st.markdown("---")
    
    st.markdown("### API Connection")
    
    # Initialize health status
    if "health_status" not in st.session_state:
        try:
            res = requests.get(f"{API_URL}/health", timeout=2)
            if res.status_code == 200:
                st.session_state.health_status = "online"
            else:
                st.session_state.health_status = "offline"
        except Exception:
            st.session_state.health_status = "offline"

    status_placeholder = st.empty()
    
    def render_health_status(status):
        if status == "online":
            status_placeholder.markdown('<div style="background-color: rgba(22, 163, 74, 0.1); border: 1px solid rgba(22, 163, 74, 0.2); color: #15803d; padding: 10px 14px; border-radius: 10px; font-weight: 600; text-align: center; margin-bottom: 10px; font-size: 0.9rem;">🟢 Online & Ready</div>', unsafe_allow_html=True)
        elif status == "offline":
            status_placeholder.markdown('<div style="background-color: rgba(220, 38, 38, 0.1); border: 1px solid rgba(220, 38, 38, 0.2); color: #b91c1c; padding: 10px 14px; border-radius: 10px; font-weight: 600; text-align: center; margin-bottom: 10px; font-size: 0.9rem;">🔴 Offline</div>', unsafe_allow_html=True)
        else:
            status_placeholder.markdown('<div style="background-color: rgba(100, 116, 139, 0.1); border: 1px solid rgba(100, 116, 139, 0.2); color: #475569; padding: 10px 14px; border-radius: 10px; font-weight: 600; text-align: center; margin-bottom: 10px; font-size: 0.9rem;">⚪ Waiting to check...</div>', unsafe_allow_html=True)

    render_health_status(st.session_state.health_status)
    
    if st.button("🔄 Check Health", use_container_width=True):
        try:
            res = requests.get(f"{API_URL}/health", timeout=2)
            if res.status_code == 200:
                st.session_state.health_status = "online"
            else:
                st.session_state.health_status = "offline"
        except Exception:
            st.session_state.health_status = "offline"
        render_health_status(st.session_state.health_status)
        
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #475569; font-size: 0.8rem; margin-top: 2rem;'>Powered by<br><b>LangChain & FastAPI</b></div>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Data Overview", "💬 Ask AI", "🔍 Anomaly Detection"])

with tab1:
    st.markdown("### 📋 Dataset Insights")
    if data_loaded:
        col_inf1, col_inf2 = st.columns(2)
        with col_inf1:
            st.info(f"📁 **Dataset Schema:** {len(df.columns)} Columns / Features")
        with col_inf2:
            st.success(f"✓ **Data Integrity:** Loaded successfully ({len(df):,} total records)")
            
        st.markdown("#### 📊 Ticket Distributions", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if 'category' in df.columns:
                st.markdown("**Category Distribution**")
                cat_counts = df['category'].value_counts()
                st.bar_chart(cat_counts, color="#3b82f6")
        with col_c2:
            if 'priority' in df.columns:
                st.markdown("**Priority Breakdown**")
                prio_counts = df['priority'].value_counts()
                st.bar_chart(prio_counts, color="#ec4899")
            
        st.markdown("#### 🔍 Preview Dataset (First 100 rows)", unsafe_allow_html=True)
        st.dataframe(df.head(100), use_container_width=True, height=400)
    else:
        st.warning("No data available to display.")

with tab2:
    st.markdown("### 💬 Chat with Your Data")
    st.markdown("<p style='color: #475569;'>Ask anything about your customer support dataset, and our AI agent will write the pandas code to find the exact answer.</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "model" in message and "response_time" in message:
                markdown_response = f"**Answer**\n\n{message['content']}\n\n**Model**\n\n{message['model']}\n\n**Response Time**\n\n{message['response_time']:.1f} sec"
                st.markdown(markdown_response)
            else:
                st.markdown(message["content"])
            
    # React to user input
    if prompt := st.chat_input("e.g., 'What is the most common issue?'"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("🧠 AI is analyzing your data..."):
                try:
                    start_time = time.time()
                    response = requests.post(f"{API_URL}/query", json={"query": prompt})
                    elapsed_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        answer = response.json().get("answer")
                        
                        markdown_response = f"**Answer**\n\n{answer}\n\n**Model**\n\n{LLM_MODEL}\n\n**Response Time**\n\n{elapsed_time:.1f} sec"
                        st.markdown(markdown_response)
                        
                        # Add assistant response with metadata to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "model": LLM_MODEL,
                            "response_time": elapsed_time
                        })
                    else:
                        st.error(f"Error: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.warning("⚠️ Failed to connect to API. Is the FastAPI server running? Run `python start.py` to launch the backend.", icon="🔌")

with tab3:
    st.markdown("### 🔍 Advanced Anomaly Detection")
    st.markdown("<p style='color: #475569;'>Automatically scan your support tickets to find unusual patterns, outliers, or suspicious activities using Isolation Forest.</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("<div style='text-align: center;'><h1 style='font-size: 5rem; margin: 0; padding-top: 1rem;'>🕵️‍♂️</h1></div>", unsafe_allow_html=True)
        
    with col2:
        if st.button("⚡ Run Deep Analysis", use_container_width=True):
            with st.spinner("Scanning for anomalies..."):
                try:
                    response = requests.get(f"{API_URL}/anomalies")
                    if response.status_code == 200:
                        data = response.json()
                        anomalies = data.get('anomalies', [])
                        
                        # Calculate dynamic anomaly metrics
                        long_resolution = len([a for a in anomalies if a['type'] == 'Statistical'])
                        critical_open = len([a for a in anomalies if a['type'] == 'Heuristic'])
                        
                        # Calculate other metrics from DataFrame
                        slow_response = len(df[df['response_time_hrs'] > df['response_time_hrs'].mean() + 2 * df['response_time_hrs'].std()]) if 'response_time_hrs' in df.columns and len(df) > 0 else 0
                        missing_rating = len(df[(df['status'] == 'Resolved') & df['customer_rating'].isnull()]) if 'status' in df.columns and 'customer_rating' in df.columns else 0

                        st.markdown(f"""
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; width: 100%;">
                            <div class="metric-card card-open">
                                <div class="card-icon orange-gradient">⏱️</div>
                                <div class="card-content">
                                    <span class="card-label">Long Resolution</span>
                                    <span class="card-val">{long_resolution}</span>
                                </div>
                            </div>
                            <div class="metric-card card-critical">
                                <div class="card-icon red-gradient">🚨</div>
                                <div class="card-content">
                                    <span class="card-label">Critical Open</span>
                                    <span class="card-val">{critical_open}</span>
                                </div>
                            </div>
                            <div class="metric-card card-escalated">
                                <div class="card-icon purple-gradient">🐢</div>
                                <div class="card-content">
                                    <span class="card-label">Slow Response</span>
                                    <span class="card-val">{slow_response}</span>
                                </div>
                            </div>
                            <div class="metric-card card-total">
                                <div class="card-icon blue-gradient">⭐</div>
                                <div class="card-content">
                                    <span class="card-label">Missing Rating</span>
                                    <span class="card-val">{missing_rating}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.success(f"Analysis Complete! Found **{data.get('count')}** primary anomalies.")
                        
                        if data.get('count') > 0:
                            st.markdown("#### 🚨 Detected Anomalies")
                            # Use Streamlit Column Config for better dataframe UI
                            df_anomalies = pd.DataFrame(anomalies)
                            st.dataframe(
                                df_anomalies,
                                use_container_width=True,
                                column_config={
                                    "ticket_id": st.column_config.TextColumn("Ticket ID", width="small"),
                                    "type": st.column_config.TextColumn("Type", width="small"),
                                    "reason": st.column_config.TextColumn("Anomaly Reason", width="medium"),
                                    "details": st.column_config.TextColumn("Details", width="large")
                                },
                                hide_index=True
                            )
                    else:
                        st.error(f"Error: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.warning("⚠️ Failed to connect to API. Is the FastAPI server running? Run `python start.py` to launch the backend.", icon="🔌")
