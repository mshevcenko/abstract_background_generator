import uvicorn
from api.app_config import app

if __name__ == "__main__":
    uvicorn.run("main:app")
