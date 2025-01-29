from fastapi import FastAPI, WebSocket, Request
from starlette.responses import HTMLResponse
from transformers import pipeline
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Hugging Face の感情分析モデルをロード
classifier = pipeline(
    task="sentiment-analysis",
    model="koheiduck/bert-japanese-finetuned-sentiment",
    tokenizer="cl-tohoku/bert-base-japanese-whole-word-masking"
)


# WebSocketエンドポイント
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        if text:
            result = classifier(text)[0]
            if result["label"] == "NEGATIVE":
                result["score"] *= -1  # NEGATIVE の場合はスコアを反転
            await websocket.send_text(json.dumps({"score": round(result["score"], 4), "text": text}))

# HTML応答
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
