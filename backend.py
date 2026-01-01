import streamlit as st
import requests
import os
import time
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
QA_KEY = os.getenv("HUGGINGFACE_QA_KEY")
SUMMARIZE_KEY = os.getenv("HUGGINGFACE_SUMMARY_KEY")

# --- INITIAL SETUP ---
st.set_page_config(page_title="AI Assistant For Smart Learning", layout="centered")

# --- VIBRANT UI STYLING ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Bright Title Styling */
    h1 {
        color: #FF4B4B !important;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        text-align: center;
        text-shadow: 3px 3px #FFE0E0;
        font-size: 3.5rem !important;
        padding-bottom: 20px;
    }
    
    /* Sidebar Gradient */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(#6a11cb 0%, #2575fc 100%);
        color: white;
    }
    
    /* Sidebar Labels */
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p {
        color: white !important;
        font-weight: bold;
        font-size: 1.1rem;
    }

    /* Vibrant Section Headings */
    h2, h3 {
        color: #00C9FF !important;
        text-transform: uppercase;
        border-bottom: 3px solid #92FE9D;
        padding-bottom: 5px;
    }

    /* Radio Button Text to Black */
    [data-testid="stRadio"] label p {
        color: black !important;
        font-weight: 500;
    }

    /* Placeholder to Blue */
    input::placeholder, textarea::placeholder {
        color: #0000FF !important;
        opacity: 1; 
    }

    /* FIX: Force ALL generated text (Questions, MCQs, and Flashcard contents) to BLACK */
    .stMarkdown p, .stMarkdown span, .stAlert p, [data-testid="stExpander"] p {
        color: black !important;
    }

    /* Glow-up Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #FF512F, #DD2476);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 15px 30px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(221, 36, 118, 0.3);
        transition: 0.3s;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(221, 36, 118, 0.5);
        color: #FFEB3B !important;
    }

    /* Styling the Expanders (Flashcards) */
    .streamlit-expanderHeader {
        background-color: #ffffff;
        border: 1px solid #FF512F;
        border-radius: 10px;
        font-weight: bold;
        color: #DD2476 !important; /* Header remains vibrant pink-red */
    }
    </style>
    """, unsafe_allow_html=True)

# Check for keys
if not all([QA_KEY, SUMMARIZE_KEY]):
    st.error("🚨 One or more API keys are missing. Check your .env file.")
    st.stop()

qa_headers = {"Authorization": f"Bearer {QA_KEY}"}
sum_headers = {"Authorization": f"Bearer {SUMMARIZE_KEY}"}

# --- LOGIC FUNCTIONS ---
def hf_api_with_retries(url, headers, payload, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e

def generate_normal_questions(text):
    sentences = text.split(". ")
    return [f"What is the meaning of '{s.strip()}?'" for s in sentences if len(s.split()) > 5]

def generate_mcq_questions(text):
    sentences = text.split(". ")
    mcqs = []
    for sentence in sentences:
        if len(sentence.split()) > 5:
            correct_answer = sentence.strip()
            distractors = random.sample([s for s in sentences if s != sentence and len(s.split()) > 5], k=min(3, len(sentences)-1))
            options = [correct_answer] + distractors
            random.shuffle(options)
            question = f"What is described by the following statement?\n'{sentence.strip()}'"
            labels = ['A', 'B', 'C', 'D']
            labeled = {labels[i]: options[i] for i in range(len(options))}
            mcqs.append((question, labeled, correct_answer))
    return mcqs

def extract_flashcards(text):
    flashcards = []
    for sentence in text.split(". "):
        sentence = sentence.strip()
        if len(sentence.split()) > 5:
            if " is " in sentence:
                term = sentence.split(" is ", 1)[0].strip()
                flashcards.append((f"What is {term}?", sentence))
            elif " are " in sentence:
                term = sentence.split(" are ", 1)[0].strip()
                flashcards.append((f"What are {term}?", sentence))
    return flashcards

def clean_manual_flashcards(text):
    lines = text.strip().split('\n')
    cleaned, term, definition = [], "", ""
    for line in lines:
        line = line.strip()
        if not line: continue
        if ':' in line and line.index(':') < 40:
            if term and definition: cleaned.append(f"{term.strip()}: {definition.strip()}")
            term, definition = line.split(":", 1)
        elif len(line.split()) <= 6 and line.istitle():
            if term and definition: cleaned.append(f"{term.strip()}: {definition.strip()}")
            term, definition = line, ""
        else:
            definition += " " + line
    if term and definition: cleaned.append(f"{term.strip()}: {definition.strip()}")
    return cleaned

# --- APP UI ---
st.title("🚀 AI Assistant For Smart Learning")

option = st.sidebar.selectbox("🎯 Choose a Feature", [
    "🤔 Ask a Doubt", 
    "📝 Summarize Notes", 
    "❓ Generate Questions", 
    "🗂️ Flashcard Generator"
])

if "result_data" not in st.session_state:
    st.session_state.result_data = None

# --- FEATURES ---
if option == "🤔 Ask a Doubt":
    st.header("🤔 Ask a Doubt")
    context = st.text_area("📖 Paste your study material:", height=200, placeholder="Enter text here...")
    question = st.text_input("❓ Type your question:", placeholder="Enter text here...")
    if st.button("Get Answer"):
        if context and question:
            with st.spinner("🧠 Thinking..."):
                payload = {"inputs": {"question": question, "context": context}}
                answer = None
                try:
                    response = hf_api_with_retries(
                        "https://api-inference.huggingface.co/models/bert-large-uncased-whole-word-masking-finetuned-squad",
                        headers=qa_headers, payload=payload)
                    result = response.json()
                    answer = result.get("answer", "").strip()
                except: pass
                if not answer:
                    sentences = context.split(". ")
                    best_sentence = max(sentences, key=lambda s: len(set(s.lower().split()) & set(question.lower().split())), default="")
                    answer = best_sentence.strip() if best_sentence else "Sorry, I couldn't find a good answer."
                st.session_state.result_data = ("answer", answer)

elif option == "📝 Summarize Notes":
    st.header("📝 Summarize Notes")
    text = st.text_area("🗒️ Paste your notes:", height=250, placeholder="Enter text here...")
    if st.button("Summarize"):
        if text:
            with st.spinner("✨ Summarizing..."):
                try:
                    response = requests.post("https://api-inference.huggingface.co/models/facebook/bart-large-cnn", 
                                          headers=sum_headers, json={"inputs": text}, timeout=60)
                    summary = response.json()[0]["summary_text"]
                except:
                    summary = ". ".join(sorted(text.split(". "), key=lambda s: len(s.split()), reverse=True)[:3]) + "."
                st.session_state.result_data = ("summary", summary)

elif option == "❓ Generate Questions":
    st.header("❓ Question Generator")
    text = st.text_area("📖 Paste a topic:", height=250, placeholder="Enter text here...")
    q_type = st.radio("Style:", ["Normal", "MCQ"])
    if st.button("Generate"):
        if text:
            with st.spinner("✍️ Writing..."):
                if q_type == "Normal": st.session_state.result_data = ("questions", generate_normal_questions(text))
                else: st.session_state.result_data = ("mcqs", generate_mcq_questions(text))

elif option == "🗂️ Flashcard Generator":
    st.header("🗂️ Flashcard Generator")
    f_mode = st.radio("Mode:", ["Manual (Term: Definition)", "Auto Extract"])
    f_text = st.text_area("📘 Paste notes:", height=250, placeholder="Enter text here...")
    if st.button("Create Flashcards"):
        if f_text:
            with st.spinner("✂️ Snipping..."):
                if f_mode == "Manual (Term: Definition)":
                    cards = [(f"What is {i.split(':',1)[0].strip()}?", i.split(':',1)[1].strip()) for i in clean_manual_flashcards(f_text) if ':' in i]
                    st.session_state.result_data = ("flashcards", cards)
                else:
                    st.session_state.result_data = ("flashcards", extract_flashcards(f_text))

# --- DISPLAY RESULTS ---
if st.session_state.result_data:
    res_type, res_val = st.session_state.result_data
    st.divider()
    
    # All text outputs below will now be BLACK due to the updated CSS rule
    if res_type == "answer": 
        st.success(f"✅ **Answer:** {res_val}")
    elif res_type == "summary": 
        st.info(f"💡 **Summary:** {res_val}")
    elif res_type == "questions":
        for i, q in enumerate(res_val): 
            st.markdown(f"**Q{i+1}:** {q}")
    elif res_type == "mcqs":
        for i, (q, opts, ans) in enumerate(res_val):
            st.markdown(f"**Q{i+1}: {q}**")
            for l, o in opts.items(): 
                st.markdown(f"{l}. {o}")
            st.success(f"Correct Answer: {ans}")
    elif res_type == "flashcards":
        for i, (q, a) in enumerate(res_val):
            with st.expander(f"🎴 Card {i+1}: {q}"): 
                st.markdown(f"**Answer:** {a}")