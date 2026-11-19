import streamlit as st
import os
import html
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from groq import Groq, AuthenticationError, BadRequestError, NotFoundError


load_dotenv()

st.set_page_config(
    page_title = "Blog Post Generator"
)

st.title("Blog Post Generator")

st.markdown(
    """
    <style>
    .blog-result {
        margin-top: 1rem;
        padding: 1.5rem;
        border: 2px solid #38bdf8;
        border-radius: 16px;
        background: #f0f9ff !important;
        color: #0f172a !important;
        font-size: 1.05rem;
        line-height: 1.75;
        white-space: normal;
        overflow-wrap: anywhere;
    }
    .blog-result * {
        color: #0f172a !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Enter your Groq API key in the sidebar, then enter a blog topic below.",
    icon="ℹ️",
)

with st.sidebar:
    st.header("🔐 Groq connection")
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


topic_text = st.text_input(
    "Blog topic",
    placeholder="Example: How AI is changing small businesses",
)

generate = st.button(
    "✍️ Generate blog post",
    type="primary",
    use_container_width=True,
)

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

            st.subheader("📝 Your generated blog post")
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
        
