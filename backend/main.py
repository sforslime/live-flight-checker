from fastapi import FastAPI

app = FastAPI(title="Live Flight Checker")

@app.get("/")
async def root():
    return {"message": "Flight Checker API is running"}
