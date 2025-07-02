from fastapi import FastAPI
from routers import user, agent, dashboard, executor, xrpl_test

app = FastAPI()

# Register routers
app.include_router(executor.router, prefix="/executor", tags=["Executor"])
app.include_router(xrpl_test.router, prefix="/xrpl_test", tags=["XRPL Test"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(agent.router, prefix="/agent", tags=["Agent"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"status": "XRPL DeFi AI Agent Backend is running!"}

