# telegram-bot-starter-lite

A **single-file** Telegram bot in plain Python — the smallest thing that still
runs in production: long polling, a few commands, an inline-button callback,
and SQLite logging. ~130 lines, no frameworks, one dependency (`requests`).

This is the free "lite" companion of the **[Telegram Bot Starter Kit](https://adonisflare56.gumroad.com/l/telegram-bot-kit)** —
a production-shaped, multi-module kit (command/callback registries, reply +
inline keyboard builders, per-chat echo mode, `--check` self-test, 409-conflict
detection, Dockerfile + docker-compose + systemd unit) for when your bot
outgrows one file.

## Quick start

```bash
pip install requests
export TELEGRAM_BOT_TOKEN=123456:AA...   # from @BotFather
python bot.py
```

Open your bot in Telegram and send `/start`.

## What's inside

- Long polling with correct `offset` tracking
- `/start` `/help` `/ping` `/echo` commands + inline yes/no buttons
- Every message logged to SQLite (WAL mode)
- Clear errors for the two classics: 401 (bad token) and 409 (another
  instance already polling with this token)

## When you outgrow it

The [full Starter Kit](https://adonisflare56.gumroad.com/l/telegram-bot-kit)
splits this into `bot.py / telegram_api.py / handlers.py / keyboards.py /
storage.py / config.py`, adds decorator-based command + callback registries
(add a command in 3 lines), reply/inline keyboard builders, a confirm/cancel
pattern, per-chat echo mode, a `--check` self-test mode, and ready-to-use
Docker + systemd deployment files.

MIT-style single-user license for the kit; this lite repo is MIT.
