import sys
import os
import logging
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 로거 설정
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 프로젝트 루트 경로 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from MYSQL.queries import get_business_type, insert_message
from customer_agent.agent_runner import run_customer_agent_with_rag

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 요청 모델
class AgentQueryRequest(BaseModel):
    user_id: int
    conversation_id: int
    question: str

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "ok", "agent": "customer_agent"}

@app.post("/agent/query")
async def query_agent(request: AgentQueryRequest = Body(...)):
    try:
        logger.info(f"Received query from user {request.user_id}: {request.question[:50]}...")
        
        # 1. user_id로 business_type 조회
        business_type = get_business_type(request.user_id) or "common"
        logger.info(f"Business type for user {request.user_id}: {business_type}")
        
        # 2. 사용자 메시지 저장
        insert_success = insert_message(
            conversation_id=request.conversation_id,
            sender_type="user",
            agent_type="customer_agent",
            content=request.question
        )
        if not insert_success:
            logger.warning(f"Failed to insert user message for conversation {request.conversation_id}")
        
        # 3. LLM 에이전트 실행
        logger.info("Running LLM agent...")
        result = run_customer_agent_with_rag(
            user_input=request.question,
            persona=business_type
        )
        
        # 4. 에이전트 답변 저장
        insert_success = insert_message(
            conversation_id=request.conversation_id,
            sender_type="agent",
            agent_type=business_type,
            content=result["answer"]
        )
        if not insert_success:
            logger.warning(f"Failed to insert agent response for conversation {request.conversation_id}")
        
        # 5. 결과 반환
        logger.info("Query processed successfully")
        return {
            "topics": result["topics"],
            "answer": result["answer"],
            "sources": result["sources"]
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "customer_agent.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
        reload_dirs=["."]
    )


# cd ~\final_test
# python -m customer_agent.main
