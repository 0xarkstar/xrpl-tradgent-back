# 날짜 관련 유틸 함수 예시
from datetime import datetime

def get_today() -> str:
    return datetime.now().strftime('%Y-%m-%d')
