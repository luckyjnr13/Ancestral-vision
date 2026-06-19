import streamlit as st
import google.generativeai as genai
from googletrans import Translator
import speech_recognition as sr
from PIL import Image
import wikipedia
import random

st.set_page_config(page_title="Ancestral Vision", page_icon="🌍", layout="wide")

GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    st.error("Add GOOGLE_API_KEY in Streamlit Cloud > Settings > Secrets")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
translator = Translator()
recognizer = sr.Recognizer()

if "messages" not in st.session_state:
    st.session_state.messages = []

HEROES = {
    "Sango (Yoruba)": "You are Sango, Yoruba god of thunder. Speak boldly with proverbs.",
    "Anansi (Akan)": "You are Anansi the spider. Be witty and teach lessons through stories.",
    "Athena (Greek)": "You are Athena, goddess of wisdom. Answer clearly and strategically.",
    "Thor (Norse)": "You are Thor. Speak strong and direct about strength and storms.",
    "Amaterasu (Japanese)": "You are Amaterasu, sun goddess. Be warm and enlightening.",
    "Quetzalcoatl (Aztec)": "You are Quetzalcoatl, feathered serpent. Speak about knowledge."
}

LANGUAGES = {"English": "en", "Yoruba": "yo", "Hausa": "ha", "Igbo": "ig",
             "French": "fr", "Arabic": "ar", "Japanese": "ja", "Spanish": "es",
             "Swahili": "sw", "Zulu": "zu", "Portuguese": "pt", "German": "de"}

st.title("🌍 Ancestral Vision")
hero = st.selectbox("Choose your hero:", list(HEROES.keys()))
lang = st.selectbox("Choose language:", list(LANGUAGES.keys()))

col1, col2 = st.columns(2)
with col1:
    img_file = st.camera_input("📸 Snap photo for vision mode")
with col2:
    uploaded_img = st.file_uploader("Or upload image", type=["jpg","png","jpeg"])

if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

voice_btn = st.button("🎤 Tap then speak")
user_input = st.text_input("Ask anything, or type: vision / fact / quiz")

if voice_btn:
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = recognizer.listen(source, timeout=8)
        try:
            user_input = recognizer.recognize_google(audio)
            st.success(f"You said: {user_input}")
        except:
            st.error("Couldn’t hear clearly")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if st.button("Send") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    prompt = HEROES

    if ("vision" in user_input.lower()) and (img_file or uploaded_img):
        img = Image.open(img_file if img_file else uploaded_img)
        st.image(img, caption="Analyzing...")
        prompt += f"\nDescribe this image in detail, then answer: {user_input}"
    elif user_input.lower().startswith("fact"):
        topic = user_input.replace("fact", "").strip()
        try:
            fact = wikipedia.summary(topic, sentences=3)
            prompt += f"\nExplain {topic} using: {fact}"
        except:
            prompt += f"\nExplain {topic}"
    elif user_input.lower() == "quiz":
        q = random.choice(["Who wields Mjolnir?", "Which Yoruba god controls thunder?", "Athena’s animal?"])
        prompt += f"\nAsk this quiz: {q} then explain answer"
    else:
        prompt += f"\nUser: {user_input}\nAnswer fully, in character."

    response = model.generate_content(prompt).text
    if lang != "English":
        response = translator.translate(response, dest=LANGUAGES).text

    st.session_state.messages.append({"role": hero, "content": response})

    with st.chat_message(hero):
        st.write(response)

st.caption("Unlimited chat + vision. Needs GOOGLE_API_KEY to work.")