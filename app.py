"""
HeyGen Interactive Avatar Simulation - Flu Vaccination Program
=============================================================
This application implements a three-phase healthcare simulation with automatic flow:
1. NOA SANDOVAL (Pre-briefing) - Virtual instructor introduces the simulation
2. SAM RICHARDS (Main simulation) - Patient with vaccine hesitancy concerns  
3. NOA SANDOVAL (Debriefing) - Virtual instructor provides feedback

The simulation automatically progresses: Noa → Sam → Noa
"""

import streamlit as st
import json
import requests
import os
from datetime import datetime
import streamlit.components.v1 as components
from pathlib import Path
from enum import Enum

# Page configuration
st.set_page_config(
    page_title="Interactive Avatar Simulation - Flu Vaccination Program",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simulation phases
class SimulationPhase(Enum):
    PRE_BRIEFING = "pre_briefing"
    MAIN_SIMULATION = "main_simulation"
    DEBRIEFING = "debriefing"

# Phase names mapping - Using string values for reliability
phase_names = {
    "pre_briefing": "Pre-Briefing (Noa)",
    "main_simulation": "Main Simulation (Sam)",
    "debriefing": "Debriefing (Noa)"
}

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'simulation_phase' not in st.session_state:
    st.session_state.simulation_phase = SimulationPhase.PRE_BRIEFING
if 'simulation_started' not in st.session_state:
    st.session_state.simulation_started = False
if 'current_avatar' not in st.session_state:
    st.session_state.current_avatar = "noa"  # Start with Noa
if 'phase_completed' not in st.session_state:
    st.session_state.phase_completed = {
        SimulationPhase.PRE_BRIEFING: False,
        SimulationPhase.MAIN_SIMULATION: False,
        SimulationPhase.DEBRIEFING: False
    }

# Avatar configurations
AVATARS = {
    "noa": {
        "name": "Noa Sandoval",
        "avatar_id": "June_HR_public",
        "knowledge_base_id": "96b0ed06f07640459bcac16439103895",
        "role": "Virtual Simulation Instructor",
        "description": "Handles pre-briefing and debriefing"
    },
    "sam": {
        "name": "Sam Richards",
        "avatar_id": "Shawn_Therapist_public",
        "knowledge_base_id": "15a0063f43ed4d1c92f5a269dc0b8f9b",
        "role": "Simulation Character",
        "description": "Patient in the Flu Vaccination Program simulation"
    }
}

# Load configuration
def load_config():
    """Load configuration from config.json or Streamlit secrets"""
    config = {}
    
    # Try to load from Streamlit secrets first
    try:
        config['heygen_api_key'] = st.secrets["heygen_api_key"]
    except:
        # If not in secrets, try config.json
        try:
            with open('config.json', 'r') as f:
                file_config = json.load(f)
                config['heygen_api_key'] = file_config.get('heygen_api_key', '')
        except FileNotFoundError:
            config['heygen_api_key'] = ''
    
    return config

# Create HeyGen session with knowledge base
def create_streaming_session(api_key, avatar_id, knowledge_base_id=None):
    """Create a new streaming session with HeyGen"""
    url = "https://api.heygen.com/v1/streaming.new"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "avatar_id": avatar_id,
        "quality": "high",
        "voice": {
            "voice_id": "default"
        }
    }
    
    # Add knowledge base if provided
    if knowledge_base_id:
        data["knowledge_base_id"] = knowledge_base_id
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to create session: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error creating session: {str(e)}")
        return None

