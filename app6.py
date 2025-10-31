import streamlit as st
import assemblyai as aai
import openai
import time
import re
import yt_dlp

# =============================
# 🔧 SETUP CONFIGURATION
# =============================
st.set_page_config(page_title="Sales Call Analyzer", layout="wide")

st.title("🎧 Sales Conversation Analyzer")
st.markdown(
    "Upload a YouTube URL and automatically generate **transcription, engagement triggers**, "
    "and **objection handling insights**."
)

# =============================
# API KEYS
# =============================
# aai.settings.api_key = "71588ef4f2b2497abfa1a1e886337aa6"

# if not aai.settings.api_key or not openai.api_key:
#     st.warning("⚠️ Please set your AssemblyAI and OpenAI API keys in Streamlit Secrets.")
#     st.stop()


import streamlit as st
from openai import OpenAI
import assemblyai as aai

# Load AssemblyAI key if you also put it in Streamlit secrets
aai.settings.api_key = st.secrets.get("ASSEMBLYAI_API_KEY")  # optional

# Load OpenAI key
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

if not client.api_key:
    st.warning("⚠️ Please set your OpenAI API key in Streamlit Secrets.")
    st.stop()



# aai_api_key = st.secrets["api_keys"]["assemblyai"]
# openai_api_key = st.secrets["api_keys"]["openai"]

# aai.settings.api_key = aai_api_key
# openai.api_key = openai_api_key

# if not aai.settings.api_key or not openai.api_key:
#     st.warning("⚠️ Please set your AssemblyAI and OpenAI API keys in Streamlit Secrets.")
#     st.stop()

# =============================
# 📥 INPUT SECTION
# =============================
youtube_url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=example")

if youtube_url:
    # Extract YouTube Video ID (supports shorts too)
    video_id_match = re.search(r"(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})", youtube_url)
    if not video_id_match:
        st.error("❌ Invalid YouTube URL.")
        st.stop()

    st.info("✅ Valid YouTube URL detected. Fetching audio URL...")

    # =============================
    # 🎧 GET DIRECT AUDIO URL
    # =============================
    try:
        ydl_opts = {"format": "bestaudio/best", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            audio_url = info['url']  # Direct audio URL

        st.success("✅ Audio URL obtained successfully!")
    except Exception as e:
        st.error(f"❌ Failed to get audio URL: {e}")
        st.stop()

    # =============================
    # 🔊 TRANSCRIPTION
    # =============================
    st.header("Step 1: Transcribing Audio")
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(speaker_labels=True, language_code="en")

    with st.spinner("Transcribing audio... this may take a few minutes ⏳"):
        transcript = transcriber.transcribe(audio_url, config)

        while transcript.status not in ["completed", "error"]:
            time.sleep(5)
            transcript = aai.get_transcription(transcript.id)

        if transcript.status == "error":
            st.error(f"❌ Transcription failed: {transcript.error}")
            st.stop()

    st.success("✅ Transcription completed successfully!")

    # Store transcript text and utterances in memory
    transcript_text = transcript.text
    utterances = transcript.utterances  # speaker diarization

    st.subheader("📝 Full Transcript")
    st.text_area("Transcript Text", transcript_text, height=300)

    # =============================
    # 👥 FORMAT SPEAKER DIALOGUE
    # =============================
    st.header("Step 2: Speaker Separation")
    dialogue = []
    for utterance in utterances:
        dialogue.append({
            "speaker": f"Speaker {utterance.speaker}",
            "text": utterance.text,
            "start_time": utterance.start,
            "end_time": utterance.end
        })

    for utt in dialogue:
        st.markdown(
            f"**{utt['speaker']}** ({utt['start_time']/1000:.1f}s - {utt['end_time']/1000:.1f}s): {utt['text']}"
        )

    # =============================
    # 🤖 AI ANALYSIS FUNCTIONS
    # =============================
    # def detect_engagement_triggers(dialogue):
    #     prompt = """
    #     You are analyzing a conversation between a salesperson and a potential customer.
    #     Detect any *engagement triggers* from the prospect, such as:
    #     - Asking follow-up questions
    #     - Showing curiosity or agreement
    #     - Sharing personal context or needs
    #     - Asking for next steps or pricing

    #     Also, mention specific salesperson phrases that caused engagement.
    #     """
    #     for utterance in dialogue:
    #         prompt += f"{utterance['speaker']}: {utterance['text']}\n"

    #     response = openai.ChatCompletion.create(
    #     model="gpt-4",  # Use the desired model (e.g., gpt-4)
    #     messages=[
    #         {"role": "system", "content": "You are a sales call analysis assistant."},
    #         {"role": "user", "content": prompt},
    #     ],
    #     max_tokens=400,
    #     temperature=0.4,
    # )

    #     return response['choices'][0]['message']['content'].strip()
    from openai import OpenAI
    
    client = OpenAI(api_key=openai_api_key)



    def detect_engagement_triggers(dialogue):
        prompt = """
        You are analyzing a conversation between a salesperson and a potential customer.
        Detect any *engagement triggers* from the prospect, such as:
        - Asking follow-up questions
        - Showing curiosity or agreement
        - Sharing personal context or needs
        - Asking for next steps or pricing

        Also, mention specific salesperson phrases that caused engagement.
        """
        for utterance in dialogue:
            prompt += f"{utterance['speaker']}: {utterance['text']}\n"

        response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a sales call analysis assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=400,
        temperature=0.4,
    )

        return response.choices[0].message.content.strip()


    def analyze_objection_handling(dialogue):
        prompt = """
        Analyze how the salesperson handles objections from the customer.
        For each objection or hesitation:
        - Did the salesperson acknowledge it?
        - Did they redirect, challenge, or ignore it?
        - Provide an evaluation of effectiveness.
        """
        for utterance in dialogue:
            prompt += f"{utterance['speaker']}: {utterance['text']}\n"

        response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a sales call analysis assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=400,
        temperature=0.4,
    )

        return response.choices[0].message.content.strip()
        


    # =============================
    # 🧠 ANALYSIS SECTION
    # =============================
    st.header("Step 3: AI-Powered Insights")

    if st.button("🔍 Analyze Conversation"):
        with st.spinner("Analyzing engagement and objection handling..."):
            engagement_report = detect_engagement_triggers(dialogue)
            objection_report = analyze_objection_handling(dialogue)

        st.subheader("💬 Engagement Triggers")
        st.markdown(engagement_report)

        st.subheader("⚔️ Objection Handling Analysis")
        st.markdown(objection_report)
