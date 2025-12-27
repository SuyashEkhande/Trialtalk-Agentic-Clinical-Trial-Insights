"""Main Streamlit application for TrialTalk - Clinical Trial AI Assistant."""
import streamlit as st
import uuid
import asyncio
from client.agent_client import agent_client

# Page configuration for a premium feel
st.set_page_config(
    page_title="TrialTalk | Clinical Trial Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin-bottom: 20px !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Center Cards for Popular Queries */
    .query-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .query-card:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: #3b82f6;
        transform: translateY(-5px);
    }

    /* Header Styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(to right, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        color: #94a3b8;
        font-size: 1.25rem;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    /* Sidebar Section */
    .sidebar-section {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

# Helper function to run async code
def run_async(coro):
    """Run async coroutine in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/microscope.png", width=60)
    st.markdown("<h2 style='color: white; margin-top: 0;'>TrialTalk</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section">
        <h4 style="margin-top:0; color: #60a5fa;">📊 Data Source</h4>
        <p style="font-size: 0.9rem; color: #94a3b8;">
            Directly connected to <b>ClinicalTrials.gov API v2</b>. 
            Accessing the world's largest database of privately and publicly funded clinical studies.
        </p>
    </div>
    
    <div class="sidebar-section">
        <h4 style="margin-top:0; color: #a78bfa;">🔗 Platform</h4>
        <p style="font-size: 0.9rem; color: #94a3b8;">
            Powered by <b>FastMCP</b> (Model Context Protocol). 
            This enables safe, standardized tool discovery between the AI agent and medical databases.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4()) # New session on reset
        try:
            run_async(agent_client.delete_session(st.session_state.session_id))
        except:
            pass
        st.rerun()
    
    st.divider()
    st.caption("TrialTalk v1.1.0 | Real-time Medical Analysis")

# Main UI
if not st.session_state.messages:
    # Landing Page / Hero Section
    st.markdown('<h1 class="main-header">TrialTalk AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent Clinical Trial Search & Analysis</p>', unsafe_allow_html=True)
    
    st.markdown("### 💡 Try a popular query to start")
    
    col1, col2 = st.columns(2)
    
    popular_queries = [
        ("Diabetes Trials", "Find active trials for diabetes"),
        ("Lung Cancer", "Phase 3 lung cancer trials"),
        ("New York Recruiting", "Trials recruiting in New York"),
        ("Inclusion Criteria", "Explain eligibility criteria for NCT04852770")
    ]
    
    for i, (label, query) in enumerate(popular_queries):
        with col1 if i % 2 == 0 else col2:
            if st.button(f"🔍 {label}", key=f"q_{i}", use_container_width=True, help=query):
                st.session_state.active_prompt = query
else:
    # Chat View
    st.markdown("### 🔬 TrialTalk Analysis")
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("thinking"):
                with st.expander("💭 View Reasoning"):
                    for step in message["thinking"]:
                        if step["type"] == "tool_start":
                            st.markdown(f"**🔧 Using Tool:** `{step['data']['tool']}`")
                            st.code(step['data']['input'], language="json")
                        elif step["type"] == "agent_action":
                            log_text = step['data'].get("log", "")
                            if "Thought:" in log_text:
                                thought = log_text.split("Action:")[0].replace("Thought:", "").strip()
                                if thought: st.write(f"🤔 {thought}")
                            else:
                                st.write(f"🤖 Action: {step['data'].get('tool', 'Thinking...')}")
            st.markdown(message["content"])

# Handle quick-action prompts
if "active_prompt" in st.session_state:
    prompt = st.session_state.active_prompt
    del st.session_state.active_prompt
else:
    prompt = st.chat_input("Ask about clinical trials...", disabled=st.session_state.processing)

# Process query
if prompt:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # If it's the first message, we need to rerun to hide the hero section but st.chat_message handles it
    # We'll force a redraw by not using st.rerun until the end
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing Clinical Trials..."):
            st.session_state.processing = True
            
            try:
                # Call agent API
                response = run_async(
                    agent_client.query(prompt, st.session_state.session_id)
                )
                
                # Update UI with thinking and response
                thinking_steps = response.get("thinking_steps", [])
                if thinking_steps:
                    with st.expander("💭 View Reasoning", expanded=False):
                        for step in thinking_steps:
                            if step["type"] == "tool_start":
                                st.markdown(f"**🔧 Using Tool:** `{step['data']['tool']}`")
                                st.code(step['data']['input'], language="json")
                            elif step["type"] == "agent_action":
                                log_text = step['data'].get("log", "")
                                if "Thought:" in log_text:
                                    thought = log_text.split("Action:")[0].replace("Thought:", "").strip()
                                    if thought: st.write(f"🤔 {thought}")
                                else:
                                    st.write(f"🤖 Action: {step['data'].get('tool', 'Thinking...')}")
                
                ai_message = response["response"]
                st.markdown(ai_message)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_message,
                    "thinking": thinking_steps
                })
                
            except Exception as e:
                error_msg = f"**Connection Error:** {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
            
            finally:
                st.session_state.processing = False
                st.rerun()