# Phase-specific scripts
def get_phase_scripts(phase):
    """Get default scripts for each phase"""
    scripts = {
        SimulationPhase.PRE_BRIEFING: [
            {
                "text": "Hello! I'm Noa Sandoval, your virtual simulation instructor. Welcome to the Flu Vaccination Program simulation.",
                "emotion": "friendly"
            },
            {
                "text": "In this simulation, you'll be interacting with Sam Richards, a patient who has concerns about getting the flu vaccine. Your goal is to address their concerns professionally and provide accurate information.",
                "emotion": "professional"
            },
            {
                "text": "Remember to listen actively, show empathy, and use evidence-based information. Are you ready to begin the simulation?",
                "emotion": "encouraging"
            }
        ],
        SimulationPhase.MAIN_SIMULATION: [
            {
                "text": "Hi there. I'm Sam Richards. I received a letter about getting a flu shot, but I'm not sure if I really need it. I've heard some concerning things about vaccines.",
                "emotion": "concerned"
            }
        ],
        SimulationPhase.DEBRIEFING: [
            {
                "text": "Welcome back! I'm Noa again. Let's debrief your simulation experience with Sam Richards.",
                "emotion": "friendly"
            },
            {
                "text": "You did a great job addressing Sam's concerns about the flu vaccine. Let's review what went well and areas for improvement.",
                "emotion": "encouraging"
            },
            {
                "text": "Key takeaways: Always validate patient concerns, provide evidence-based information, and maintain a professional yet empathetic approach. Do you have any questions about the simulation?",
                "emotion": "professional"
            }
        ]
    }
    return scripts.get(phase, [])

# Switch avatar based on phase
def switch_avatar(avatar_key):
    """Switch to a different avatar"""
    st.session_state.current_avatar = avatar_key
    st.session_state.session_id = None  # Reset session for new avatar

# Helper function to get phase name
def get_phase_name(phase):
    """Get the display name for a phase"""
    if isinstance(phase, SimulationPhase):
        return phase_names.get(phase.value, "Unknown Phase")
    return phase_names.get(str(phase), "Unknown Phase")

