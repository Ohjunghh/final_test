from langgraph.graph import StateGraph, END
from .state import CustomerAgentState
from .nodes import analyze_inquiry_node, rag_node, small_talk_node

def create_workflow():
    builder = StateGraph(CustomerAgentState)
    
    # 노드 등록
    builder.add_node("analyze_inquiry", analyze_inquiry_node)  # LLM 분류 노드
    builder.add_node("small_talk", small_talk_node)  # 통합 노드
    builder.add_node("run_rag", rag_node)   # RAG 실행 노드
    
    # 조건부 라우팅 함수
    def route_based_on_type(state: CustomerAgentState) -> str:
        inquiry_type = state.get("inquiry_type", "")
        return "small_talk" if inquiry_type in ["인사", "잡담"] else "run_rag"
    
    # 엣지 설정
    # 실행 흐름 설정
    builder.set_entry_point("analyze_inquiry")
    builder.add_conditional_edges(
        "analyze_inquiry",
        route_based_on_type,
        {"small_talk": "small_talk", "run_rag": "run_rag"}
    )
    builder.add_edge("small_talk", END)
    builder.add_edge("run_rag", END)
    
    return builder.compile()

customer_workflow = create_workflow()
