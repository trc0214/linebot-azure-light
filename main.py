import os
import dotenv
import subprocess
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import uvicorn

from linebot.v3.messaging import MessagingApi, Configuration, ApiClient, TextMessage, ReplyMessageRequest
from linebot.v3.webhook import WebhookHandler, MessageEvent
from openai import AzureOpenAI

dotenv.load_dotenv()

app = FastAPI()

line_config = Configuration(access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
line_api = MessagingApi(ApiClient(line_config))

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_KEY")
api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

user_histories = defaultdict(lambda: deque(maxlen=10))

@app.get("/")
async def home():
    return PlainTextResponse("Line Bot is running!")

@app.post("/line/webhook")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")
    handler.handle(body_text, signature)
    return PlainTextResponse("OK")

@handler.add(MessageEvent)
def handle_message(event):
    from linebot.v3.webhooks import TextMessageContent
    if not hasattr(event, "message") or not isinstance(event.message, TextMessageContent):
        return
    user_message = event.message.text
    user_id = event.source.user_id
    try:
        profile = line_api.get_profile(user_id)
        display_name = profile.display_name
    except:
        display_name = "user"
    user_histories[user_id].append({"role": "user", "content": user_message})
    history = list(user_histories[user_id])
    system_prompt = f"You are a helpful assistant. The user's name is {display_name}. And anser the question in Chinese and simple. " 
    messages = [{"role": "system", "content": system_prompt}] + history
    try:
        response = client.chat.completions.create(messages=messages, max_completion_tokens=5000, model=deployment)
        reply = response.choices[0].message.content.strip()
        if not reply:
            reply = "很抱歉，目前無法回應您的訊息，請稍後再試。"
            print(response)
        user_histories[user_id].append({"role": "assistant", "content": reply})
    except Exception as e:
        reply = "很抱歉，您的訊息觸發了內容審查，請換個方式再試一次。"
    line_api.reply_message(ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[TextMessage(text=reply)]
    ))

if __name__ == "__main__":
    ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
    ngrok_port = os.getenv("NGROK_PORT", "5000")
    ngrok_url = os.getenv("NGROK_URL")
    ngrok_cmd = ["ngrok", "http", ngrok_port]
    if ngrok_url:
        domain = ngrok_url.replace("https://", "").replace("http://", "").split("/")[0]
        ngrok_cmd += ["--domain", domain]
    if ngrok_auth_token:
        subprocess.run(["ngrok", "config", "add-authtoken", ngrok_auth_token])
    ngrok_process = subprocess.Popen(ngrok_cmd)
    import time, requests
    time.sleep(2)
    try:
        tunnels = requests.get("http://localhost:4040/api/tunnels").json()
        public_url = next(
            (t["public_url"] for t in tunnels["tunnels"] if t["public_url"].startswith("https://")),
            None
        )
        if public_url:
            print(f"ngrok public URL: {public_url}")
        else:
            print("ngrok public URL not found.")
    except Exception as e:
        print("無法取得 ngrok public URL:", e)
    uvicorn.run(app, host="0.0.0.0", port=int(ngrok_port))