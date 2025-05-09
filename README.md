[English](README.md) | [中文說明](README.zh-TW.md)

# LINE Bot + Azure OpenAI + ngrok

This project is a Python Flask example that integrates the LINE Messaging API, Azure OpenAI, and ngrok.

## Prerequisites

1. **Python Environment**
   - Install Python 3.8 or higher

2. **LINE Bot Setup**
   - Apply for a LINE Messaging API Channel
   - Obtain the Channel Access Token and Channel Secret

3. **Azure OpenAI Setup**
   - Apply for Azure OpenAI service
   - Obtain the Endpoint, API Key, and Deployment Name

4. **ngrok**
   - Register for an ngrok account and obtain the Auth Token
   - Download and install ngrok

5. **Environment Variable Setup**
   - Copy `.env.example` to `.env` and fill in the information obtained above

## Installation Steps

```bash
pip install -r requirements.txt
```

## How to Run

```bash
python main.py
```

- The program will automatically start ngrok and display a public URL.
- Set the ngrok public URL as the LINE Webhook URL (e.g., `https://xxxx.ngrok-free.app/line/webhook`).

## Notes

- It is recommended to set `max_completion_tokens` to 256~512 to avoid timeouts.
- The `reply_token` can only be used once and must be replied to within 1 minute.
- If you encounter slow responses from the OpenAI API, please adjust the token or optimize the prompt.

## File Descriptions

- `main.py`: Main program
- `.env.example`: Example environment variable file
- `requirements.txt`: List of dependency packages

---

If you have any questions, please refer to the source code comments or submit an Issue.