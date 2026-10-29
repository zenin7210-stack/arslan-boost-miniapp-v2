"""Validated orders and payment accounting shared by the bot and Mini App API."""
import hashlib
import hmac
import json
import math
import re
import sqlite3
import time
import uuid
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import parse_qsl

RANKS = ('Calibration', 'Bronze', 'Silver', 'Gold', 'Phoenix', 'Ranger',
         'Champion', 'Master', 'Elite', 'The Legend')
PRICES = (0, 3000, 4000, 6000, 9000, 13000, 18000, 25000, 35000, 50000)
MODES = {'wing': 'Напарники', 'comp': 'Соревновательный', 'duel': 'Дуэль'}
METHODS = ('humo', 'uzcard', 'terminal', 'stars', 'balance')
ALIASES = {'Калибровка': 'Calibration', 'Fenix': 'Phoenix', 'Elita': 'Elite'}
PAYMENT_TAGS = {'uzcard':'Оплачу на узкард #uzcard', 'humo':'Оплачу на хумо #humo',
                'stars':'Оплачу на тг старс #stars', 'terminal':'Оплачу на терминал #terminal',
                'balance':'Оплачу с баланса #balance'}


def player_name(value):
    if not isinstance(value, str):
        raise ValidationError('invalid_game_id')
    value=value.strip()
    if not 1 <= len(value) <= 32 or any(unicodedata.category(c).startswith('C') or c in '<>\u2028\u2029' for c in value):
        raise ValidationError('invalid_game_id')
    return value


def payment_tag(message):
    """Recognize one explicit tag/keyword, never silently choose between methods."""
    lowered=message.casefold()
    tagged=set(re.findall(r'(?<!\w)#(uzcard|humo|stars|terminal)(?!\w)',lowered))
    if len(tagged)==1:
        return tagged.pop()
    if tagged:
        return None
    matches={method for method,phrase in {'uzcard':'оплачу на узкард','humo':'оплачу на хумо',
            'stars':'оплачу на тг старс','terminal':'оплачу на терминал'}.items() if phrase in lowered}
    return matches.pop() if len(matches)==1 else None


class ValidationError(ValueError):
    pass


def integer(value, low, high):
    if isinstance(value, bool) or not re.fullmatch(r'\d+', str(value)):
        raise ValidationError('invalid_number')
    value = int(value)
    if not low <= value <= high:
        raise ValidationError('invalid_number')
    return value


def rank_index(data, index_key, name_key):
    if index_key in data:
        return integer(data[index_key], 0, len(RANKS) - 1)
    name = data.get(name_key)
    if not isinstance(name, str):
        raise ValidationError('invalid_rank')
    name = ALIASES.get(name, name)
    if name not in RANKS:
        raise ValidationError('invalid_rank')
    return RANKS.index(name)


def validate_order(data):
    if not isinstance(data, dict):
        raise ValidationError('invalid_order')
    start = rank_index(data, 'fromIndex', 'from')
    end = rank_index(data, 'toIndex', 'to')
    game_id = player_name(data.get('gameId', ''))
    if end <= start or data.get('mode') not in MODES:
        raise ValidationError('invalid_rank')
    method = data.get('paymentMethod', 'terminal')
    if method not in METHODS:
        raise ValidationError('invalid_payment_method')
    return dict(mode=data['mode'], start=start, end=end, game_id=game_id,
                amount=sum(PRICES[start + 1:end + 1]), method=method,
                lang='ru' if data.get('lang') == 'ru' else 'uz')


