import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI


# ✅ 환경변수 로드
load_dotenv()
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_DIR = os.getenv("CHROMA_DIR", "../vector_db_text-3-small_merge")



# ✅ 임베딩 모델 초기화
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=1536,
    openai_api_key=OPENAI_API_KEY
)

# ✅ 벡터스토어 불러오기
vectorstore = Chroma(
    collection_name="global-documents",
    persist_directory=CHROMA_DIR,
    embedding_function=embedding
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# ✅ LLM 초기화 # model="gpt-3.5-turbo"
#llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
# llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0.2)


# OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# Gemini (Google Generative AI)
llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)


# pip install -U langchain-google-genai
