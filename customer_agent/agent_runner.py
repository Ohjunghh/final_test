from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.output_parsers import StrOutputParser
import os
import sys
import logging
import pathlib  # 추가: 경로 처리를 위해 필요

# 로거 설정
logger = logging.getLogger(__name__)

# 경로 설정: 현재 파일 위치 → 프로젝트 루트
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 절대경로로 임포트

from config.env_config import llm, vectorstore
from customer_agent.prompts_config import PROMPT_META


# 경로 처리를 위한 베이스 디렉토리 설정
BASE_DIR = pathlib.Path(__file__).parent.resolve()  # 추가

# 관련 토픽 추론
TOPIC_CLASSIFY_SYSTEM_PROMPT = """
너는 고객 질문을 분석해서 관련된 고객관리 토픽을 모두 골라주는 역할이야.

아래의 토픽 중에서 질문과 관련된 키워드를 **가장 밀접한 키워드 1개만** 골라줘.
키만 출력하고, 설명은 하지마. (예: customer_service)

가능한 토픽:
- customer_service – 응대, 클레임
- customer_retention – 재방문, 단골 전략
- customer_satisfaction – 만족도, 여정
- customer_feedback – 의견 수집 및 개선
- customer_segmentation – 타겟 분류, 페르소나
- community_building – 팬, 팬덤, 커뮤니티
- customer_data – 고객DB, CRM
- privacy_compliance – 개인정보, 동의 관리
"""

def classify_topics(user_input: str) -> list:
    # 수정: 변수화된 템플릿 사용
    classify_prompt = ChatPromptTemplate.from_messages([
        ("system", TOPIC_CLASSIFY_SYSTEM_PROMPT),
        ("human", "사용자 질문: {input}")  # 고정 문자열 → 변수
    ])
    
    chain = classify_prompt | llm | StrOutputParser()
    result = chain.invoke({"input": user_input}).strip()
    
    # 수정: 단일 토픽 반환 (시스템 지침에 따라)
    return [result.strip()] if result.strip() in PROMPT_META else []

# 에이전트 프롬프트 구성 함수
def build_agent_prompt(topics: list, persona: str):  # 수정: user_input 매개변수 제거
    merged_prompts = []
    for topic in topics:
        file_name = PROMPT_META[topic]["file"]  # 파일명만 사용
        prompt_text = load_prompt_text(file_name)
        merged_prompts.append(f"# {topic}\n{prompt_text}")
    
    role_descriptions = [PROMPT_META[topic]["role"] for topic in topics]
    
    if persona == "common":
        system_template = f"""#역할\n너는 1인 창업 전문 컨설턴트로서 {', '.join(role_descriptions)}야. 목표와 출력포맷에 맞게 응답해줘."""
    else:
        system_template = f"""#역할\n너는 {persona} 1인 창업 전문 컨설턴트로서 {', '.join(role_descriptions)}야. 목표와 출력포맷에 맞게 응답해줘."""

    system_template += " 제공된 문서가 비어있거나, 질문과 전혀 관련 없는 내용일 경우, 문서를 무시하고 너의 일반적인 지식을 기반으로 답변해줘."

    # 수정: 동적 변수 사용 (input, context)
    human_template = f"""
    {chr(10).join(merged_prompts)}
    
    #참고 문서
    {{context}}
    
    #사용자 입력
    {{input}}
    """
    
    return ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template)
    ])

def load_prompt_text(file_name: str) -> str:
    # 수정: pathlib를 사용한 강화된 경로 처리
    prompt_dir = BASE_DIR / "prompt"
    full_path = prompt_dir / file_name
    
    try:
        # 수정: pathlib로 파일 읽기
        return full_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {full_path}")
        return ""
    except Exception as e:
        logger.error(f"Error loading prompt: {str(e)}")
        return ""

def run_customer_agent_with_rag(user_input: str, persona: str = "common"):
    # 1. 토픽 분류
    topics = classify_topics(user_input)
    logger.info(f"Classified topics: {topics}")
    
    # 2. 프롬프트 구성 (수정: user_input 제거)
    prompt = build_agent_prompt(topics, persona)
    
    # 3. 검색 필터 설정
    base_filter = {"category": "customer_management"}
    topic_filter = base_filter
    if topics:
        topic_filter = {"$and": [base_filter, {"topic": {"$in": topics}}]}
    
    # 4. 검색기 구성
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5, "filter": topic_filter}
    )
    
    # 5. 문서 처리 체인 구성
    document_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=prompt
    )
    
    # 6. 검색 체인 구성
    retrieval_chain = create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=document_chain
    )
    
    # 7. 실행 및 결과 처리 (수정: 변수명 통일)
    result = retrieval_chain.invoke({"input": user_input})
    
    # 8. 소스 문서 포맷팅
    sources = "\n\n".join(
        [f"# 문서\n{doc.page_content}\n" for doc in result["context"]]
    )
    
    return {
        "topics": topics,
        "answer": result["answer"],
        "sources": sources
    }
