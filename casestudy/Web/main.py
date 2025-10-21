from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def welcome():
    return {"message": "Welcome to the Web Case Study API!"}