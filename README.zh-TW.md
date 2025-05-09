[English](README.md) | [中文說明](README.zh-TW.md)

# LINE Bot + Azure OpenAI + ngrok

本專案為一個結合 LINE Messaging API、Azure OpenAI 與 ngrok 的 Python Flask 範例。

## 事前準備

1. **Python 環境**
   - 安裝 Python 3.8 以上版本

2. **LINE Bot 設定**
   - 申請 LINE Messaging API Channel
   - 取得 Channel Access Token 與 Channel Secret

3. **Azure OpenAI 設定**
   - 申請 Azure OpenAI 服務
   - 取得 Endpoint、API Key、Deployment Name

4. **ngrok**
   - 註冊 ngrok 帳號並取得 Auth Token
   - 下載並安裝 ngrok

5. **設定環境變數**
   - 複製 `.env.example` 為 `.env`，填入上述資訊

## 安裝步驟

```bash
pip install -r requirements.txt
```

## 啟動方式

```bash
python main.py
```

- 程式會自動啟動 ngrok 並顯示 public URL
- 將 ngrok public URL 設為 LINE Webhook URL（如 `https://xxxx.ngrok-free.app/line/webhook`）

## 注意事項

- `max_completion_tokens` 建議設 256~512，避免超時
- reply_token 只能用一次，且需在 1 分鐘內回覆
- 若遇到 OpenAI API 回應過慢，請調整 token 或優化 prompt

## 檔案說明

- `main.py`：主程式
- `.env.example`：環境變數範例
- `requirements.txt`：依賴套件列表

---

如有問題請參考原始碼註解或提出 Issue。