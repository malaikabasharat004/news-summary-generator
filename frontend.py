import streamlit as st
import requests

# Set page configuration
st.set_page_config(layout="wide")

API_URL = "http://127.0.0.1:8000"

# Apply custom CSS for styling
st.markdown("""
    <style>
    .title {
        text-align: center;
        color: brown;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .sidebar {
        background-color: #f5f5f5;
    }
    .content {
        padding: 2em;
    }
    .header {
        font-size: 2em;
        color: #0073e6;
    }
    .button-primary {
        background-color: #0073e6;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 1em;
    }
    .button-primary:hover {
        background-color: #005bb5;
    }
    </style>
""", unsafe_allow_html=True)

# Title with custom styling
st.markdown('<div class="title">Personalized News Generator</div>', unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([0.8, 2])  # Adjust column width ratio as needed

# Input Fields and Buttons on the left side
with col1:
    # Dropdown for input method
    option = st.selectbox("How do you want to enter the news?", ("URL", "Title"))

    # Language selection dropdown
    language = st.selectbox("Select the language for the article:", ("English", "Urdu", "Spanish", "French"))

    if option == "URL":
        url = st.text_input("Enter the news URL:")
        title = None
    else:
        title = st.text_input("Enter the news title:")
        url = None

    # Use a custom class for buttons
    if st.button("Get Article", key="get_article", help="Fetch article based on URL or Title"):
        if url or title:
            # Convert language to lowercase for backend compatibility if needed
            language_map = {"English": "en", "Urdu": "ur", "Spanish": "es", "French": "fr"}
            response = requests.post(f"{API_URL}/article", json={"url": url, "title": title, "language": language_map.get(language, "en")})
            if response.status_code == 200:
                data = response.json()
                st.session_state.article_text = data["article_text"]
                st.session_state.authors = data.get("authors", [])
                st.session_state.source_url = data.get("source_url", "")
                st.session_state.summary = None
                st.session_state.answers = []  # Clear previous answers
            else:
                st.error("Failed to fetch article")
        else:
            st.error("Please enter a URL or title")

    question = st.text_input("Ask a question about the article:")
    if st.button("Ask Question", key="ask_question", help="Ask a question about the fetched article"):
        if 'article_text' in st.session_state and question:
            language_map = {"English": "en", "Urdu": "ur", "Spanish": "es", "French": "fr"}
            response = requests.post(f"{API_URL}/question", json={"question": question, "language": language_map.get(language, "en")})
            if response.status_code == 200:
                answer = response.json()["answer"]
                st.session_state.answers.append({"question": question, "answer": answer})
            else:
                st.error("Failed to get an answer for the question")
        else:
            st.error("Please enter a question or fetch an article first")

    if st.button("Summarize Article", key="summarize_article", help="Summarize the fetched article"):
        if 'article_text' in st.session_state:
            language_map = {"English": "en", "Urdu": "ur", "Spanish": "es", "French": "fr"}
            response = requests.post(f"{API_URL}/summarize", json={"max_words": 150, "language": language_map.get(language, "en")})
            if response.status_code == 200:
                st.session_state.summary = response.json()["summary"]
            else:
                st.error("Failed to summarize the article")
        else:
            st.error("No article text available for summarization")

# Display Output (conditionally based on session state)
with col2:
    if 'article_text' in st.session_state:
        # Highlight the source and authors at the top
        if st.session_state.authors:
            st.markdown(f"**Author(s):** *{', '.join(st.session_state.authors)}*", unsafe_allow_html=True)
        if st.session_state.source_url:
            st.markdown(f"**Source:** [Link to the article]({st.session_state.source_url})", unsafe_allow_html=True)
        
        st.markdown('<div class="header">Article</div>', unsafe_allow_html=True)

        # Then display the article text
        st.write(st.session_state.article_text)

    if 'summary' in st.session_state:
        st.markdown('<div class="header">Summary</div>', unsafe_allow_html=True)
        st.write(st.session_state.summary)

    if 'answers' in st.session_state:
        st.markdown('<div class="header">Questions and Answers</div>', unsafe_allow_html=True)
        for qa in st.session_state.answers:
            st.write(f"**Question:** {qa['question']}")
            st.write(f"**Answer:** {qa['answer']}")