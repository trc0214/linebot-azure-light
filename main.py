from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os
import dotenv
import subprocess

from openai import AzureOpenAI

dotenv.load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# Azure OpenAI setup
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_KEY")
api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)


@app.route("/")
def home():
    return "Line Bot is running!"


@app.route("/webhook", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
            max_completion_tokens=500,
            model=deployment,
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        reply = "很抱歉，您的訊息觸發了內容審查，請換個方式再試一次。"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))


if __name__ == "__main__":
    ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
    ngrok_port = os.getenv("NGROK_PORT", "5000")
    ngrok_url = os.getenv("NGROK_URL")

    if ngrok_url:
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", f"--url={ngrok_url}", ngrok_port]
        )
    else:
        if ngrok_auth_token:
            subprocess.run(["ngrok", "config", "add-authtoken", ngrok_auth_token])
        ngrok_process = subprocess.Popen(["ngrok", "http", ngrok_port])

    app.run(port=int(ngrok_port))
