import streamlit as st
import os
import html
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from groq import Groq, AuthenticationError, BadRequestError, NotFoundError


load_dotenv()

st.set_page_config(
    page_title="Blog Post Generator",
    page_icon="✍️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 12% 10%, rgba(56, 189, 248, 0.16), transparent 26rem),
            radial-gradient(circle at 88% 18%, rgba(168, 85, 247, 0.12), transparent 24rem),
            linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
    }
    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #172554 0%, #312e81 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #c7d2fe;
    }
    .hero {
        margin-bottom: 1.25rem;
        padding: 2.3rem 2.5rem;
        border-radius: 26px;
        color: #ffffff;
        background: linear-gradient(120deg, #2563eb 0%, #7c3aed 55%, #ec4899 100%);
        box-shadow: 0 20px 50px rgba(37, 99, 235, 0.22);
    }
    .hero h1 {
        margin: 0;
        font-size: 2.65rem;
        line-height: 1.12;
        letter-spacing: -0.035em;
    }
    .hero p {
        margin: 0.7rem 0 0;
        max-width: 760px;
        color: #e0e7ff;
        font-size: 1.05rem;
    }
    .section-card {
        padding: 1.35rem 1.45rem 1.2rem;
        border: 1px solid #dbeafe;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.96);
        box-shadow: 0 10px 30px rgba(30, 64, 175, 0.08);
    }
    .section-card label,
    .section-card p {
        color: #1e293b;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stTextArea"] textarea {
        border: 2px solid #c7d2fe;
        border-radius: 12px;
        background: #ffffff;
        color: #0f172a;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #64748b;
        opacity: 1;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stSelectbox"] > div > div:focus-within,
    [data-testid="stTextArea"] textarea:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
    }
    button[kind="primary"] {
        min-height: 48px;
        border: 0;
        border-radius: 12px;
        background: linear-gradient(90deg, #2563eb, #7c3aed, #db2777);
        color: #ffffff;
        font-weight: 750;
        box-shadow: 0 10px 24px rgba(124, 58, 237, 0.20);
    }
    .result-heading {
        margin: 1.6rem 0 0.7rem;
        color: #1e1b4b;
        font-size: 1.35rem;
        font-weight: 800;
    }
    .blog-result {
        margin-top: 1rem;
        padding: 1.5rem;
        border: 2px solid #a5b4fc;
        border-radius: 18px;
        background: #ffffff !important;
        color: #111827 !important;
        font-size: 1.08rem;
        line-height: 1.75;
        white-space: normal;
        overflow-wrap: anywhere;
        box-shadow: 0 12px 34px rgba(67, 56, 202, 0.10);
    }
    .blog-result * {
        color: #111827 !important;
    }
    [data-testid="stAlert"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>✍️ Blog Post Generator</h1>
        <p>Create polished, audience-ready startup and business articles with Groq.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🔐 API Connection")
    st.write("Connect your Groq account")
    groq_api_key = st.text_input(
        "Groq API key",
        type="password",
        placeholder="gsk_...",
        help="Create a key at https://console.groq.com/keys",
    )
    st.caption("Your key is used only for this session.")

@st.cache_data(ttl=300)
def get_available_models(api_key):
    if not api_key:
        return []
    client = Groq(api_key=api_key)
    response = client.models.list()
    model_ids = [model.id for model in response.data]
    excluded = ("whisper", "tts", "guard", "embedding", "distil")
    return [
        model_id
        for model_id in model_ids
        if not any(token in model_id.lower() for token in excluded)
    ]


selected_model = None
if groq_api_key:
    try:
        available_models = get_available_models(groq_api_key)
        if available_models:
            preferred = os.getenv("GROQ_MODEL")
            if preferred not in available_models:
                preferred = next(
                    (
                        model_id
                        for model_id in available_models
                        if "llama-3.3" in model_id
                    ),
                    available_models[0],
                )

            selected_model = st.sidebar.selectbox(
                "Groq model",
                options=available_models,
                index=available_models.index(preferred),
                help="Models available to this API key",
            )
        else:
            st.sidebar.warning("No text-generation models are available.")
    except AuthenticationError:
        st.sidebar.error("This Groq API key is invalid or inactive.")
    except Exception as error:
        st.sidebar.error("Could not retrieve models.")
        st.sidebar.caption(str(error))


def generate_response(topic, model_id):
    llm = ChatGroq(
        api_key=groq_api_key,
        model=model_id,
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
    content = response.content
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                text_parts.append(str(block["text"]))
        return "\n".join(text_parts).strip()
    return str(content).strip()


st.markdown('<div class="section-card">', unsafe_allow_html=True)
topic_text = st.text_input(
    "💡 Blog topic",
    placeholder="Example: How AI is changing small businesses",
)

st.caption("The result will follow a professional startup and venture-writing style.")

generate = st.button(
    "✨ Generate my blog post",
    type="primary",
    use_container_width=True,
)
st.markdown("</div>", unsafe_allow_html=True)

if generate:
    if not groq_api_key:
        st.warning(
            "Please enter your Groq API key in the sidebar.",
            icon="⚠️",
        )
    elif not topic_text.strip():
        st.warning("Please enter a blog topic.", icon="⚠️")
    elif not selected_model:
        st.warning("Please select an available Groq model from the sidebar.")
    else:
        try:
            with st.spinner("Writing your blog post..."):
                blog_post = generate_response(topic_text.strip(), selected_model)

            st.markdown(
                '<div class="result-heading">📝 Your generated blog post</div>',
                unsafe_allow_html=True,
            )
            if not blog_post:
                st.error(
                    "Groq returned no text. Check the selected model in "
                    "`GROQ_MODEL` or remove it to use the default model."
                )
            else:
                formatted_post = html.escape(blog_post).replace("\n", "<br>")
                st.markdown(
                    f'<div class="blog-result">{formatted_post}</div>',
                    unsafe_allow_html=True,
                )
        except AuthenticationError:
            st.error(
                "Groq rejected your API key. Check that it is active and "
                "starts with `gsk_`."
            )
        except NotFoundError as error:
            st.error(
                "The selected Groq model is unavailable. "
                "Please choose another model from the sidebar."
            )
            st.caption(str(error))
        except BadRequestError as error:
            st.error(f"Groq rejected the request: {error}")
        except Exception as error:
            st.error(
                "The blog post could not be generated. "
                "Check your Groq model and API key, then try again."
            )
            st.exception(error)
        
