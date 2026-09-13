import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(input("API ID: ").strip())
api_hash = input("API HASH: ").strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\nLogin to your Telegram account.")
    print("Your phone/OTP/2FA stay on this local machine.")
    print("\nSESSION_STRING:\n")
    print(client.session.save())
