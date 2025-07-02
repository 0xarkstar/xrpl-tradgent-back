# 대시보드 서비스 예시
def get_summary(user_id):
    # TODO: DB에서 요약 정보 조회
    return {"expected_return": 0.12, "current_position": {}, "strategy": "AI 추천 전략"}

def get_transactions(user_id, page, size):
    # TODO: DB에서 거래 내역 조회
    return {"transactions": [], "total": 0}

def get_performance(user_id, period):
    # TODO: DB에서 수익률 그래프 데이터 조회
    return {"dates": [], "values": []}
