import json
from datetime import datetime
from sqlalchemy import text
from MYSQL.connection import engine

# JSON 파일 경로
json_path = "new_crm_template.json" 

# user_id는 실제 사용자 ID로 지정
user_id = 1004

# JSON 파일 읽기
with open(json_path, "r", encoding="utf-8") as f:
    templates = json.load(f)

with engine.begin() as conn:
    for template in templates:
        conn.execute(
            text("""
                INSERT INTO template_message 
                (user_id, template_type, channel_type, title, content, created_at)
                VALUES (:user_id, :template_type, :channel_type, :title, :content, :created_at)
            """),
            {
                "user_id": user_id,
                "template_type": template.get('template_type'),
                "channel_type": template.get('channel_type'),
                "title": template.get('title'),
                "content": template.get('content'),
                "created_at": datetime.utcnow()
            }
        )

print("템플릿 데이터가 정상적으로 저장되었습니다.")
