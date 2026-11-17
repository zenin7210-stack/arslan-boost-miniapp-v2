"""Read-only diagnostic for Telegram payment-notification bot dialogs.

Requires a *user* MTProto session (Telethon StringSession), not a BotFather token.
This intentionally DOES NOT parse payments or credit any balances.
Environment:
  TG_API_ID, TG_API_HASH, TG_SESSION (secret StringSession)
  PAYMENT_BOT_USERNAMES (optional; default CardXabarBot,HUMOcardbot)
Run: python scripts/payment_bot_reader.py
"""

import asyncio
import os
from datetime import timezone

from telethon import TelegramClient, events
from telethon.sessions import StringSession


async def main():
    try:
        api_id = int(os.environ["TG_API_ID"])
        api_hash = os.environ["TG_API_HASH"]
        session = os.environ["TG_SESSION"]
    except (KeyError, ValueError) as exc:
        raise SystemExit("Set TG_API_ID, TG_API_HASH and TG_SESSION in private environment variables.") from exc

    handles = [
        handle.strip().lstrip("@")
        for handle in os.getenv("PAYMENT_BOT_USERNAMES", "CardXabarBot,HUMOcardbot").split(",")
        if handle.strip()
    ]
    if not handles:
        raise SystemExit("No payment bot usernames configured.")

    client = TelegramClient(StringSession(session), api_id, api_hash)
    async with client:
        if not await client.is_user_authorized():
            raise SystemExit("TG_SESSION is not an authorized USER session. A BotFather token will not work.")

        me = await client.get_me()
        print(f"Authorized Telegram user ID: {me.id}")
        watch = []
        for handle in handles:
            try:
                peer = await client.get_entity(handle)
                if not getattr(peer, "bot", False):
                    print(f"@{handle}: resolved account is NOT a bot; skipped")
                    continue
                last = await client.get_messages(peer, limit=1)
                if last:
                    msg = last[0]
                    date = msg.date.astimezone(timezone.utc).isoformat() if msg.date else "unknown"
                    print(f"@{handle}: bot visible, peer_id={peer.id}, latest_message_id={msg.id}, UTC={date}")
                else:
                    print(f"@{handle}: bot visible, but no accessible message history")
                watch.append(peer)
            except Exception as exc:
                # Do not display session strings, message text, or payment details.
                print(f"@{handle}: not accessible ({type(exc).__name__})")

        if not watch:
            raise SystemExit("No notification-bot dialogs resolved. Check the user session and usernames.")

        @client.on(events.NewMessage(chats=watch))
        async def on_notification(event):
            # Diagnostics only: do not interpret message text as proof of payment.
            dt = event.message.date.astimezone(timezone.utc).isoformat()
            print(f"Notification seen: bot_chat={event.chat_id}, msg_id={event.id}, UTC={dt}")

        print("Listening for NEW messages from configured bots (read-only). Press Ctrl+C to stop.")
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
