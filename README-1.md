# Telegram UserBot

This project uses your own Telegram account through a Telethon session.
It does NOT require putting your Telegram password or OTP in the source code.

## 1) Get API credentials
Create Telegram API credentials at my.telegram.org and set:
- API_ID
- API_HASH

## 2) Generate SESSION_STRING locally
Install:
    pip install telethon

Then run:
    python session_gen.py

Enter your phone number and the OTP on your own device. If 2FA is enabled,
enter the password locally. The script prints a SESSION_STRING. Keep it secret.

## 3) Deploy
Upload these files to GitHub and create a Render/Railway service.
Set the environment variables from `.env.example`.
Start command:
    python bot.py

IMPORTANT:
- Do not commit SESSION_STRING, API_HASH, or bot tokens.
- If a Telegram bot token has already been posted publicly, revoke it with BotFather
  and create a new one.
- Tagging is admin-only and has a 5-second default delay.
