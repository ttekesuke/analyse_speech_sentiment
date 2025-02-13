from fastapi import FastAPI, WebSocket, Request
from starlette.responses import HTMLResponse
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Dockerコンテナ内のパスにある学習済みモデルをロード
model_path = "/app/trained_model"
model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# ソフトマックス関数
def np_softmax(x):
    f_x = np.exp(x) / np.sum(np.exp(x))
    return f_x

@app.get("/predict/")
def predict(text: str):

# WebSocketエンドポイント
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        text = await websocket.receive_text()
        if text:
            tokens = tokenizer(text, truncation=True, return_tensors="pt")
            tokens.to(model.device)
            preds = model(**tokens)
            prob = np_softmax(preds.logits.cpu().detach().numpy()[0])

            emotion_names_jp = ["joy", "sadness","anger","surprise","disgust","trust","expectation","fear"]
            result = {n: p for n, p in zip(emotion_names_jp, prob)}

            await websocket.send_text(json.dumps({"score": result, "text": text}))

# HTML応答
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
