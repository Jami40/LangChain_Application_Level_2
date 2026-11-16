import streamlit as st
import os
import html
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from groq import AuthenticationError, BadRequestError


load_dotenv()

template = """
    Below is a draft text that may be poorly worded.
    Your goal is to:
    - Properly redact the draft text
    - Convert the draft text to a specified tone
    - Convert the draft text to a specified dialect

    Here are some examples different Tones:
    - Formal: Greetings! OpenAI has announced that Sam Altman is rejoining the company as its Chief Executive Officer. After a period of five days of conversations, discussions, and deliberations, the decision to bring back Altman, who had been previously dismissed, has been made. We are delighted to welcome Sam back to OpenAI.
    - Informal: Hey everyone, it's been a wild week! We've got some exciting news to share - Sam Altman is back at OpenAI, taking up the role of chief executive. After a bunch of intense talks, debates, and convincing, Altman is making his triumphant return to the AI startup he co-founded.  

    Here are some examples of words in different dialects:
    - American: French Fries, cotton candy, apartment, garbage, \
        cookie, green thumb, parking lot, pants, windshield
    - British: chips, candyfloss, flag, rubbish, biscuit, green fingers, \
        car park, trousers, windscreen

    Example Sentences from each dialect:
    - American: Greetings! OpenAI has announced that Sam Altman is rejoining the company as its Chief Executive Officer. After a period of five days of conversations, discussions, and deliberations, the decision to bring back Altman, who had been previously dismissed, has been made. We are delighted to welcome Sam back to OpenAI.
    - British: On Wednesday, OpenAI, the esteemed artificial intelligence start-up, announced that Sam Altman would be returning as its Chief Executive Officer. This decisive move follows five days of deliberation, discourse and persuasion, after Altman's abrupt departure from the company which he had co-established.

    Please start the redaction with a warm introduction. Add the introduction \
        if you need to.
    
    Below is the draft text, tone, and dialect:
    DRAFT: {draft}
    TONE: {tone}
    DIALECT: {dialect}

    YOUR {dialect} RESPONSE:
"""

#PromptTemplate variables definition
prompt = PromptTemplate(
    input_variables=["tone", "dialect", "draft"],
    template=template,
)


# LLM and key loading function
def load_llm(groq_api_key):
    """Create the Groq chat model used for rewriting."""
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0.7,
        groq_api_key=groq_api_key,
    )


def get_groq_api_key():
    input_text = st.text_input(
        label="Your Groq API key",
        placeholder="Enter your Groq API key (usually starts with gsk_)",
        key="groq_api_key_input",
        type="password",
    )
    return input_text


def get_draft():
    draft_text = st.text_area(
        label="Paste your draft here",
        placeholder="Type or paste the text you want to rewrite...",
        key="draft_input",
        height=180,
    )
    return draft_text