def validate_init_data(raw, token, now=None):
    """Accept only Telegram-signed, recent initData. Client user fields are untrusted."""
    if not raw or len(raw) > 16000:
        raise ValidationError('unauthorized')
    pairs = parse_qsl(raw, keep_blank_values=True)
    data = dict(pairs)
    if len(data) != len(pairs):
        raise ValidationError('unauthorized')
    received_hash = data.pop('hash', '')
    check = '\n'.join(f'{key}={value}' for key, value in sorted(data.items()))
    key = hmac.new(b'WebAppData', token.encode(), hashlib.sha256).digest()
    expected = hmac.new(key, check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received_hash):
        raise ValidationError('unauthorized')
    now = int(time.time()) if now is None else now
    auth_date = integer(data.get('auth_date', ''), 1, 10**12)
    if now - auth_date > 86400 or auth_date > now + 30:
        raise ValidationError('session_expired')
    try:
        user = json.loads(data.get('user', '{}'))
        if not isinstance(user, dict):
            raise ValidationError('unauthorized')
        user['id'] = integer(user.get('id'), 1, 2**63 - 1)
    except (TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValidationError('unauthorized') from exc
    return user


def request_key(data):
    key = data.get('requestId') or uuid.uuid4().hex
    if not isinstance(key, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{8,80}', key):
        raise ValidationError('invalid_request')
    return key


class Store:
    def __init__(self, path, stars_rate=0):
        self.path = str(path)
        self.stars_rate = integer(stars_rate, 0, 1000000)
        self.init_db()

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.path, timeout=15)
        con.row_factory = sqlite3.Row
        try:
            con.execute('BEGIN IMMEDIATE')
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def init_db(self):
        with self.connect() as con:
            con.execute('''CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT,
                access_type TEXT, mode TEXT, current_rank INTEGER, target_rank INTEGER,
                amount INTEGER, card TEXT, receipt_file_id TEXT, receipt_type TEXT,
                status TEXT DEFAULT 'pending', created_at TEXT)''')
            columns = {row['name'] for row in con.execute('PRAGMA table_info(orders)')}
            for name, definition in {'game_id': "TEXT DEFAULT ''", 'request_key': 'TEXT',
                                     'lang': "TEXT DEFAULT 'uz'"}.items():
                if name not in columns:
                    con.execute(f'ALTER TABLE orders ADD COLUMN {name} {definition}')
            con.execute('CREATE UNIQUE INDEX IF NOT EXISTS order_requests ON orders(user_id, request_key)')
            con.execute('''CREATE TABLE IF NOT EXISTS accounts (
                user_id INTEGER PRIMARY KEY, balance INTEGER NOT NULL DEFAULT 0 CHECK(balance >= 0))''')
            account_columns={row['name'] for row in con.execute('PRAGMA table_info(accounts)')}
            for name,definition in {'game_id':"TEXT DEFAULT ''",'lang':"TEXT DEFAULT 'uz'"}.items():
                if name not in account_columns:
                    con.execute(f'ALTER TABLE accounts ADD COLUMN {name} {definition}')
            con.execute('''CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
                order_id INTEGER, kind TEXT NOT NULL, method TEXT NOT NULL,
                amount INTEGER NOT NULL, stars INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending', request_key TEXT NOT NULL,
                telegram_charge_id TEXT UNIQUE, created_at TEXT NOT NULL,
                receipt_file_id TEXT, receipt_type TEXT,
                UNIQUE(user_id, request_key))''')
            con.execute('''CREATE TABLE IF NOT EXISTS admin_credits (
                request_key TEXT PRIMARY KEY, user_id INTEGER NOT NULL, amount INTEGER NOT NULL)''')
            con.execute('''CREATE TABLE IF NOT EXISTS business_replies (
                connection_id TEXT,chat_id INTEGER,message_id INTEGER,
                PRIMARY KEY(connection_id,chat_id,message_id))''')

    def stars_for(self, amount, method):
        if method != 'stars':
            return 0
        if not self.stars_rate:
            raise ValidationError('stars_not_configured')
        return math.ceil(amount / self.stars_rate)

    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    def create_order(self, user, data):
        order = validate_order(data)
        key = request_key(data)
        with self.connect() as con:
            existing = con.execute('SELECT * FROM orders WHERE user_id=? AND request_key=?',
                                   (user['id'], key)).fetchone()
            if existing:
                values = (existing['mode'], existing['current_rank'], existing['target_rank'],
                          existing['game_id'], existing['card'])
                if values != (order['mode'], order['start'], order['end'], order['game_id'], order['method']):
                    raise ValidationError('request_conflict')
                return dict(existing), False
            stars = self.stars_for(order['amount'], order['method'])
            status = 'paid' if order['method'] == 'balance' else 'pending'
            if order['method'] == 'balance':
                updated = con.execute('UPDATE accounts SET balance=balance-? WHERE user_id=? AND balance>=?',
                                      (order['amount'], user['id'], order['amount'])).rowcount
                if not updated:
                    raise ValidationError('insufficient_balance')
            row = con.execute('''INSERT INTO orders (user_id, username, access_type, mode,
                current_rank, target_rank, game_id, amount, card, status, created_at, request_key, lang)
                VALUES (?, ?, 'yes', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (user['id'], user.get('username', ''), order['mode'], order['start'], order['end'],
                 order['game_id'], order['amount'], order['method'], status, self.now(), key, order['lang']))
            order_id = row.lastrowid
            con.execute('''INSERT INTO accounts(user_id,game_id,lang) VALUES (?,?,?)
                ON CONFLICT(user_id) DO UPDATE SET game_id=excluded.game_id,lang=excluded.lang''',
                (user['id'],order['game_id'],order['lang']))
            con.execute('''INSERT INTO payments (user_id, order_id, kind, method, amount,
                stars, status, request_key, created_at) VALUES (?, ?, 'order', ?, ?, ?, ?, ?, ?)''',
                (user['id'], order_id, order['method'], order['amount'], stars, status, key, self.now()))
            return dict(con.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()), True

    def create_topup(self, user, data):
        if not isinstance(data, dict):
            raise ValidationError('invalid_request')
        amount = integer(data.get('amount'), 1, 100000000)
        method = data.get('paymentMethod')
        if method not in METHODS[:-1]:
            raise ValidationError('invalid_payment_method')
        key = request_key(data)
        with self.connect() as con:
            existing = con.execute('SELECT * FROM payments WHERE user_id=? AND request_key=?',
                                   (user['id'], key)).fetchone()
            if existing:
                if (existing['kind'], existing['method'], existing['amount']) != ('topup', method, amount):
                    raise ValidationError('request_conflict')
                return dict(existing), False
            stars = self.stars_for(amount, method)
            row = con.execute('''INSERT INTO payments (user_id, kind, method, amount,
                stars, request_key, created_at) VALUES (?, 'topup', ?, ?, ?, ?, ?)''',
                (user['id'], method, amount, stars, key, self.now()))
            return dict(con.execute('SELECT * FROM payments WHERE id=?', (row.lastrowid,)).fetchone()), True

    def payment(self, payment_id=None, order_id=None):
        with self.connect() as con:
            if payment_id is not None:
                row = con.execute('SELECT * FROM payments WHERE id=?', (payment_id,)).fetchone()
            else:
                row = con.execute('SELECT * FROM payments WHERE order_id=?', (order_id,)).fetchone()
            if not row:
                raise ValidationError('payment_not_found')
            return dict(row)

    def check_stars(self, payment_id, user_id, currency, total):
        payment = self.payment(payment_id)
        if (payment['method'] != 'stars' or payment['status'] != 'pending'
                or payment['user_id'] != user_id or currency != 'XTR' or payment['stars'] != total):
            raise ValidationError('invalid_payment')
        return payment

    @staticmethod
    def apply_paid(con, payment):
        if payment['kind'] == 'topup':
            con.execute('''INSERT INTO accounts(user_id, balance) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET balance=balance+excluded.balance''',
                (payment['user_id'], payment['amount']))
        else:
            con.execute("UPDATE orders SET status='paid' WHERE id=? AND status='pending'", (payment['order_id'],))

    def settle_stars(self, payment_id, user_id, currency, total, charge_id):
        if not isinstance(charge_id, str) or not charge_id:
            raise ValidationError('invalid_payment')
        with self.connect() as con:
            payment = con.execute('SELECT * FROM payments WHERE id=?', (payment_id,)).fetchone()
            if not payment or (payment['method'], payment['user_id'], currency, payment['stars']) != ('stars', user_id, 'XTR', total):
                raise ValidationError('invalid_payment')
            if payment['status'] == 'paid':
                if payment['telegram_charge_id'] != charge_id:
                    raise ValidationError('duplicate_payment')
                return False
            if payment['status'] != 'pending':
                raise ValidationError('invalid_payment')
            duplicate = con.execute('SELECT id FROM payments WHERE telegram_charge_id=?', (charge_id,)).fetchone()
            if duplicate:
                raise ValidationError('duplicate_payment')
            con.execute("UPDATE payments SET status='paid', telegram_charge_id=? WHERE id=?", (charge_id, payment_id))
            self.apply_paid(con, payment)
            return True

    def decide_manual(self, payment_id, approve):
        with self.connect() as con:
            payment = con.execute('SELECT * FROM payments WHERE id=?', (payment_id,)).fetchone()
            if not payment or payment['method'] not in ('humo', 'uzcard', 'terminal'):
                raise ValidationError('invalid_payment')
            if payment['status'] != 'pending':
                return False
            con.execute('UPDATE payments SET status=? WHERE id=?', ('paid' if approve else 'rejected', payment_id))
            if approve:
                self.apply_paid(con, payment)
            elif payment['order_id']:
                con.execute("UPDATE orders SET status='rejected' WHERE id=?", (payment['order_id'],))
            return True

    def attach_receipt(self, payment_id, user_id, file_id, file_type):
        with self.connect() as con:
            return bool(con.execute('''UPDATE payments SET receipt_file_id=?, receipt_type=?
                WHERE id=? AND user_id=? AND status='pending' AND method IN ('humo','uzcard','terminal')''',
                (file_id, file_type, payment_id, user_id)).rowcount)

    def credit(self, user_id, amount, key):
        user_id = integer(user_id, 1, 2**63 - 1)
        amount = integer(amount, 1, 100000000)
        with self.connect() as con:
            if not con.execute('INSERT OR IGNORE INTO admin_credits VALUES (?, ?, ?)', (key, user_id, amount)).rowcount:
                return False
            con.execute('''INSERT INTO accounts(user_id,balance) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET balance=balance+excluded.balance''', (user_id, amount))
            return True

    def profile(self,user_id,game_id=None,lang=None):
        if game_id is not None:
            game_id=player_name(game_id)
        if lang is not None and lang not in ('uz','ru'):
            raise ValidationError('invalid_language')
        with self.connect() as con:
            con.execute('INSERT OR IGNORE INTO accounts(user_id) VALUES (?)',(user_id,))
            if game_id is not None:
                con.execute('UPDATE accounts SET game_id=? WHERE user_id=?',(game_id,user_id))
            if lang is not None:
                con.execute('UPDATE accounts SET lang=? WHERE user_id=?',(lang,user_id))
            return dict(con.execute('SELECT * FROM accounts WHERE user_id=?',(user_id,)).fetchone())

    def state(self, user_id):
        with self.connect() as con:
            account = con.execute('SELECT balance,game_id,lang FROM accounts WHERE user_id=?', (user_id,)).fetchone()
            orders = [dict(r) for r in con.execute('''SELECT id, mode, current_rank, target_rank,
                game_id, amount, card, status, created_at FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 100''', (user_id,))]
            payments = [dict(r) for r in con.execute('''SELECT id, order_id, kind, method, amount,
                stars, status, created_at FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 100''', (user_id,))]
        return {'balance': account['balance'] if account else 0, 'gameId': account['game_id'] if account else '',
                'lang':account['lang'] if account else 'uz','orders': orders, 'payments': payments}

    def claim_business_reply(self,connection_id,chat_id,message_id):
        with self.connect() as con:
            return bool(con.execute('INSERT OR IGNORE INTO business_replies VALUES (?,?,?)',
                (connection_id,chat_id,message_id)).rowcount)

    def release_business_reply(self,connection_id,chat_id,message_id):
        with self.connect() as con:
            con.execute('DELETE FROM business_replies WHERE connection_id=? AND chat_id=? AND message_id=?',
                        (connection_id,chat_id,message_id))
