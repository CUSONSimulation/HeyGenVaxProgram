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

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'session_data' not in st.session_state:
    st.session_state.session_data = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'simulation_phase' not in st.session_state:
    st.session_state.simulation_phase = SimulationPhase.PRE_BRIEFING
if 'simulation_started' not in st.session_state:
    st.session_state.simulation_started = False
if 'current_avatar' not in st.session_state:
    st.session_state.current_avatar = "noa"  # Start with Noa
if 'phase_completed' not in st.session_state:
    # Initialize with string keys to avoid enum issues
    st.session_state.phase_completed = {
        "pre_briefing": False,
        "main_simulation": False,
        "debriefing": False
    }

# Avatar configurations
AVATARS = {
    "noa": {
        "name": "Noa Sandoval",
        "avatar_id": "Kristin_public_3_20240108",  # Using a known public avatar
        "knowledge_base_id": "96b0ed06f07640459bcac16439103895",
        "role": "Virtual Simulation Instructor",
        "description": "Handles pre-briefing and debriefing"
    },
    "sam": {
        "name": "Sam Richards",
        "avatar_id": "Tyler_public_2_20230808",  # Using a known public avatar
        "knowledge_base_id": "15a0063f43ed4d1c92f5a269dc0b8f9b",
        "role": "Simulation Character",
        "description": "Patient in the Flu Vaccination Program simulation"
    }
}

# Helper function to get phase display name
def get_phase_display_name(phase):
    """Get the display name for a phase"""
    phase_names = {
        "pre_briefing": "Pre-Briefing (Noa)",
        "main_simulation": "Main Simulation (Sam)",
        "debriefing": "Debriefing (Noa)"
    }
    
    if isinstance(phase, SimulationPhase):
        return phase_names.get(phase.value, "Unknown Phase")
    return phase_names.get(str(phase), "Unknown Phase")

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
                
                # Check if it's still the placeholder
                if config['heygen_api_key'] == 'YOUR_HEYGEN_API_KEY_HERE':
                    config['heygen_api_key'] = ''
        except FileNotFoundError:
            config['heygen_api_key'] = ''
    
    return config

# Create streaming token from API key
def create_streaming_token(api_key):
    """Create a streaming token from API key"""
    url = "https://api.heygen.com/v1/streaming.create_token"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('data', {}).get('token')
        else:
            error_msg = f"Failed to create token: Status {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('message', str(error_detail))}"
            except:
                error_msg += f" - {response.text}"
            st.error(error_msg)
            
            if response.status_code == 401:
                st.error("⚠️ Invalid API key. Please check your HeyGen API key.")
            elif response.status_code == 403:
                st.error("⚠️ API key doesn't have permission for streaming avatars.")
            
            return None
    except Exception as e:
        st.error(f"Error creating token: {str(e)}")
        return None

# Create HeyGen session with knowledge base
def create_streaming_session(api_key, avatar_id, knowledge_base_id=None):
    """Create a new streaming session with HeyGen"""
    # First create a token
    token = create_streaming_token(api_key)
    if not token:
        return None
        
    url = "https://api.heygen.com/v1/streaming.new"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "quality": "high",
        "avatar_name": avatar_id
    }
    
    # Add knowledge base if provided
    if knowledge_base_id:
        data["knowledge_base_id"] = knowledge_base_id
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json().get('data', {})
            result['token'] = token  # Include token in response
            
            # Debug: Show what we got back
            st.success(f"Session created successfully! Session ID: {result.get('session_id', 'N/A')}")
            
            # Ensure all required fields are present
            if not all(key in result for key in ['session_id', 'access_token', 'url']):
                st.warning("Session created but some fields are missing. Available fields: " + str(list(result.keys())))
            
            return result
        else:
            error_msg = f"Failed to create session: Status {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('message', str(error_detail))}"
            except:
                error_msg += f" - {response.text}"
            st.error(error_msg)
            return None
    except Exception as e:
        st.error(f"Error creating session: {str(e)}")
        return None

# Send text to avatar to speak
def speak_to_avatar(api_key, session_id, text, emotion="neutral"):
    """Send text to avatar to speak"""
    token = create_streaming_token(api_key)
    if not token:
        return False
        
    url = "https://api.heygen.com/v1/streaming.task"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "session_id": session_id,
        "text": text,
        "task_type": "talk",
        "task_mode": "sync"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error speaking: {str(e)}")
        return False

