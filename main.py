from fastapi import FastAPI
from routers import user, agent, executor, dashboard, xrpl_test

app = FastAPI()

# Register routers
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(agent.router, prefix="/agent", tags=["Agent"])
app.include_router(executor.router, prefix="/executor", tags=["Executor"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(xrpl_test.router, prefix="/test", tags=["XRPL Test Tools"])

@app.get("/")
def root():
    return {"status": "XRPL DeFi AI Agent Backend is running!"}

