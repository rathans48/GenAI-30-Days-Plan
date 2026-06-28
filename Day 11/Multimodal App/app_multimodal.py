import os
import streamlit as st
import base64
from openai import OpenAI
from dotenv import load_dotenv
from streamlit_mic_recorder import speech_to_text

load_dotenv()

st.set_page_config(page_title="Day 11: Free Multi-Modal Engine", page_icon="👁️", layout="wide")
st.title("👁️ Day 11: Multi-Modal Vision & Voice Interface")
st.subheader("Free-Tier Visual Intelligence & Browser Voice Pipeline")

# Initialize OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def encode_image_to_base64(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode("utf-8")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📦 Input Modality Vault")
    
    # 1. Image Asset Upload
    uploaded_image = st.file_uploader("Upload a system diagram or image:", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        st.image(uploaded_image, caption="Ingested Visual Asset", use_container_width=True)
        
    st.write("---")
    st.markdown("### 🎙️ Voice Command Input")
    
    # 2. Free Browser-Native Speech-to-Text Widget
    # It renders a native button that captures speech and transcribes it directly via the browser engine.
    voice_transcription = speech_to_text(
        language='en',
        start_prompt="🎙️ Click to Speak Command",
        stop_prompt="🛑 Stop & Transcribe",
        just_once=True,
        use_container_width=True,
        key='browser_stt'
    )
    
    # Track the final prompt state across browser text and voice
    if voice_transcription:
        st.success(f"🗣️ Transcribed Command: '{voice_transcription}'")
        st.session_state["active_prompt"] = voice_transcription

    # Fallback/Manual Text Box (Synced with session state if voice ran)
    default_text = st.session_state.get("active_prompt", "")
    user_question = st.text_input("Confirm or type your question here:", value=default_text)

with col2:
    st.header("🤖 Multi-Modal Engine Output")
    
    if st.button("Execute Multi-Modal Analysis"):
        if not uploaded_image:
            st.warning("Please upload an image asset first to provide context.")
        elif not user_question:
            st.warning("Please provide a text or voice question regarding the uploaded asset.")
        else:
            # LOADING CIRCLE: Fired during active visual-token processing
            with st.spinner("🧠 Analyzing image assets... Routing token blocks to the model..."):
                try:
                    base64_image = encode_image_to_base64(uploaded_image)
                    
                    # Target OpenRouter's auto-routing layer for free vision processing
                    response = client.chat.completions.create(
                        model="openrouter/free",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": user_question},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                        ]
                    )
                    
                    st.markdown("### 🎯 Model Analysis Result:")
                    st.info(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Vision Engine Processing Error: {e}")