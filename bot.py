"""telegram_bot_starter_lite.py — one-file Telegram bot, production basics.

Long polling + SQLite logging + commands + inline buttons, ~130 lines.
The multi-module production version with keyboard builders, command
registries, self-test mode and deploy files is the Telegram Bot Starter Kit.

Run:  TELEGRAM_BOT_TOKEN=123:AA... python bot.py
"""
import os
import sqlite3
import sys
import time

import requests

API = "https://api.telegram.org"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


def api(method, **payload):
    resp = requests.post(f"{API}/bot{TOKEN}/{method}", json=payload, timeout=40)
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"{method} failed: {data.get('description')}")
    return data["result"]


def init_db(path="bot.db"):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY, username TEXT, first_seen TEXT)""")
    conn.commit()
    return conn


def log_user(conn, chat_id, username):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conn.execute("""INSERT INTO users (chat_id, username, first_seen) VALUES (?, ?, ?)
                    ON CONFLICT(chat_id) DO NOTHING""", (chat_id, username, now))
    conn.commit()


def confirm_keyboard(action):
    return {"inline_keyboard": [[
        {"text": "✅ Yes", "callback_data": f"confirm:{action}"},
        {"text": "❌ No", "callback_data": f"cancel:{action}"},
    ]]}


HELP = """Commands:
  /start — welcome + menu
  /ping  — liveness check
  /stats — how many users/messages logged
  /reset — inline confirm/cancel demo
Anything else is echoed back."""


def handle_command(api_call, conn, chat_id, text, msg_count):
    name = text[1:].split("@")[0].split(maxsplit=1)[0]
    if name in ("start", "hello"):
        api_call("sendMessage", chat_id=chat_id, text="Hi! I'm the starter-lite bot.\n\n" + HELP)
    elif name == "ping":
        api_call("sendMessage", chat_id=chat_id, text="pong ✅")
    elif name == "stats":
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        api_call("sendMessage", chat_id=chat_id, text=f"Users: {users}\nMessages handled: {msg_count}")
    elif name == "reset":
        api_call("sendMessage", chat_id=chat_id, text="Wipe your data?",
                 reply_markup=confirm_keyboard("reset"))
    elif name == "help":
        api_call("sendMessage", chat_id=chat_id, text=HELP)
    else:
        api_call("sendMessage", chat_id=chat_id, text=f"Unknown command /{name}. Try /help")


def main():
    if ":" not in TOKEN or len(TOKEN.split(":", 1)[1]) < 30:
        print("No valid token. Get one from @BotFather and set TELEGRAM_BOT_TOKEN.")
        sys.exit(1)
    try:
        me = api("getMe")
    except RuntimeError as e:
        if "401" in e.args[0]:
            print("Telegram rejected the token (401). Re-copy it from @BotFather.")
        else:
            print(e)
        sys.exit(1)
    conn = init_db()
    print(f"Bot @{me['username']} started — Ctrl+C to stop.")
    offset, msg_count = 0, 0
    try:
        while True:
            try:
                updates = api("getUpdates", offset=offset, timeout=25,
                              allowed_updates=["message", "callback_query"])
            except RuntimeError as e:
                if "409" in e.args[0]:
                    print("[fatal] Another instance is polling with this token.")
                    sys.exit(1)
                print(f"[warn] {e} — retrying in 5s")
                time.sleep(5)
                continue
            for upd in updates:
                offset = upd["update_id"] + 1
                if "message" in upd:
                    msg = upd["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text") or ""
                    msg_count += 1
                    log_user(conn, chat_id, (msg.get("from") or {}).get("username"))
                    if text.startswith("/"):
                        handle_command(api, conn, chat_id, text, msg_count)
                    else:
                        api("sendMessage", chat_id=chat_id, text=f"🔁 {text}")
                elif "callback_query" in upd:
                    cb = upd["callback_query"]
                    data = cb.get("data", "")
                    answer = "Done." if data.startswith("confirm:") else "Cancelled."
                    api("answerCallbackQuery", callback_query_id=cb["id"], text=answer)
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\nBye — data saved.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
