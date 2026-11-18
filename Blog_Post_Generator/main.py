import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate


load_dotenv()

st.set_page_config(
    page_title = "Blog Post Generator"
)

st.title("Blog Post Generator")

groq_api_key = st.sidebar.text_input(
    "Groq API Key",
    type="password",
    placeholder="Enter your Groq API key",
)

def generate_response(topic):
    llm = ChatGroq(
        api_key=groq_api_key,
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0.7,
        max_tokens=2048,
    )
    template = """
    As experienced startup and venture capital writer, 
    generate a 400-word blog post about {topic}
    
    Your response should be in this format:
    First, print the blog post.
    Then, sum the total number of words on it and print the result like this: This post has X words.
    """
    prompt = PromptTemplate(
        input_variables = ["topic"],
        template = template
    )
    query = prompt.format(topic=topic)
    response = llm.invoke(query)
    return st.write(response.content)


topic_text = st.text_input("Enter topic: ")
if not groq_api_key:
    st.warning("Enter your Groq API key")
elif topic_text:
    generate_response(topic_text)
        
