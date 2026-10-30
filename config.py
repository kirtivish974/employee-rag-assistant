import os


def get_api_key(key_name: str) -> str:
    # First, check environment variables
    api_key = os.getenv(key_name)

    if api_key:
        return api_key

    # Then, check Streamlit Cloud secrets
    try:
        import streamlit as st
        api_key = st.secrets.get(key_name)
    except Exception:
        api_key = None

    if not api_key:
        raise ValueError(f"Missing API key: {key_name}")

    return api_key
