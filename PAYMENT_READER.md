# Reading UZCARD / HUMO notification bots — diagnostic only

The main payment bot uses aiogram / Bot API. A Bot API token cannot read
the owner's private dialog with another bot. This script uses **Telethon
and an authorized USER session** to verify access to `@CardXabarBot` and
`@HUMOcardbot`.

1. Install separately: `pip install -r requirements-payment-reader.txt`.
2. Create a Telegram API ID/hash on the official Telegram developer site.
3. Authorize your own account in a trusted local environment and obtain a
   Telethon `StringSession`. Store it only as the private `TG_SESSION`
   environment variable. Never commit session strings, API hashes,
   phone codes, or bank notifications to GitHub.
4. Set `TG_API_ID`, `TG_API_HASH`, `TG_SESSION`. Optionally set
   `PAYMENT_BOT_USERNAMES=CardXabarBot,HUMOcardbot`.
5. Run `python scripts/payment_bot_reader.py` on a machine with
   persistent connectivity. It prints resolved bot IDs and the timestamp
   of their latest messages, then watches *new* messages. It does not
   print banking message bodies or change customer balances.

If normal chats are visible but bot chats are missing, verify that the
authorized user session is **the same Telegram account that receives
the notification bot messages**. Some bot services can be accessed only
through a specific user account. The diagnostic is independent of any
Business API connection.

IMPORTANT: These are **unverified Telegram notifications**, not
provider-signed bank settlement webhooks. They must not automatically
credit wallets based on amount/card/time alone; identical transfers,
replays, deleted/late messages, and notification format changes can
cause errors. Keep admin approval in place until a trusted payment
source, unique transaction reference, and idempotent transaction
matching are available.

Cloudflare Workers accept inbound HTTP requests; they cannot
automatically intercept phone push notifications or another bot's
private Telegram messages. If an official payment provider webhook
is available, verify the provider signature and merchant/order ID
before relaying its event to the Render backend. The Worker-to-Render
shared secret alone does not establish the authenticity of the
original bank event.

Render's default filesystem is ephemeral: orders.sqlite3 must be moved
to persistent storage (or replaced by a managed database) before real
money is settled, otherwise balances can be lost on restart/redeploy.
