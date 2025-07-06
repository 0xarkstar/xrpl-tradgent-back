from fastapi import FastAPI
from routers import user, agent, dashboard, executor, xrpl_test
from config.settings import TAG_EXECUTOR, TAG_XRPL_TEST, TAG_USER, TAG_AGENT, TAG_DASHBOARD, ROOT_MESSAGE

app = FastAPI()

# Register routers
app.include_router(executor.router, prefix="/executor", tags=[TAG_EXECUTOR])
app.include_router(xrpl_test.router, prefix="/xrpl_test", tags=[TAG_XRPL_TEST])
app.include_router(user.router, prefix="/user", tags=[TAG_USER])
app.include_router(agent.router, prefix="/agent", tags=[TAG_AGENT])
app.include_router(dashboard.router, prefix="/dashboard", tags=[TAG_DASHBOARD])

@app.get("/")
def root():
    return {"status": ROOT_MESSAGE}

