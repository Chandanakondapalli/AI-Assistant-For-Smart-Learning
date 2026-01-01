Exam Preparation Chatbot This is a smart and interactive chatbot designed to help students prepare for exams in a more efficient way.

With this app, you can ask doubts, summarize your notes, generate questions, and even create flashcards. It uses powerful AI models from Hugging Face and is built using the Streamlit framework.

Features Ask a Doubt Paste your study material and type in your question. The chatbot will find and display the most relevant answer using natural language processing.

Summarize Notes If you have long notes and want to shorten them for quick revision, just paste them in and get a meaningful summary.

Generate Questions This tool can automatically generate two types of questions:

Normal short-answer questions for revision

Multiple Choice Questions with shuffled options and correct answer marked

Flashcard Generator You can choose between two flashcard modes:

Manual Mode where you paste your own "Term: Definition" format

Auto Mode where the app creates flashcards from your notes using sentence analysis

Technology Used Frontend is built with Streamlit for quick and easy web app creation. Backend uses Hugging Face models:

roberta-base-squad2 for question answering

bart-large-cnn and distilbart-cnn-12-6 for summarization Environment variables are managed using python-dotenv.