# Stop avatar session
def stop_avatar_session(api_key, session_id):
    """Stop the avatar streaming session"""
    token = create_streaming_token(api_key)
    if not token:
        return False
        
    url = "https://api.heygen.com/v1/streaming.stop"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "session_id": session_id
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error stopping session: {str(e)}")
        return False

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
    # Stop current session if exists
    if st.session_state.session_id and 'api_key' in st.session_state:
        stop_avatar_session(st.session_state.api_key, st.session_state.session_id)
    
    st.session_state.current_avatar = avatar_key
    st.session_state.session_id = None
    st.session_state.session_data = None

# Get phase completion status
def is_phase_completed(phase):
    """Check if a phase is completed"""
    if isinstance(phase, SimulationPhase):
        return st.session_state.phase_completed.get(phase.value, False)
    return st.session_state.phase_completed.get(str(phase), False)

# Set phase completion status
def set_phase_completed(phase, completed=True):
    """Set phase completion status"""
    if isinstance(phase, SimulationPhase):
        st.session_state.phase_completed[phase.value] = completed
    else:
        st.session_state.phase_completed[str(phase)] = completed

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
        
        if not api_key:
            st.warning("⚠️ Please enter your HeyGen API key above")
            st.info("Get your API key from: https://app.heygen.com/settings?nav=API")
    
    # Store API key in session state for use in other functions
    if api_key:
        st.session_state.api_key = api_key
    
    st.divider()
    
    # Current phase display
    st.subheader("📍 Current Phase")
    st.info(get_phase_display_name(st.session_state.simulation_phase))
    
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
                set_phase_completed(SimulationPhase.PRE_BRIEFING)
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
                set_phase_completed(SimulationPhase.MAIN_SIMULATION)
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
                set_phase_completed(SimulationPhase.DEBRIEFING)
                st.success("Simulation completed successfully!")
    
    st.divider()
    
    # Progress tracker
    st.subheader("📊 Progress")
    phases = [
        (SimulationPhase.PRE_BRIEFING, "Pre-Briefing (Noa)"),
        (SimulationPhase.MAIN_SIMULATION, "Main Simulation (Sam)"),
        (SimulationPhase.DEBRIEFING, "Debriefing (Noa)")
    ]
    
    for phase, name in phases:
        if is_phase_completed(phase):
            st.success(f"✅ {name}")
        else:
            st.info(f"⏳ {name}")
    
    st.divider()
    
    if st.button("🔄 Reset Simulation", use_container_width=True):
        # Stop current session if exists
        if st.session_state.session_id and api_key:
            stop_avatar_session(api_key, st.session_state.session_id)
        
        st.session_state.conversation_history = []
        st.session_state.simulation_phase = SimulationPhase.PRE_BRIEFING
        st.session_state.simulation_started = False
        st.session_state.session_id = None
        st.session_state.session_data = None
        st.session_state.current_avatar = "noa"
        st.session_state.phase_completed = {
            "pre_briefing": False,
            "main_simulation": False,
            "debriefing": False
        }
        st.rerun()

# Main content area
st.title("💉 Flu Vaccination Program Simulation")

# Flow indicator at the top
col_flow1, col_flow2, col_flow3 = st.columns(3)
with col_flow1:
    if st.session_state.simulation_phase == SimulationPhase.PRE_BRIEFING:
        st.info("**📍 STEP 1: Pre-Brief with Noa**")
    elif is_phase_completed(SimulationPhase.PRE_BRIEFING):
        st.success("✅ Pre-Brief Complete")
    else:
        st.info("⏳ Pre-Brief Pending")

with col_flow2:
    if st.session_state.simulation_phase == SimulationPhase.MAIN_SIMULATION:
        st.info("**📍 STEP 2: Simulation with Sam**")
    elif is_phase_completed(SimulationPhase.MAIN_SIMULATION):
        st.success("✅ Simulation Complete")
    else:
        st.info("⏳ Simulation Pending")

