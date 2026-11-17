"""One-time LOCAL login for your own Telegram account.

Run only on a trusted personal computer, never in a public server or chat.
Creates ~/.arslan_payment_session.env with mode 0600 where supported.
Do not upload this file to GitHub and NEVER share it in chat.
"""

import asyncio
import getpass
import os
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession


def secret_input(label):
    return getpass.getpass(label).strip()


async def main():
    print("ARSLAN BOOST: local Telegram USER session setup")
    print("Use the Telegram account that receives CardXabarBot / HUMOcardbot notifications.")
    print("Never send your login code, API hash, password, or session to anyone.")
    raw_id = os.environ.get("TG_API_ID") or input("my.telegram.org API ID: ").strip()
    api_hash = os.environ.get("TG_API_HASH") or secret_input("my.telegram.org API hash (hidden): ")
    try:
        api_id = int(raw_id)
    except ValueError as exc:
        raise SystemExit("Invalid API ID (must be a number).") from exc
    if api_id <= 0 or not api_hash:
        raise SystemExit("Both API ID and API hash are required.")

    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        await client.start(
            phone=lambda: input("Your Telegram phone number (international format): ").strip(),
            code_callback=lambda: secret_input("Telegram login code (hidden): "),
            password=lambda: secret_input("Two-step verification password if prompted (hidden): "),
        )
        me = await client.get_me()
        if getattr(me, "bot", False):
            raise SystemExit("Login belongs to a bot, not a personal account.")
        session = client.session.save()
        if not session:
            raise SystemExit("Failed to create an authenticated session.")

    target = Path.home() / ".arslan_payment_session.env"
    if target.exists():
        raise SystemExit(f"{target} already exists. Not overwriting your session.")
    fd = os.open(str(target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        out.write(f"TG_API_ID={api_id}\nTG_API_HASH={api_hash}\nTG_SESSION={session}\n")
    try:
        target.chmod(0o600)
    except OSError:
        pass
    print(f"Authorized personal account ID: {me.id}")
    print(f"Session saved locally to: {target}")
    print("KEEP THE FILE PRIVATE. Add these values to Render's private environment variables.")
    print("Do not paste its contents into ChatGPT, Telegram, GitHub or screenshots.")


if __name__ == "__main__":
    asyncio.run(main())
