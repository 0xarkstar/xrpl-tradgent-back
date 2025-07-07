from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user, agent, dashboard, executor, xrpl_test
from config.settings import TAG_EXECUTOR, TAG_XRPL_TEST, TAG_USER, TAG_AGENT, TAG_DASHBOARD, ROOT_MESSAGE

app = FastAPI()

# CORS 설정 추가
origins = [
    "http://localhost",
    "http://localhost:3000", # Next.js 프론트엔드의 주소와 포트
    # 배포 시에는 실제 프론트엔드 도메인을 추가해야 합니다.
    # 예: "https://your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"], # 모든 헤더 허용
)

# Register routers
app.include_router(executor.router, prefix="/executor", tags=[TAG_EXECUTOR])
app.include_router(xrpl_test.router, prefix="/xrpl_test", tags=[TAG_XRPL_TEST])
app.include_router(user.router, prefix="/user", tags=[TAG_USER])
app.include_router(agent.router, prefix="/agent", tags=[TAG_AGENT])
app.include_router(dashboard.router, prefix="/dashboard", tags=[TAG_DASHBOARD])

@app.get("/")
def root():
    return {"status": ROOT_MESSAGE}

