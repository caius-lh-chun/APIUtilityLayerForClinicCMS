from fastapi import FastAPI
from app.api import routes

def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI API Utility Layer")
    app.include_router(routes.router)
    return app

app = create_app()