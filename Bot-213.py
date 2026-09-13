import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Put these in Render/Railway Variables — NEVER hard-code secrets.
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION_STRING"]

# Safety limits: admin-only and a delay between mentions.
DELAY = float(os.getenv("TAG_DELAY", "5"))
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
running = {}

async def is_admin(event):
    if OWNER_ID and event.sender_id == OWNER_ID:
        return True
    try:
        p = await event.client.get_permissions(event.chat_id, event.sender_id)
        return bool(p.is_admin or p.is_creator)
    except Exception:
        return False

async def stop_task(chat_id):
    task = running.pop(chat_id, None)
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

async def tag_one_by_one(event):
    chat_id = event.chat_id
    try:
        participants = []
        async for u in client.iter_participants(chat_id):
            if not u.bot and not u.deleted:
                participants.append(u)

        for u in participants:
            if running.get(chat_id) is not asyncio.current_task():
                return
            name = (u.first_name or "User").replace("\n", " ")
            await event.respond(f"👤 {name}", formatting_entities=[
                # Telethon supports a mention entity through get_input_entity below;
                # using the built-in mention helper keeps the user's account as sender.
            ])
            # Replace the plain-name message with a safe mention.
            msg = await event.respond(f"@{u.username}" if u.username else name)
            await asyncio.sleep(DELAY)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        await event.respond(f"⚠️ Tag stopped: {type(e).__name__}")
    finally:
        if running.get(chat_id) is asyncio.current_task():
            running.pop(chat_id, None)

@client.on(events.NewMessage(pattern=r"^/tagone$"))
async def tagone(event):
    if not event.is_group:
        return
    if not await is_admin(event):
        return
    if event.chat_id in running:
        await event.respond("⚠️ Tagging already running. Use /stop first.")
        return
    task = asyncio.create_task(tag_one_by_one(event))
    running[event.chat_id] = task
    await event.respond("▶️ One-by-one tagging started. Use /stop to stop.")

@client.on(events.NewMessage(pattern=r"^/stop$"))
async def stop(event):
    if not event.is_group:
        return
    if not await is_admin(event):
        return
    if event.chat_id in running:
        await stop_task(event.chat_id)
        await event.respond("🛑 Tagging stopped.")
    else:
        await event.respond("ℹ️ Nothing is running.")

@client.on(events.NewMessage(pattern=r"^/status$"))
async def status(event):
    if not event.is_group:
        return
    if not await is_admin(event):
        return
    await event.respond("🟢 Running" if event.chat_id in running else "⚪ Idle")

@client.on(events.NewMessage(pattern=r"^/help$"))
async def help_cmd(event):
    await event.respond(
        "🤖 UserBot\n\n"
        "/tagone — one-by-one member tagging (admin only)\n"
        "/stop — stop current tagging\n"
        "/status — show status\n"
        "/help — commands"
    )

print("UserBot starting…")
client.start()
print("UserBot is online.")
client.run_until_disconnected()