st.set_page_config(
    page_title="Rewrite Studio",
    page_icon="✨",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #fff7ed 0%, #f5f3ff 48%, #ecfeff 100%);
    }
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 2.2rem 2.5rem;
        border-radius: 28px;
        color: white;
        background: linear-gradient(120deg, #7c3aed, #db2777 55%, #f97316);
        box-shadow: 0 18px 45px rgba(124, 58, 237, 0.22);
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.8rem;
        letter-spacing: -0.04em;
    }
    .hero p {
        margin: 0.65rem 0 0;
        font-size: 1.08rem;
        opacity: 0.92;
    }
    .section-title {
        color: #4c1d95;
        font-size: 1.35rem;
        font-weight: 700;
        margin: 1.25rem 0 0.6rem;
    }
    .hint {
        color: #64748b;
        font-size: 0.92rem;
    }
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        border: 2px solid #ddd6fe;
        border-radius: 14px;
        background: #ffffff !important;
        color: #1e293b !important;
        caret-color: #7c3aed !important;
        opacity: 1 !important;
    }
    div[data-testid="stTextArea"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label {
        color: #4c1d95 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stTextArea"] textarea::placeholder,
    div[data-testid="stTextInput"] input::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stTextInput"] input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.16);
    }
    div[data-testid="stCaptionContainer"] p {
        color: #64748b !important;
    }
    div[data-testid="stSelectbox"] > div > div {
        background: #ffffff !important;
        color: #1e293b !important;
        border-color: #ddd6fe !important;
    }
    button[kind="primary"] {
        background: linear-gradient(90deg, #7c3aed, #db2777) !important;
        border: 0 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 2px solid #c4b5fd !important;
        border-radius: 18px;
        background: #ffffff !important;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.08);
    }
    div[data-testid="stVerticalBlockBorderWrapper"]
    div[data-testid="stMarkdownContainer"] {
        color: #1e293b !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stVerticalBlockBorderWrapper"]
    div[data-testid="stMarkdownContainer"] li,
    div[data-testid="stVerticalBlockBorderWrapper"]
    div[data-testid="stMarkdownContainer"] strong,
    div[data-testid="stVerticalBlockBorderWrapper"]
    div[data-testid="stMarkdownContainer"] em {
        color: #1e293b !important;
        line-height: 1.7;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stVerticalBlockBorderWrapper"]
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stVerticalBlockBorderWrapper"]
    div[data-testid="stMarkdownContainer"] h3 {
        color: #4c1d95 !important;
    }
    .output-text {
        width: 100%;
        box-sizing: border-box;
        padding: 1.25rem 1.4rem;
        border: 2px solid #c4b5fd;
        border-radius: 16px;
        background: #ffffff !important;
        color: #111827 !important;
        font-size: 1rem;
        line-height: 1.75;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    .output-text * {
        color: #111827 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>✨ Rewrite Studio</h1>
        <p>Turn rough ideas into polished writing with your preferred tone and dialect.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


col1, col2 = st.columns(2)

with col1:
    st.markdown(
        '<div class="hint">🎨 Choose a style, paste your draft, and let the '
        "rewriting assistant do the polishing.</div>",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        '<div class="hint">Built with 💜 by '
        '<a href="https://www.youtube.com/@dswithbappy">Sumsed Tareq Jami</a></div>',
        unsafe_allow_html=True,
    )


with st.form("rewrite_form", clear_on_submit=False):
    st.markdown('<div class="section-title">🔐 Connect to Groq</div>', unsafe_allow_html=True)
    groq_api_key = get_groq_api_key()
    st.caption("Your key is used only for your request and is not shown on screen.")

    st.markdown('<div class="section-title">📝 Your draft</div>', unsafe_allow_html=True)
    draft_input = get_draft()
    st.caption("Maximum 700 words")

    st.markdown(
        '<div class="section-title">🎯 Customize your rewrite</div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        option_tone = st.selectbox(
            "Tone",
            ("Formal", "Informal"),
        )

    with col2:
        option_dialect = st.selectbox(
            "English dialect",
            ("American", "British"),
        )

    submitted = st.form_submit_button(
        "✨ Rewrite my text",
        type="primary",
        use_container_width=True,
    )

st.markdown('<div class="section-title">🌟 Your polished text</div>', unsafe_allow_html=True)

if submitted:
    if not draft_input.strip():
        st.warning("Please enter some text before rewriting.", icon="✍️")
        st.stop()

    if len(draft_input.split()) > 700:
        st.warning("Please enter a shorter text. The maximum length is 700 words.")
        st.stop()

    if not groq_api_key:
        st.warning(
            "Please insert a Groq API key. Create one at "
            "[console.groq.com](https://console.groq.com/keys)",
            icon="⚠️",
        )
        st.stop()

    llm = load_llm(groq_api_key=groq_api_key)

    prompt_with_draft = prompt.format(
        tone=option_tone, 
        dialect=option_dialect, 
        draft=draft_input
    )

    try:
        improved_redaction = llm.invoke(prompt_with_draft)
    except AuthenticationError:
        st.error(
            "Groq rejected this API key. Check that it is an active key "
            "from [console.groq.com](https://console.groq.com/keys)."
        )
        st.stop()
    except BadRequestError as error:
        st.error(f"Groq rejected the request: {error}")
        st.stop()

    output_text = html.escape(improved_redaction.content).replace("\n", "<br>")
    st.markdown(
        f'<div class="output-text">{output_text}</div>',
        unsafe_allow_html=True,
    )