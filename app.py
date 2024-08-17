import streamlit as st

# Set the page configuration to have the sidebar on the left side
st.set_page_config(layout="wide")

# Left Sidebar for input options
with st.sidebar:
    st.markdown("## Input Options")
    st.markdown("**Input your news channel or paste an article to summarize**")
    input_type = st.radio("", ["News Channel", "Article"])

    if input_type == "News Channel":
        news_channel = st.text_input("Enter news channel:")
    else:
        article_text = st.text_area("Paste article here:")

    st.markdown("**Or provide more context:**")
    question_type = st.radio("", ["Write a question", "Summarize in 150 words"])

    if question_type == "Write a question":
        question = st.text_input("Write your question regarding this news:")
    else:
        word_count = st.slider("Word count:", min_value=50, max_value=200, value=150)

# Main Content
st.title("News Summary Generator")

# Placeholder for generated output
st.markdown("**Output:**")
output_placeholder = st.empty()

# Button to trigger summarization
if st.button("Generate Summary"):
    # Replace this with actual logic for summarization
    if input_type == "News Channel":
        # Use news_channel to fetch article and generate summary
        summary = "Summary based on news channel"
    else:
        # Use article_text to generate summary
        summary = "Summary based on article text"

    # Display summary
    output_placeholder.markdown(f"**Generated Summary:**\n{summary}")

# Sidebar for generated article (if applicable)
if input_type != "News Channel":
    st.sidebar.markdown("## Generated Article")
    st.sidebar.empty()  # Placeholder for the generated article content