with col_flow3:
    if st.session_state.simulation_phase == SimulationPhase.DEBRIEFING:
        st.info("**📍 STEP 3: Debrief with Noa**")
    elif is_phase_completed(SimulationPhase.DEBRIEFING):
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
                st.warning("⚠️ Please configure your HeyGen API key in the sidebar")
                st.info("📝 Steps to get started:")
                st.markdown("""
                1. **Get your API key**: Visit [HeyGen Settings](https://app.heygen.com/settings?nav=API)
                2. **Add your key**: Either:
                   - Enter it in the sidebar text field, OR
                   - For Streamlit Cloud: Add `heygen_api_key = 'YOUR_KEY'` to your app's secrets
                3. **Start the simulation**: Click the button below once your key is configured
                """)
                
                # Show button but disabled
                st.button("🚀 Start Simulation", use_container_width=True, disabled=True)
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
                            st.session_state.session_data = session_data
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
                            st.error("Failed to create avatar session. Please check your API key and try again.")
        else:
            # Load and inject the custom HTML/JS component
            try:
                html_file = Path("avatar_component.html").read_text()
                
                # Replace placeholders with actual values
                session_data = st.session_state.session_data or {}
                html_content = html_file.replace("{{SESSION_ID}}", st.session_state.session_id or "")
                html_content = html_content.replace("{{TOKEN}}", session_data.get('token', ''))
                html_content = html_content.replace("{{ACCESS_TOKEN}}", session_data.get('access_token', ''))
                html_content = html_content.replace("{{URL}}", session_data.get('url', ''))
                
                # Display the avatar component
                components.html(html_content, height=600)
            except FileNotFoundError:
                st.error("avatar_component.html file not found. Please ensure all files are in the project directory.")
            except Exception as e:
                st.error(f"Error loading avatar component: {str(e)}")
                st.info("Debug info: Session data keys: " + str(list(session_data.keys()) if session_data else "No session data"))
    
    # Control buttons for phase scripts
    st.divider()
    
    if st.session_state.simulation_started:
        phase_scripts = get_phase_scripts(st.session_state.simulation_phase)
        
        if st.session_state.simulation_phase == SimulationPhase.PRE_BRIEFING:
            st.write("**Pre-Briefing Controls:**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📋 Introduction"):
                    if speak_to_avatar(api_key, st.session_state.session_id, phase_scripts[0]['text']):
                        st.session_state.conversation_history.append({
                            "role": "avatar",
                            "content": phase_scripts[0]['text'],
                            "emotion": phase_scripts[0].get('emotion', 'neutral'),
                            "timestamp": datetime.now().isoformat(),
                            "avatar": st.session_state.current_avatar
                        })
                        st.rerun()
            with col_b:
                if st.button("🎯 Objectives"):
                    if speak_to_avatar(api_key, st.session_state.session_id, phase_scripts[1]['text']):
                        st.session_state.conversation_history.append({
                            "role": "avatar",
                            "content": phase_scripts[1]['text'],
                            "emotion": phase_scripts[1].get('emotion', 'neutral'),
                            "timestamp": datetime.now().isoformat(),
                            "avatar": st.session_state.current_avatar
                        })
                        st.rerun()
            with col_c:
                if st.button("✅ Ready Check"):
                    if speak_to_avatar(api_key, st.session_state.session_id, phase_scripts[2]['text']):
                        st.session_state.conversation_history.append({
                            "role": "avatar",
                            "content": phase_scripts[2]['text'],
                            "emotion": phase_scripts[2].get('emotion', 'neutral'),
                            "timestamp": datetime.now().isoformat(),
                            "avatar": st.session_state.current_avatar
                        })
                        st.rerun()
        
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
                st.rerun()
        
        elif st.session_state.simulation_phase == SimulationPhase.DEBRIEFING:
            st.write("**Debriefing Controls:**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("👋 Welcome Back"):
                    if speak_to_avatar(api_key, st.session_state.session_id, phase_scripts[0]['text']):
                        st.session_state.conversation_history.append({
                            "role": "avatar",
                            "content": phase_scripts[0]['text'],
                            "emotion": phase_scripts[0].get('emotion', 'neutral'),
                            "timestamp": datetime.now().isoformat(),
                            "avatar": st.session_state.current_avatar
                        })
                        st.rerun()
            with col_b:
                if st.button("📊 Performance Review"):
                    if speak_to_avatar(api_key, st.session_state.session_id, phase_scripts[1]['text']):
                        st.session_state.conversation_history.append({
                            "role": "avatar",
                            "content": phase_scripts[1]['text'],
                            "emotion": phase_scripts[1].get('emotion', 'neutral'),
                            "timestamp": datetime.now().isoformat(),
                            "avatar": st.session_state.current_avatar
                        })
                        st.rerun()
            with col_c:
                if st.button("📚 Key Takeaways"):
                    if speak_to_avatar(api_key, st.session_state.session_id, phase_scripts[2]['text']):
                        st.session_state.conversation_history.append({
                            "role": "avatar",
                            "content": phase_scripts[2]['text'],
                            "emotion": phase_scripts[2].get('emotion', 'neutral'),
                            "timestamp": datetime.now().isoformat(),
                            "avatar": st.session_state.current_avatar
                        })
                        st.rerun()

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

# Handle any pending scripts (for initial launch)
if 'pending_script' in st.session_state and st.session_state.simulation_started:
    script = st.session_state.pending_script
    
    # Send to avatar
    if speak_to_avatar(api_key, st.session_state.session_id, script['text']):
        # Clear pending script only if successfully sent
        del st.session_state.pending_script
