from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import random
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="learning ais API")

# Allow CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/", StaticFiles(directory="static", html=True), name="static")


# Load pre-trained model
generator = pipeline("text-generation", model="gpt2")

@app.get("/api/question")
async def get_question():
    questions = ["请解释强化学习的基本原理。", "如何提高英语口语能力？", "面试时如何回答自我介绍？"]
    return {"question": random.choice(questions)}

@app.post("/api/answer")
async def evaluate_answer(answer: dict):
    user_answer = answer["answer"]
    feedback = "你的回答不错，但可以更详细一些。"
    return {"feedback": feedback}

@app.get("/api/progress")
async def get_progress():
    return {"correct": 8, "total": 10}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "status": "上传成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)