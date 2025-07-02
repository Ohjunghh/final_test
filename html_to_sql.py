import os
from datetime import datetime
from sqlalchemy import text
from MYSQL.connection import engine


# html_personalized/birthday_personalize.html
# html_personalized/join_personalize.html
# html_personalized/track_order_personalize.html

# HTML 파일 경로
html_path = "html_personalized/track_order_personalize.html"  # 실제 파일명으로 변경

# DB에 저장할 값들
user_id = 3
template_type = "구매 후 안내"   
channel_type = "email"          
title = "주문 배송 안내 #5"  

# HTML 파일 읽기
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

with engine.begin() as conn:
    conn.execute(
        text("""
            INSERT INTO template_message 
            (user_id, template_type, channel_type, title, content, content_type, created_at)
            VALUES (:user_id, :template_type, :channel_type, :title, :content, :content_type, :created_at)
        """),
        {
            "user_id": user_id,
            "template_type": template_type,
            "channel_type": channel_type,
            "title": title,
            "content": html_content,
            "content_type": "html",           # ★ 반드시 'html'로 저장
            "created_at": datetime.now()
        }
    )

print("HTML 템플릿이 정상적으로 저장되었습니다.")
