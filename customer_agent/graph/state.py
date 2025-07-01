#  상태 객체 정의
from typing import TypedDict, Literal
from langchain_core.messages import BaseMessage

class CustomerAgentState(TypedDict):
    user_input: str
    business_type: str
    mode: Literal["owner", "customer"]
    inquiry_type: Literal["general","request"]  # 문의 유형
    topics: list[str]
    answer: str
    sources: str
    a2a_data: dict  # A2A 통신용 데이터
    messages: list[BaseMessage]  # 대화 이력