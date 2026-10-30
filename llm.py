from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from config import get_api_key

load_dotenv()


Inception_llm = ChatOpenAI(
    model="mercury-3",
    api_key=get_api_key("INCEPTION_API_KEY"),
    base_url="https://api.inceptionlabs.ai/v1",
    temperature=0.2,
    streaming=True
)