from .state import CustomerAgentState
from customer_agent.agent_runner import run_customer_agent_with_rag
from langchain_core.prompts import ChatPromptTemplate
import os
import sys
import logging
from langchain_core.output_parsers import StrOutputParser

# 로거 설정
logger = logging.getLogger(__name__)

# 경로 설정: 현재 파일 위치 → 프로젝트 루트
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 절대경로로 임포트

from config.env_config import llm



def analyze_inquiry_node(state: CustomerAgentState) -> dict:
    system_prompt = """
    문의를 다음 유형으로 분류하세요. 반드시 [인사],[요청] 중 하나로 답변:
    - [인사]: 인사, 감사, 칭찬 ("안녕하세요", "감사합니다")
    - [상담]:  정보 요청, 고민 상담 ("고객 유지 방법이 궁금해요")
    - [잡담]: 상담과 무관한 대화 ("오늘 날씨 좋네요")
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "문의 내용: {input}")
    ])
    
    # 2. LLM 체인 구성 
    chain = prompt | llm | StrOutputParser()
    
    # 3. 분류 실행
    inquiry_type = chain.invoke({"input": state["user_input"]})
    
    # 4. 결과 표준화
    return {"inquiry_type": inquiry_type.strip().replace("[", "").replace("]", "")}

def small_talk_node(state: CustomerAgentState) -> dict:
    """인사/잡담 전용 응답 (LLM 기반)"""
    prompt = ChatPromptTemplate.from_template(
        "사용자의 인사나 잡담에 정중한 어투로 답변하세요: {input}"
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"input": state["user_input"]})
    return {"answer": response}

def rag_node(state: CustomerAgentState) -> dict:
    """기존 RAG 로직 실행 (수정 없음)"""
    result = run_customer_agent_with_rag(
        user_input=state["user_input"],
        persona=state["business_type"]
    )
    return {
        "topics": result["topics"],
        "answer": result["answer"],
        "sources": result["sources"]
    }
