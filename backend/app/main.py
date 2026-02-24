from fastapi import FastAPI

from app.core.config import APP_TITLE, APP_VERSION, DEBUG

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    debug=DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "version": APP_VERSION}