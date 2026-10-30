
import streamlit as st
import re
from main import rag_chain


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CivicActions AI Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# 2. CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F5F7FB;
    color: #172B4D;
}

[data-testid="stAppViewContainer"] {
    background-color: #F5F7FB;
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

#MainMenu,
footer {
    visibility: hidden;
}

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp p,
.stApp label {
    color: #172B4D;
}

.main-header {
    background: linear-gradient(120deg, #101D3A, #183F70);
    padding: 30px;
    border-radius: 18px;
    margin-bottom: 25px;
    color: white;
    box-shadow: 0 8px 25px rgba(16, 29, 58, 0.12);
}

.main-header h1 {
    color: #FFFFFF !important;
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 8px;
}

.main-header p {
    color: #D5E3F5 !important;
    font-size: 15px;
    margin-bottom: 0;
}

.status-pill {
    display: inline-block;
    background: rgba(46, 204, 113, 0.15);
    color: #8EF0B5;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 12px;
}

.welcome-card {
    background: #FFFFFF;
    border: 1px solid #E5EAF2;
    border-radius: 16px;
    padding: 25px;
    margin: 20px 0;
    box-shadow: 0 3px 12px rgba(0,0,0,0.025);
}

.welcome-card h3 {
    color: #172B4D !important;
    margin: 0 0 10px 0;
}

.welcome-card p {
    color: #65758B !important;
    margin: 0;
    line-height: 1.6;
}

.stChatMessage {
    background-color: #FFFFFF !important;
    border: 1px solid #E7ECF3;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}

.stChatMessage [data-testid="stMarkdownContainer"],
.stChatMessage [data-testid="stMarkdownContainer"] p {
    color: #26364D !important;
}

[data-testid="stChatInput"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DCE5F0 !important;
    border-radius: 14px !important;
}

[data-testid="stChatInput"] textarea {
    color: #172B4D !important;
    background-color: #FFFFFF !important;
    -webkit-text-fill-color: #172B4D !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #8996A8 !important;
    -webkit-text-fill-color: #8996A8 !important;
}

section[data-testid="stSidebar"] {
    background-color: #101D32;
}

section[data-testid="stSidebar"] * {
    color: #E8EEF7;
}

.sidebar-title {
    font-size: 21px;
    font-weight: 700;
    color: #FFFFFF !important;
    margin-bottom: 5px;
}

.sidebar-subtitle {
    color: #A9B9CF !important;
    font-size: 13px;
    line-height: 1.6;
}

div[data-testid="stExpander"] {
    background-color: #F8FAFD;
    border: 1px solid #E1E8F0;
    border-radius: 12px;
}

div.stButton > button {
    border-radius: 10px;
    border: 1px solid #DCE5F0;
    background-color: #FFFFFF;
    color: #183F70 !important;
    font-weight: 500;
    transition: 0.2s;
}

div.stButton > button:hover {
    border-color: #3679C9;
    color: #1E63AA !important;
    background-color: #F0F6FF;
}

.app-footer {
    text-align: center;
    color: #8996A8 !important;
    font-size: 12px;
    padding: 25px 0 10px 0;
}

.app-footer p {
    color: #8996A8 !important;
}

@media (max-width: 768px) {
    .main-header {
        padding: 22px;
    }

    .main-header h1 {
        font-size: 24px;
    }

    .block-container {
        padding-top: 1rem;
    }
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. SESSION STATE
# ==========================================

if "message_history" not in st.session_state:
    st.session_state.message_history = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "selected_source" not in st.session_state:
    st.session_state.selected_source = None


# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================

def get_simple_response(message):

    message = message.lower().strip().rstrip("!.,?")

    greetings = {
        "hi", "hii", "hiii",
        "hello", "hey", "heyy",
        "good morning",
        "good afternoon",
        "good evening"
    }

    if message in greetings:
        return (
            "Hello! I'm your CivicActions Handbook Assistant. "
            "You can ask me about employee policies, benefits, "
            "paid time off, leaves, and workplace guidelines."
        )

    introduction = re.fullmatch(
        r"(?:hey|hi|hello)?\s*,?\s*(?:i am|i'm|my name is)\s+([a-z][a-z'-]*)",
        message
    )

    if introduction:
        name = introduction.group(1).capitalize()

        return (
            f"Hey, {name}! Nice to meet you. "
            "I'm your CivicActions Handbook Assistant. "
            "Feel free to ask me anything about employee policies "
            "or benefits."
        )

    if message in {"how are you", "how are you doing"}:
        return (
            "I'm doing well! What would you like to know "
            "about the CivicActions handbook?"
        )

    if message in {"thanks", "thank you", "thankyou", "thx"}:
        return (
            "You're welcome! Let me know if you have "
            "another handbook question."
        )

    if message in {"bye", "goodbye", "see you"}:
        return (
            "Goodbye! Feel free to return whenever "
            "you have a handbook question."
        )

    return None


def render_sources(sources, message_id):

    if not sources:
        return

    st.markdown("**Verify this answer:**")

    columns = st.columns(min(len(sources), 5))

    for index, source in enumerate(sources):

        with columns[index % len(columns)]:

            if st.button(
                f"📄 [{source['id']}]",
                key=f"{message_id}_{source['id']}",
                help=f"Open source: {source['source']}"
            ):

                st.session_state.selected_source = {
                    **source,
                    "message_id": message_id
                }

    with st.expander(f"📎 View sources ({len(sources)})"):

        for source in sources:

            st.markdown(
                f"**[{source['id']}]** `{source['source']}`"
            )

            if st.button(
                f"Open [{source['id']}]",
                key=f"open_{message_id}_{source['id']}"
            ):

                st.session_state.selected_source = {
                    **source,
                    "message_id": message_id
                }


# ==========================================
# 5. SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">📚 CivicActions AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Your intelligent employee handbook assistant.'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### About this project")

    st.markdown("""
    This application uses Retrieval-Augmented Generation
    to answer questions from the CivicActions employee handbook.

    **Technology stack**
    - LangChain
    - Pinecone
    - Multilingual E5 Large
    - LLM
    - Streamlit
    """)

    st.divider()

    st.markdown("### How it works")

    st.markdown("""
    1. Ask a question.
    2. Retrieve relevant handbook chunks.
    3. Rerank the retrieved results.
    4. Generate an answer with citations.
    """)

    st.divider()

    st.markdown("### Conversation")

    st.caption(
        f"{len(st.session_state.message_history) // 2} messages exchanged"
    )

    if st.button("🗑️ Clear conversation", use_container_width=True):

        st.session_state.message_history = []
        st.session_state.pending_prompt = None
        st.session_state.selected_source = None
        st.rerun()

    st.divider()

    st.caption("Built as an AI/GenAI portfolio project.")


# ==========================================
# 6. MAIN HEADER
# ==========================================

st.markdown("""
<div class="main-header">
    <div class="status-pill">● AI ASSISTANT</div>
    <h1>Employee Handbook Assistant</h1>
    <p>
        Find answers about employee policies, benefits,
        paid time off, leaves and workplace guidelines.
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 7. WELCOME SCREEN
# ==========================================

if not st.session_state.message_history:

    st.markdown("""
    <div class="welcome-card">
        <h3>👋 Welcome to your handbook assistant</h3>
        <p>
            Need help understanding an employee policy?
            Ask a question in natural language. I'll search
            the handbook and provide an answer with source references.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Try asking something")

    suggestions = [
        "What are the leave policies?",
        "How does paid time off work?",
        "What are the maternity leave benefits?",
        "How do I request medical insurance?"
    ]

    col1, col2 = st.columns(2)

    for index, suggestion in enumerate(suggestions):

        target_col = col1 if index % 2 == 0 else col2

        with target_col:

            if st.button(
                suggestion,
                key=f"suggestion_{index}",
                use_container_width=True
            ):

                st.session_state.pending_prompt = suggestion
                st.rerun()


# ==========================================
# 8. DISPLAY CHAT HISTORY
# ==========================================

for index, message in enumerate(st.session_state.message_history):

    avatar = "🧑" if message["role"] == "user" else "📚"

    with st.chat_message(message["role"], avatar=avatar):

        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):

            render_sources(
                message["sources"],
                f"history_{index}"
            )


# ==========================================
# 9. SOURCE VIEWER
# ==========================================

selected_source = st.session_state.selected_source

if selected_source:

    st.divider()

    st.markdown("### 📖 Source document")

    st.markdown(
        f"**Citation: [{selected_source['id']}]**"
    )

    st.caption(selected_source.get("source", "Unknown source"))

    st.markdown("#### Retrieved document passage")

    source_content = selected_source.get("content", "")

    if source_content and source_content.strip():
        st.markdown(source_content)
    else:
        st.warning(
            "The retrieved passage is unavailable for this citation. "
            "Please try asking the question again."
        )

    if st.button("Close source viewer", key="close_source"):
        st.session_state.selected_source = None
        st.rerun()

# ==========================================
# 10. CHAT INPUT
# ==========================================

typed_input = st.chat_input(
    "Ask anything about employee policies..."
)

user_input = st.session_state.pending_prompt or typed_input

if st.session_state.pending_prompt:
    st.session_state.pending_prompt = None


# ==========================================
# 11. PROCESS USER QUERY
# ==========================================

if user_input:

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    st.session_state.message_history.append({
        "role": "user",
        "content": user_input
    })

    simple_response = get_simple_response(user_input)

    with st.chat_message("assistant", avatar="📚"):

        if simple_response:

            answer = simple_response
            sources = []

            st.markdown(answer)

        else:

            previous_messages = (
                st.session_state.message_history[-7:-1]
            )

            chat_history = "\n".join(
                f"{'Human' if msg['role'] == 'user' else 'Assistant'}: "
                f"{msg['content']}"
                for msg in previous_messages
            )

            try:

                with st.spinner("Searching the handbook..."):

                    # Get the complete answer and sources together
                    result = rag_chain.invoke({
                        "question": user_input,
                        "chat_history": chat_history
                    })

                answer = result.get("answer", "")

                # Retrieve complete citation metadata
                sources = result.get("sources", [])

                # Validate source data
                sources = [
                    source for source in sources
                    if isinstance(source, dict)
                    and source.get("id")
                    and source.get("source")
                ]

                if not answer:
                    answer = (
                        "I could not generate an answer. "
                        "Please try asking your question again."
                    )

                st.markdown(answer)

            except Exception as e:

                answer = (
                    "I encountered a technical issue while processing "
                    "your question. Please try again in a moment."
                )

                sources = []

                st.error(answer)

                print(f"RAG pipeline error: {e}")

    # Save the complete response and source metadata
    st.session_state.message_history.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })

    st.rerun()

# ==========================================
# 12. FOOTER
# ==========================================

st.markdown("""
<div class="app-footer">
    <p>
        Built with Streamlit, LangChain, Pinecone and Generative AI.
    </p>
    <p>
        AI-generated answers may require verification.
        Always refer to the original handbook for official policies.
    </p>
</div>
""", unsafe_allow_html=True)
