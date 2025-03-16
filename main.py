import uvicorn
from fastapi import FastAPI
from api.api_endpoints import api_router

app = FastAPI()
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app")
