from datetime import datetime
from sqlalchemy import text
from MYSQL.connection import engine

# 수정할 template_id
template_id = 25

# 변경할 HTML 파일 경로
html_path = "signup_success.html" 

# HTML 파일 읽기
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# DB 업데이트 쿼리 실행
with engine.begin() as conn:
    conn.execute(
        text("""
            UPDATE template_message
            SET content = :content
            WHERE template_id = :template_id
        """),
        {
            "content": html_content,
            "template_id": template_id
        }
    )

print(f"template_id={template_id }의 content가 HTML 파일 내용으로 정상적으로 업데이트되었습니다.")