# Sidebar configuration
with st.sidebar:
    st.title("🏥 Simulation Control")
    
    config = load_config()
    api_key = ""
    
    # API key handling - check secrets first, then allow manual input
    if config and config.get('heygen_api_key'):
        api_key = config['heygen_api_key']
        st.success("✅ API Key loaded from secrets")
    else:
        api_key = st.text_input("HeyGen API Key", 
                               value='', 
                               type="password",
                               help="Your HeyGen API key (or add to Streamlit secrets)")
    
    st.divider()
    
    # Current phase display
    st.subheader("📍 Current Phase")
    st.info(get_phase_name(st.session_state.simulation_phase))
    
    # Current avatar info
    current_avatar_info = AVATARS[st.session_state.current_avatar]
    st.subheader(f"👤 Current Avatar")
    st.write(f"**{current_avatar_info['name']}**")
    st.write(f"Role: {current_avatar_info['role']}")
    
    st.divider()
    
    # Phase navigation
    st.subheader("🎯 Simulation Flow")
    
    # Visual flow indicator
    if st.session_state.simulation_phase == SimulationPhase.PRE_BRIEFING:
        st.markdown("**→ NOA (Pre-Brief) → Sam → Noa**")
    elif st.session_state.simulation_phase == SimulationPhase.MAIN_SIMULATION:
        st.markdown("**Noa → SAM (Simulation) → Noa**")
    else:
        st.markdown("**Noa → Sam → NOA (Debrief)**")
    
    # Automatic progression buttons
    if st.session_state.simulation_started:
        if st.session_state.simulation_phase == SimulationPhase.PRE_BRIEFING:
            if st.button("✅ Pre-Brief Complete - Start Simulation", use_container_width=True, type="primary"):
                st.session_state.simulation_phase = SimulationPhase.MAIN_SIMULATION
                st.session_state.phase_completed[SimulationPhase.PRE_BRIEFING] = True
                switch_avatar("sam")
                
                # Queue Sam's initial greeting
                sam_scripts = get_phase_scripts(SimulationPhase.MAIN_SIMULATION)
                if sam_scripts:
                    st.session_state.pending_script = sam_scripts[0]
                    st.session_state.conversation_history.append({
                        "role": "avatar",
                        "content": sam_scripts[0]['text'],
                        "emotion": sam_scripts[0].get('emotion', 'neutral'),
                        "timestamp": datetime.now().isoformat(),
                        "avatar": "sam"
                    })
                
                st.rerun()
        
        elif st.session_state.simulation_phase == SimulationPhase.MAIN_SIMULATION:
            if st.button("✅ Simulation Complete - Start Debrief", use_container_width=True, type="primary"):
                st.session_state.simulation_phase = SimulationPhase.DEBRIEFING
                st.session_state.phase_completed[SimulationPhase.MAIN_SIMULATION] = True
                switch_avatar("noa")
                
                # Queue Noa's debrief welcome
                debrief_scripts = get_phase_scripts(SimulationPhase.DEBRIEFING)
                if debrief_scripts:
                    st.session_state.pending_script = debrief_scripts[0]
                    st.session_state.conversation_history.append({
                        "role": "avatar",
                        "content": debrief_scripts[0]['text'],
                        "emotion": debrief_scripts[0].get('emotion', 'neutral'),
                        "timestamp": datetime.now().isoformat(),
                        "avatar": "noa"
                    })
                
                st.rerun()
        
        else:  # DEBRIEFING
            if st.button("🎓 Complete Session", use_container_width=True, type="primary"):
                st.session_state.phase_completed[SimulationPhase.DEBRIEFING] = True
                st.success("Simulation completed successfully!")
    
    st.divider()
    
    # Progress tracker
    st.subheader("📊 Progress")
    for phase, completed in st.session_state.phase_completed.items():
        if completed:
            st.success(f"✅ {get_phase_name(phase)}")
        else:
            st.info(f"⏳ {get_phase_name(phase)}")
    
    st.divider()
    
    if st.button("🔄 Reset Simulation", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.simulation_phase = SimulationPhase.PRE_BRIEFING
        st.session_state.simulation_started = False
        st.session_state.session_id = None
        st.session_state.current_avatar = "noa"
        st.session_state.phase_completed = {
            SimulationPhase.PRE_BRIEFING: False,
            SimulationPhase.MAIN_SIMULATION: False,
            SimulationPhase.DEBRIEFING: False
        }
        st.rerun()

# Main content area
st.title("💉 Flu Vaccination Program Simulation")

# Flow indicator at the top
col_flow1, col_flow2, col_flow3 = st.columns(3)
with col_flow1:
    if st.session_state.simulation_phase == SimulationPhase.PRE_BRIEFING:
        st.info("**📍 STEP 1: Pre-Brief with Noa**")
    else:
        st.success("✅ Pre-Brief Complete")

with col_flow2:
    if st.session_state.simulation_phase == SimulationPhase.MAIN_SIMULATION:
        st.info("**📍 STEP 2: Simulation with Sam**")
    elif st.session_state.phase_completed[SimulationPhase.MAIN_SIMULATION]:
        st.success("✅ Simulation Complete")
    else:
        st.info("⏳ Simulation Pending")

with col_flow3:
    if st.session_state.simulation_phase == SimulationPhase.DEBRIEFING:
        st.info("**📍 STEP 3: Debrief with Noa**")
    elif st.session_state.phase_completed[SimulationPhase.DEBRIEFING]:
        st.success("✅ Debrief Complete")
    else:
        st.info("⏳ Debrief Pending")

st.markdown("---")

# Create two columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Avatar display area
    avatar_info = AVATARS[st.session_state.current_avatar]
    st.subheader(f"🎭 {avatar_info['name']} - {avatar_info['role']}")
    
    avatar_container = st.container()
    
    with avatar_container:
        if not st.session_state.simulation_started:
            # Check if API key is configured
            if not api_key:
                st.warning("⚠️ Please configure your HeyGen API key in the sidebar or add it to Streamlit secrets")
                st.info("For Streamlit Cloud: Add `heygen_api_key = 'YOUR_KEY'` to your app's secrets")
            else:
                if st.button("🚀 Start Simulation", use_container_width=True):
                    with st.spinner(f"Initializing {avatar_info['name']}..."):
                        session_data = create_streaming_session(
                            api_key, 
                            avatar_info['avatar_id'],
                            avatar_info['knowledge_base_id']
                        )
                        if session_data:
                            st.session_state.session_id = session_data.get('session_id')
                            st.session_state.simulation_started = True
                            
                            # Automatically start with Noa's introduction
                            initial_scripts = get_phase_scripts(SimulationPhase.PRE_BRIEFING)
                            if initial_scripts:
                                st.session_state.pending_script = initial_scripts[0]
                                st.session_state.conversation_history.append({
                                    "role": "avatar",
                                    "content": initial_scripts[0]['text'],
                                    "emotion": initial_scripts[0].get('emotion', 'neutral'),
                                    "timestamp": datetime.now().isoformat(),
                                    "avatar": "noa"
                                })
                            
                            st.rerun()
        else:
            # Load and inject the custom HTML/JS component
            try:
                html_file = Path("avatar_component.html").read_text()
                
                # Replace placeholders with actual values
                html_content = html_file.replace("{{SESSION_ID}}", st.session_state.session_id or "")
                html_content = html_content.replace("{{API_KEY}}", api_key)
                html_content = html_content.replace("{{KNOWLEDGE_BASE_ID}}", avatar_info['knowledge_base_id'])
                
                # Display the avatar component
                components.html(html_content, height=600)
            except FileNotFoundError:
                st.error("avatar_component.html file not found. Please ensure all files are in the project directory.")
    
    # Control buttons for phase scripts
    st.divider()
    
    if st.session_state.simulation_started:
        phase_scripts = get_phase_scripts(st.session_state.simulation_phase)
        
        if st.session_state.simulation_phase == SimulationPhase.PRE_BRIEFING:
            st.write("**Pre-Briefing Controls:**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📋 Introduction"):
                    st.session_state.pending_script = phase_scripts[0]
            with col_b:
                if st.button("🎯 Objectives"):
                    st.session_state.pending_script = phase_scripts[1]
            with col_c:
                if st.button("✅ Ready Check"):
                    st.session_state.pending_script = phase_scripts[2]
        
        elif st.session_state.simulation_phase == SimulationPhase.MAIN_SIMULATION:
            st.write("**Simulation Controls:**")
            user_input = st.text_input("💬 Your response to Sam:", 
                                      placeholder="Type your response here...",
                                      key="user_response")
            
            if st.button("Send Response", use_container_width=True) and user_input:
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                # In a real implementation, this would trigger Sam's response
                # based on the knowledge base
        
        elif st.session_state.simulation_phase == SimulationPhase.DEBRIEFING:
            st.write("**Debriefing Controls:**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("👋 Welcome Back"):
                    st.session_state.pending_script = phase_scripts[0]
            with col_b:
                if st.button("📊 Performance Review"):
                    st.session_state.pending_script = phase_scripts[1]
            with col_c:
                if st.button("📚 Key Takeaways"):
                    st.session_state.pending_script = phase_scripts[2]

with col2:
    # Conversation history and notes
    st.subheader("📝 Session Notes")
    
    tabs = st.tabs(["Conversation History", "Learning Notes"])
    
    with tabs[0]:
        history_container = st.container(height=600)
        
        with history_container:
            if st.session_state.conversation_history:
                for entry in st.session_state.conversation_history:
                    if entry['role'] == 'user':
                        st.chat_message("user").write(entry['content'])
                    else:
                        with st.chat_message("assistant"):
                            st.write(entry['content'])
                            if 'emotion' in entry:
                                st.caption(f"Emotion: {entry.get('emotion', 'neutral')}")
            else:
                st.info("Conversation history will appear here...")
    
    with tabs[1]:
        st.text_area("📝 Your notes:", height=550, key="user_notes",
                    placeholder="Take notes during the simulation...")

# Script processing for avatar
if 'pending_script' in st.session_state and st.session_state.simulation_started:
    # Add script to conversation history
    script = st.session_state.pending_script
    st.session_state.conversation_history.append({
        "role": "avatar",
        "content": script['text'],
        "emotion": script.get('emotion', 'neutral'),
        "timestamp": datetime.now().isoformat(),
        "avatar": st.session_state.current_avatar
    })
    
    # Clear pending script
    del st.session_state.pending_script
    st.rerun()
