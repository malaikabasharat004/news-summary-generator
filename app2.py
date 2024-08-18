import streamlit as st
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

# API and base URL for LLaMA
API_KEY = "3de2255107ef4f42a7a4fc08a8c6bb2e"
BASE_URL = "https://api.aimlapi.com"

# Initialize translator
translator = Translator()

# Language mapping
LANGUAGE_NAMES = {
    "auto": "Auto Detect",
    "ar": "Arabic",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh-cn": "Chinese (Simplified)",
    "ja": "Japanese",
    "ko": "Korean",
}

LANGUAGE_CODES = {name: code for code, name in LANGUAGE_NAMES.items()}

# Function to fetch article content from a URL
def fetch_article_content(url):
    try:
        response = requests.get(f"https://api.allorigins.win/get?url={url}")
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.json()['contents'], 'html.parser')
        
        # Extract article content
        paragraphs = soup.find_all('p')
        content = ' '.join(p.get_text() for p in paragraphs)

        # Extract author and newspaper
        author_meta = soup.find('meta', {'name': 'author'})
        author_name = author_meta['content'] if author_meta else 'Author not found'
        
        newspaper_meta = soup.find('meta', {'property': 'og:site_name'})
        newspaper_name = newspaper_meta['content'] if newspaper_meta else 'Newspaper not found'
        
        return content, author_name, newspaper_name
    except Exception as e:
        return None, str(e), None

# Function to fetch article titles from a website URL
def fetch_article_titles_from_website(url):
    try:
        response = requests.get(f"https://api.allorigins.win/get?url={url}")
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.json()['contents'], 'html.parser')
        
        # Extract article titles and URLs
        articles = []
        for link in soup.find_all('a'):
            title = link.get_text()
            href = link.get('href')
            if href and href.startswith('http'):
                articles.append((title, href))
        
        return articles, None
    except Exception as e:
        return None, str(e)

# Function to interact with the LLaMA API
def get_llama_summary(content, max_tokens):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "messages": [
            {"role": "system", "content": "You are an assistant. Summarize the article."},
            {"role": "user", "content": f"Please summarize this article:\n{content}"}
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        choices = result.get('choices', [])
        summary = choices[0].get('message', {}).get('content', 'No content') if choices else 'No content'
        return summary.strip()
    except Exception as e:
        return str(e)

# Function to truncate summary to the desired length
def truncate_summary(summary, max_length):
    words = summary.split()
    if len(words) > max_length:
        return ' '.join(words[:max_length]) + '...'
    return summary

# Function to translate text
def translate_text(text, src_lang, dest_lang):
    try:
        translated = translator.translate(text, src=src_lang, dest=dest_lang)
        return translated.text
    except Exception as e:
        return str(e)

# Function to interact with the LLaMA API for questions
def get_llama_answer(content, question):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "messages": [
            {"role": "system", "content": "You are an assistant. Answer the question based on the article."},
            {"role": "user", "content": f"Article:\n{content}\n\nQuestion: {question}"}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        choices = result.get('choices', [])
        answer = choices[0].get('message', {}).get('content', 'No content') if choices else 'No content'
        return answer.strip()
    except Exception as e:
        return str(e)

# Streamlit UI
def main():
    st.sidebar.title("Settings")

    # Language selection
    src_language_name = st.sidebar.selectbox("Select the language of the article:", list(LANGUAGE_NAMES.values()))
    dest_language_name = st.sidebar.selectbox("Select the language for the summary:", list(LANGUAGE_NAMES.values()))
    
    src_language = LANGUAGE_CODES.get(src_language_name, "auto")
    dest_language = LANGUAGE_CODES.get(dest_language_name, "en")

    # Select box for action options
    action = st.sidebar.selectbox(
        "What would you like to do with the URL?",
        ["Select an option", "Fetch Specific Article", "Fetch Website Articles"]
    )

    # Ask for the summary length
    max_words = st.sidebar.slider("Select the length of the summary (in words):", min_value=50, max_value=500, value=150)

    # Button to get summary
    summarize_button = st.sidebar.button("Summarize")

    # Display author and newspaper information
    author_name = st.sidebar.empty()
    newspaper_name = st.sidebar.empty()

    st.title("Article Summarizer")

    # Input for the URL
    url = st.text_input("Enter the URL:")

    if url:
        if action == "Fetch Website Articles":
            articles, error = fetch_article_titles_from_website(url)
            if articles:
                st.subheader("Articles on the Website")
                num_articles = st.slider("Select the number of articles to display:", min_value=1, max_value=len(articles), value=10)
                articles_to_show = articles[:num_articles]
                
                selected_article = st.selectbox("Select an article:", [title for title, _ in articles_to_show])
                
                if selected_article:
                    selected_url = next(url for title, url in articles_to_show if title == selected_article)
                    content, author, newspaper = fetch_article_content(selected_url)
                    if content:
                        st.subheader("Fetched Article Content")
                        st.write(content)
                        author_name.write(f"Author: {author}")
                        newspaper_name.write(f"Newspaper: {newspaper}")

                        option = st.sidebar.selectbox(
                            "What would you like to do with the fetched article?",
                            ["Select an option", "Generate Summary", "Ask Questions"]
                        )

                        if option == "Generate Summary" and summarize_button:
                            max_tokens = max_words * 4
                            with st.spinner("Summarizing..."):
                                raw_summary = get_llama_summary(content, max_tokens)
                                if raw_summary:
                                    summary = truncate_summary(raw_summary, max_words)
                                    if dest_language != "en":
                                        summary = translate_text(summary, "en", dest_language)
                                    st.subheader("Summary")
                                    st.write(summary)
                                else:
                                    st.error("Failed to generate summary.")
                        
                        elif option == "Ask Questions":
                            question = st.text_input("Enter your question about the article:")
                            if question:
                                with st.spinner("Getting answer..."):
                                    answer = get_llama_answer(content, question)
                                    if answer:
                                        st.subheader("Answer")
                                        st.write(answer)
                                    else:
                                        st.error("Failed to get answer.")
                    else:
                        st.error("Failed to fetch article content.")
            else:
                st.error(f"Error: {error}")
        
        elif action == "Fetch Specific Article":
            content, author, newspaper = fetch_article_content(url)
            if content:
                st.subheader("Fetched Article Content")
                st.write(content)
                author_name.write(f"Author: {author}")
                newspaper_name.write(f"Newspaper: {newspaper}")

                option = st.sidebar.selectbox(
                    "What would you like to do with the fetched article?",
                    ["Select an option", "Generate Summary", "Ask Questions"]
                )

                if option == "Generate Summary" and summarize_button:
                    max_tokens = max_words * 4
                    with st.spinner("Summarizing..."):
                        raw_summary = get_llama_summary(content, max_tokens)
                        if raw_summary:
                            summary = truncate_summary(raw_summary, max_words)
                            if dest_language != "en":
                                summary = translate_text(summary, "en", dest_language)
                            st.subheader("Summary")
                            st.write(summary)
                        else:
                            st.error("Failed to generate summary.")
                
                elif option == "Ask Questions":
                    question = st.text_input("Enter your question about the article:")
                    if question:
                        with st.spinner("Getting answer..."):
                            answer = get_llama_answer(content, question)
                            if answer:
                                st.subheader("Answer")
                                st.write(answer)
                            else:
                                st.error("Failed to get answer.")
            else:
                st.error("Failed to fetch article content.")
        else:
            st.error("Please select a valid action.")

if __name__ == "__main__":
    main()
