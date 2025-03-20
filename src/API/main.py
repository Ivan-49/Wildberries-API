from fastapi import FastAPI
import logging


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=80, reload=True)
