# HeyGen Flu Vaccination Simulation - Dual Avatar System

This application integrates HeyGen's Interactive Avatar API with Streamlit to create an immersive healthcare communication training simulation. It features two interactive AI avatars: Noa Sandoval (instructor) and Sam Richards (patient), specifically designed for the "Implementing Flu Vaccination Program" simulation.

## 🎯 Features

- **Dual Avatar System**: Two distinct avatars for different simulation phases
  - **Noa Sandoval**: Virtual instructor for pre-briefing and debriefing
  - **Sam Richards**: Patient character for the main simulation
- **Three-Phase Structure**: Pre-briefing → Main Simulation → Debriefing
- **Pre-configured Knowledge Bases**: Each avatar has their own knowledge base
- **Real-time WebRTC Communication**: Low-latency avatar interactions
- **Progress Tracking**: Monitor completion of each simulation phase
- **Conversation History**: Track all interactions during the session
- **Session Notes**: Take notes during the simulation for later review

## 📋 Prerequisites

Before you begin, you'll need:

1. **HeyGen API Key**: Get yours from [HeyGen Dashboard](https://app.heygen.com/settings/api)
2. **Python 3.8+**: Required for running Streamlit
3. **Modern Web Browser**: Chrome, Firefox, or Edge with WebRTC support

### Pre-configured Components

This simulation comes with the following pre-configured elements:

**Avatars:**
- **Noa Sandoval** (Avatar ID: `June_HR_public`)
  - Role: Virtual Simulation Instructor
  - Knowledge Base ID: `96b0ed06f07640459bcac16439103895`
  
- **Sam Richards** (Avatar ID: `Shawn_Therapist_public`)
  - Role: Patient in Flu Vaccination Simulation
  - Knowledge Base ID: `15a0063f43ed4d1c92f5a269dc0b8f9b`

## 🚀 Quick Start

### 1. Clone or Download Files

Create a new directory for your project and add all the provided files:

```
your-project/
├── app.py                      # Main Streamlit application
├── avatar_component.html       # WebRTC component for avatar
├── config.json                 # Configuration file (optional if using secrets)
├── flu_simulation_scripts.json # Pre-written simulation scripts
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── INSTRUCTOR_GUIDE.md         # Quick reference for facilitators
├── .gitignore                  # Git ignore file
└── .streamlit/
    └── secrets.toml           # Streamlit secrets (create this locally)
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Your API Key

You have two options for configuring your HeyGen API key:

#### Option A: Using Streamlit Secrets (Recommended)
Create a `.streamlit` folder in your project directory and add a `secrets.toml` file:

```bash
mkdir .streamlit
```

Then create `.streamlit/secrets.toml`:
```toml
heygen_api_key = "YOUR_ACTUAL_API_KEY_HERE"
```

#### Option B: Using config.json
Edit `config.json` and add your API key:

```json
{
  "heygen_api_key": "YOUR_ACTUAL_API_KEY_HERE"
}
```

**Note**: The avatar IDs and knowledge base IDs are already pre-configured. The simulation flow is set to: Noa (Pre-Brief) → Sam (Simulation) → Noa (Debrief).

## 📖 Using the Simulation

### Starting a Session

1. **Launch the Application**: Run `streamlit run app.py`
2. **Enter API Key**: Input your HeyGen API key in the sidebar
3. **Start Simulation**: Click the "Start Simulation" button
4. **Phase Navigation**: Use the phase control buttons to move between:
   - Pre-Briefing (Noa)
   - Main Simulation (Sam)
   - Debriefing (Noa)

### During the Simulation

- **Pre-Briefing**: Click the topic buttons to hear Noa's instructions
- **Main Simulation**: Type responses to Sam's concerns in the text input
- **Debriefing**: Review your performance with Noa's feedback
- **Take Notes**: Use the notes section to record observations

### Best Practices for Students

1. **Listen Carefully**: Let Sam fully express concerns before responding
2. **Show Empathy**: Acknowledge Sam's worries as valid
3. **Provide Clear Information**: Use simple language, avoid jargon
4. **Build Trust**: Focus on rapport, not just information delivery
5. **Respect Autonomy**: Remember the goal is informed choice, not compliance

The application will open in your default browser at `http://localhost:8501`

## 🎭 Simulation Flow

The Flu Vaccination simulation follows an automatic three-phase structure:

### ➤ Phase 1: Pre-Briefing (NOA SANDOVAL)
- Noa automatically appears when simulation starts
- Provides introduction, objectives, and communication tips
- Student clicks "Pre-Brief Complete" when ready

### ➤ Phase 2: Main Simulation (SAM RICHARDS)
- Automatically switches to Sam after pre-briefing
- Sam presents as a vaccine-hesitant patient
- Student interacts through text responses
- Student clicks "Simulation Complete" when finished

### ➤ Phase 3: Debriefing (NOA SANDOVAL)
- Automatically returns to Noa for debriefing
- Reviews performance and provides feedback
- Discusses key learning points
- Student clicks "Complete Session" to finish

**The flow is always: Noa → Sam → Noa**

## 🎯 Learning Objectives

This simulation helps healthcare professionals develop:

1. **Communication Skills**
   - Active listening techniques
   - Empathetic response strategies
   - Clear health information delivery

2. **Vaccine Hesitancy Management**
   - Understanding common concerns
   - Addressing misinformation respectfully
   - Building patient trust

3. **Professional Practice**
   - Patient-centered care approach
   - Ethical consideration of autonomy
   - Evidence-based practice

## 🔧 Technical Configuration

### API Setup

The only required configuration is your HeyGen API key in `config.json`:

```json
"heygen_api_key": "YOUR_API_KEY_HERE"
```

### Pre-configured Elements

- **Avatar IDs**: Already set for Noa and Sam
- **Knowledge Base IDs**: Linked to each avatar
- **Simulation Scripts**: Pre-written in `flu_simulation_scripts.json`
- **Phase Flow**: Automated transitions between instructors

## 🚀 Deployment Options

### Streamlit Cloud (Recommended)

1. Push your code to GitHub (ensure `.gitignore` excludes sensitive data)
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. In Streamlit Cloud settings, go to "Secrets" and add:
   ```toml
   heygen_api_key = "YOUR_API_KEY_HERE"
   ```
5. Deploy your app

The app will automatically use the secret from Streamlit Cloud, no config.json needed!

### Local Network Deployment

For training sessions on local networks:
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 🐛 Troubleshooting

### Common Issues

1. **Avatar Not Loading**
   - Verify API key is correct
   - Check browser console for WebRTC errors
   - Ensure firewall allows WebRTC connections

2. **Knowledge Base Not Responding**
   - Verify knowledge base IDs match those in config
   - Check HeyGen dashboard for API usage limits
   - Ensure stable internet connection

3. **Phase Transitions Not Working**
   - Clear browser cache
   - Restart the Streamlit application
   - Check session state in browser developer tools

### Getting Help

- **HeyGen Support**: For API and avatar issues
- **Streamlit Forums**: For application framework questions
- **Browser Console**: Press F12 to view detailed error messages

## 📊 Extending the Simulation

### Adding More Scenarios

1. Create additional avatar pairs in HeyGen
2. Add their IDs to `config.json`
3. Create new script files for different medical scenarios
4. Modify `app.py` to include scenario selection

### Analytics Integration

Track student performance by adding:
- Response time tracking
- Decision path analysis
- Completion rates
- Performance scoring

## 🛡️ Important Notes

- **API Security**: Never commit your API key to version control
- **HIPAA Compliance**: This is a training simulation - no real patient data should be used
- **Browser Requirements**: Ensure students use modern browsers with WebRTC support
- **Network Requirements**: Stable internet connection required for avatar streaming

## 📝 License & Attribution

This simulation framework is designed for educational use with HeyGen's Interactive Avatar API. Ensure compliance with:
- HeyGen's terms of service
- Your institution's training protocols
- Healthcare education standards

---

**Ready to revolutionize healthcare communication training!** 🏥✨