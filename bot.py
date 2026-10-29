"""Arslan Boost bot and authenticated Mini App API. Run: python bot.py."""
import asyncio
import base64
import json
import html
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup,
                           FSInputFile, LabeledPrice, PreCheckoutQuery, ReplyKeyboardMarkup,
                           KeyboardButton, WebAppInfo, InputMediaPhoto, BusinessConnection)
from dotenv import load_dotenv
from service import (Store, ValidationError, RANKS, PRICES, MODES, integer, validate_init_data,
                     player_name, payment_tag, PAYMENT_TAGS)

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / '.env')
TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_ID = int(os.getenv('ADMIN_ID') or 0)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', '').lstrip('@').strip()
APP_URL = os.getenv('MINIAPP_URL', '').strip()
BOT_USERNAME = os.getenv('BOT_USERNAME', '').lstrip('@').strip()
CARDS = {key: os.getenv(key.upper(), '').strip() for key in ('humo', 'uzcard')}
CARD_HOLDER=os.getenv('CARD_HOLDER','').strip()
store = Store(os.getenv('DB_PATH') or BASE / 'orders.sqlite3', os.getenv('STARS_RATE_UZS') or 0)
dp = Dispatcher()


class Flow(StatesGroup):
    game_id = State()
    receipt = State()


TEXT = {
 'ru': {
  'welcome':'🔷 <b>Arslan Boost</b>\n\n🎮 Выберите режим:', 'mode':'Выберите режим:',
  'from':'Выберите текущий ранг:', 'to':'Выберите желаемый ранг:', 'game_id':'🆔 Отправьте игровой ID или ник:',
  'invalid':'Проверьте данные и попробуйте ещё раз. /start — начать заново.',
  'pay':'💳 Выберите способ оплаты:', 'open':'Открыть Mini App',
  'humo':'HUMO', 'uzcard':'UZCARD', 'terminal':'Банкомат / терминал', 'stars':'Telegram Stars', 'balance':'С баланса',
  'amount':'Сумма', 'currency':'сум', 'order':'Заказ', 'topup':'Пополнение баланса', 'id':'Игровой ID',
  'calculation':'Расчёт', 'payment_method':'Способ оплаты',
  'receipt':'После оплаты отправьте сюда фото или файл чека. Зачисление произойдёт только после подтверждения.',
  'no_card':'Реквизиты и условия оплаты уточните у администратора.', 'contact':'👤 Написать администратору',
  'receipt_saved':'Чек передан администратору. Ожидайте проверки.', 'wrong_receipt':'Отправьте фото или файл чека.',
  'paid':'✅ Оплата подтверждена. Заказ передан администратору.', 'credited':'✅ Оплата подтверждена. Баланс пополнен.',
  'rejected':'Оплата отклонена. Уточните причину у администратора.', 'already':'Платёж уже обработан.',
  'no_access':'Нет доступа', 'insufficient_balance':'На балансе недостаточно средств. Выберите другой способ оплаты.',
  'stars_not_configured':'Владелец ещё не настроил цену в Stars. Обратитесь к администратору.',
  'support':'По вопросам заказа и оплаты обратитесь к администратору.', 'calibration':'Калибровка',
  'balance_info':'Баланс', 'request':'Хочу оформить заказ. Подскажите условия оплаты.',
  'invoice':'Arslan Boost', 'invoice_desc':'Оплата заказа повышения ранга Standoff 2', 'invoice_topup':'Пополнение баланса Arslan Boost',
  'invalid_payment':'Платёж не прошёл проверку. Откройте новый счёт.', 'saved':'Сохранено',
 },
 'uz': {
  'welcome':'🔷 <b>Arslan Boost</b>\n\n🎮 Rejimni tanlang:', 'mode':'Rejimni tanlang:',
  'from':'Hozirgi rankingizni tanlang:', 'to':'Maqsad rankni tanlang:', 'game_id':'🆔 O‘yin ID yoki nickni yuboring:',
  'invalid':'Ma’lumotlarni tekshirib, qayta urinib ko‘ring. /start — qaytadan boshlash.',
  'pay':'💳 To‘lov usulini tanlang:', 'open':'Mini App’ni ochish',
  'humo':'HUMO', 'uzcard':'UZCARD', 'terminal':'Bankomat / terminal', 'stars':'Telegram Stars', 'balance':'Balansdan',
  'amount':'Summa', 'currency':'so‘m', 'order':'Buyurtma', 'topup':'Balansni to‘ldirish', 'id':'O‘yin ID',
  'calculation':'Hisob', 'payment_method':'To‘lov usuli',
  'receipt':'To‘lovdan keyin chek rasmini yoki faylini shu yerga yuboring. Mablag‘ tasdiqlangandan keyin hisoblanadi.',
  'no_card':'Rekvizit va to‘lov shartlarini administratordan oling.', 'contact':'👤 Administratorga yozish',
  'receipt_saved':'Chek administratorga yuborildi. Tekshiruvni kuting.', 'wrong_receipt':'Chekni rasm yoki fayl sifatida yuboring.',
  'paid':'✅ To‘lov tasdiqlandi. Buyurtma administratorga yuborildi.', 'credited':'✅ To‘lov tasdiqlandi. Balans to‘ldirildi.',
  'rejected':'To‘lov rad etildi. Sababini administratordan bilib oling.', 'already':'To‘lov allaqachon ko‘rib chiqilgan.',
  'no_access':'Ruxsat yo‘q', 'insufficient_balance':'Balansda mablag‘ yetarli emas. Boshqa to‘lov usulini tanlang.',
  'stars_not_configured':'Stars narxi hali belgilanmagan. Administratorga murojaat qiling.',
  'support':'Buyurtma va to‘lov bo‘yicha administratorga murojaat qiling.', 'calibration':'Kalibrovka',
  'balance_info':'Balans', 'request':'Buyurtma bermoqchiman. To‘lov shartlarini yuboring.',
  'invoice':'Arslan Boost', 'invoice_desc':'Standoff 2 rank oshirish buyurtmasi uchun to‘lov', 'invoice_topup':'Arslan Boost balansini to‘ldirish',
  'invalid_payment':'To‘lov tekshiruvdan o‘tmadi. Yangi hisob oching.', 'saved':'Saqlandi',
 }
}


def text(key, lang='uz'):
    return TEXT['ru' if lang == 'ru' else 'uz'].get(key, TEXT['uz']['invalid'])


def language(user):
    return 'ru' if getattr(user, 'language_code', '') == 'ru' else 'uz'


def user_data(user):
    return {'id': user.id, 'username': user.username or ''}


def fmt(amount):
    return f'{amount:,}'.replace(',', ' ')


def rank_name(index, lang='uz'):
    return text('calibration', lang) if index == 0 else RANKS[index]


def single(items):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data=payload)] for label, payload in items])


def admin_link(message=''):
    if not re.fullmatch(r'[a-zA-Z0-9_]{3,32}', ADMIN_USERNAME):
        return None
    return 'https://t.me/' + ADMIN_USERNAME + ('?' + urlencode({'text': message}) if message else '')


def contact_markup(lang='uz', message=''):
    url = admin_link(message)
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=text('contact', lang), url=url)]]) if url else None


def modes_markup(lang='uz'):
    labels = {'wing':'Напарники','comp':'Соревновательный','duel':'Дуэль'} if lang=='ru' else {'wing':'Naparniklar','comp':'Raqobat','duel':'Duel'}
    return single([(label, 'mode:' + mode) for mode, label in labels.items()])


def payment_markup(lang):
    return single([(text(method, lang), 'pay:' + method) for method in ('humo','uzcard','terminal','stars','balance')])


def summary(order, lang='uz'):
    terms = PRICES[order['current_rank'] + 1:order['target_rank'] + 1]
    formula = ' + '.join(map(fmt, terms)) + ' = ' + fmt(order['amount'])
    return (f'🔷 Arslan Boost · {text("order",lang)} #{order["id"]}\n'
            f'🎮 {MODES[order["mode"]]}\n'
            f'🏅 {rank_name(order["current_rank"],lang)} → {rank_name(order["target_rank"],lang)}\n'
            f'🆔 {text("id",lang)}: {order["game_id"]}\n'
            f'🧮 {text("calculation",lang)}: {formula} {text("currency",lang)}\n'
            f'💳 {text("payment_method",lang)}: {text(order["card"],lang)}')


def parse_deep_link(payload):
    if not payload.startswith('ab_') or len(payload) > 64:
        raise ValidationError('invalid_request')
    try:
        raw = payload[3:]
        parts = base64.urlsafe_b64decode(raw + '=' * (-len(raw) % 4)).decode('utf-8').split(',',7)
        method = {'h':'humo','u':'uzcard','t':'terminal','s':'stars','b':'balance'}
        if parts[0] == 'o' and len(parts) == 8:
            return 'order', {'mode':{'w':'wing','c':'comp','d':'duel'}[parts[1]],
                'fromIndex':parts[2], 'toIndex':parts[3], 'paymentMethod':method[parts[4]],
                'lang':'ru' if parts[5]=='r' else 'uz','gameId':parts[7], 'requestId':parts[6]}
        if parts[0] == 't' and len(parts) == 5:
            return 'topup', {'amount':parts[1], 'paymentMethod':method[parts[2]],
                'lang':'ru' if parts[3]=='r' else 'uz', 'requestId':parts[4]}
    except (ValueError, KeyError, UnicodeDecodeError, IndexError) as exc:
        raise ValidationError('invalid_request') from exc
    raise ValidationError('invalid_request')


async def notify_admin(bot, payment, paid=False):
    if not ADMIN_ID:
        return
    if payment['order_id']:
        with store.connect() as con:
            order = dict(con.execute('SELECT * FROM orders WHERE id=?', (payment['order_id'],)).fetchone())
        message = summary(order, 'ru')
    else:
        message = f'Пополнение #{payment["id"]}\n💰 {fmt(payment["amount"])} сум\n💳 {payment["method"].upper()}'
    message += f'\n👤 Telegram ID: {payment["user_id"]}\n' + ('✅ Оплата подтверждена' if paid else '⏳ Ожидает проверки оплаты')
    markup = single([('✅ Подтвердить оплату', f'approve:{payment["id"]}'),
                     ('❌ Отклонить', f'reject:{payment["id"]}')]) if not paid and payment['method'] in ('humo','uzcard','terminal') else None
    try:
        await bot.send_message(ADMIN_ID, message, reply_markup=markup)
    except Exception:
        logging.exception('Could not notify the configured admin')


def invoice_args(payment, lang='uz'):
    return dict(title=text('invoice',lang), description=text('invoice_topup' if payment['kind']=='topup' else 'invoice_desc',lang),
                payload=f'ab:{payment["id"]}', provider_token='', currency='XTR',
                prices=[LabeledPrice(label=text('amount',lang), amount=payment['stars'])])


async def deliver_payment(message, bot, state, payment, lang='uz', order=None, new=True):
    await state.update_data(payment_id=payment['id'], lang=lang)
    if new:
        await notify_admin(bot, payment, payment['status']=='paid')
    if payment['status'] == 'paid':
        await state.clear()
        return await message.answer(text('credited' if payment['kind']=='topup' else 'paid', lang))
    if payment['method'] == 'stars':
        await state.set_state(None)
        return await bot.send_invoice(chat_id=message.chat.id, **invoice_args(payment,lang), start_parameter=f'pay_{payment["id"]}')
    await state.set_state(Flow.receipt)
    description = summary(order,lang) if order else f'{text("topup",lang)} #{payment["id"]}\n💰 {fmt(payment["amount"])} {text("currency",lang)}'
    card = CARDS.get(payment['method'])
    description += '\n\n' + (f'{payment["method"].upper()}: {card}' if card else text('no_card',lang))
    description += '\n\n' + text('receipt',lang)
    draft = (summary(order,lang) if order else description) + '\n\n' + PAYMENT_TAGS[payment['method']]
    await message.answer(description, reply_markup=contact_markup(lang,draft))


connections={}


@dp.business_connection()
async def business_connection(connection:BusinessConnection):
    connections[connection.id]=connection


@dp.business_message(F.text)
async def business_auto_reply(message:Message,bot:Bot):
    """Reply only in explicitly connected admin business chats, with configured details."""
    if not ADMIN_ID or os.getenv('BUSINESS_AUTOREPLY','1')!='1' or not message.business_connection_id:
        return
    method=payment_tag(message.text)
    if not method or not message.from_user or message.from_user.id==ADMIN_ID or message.from_user.is_bot:
        return
    connection=connections.get(message.business_connection_id)
    if connection is None:
        connection=await bot.get_business_connection(message.business_connection_id)
        connections[connection.id]=connection
    if (connection.user.id!=ADMIN_ID or not connection.is_enabled
            or not connection.rights or not connection.rights.can_reply):
        return
    if method in ('humo','uzcard'):
        card=CARDS.get(method)
        if not card:
            return
        reply=f'💳 <b>{method.upper()} orqali to‘lov</b>\n\n<code>{html.escape(card)}</code>'
        if CARD_HOLDER:
            reply+='\n👤 '+html.escape(CARD_HOLDER)
        reply+='\n\nTo‘lovdan so‘ng chekni shu chatga yuboring.'
    elif method=='terminal':
        instructions=os.getenv('TERMINAL_INSTRUCTIONS','').strip()
        if not instructions:
            return
        reply='🏧 <b>Terminal / Bankomat</b>\n\n'+html.escape(instructions)
    else:
        if not BOT_USERNAME:
            return
        reply='⭐️ Telegram Stars orqali to‘lov uchun botda hisobni oching:\nhttps://t.me/'+BOT_USERNAME
    if not store.claim_business_reply(message.business_connection_id,message.chat.id,message.message_id):
        return
    try:
        await bot.send_message(message.chat.id,reply,parse_mode='HTML',business_connection_id=message.business_connection_id)
    except Exception:
        store.release_business_reply(message.business_connection_id,message.chat.id,message.message_id)
        logging.exception('Could not send business payment details')


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    lang = store.profile(message.from_user.id)['lang']
    payload = (message.text or '').split(maxsplit=1)
    if len(payload) == 2 and payload[1].startswith('ab_'):
        try:
            kind, data = parse_deep_link(payload[1]); lang = data['lang']
            if kind == 'order':
                order, new = store.create_order(user_data(message.from_user), data)
                payment = store.payment(order_id=order['id'])
            else:
                payment, new = store.create_topup(user_data(message.from_user), data); order = None
            await deliver_payment(message,bot,state,payment,lang,order,new)
        except ValidationError as exc:
            await message.answer(text(str(exc),lang))
        return
    await state.update_data(lang=lang)
    if APP_URL:
        keyboard=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=text('open',lang),web_app=WebAppInfo(url=APP_URL))]],resize_keyboard=True)
        await message.answer('Arslan Boost', reply_markup=keyboard)
    caption='🤖 Assalomu alaykum! Arslan Boost botiga xush kelibsiz!\n\n🎮 Standoff 2 rank oshirish xizmati.\n\n👇 Tilni tanlang / Выберите язык:'
    markup=InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='🇺🇿 O‘zbekcha',callback_data='setlang:uz'),
        InlineKeyboardButton(text='🇷🇺 Русский',callback_data='setlang:ru')]])
    await message.answer_photo(banner_media(lang),caption=caption,reply_markup=markup)


def banner_media(lang):
    configured=os.getenv('BANNER_FILE_ID_'+lang.upper()) or os.getenv('BANNER_URL_'+lang.upper())
    return configured or FSInputFile(BASE/'assets/hero-banner-hd.png')


@dp.callback_query(F.data.startswith('setlang:'))
async def choose_language(call:CallbackQuery,state:FSMContext):
    lang=call.data.split(':',1)[1]
    if lang not in ('ru','uz'):
        return await call.answer()
    store.profile(call.from_user.id,lang=lang);await state.update_data(lang=lang)
    caption=text('welcome',lang)
    if call.message.caption!=caption:
        await call.message.edit_media(InputMediaPhoto(media=banner_media(lang),caption=caption,parse_mode='HTML'))
    await call.message.answer(text('mode',lang),reply_markup=modes_markup(lang));await call.answer()


@dp.callback_query(F.data.startswith('access:'))
async def legacy_access(call: CallbackQuery, state: FSMContext):
    # Old inline buttons go directly to modes; the removed surcharge stays removed.
    lang=language(call.from_user);await state.update_data(lang=lang)
    await call.message.answer(text('mode',lang),reply_markup=modes_markup(lang)); await call.answer()


@dp.callback_query(F.data.startswith('mode:'))
async def choose_mode(call: CallbackQuery, state: FSMContext):
    mode=call.data.split(':',1)[1]
    if mode not in MODES:
        return await call.answer(text('invalid',language(call.from_user)),show_alert=True)
    data=await state.get_data();lang=data.get('lang',language(call.from_user))
    await state.clear();await state.update_data(mode=mode,lang=lang)
    markup=single([(rank_name(i,lang),f'from:{i}') for i in range(len(RANKS)-1)])
    image=BASE/'assets/ranks.webp'
    if image.is_file():
        await call.message.answer_photo(FSInputFile(image),caption=text('from',lang),reply_markup=markup)
    else:
        await call.message.answer(text('from',lang),reply_markup=markup)
    await call.answer()


@dp.callback_query(F.data.startswith('from:'))
async def choose_from(call: CallbackQuery, state: FSMContext):
    data=await state.get_data();lang=data.get('lang',language(call.from_user))
    try:
        index=integer(call.data.split(':',1)[1],0,len(RANKS)-2)
        if data.get('mode') not in MODES:
            raise ValidationError('invalid')
    except ValidationError:
        return await call.answer(text('invalid',lang),show_alert=True)
    await state.update_data(start=index)
    await call.message.answer(text('to',lang),reply_markup=single([(rank_name(i,lang),f'to:{i}') for i in range(index+1,len(RANKS))]));await call.answer()


@dp.callback_query(F.data.startswith('to:'))
async def choose_to(call: CallbackQuery, state: FSMContext):
    data=await state.get_data();lang=data.get('lang',language(call.from_user))
    try:
        index=integer(call.data.split(':',1)[1],1,len(RANKS)-1)
        if 'start' not in data or index<=data['start'] or data.get('mode') not in MODES:
            raise ValidationError('invalid')
    except ValidationError:
        return await call.answer(text('invalid',lang),show_alert=True)
    await state.update_data(end=index);await state.set_state(Flow.game_id)
    await call.message.answer(text('game_id',lang));await call.answer()


@dp.message(Flow.game_id,F.text,~F.text.startswith('/'))
async def receive_id(message: Message, state: FSMContext):
    data=await state.get_data();lang=data.get('lang','uz'); game_id=(message.text or '').strip()
    try:
        game_id=player_name(game_id)
    except ValidationError:
        return await message.answer(text('game_id',lang))
    store.profile(message.from_user.id,game_id=game_id,lang=lang)
    await state.update_data(game_id=game_id);await state.set_state(None)
    amount=sum(PRICES[data['start']+1:data['end']+1])
    await message.answer(f'🏅 {rank_name(data["start"],lang)} → {rank_name(data["end"],lang)}\n'
                         f'🆔 {game_id}\n💰 {fmt(amount)} {text("currency",lang)}\n\n{text("pay",lang)}',reply_markup=payment_markup(lang))


@dp.callback_query(F.data.startswith('pay:'))
async def choose_payment(call: CallbackQuery,state:FSMContext,bot:Bot):
    data=await state.get_data();lang=data.get('lang',language(call.from_user))
    try:
        if not {'mode','start','end','game_id'}<=data.keys():
            raise ValidationError('invalid')
        method=call.data.split(':',1)[1];key=data.get('draft_key') or os.urandom(12).hex()
        await state.update_data(draft_key=key)
        order,new=store.create_order(user_data(call.from_user),dict(mode=data['mode'],fromIndex=data['start'],toIndex=data['end'],
            gameId=data['game_id'],paymentMethod=method,lang=lang,requestId=key+'_'+method))
        payment=store.payment(order_id=order['id']);await call.answer()
        await deliver_payment(call.message,bot,state,payment,lang,order,new)
    except ValidationError as exc:
        await call.answer(text(str(exc),lang),show_alert=True)


@dp.message(F.web_app_data)
async def web_app_order(message:Message,state:FSMContext,bot:Bot):
    try:
        data=json.loads(message.web_app_data.data)
        if data.get('type')=='topup':
            payment,new=store.create_topup(user_data(message.from_user),data);order=None
        else:
            order,new=store.create_order(user_data(message.from_user),data);payment=store.payment(order_id=order['id'])
        await deliver_payment(message,bot,state,payment,data.get('lang','uz'),order,new)
    except (ValidationError,ValueError,TypeError,AttributeError):
        await message.answer(text('invalid',language(message.from_user)))


@dp.message(Flow.receipt,F.photo|F.document)
async def receipt(message:Message,state:FSMContext,bot:Bot):
    data=await state.get_data();lang=data.get('lang','uz');file_id=message.photo[-1].file_id if message.photo else message.document.file_id
    if not data.get('payment_id') or not store.attach_receipt(data['payment_id'],message.from_user.id,file_id,'photo' if message.photo else 'document'):
        return await message.answer(text('invalid',lang))
    await message.answer(text('receipt_saved',lang))
    if ADMIN_ID:
        await notify_admin(bot,store.payment(data['payment_id']))
        try:
            await message.copy_to(ADMIN_ID)
        except Exception:
            logging.exception('Could not forward receipt')
    await state.clear()


@dp.message(Flow.receipt,~F.successful_payment,~F.web_app_data,~F.text.startswith('/'))
async def wrong_receipt(message:Message,state:FSMContext):
    data=await state.get_data();await message.answer(text('wrong_receipt',data.get('lang','uz')))


@dp.pre_checkout_query()
async def pre_checkout(query:PreCheckoutQuery):
    try:
        if not re.fullmatch(r'ab:\d+',query.invoice_payload):
            raise ValidationError('invalid_payment')
        store.check_stars(int(query.invoice_payload.split(':')[1]),query.from_user.id,query.currency,query.total_amount)
    except ValidationError:
        return await query.answer(ok=False,error_message=text('invalid_payment',language(query.from_user)))
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message:Message,bot:Bot):
    successful=message.successful_payment;lang=language(message.from_user)
    try:
        if not re.fullmatch(r'ab:\d+',successful.invoice_payload):
            raise ValidationError('invalid_payment')
        payment_id=int(successful.invoice_payload.split(':')[1])
        changed=store.settle_stars(payment_id,message.from_user.id,successful.currency,successful.total_amount,successful.telegram_payment_charge_id)
    except ValidationError:
        logging.exception('Payment verification failed')
        return await message.answer(text('invalid_payment',lang),reply_markup=contact_markup(lang))
    if changed:
        payment=store.payment(payment_id);await message.answer(text('credited' if payment['kind']=='topup' else 'paid',lang))
        await notify_admin(bot,payment,paid=True)


@dp.callback_query(F.data.startswith(('approve:','reject:')))
async def admin_action(call:CallbackQuery,bot:Bot):
    if call.from_user.id!=ADMIN_ID:
        return await call.answer(text('no_access',language(call.from_user)),show_alert=True)
    try:
        action,payment_id=call.data.split(':',1);payment_id=integer(payment_id,1,2**63-1)
        changed=store.decide_manual(payment_id,action=='approve');payment=store.payment(payment_id)
    except ValidationError:
        return await call.answer('Неверный платёж',show_alert=True)
    if changed:
        await bot.send_message(payment['user_id'],text('credited' if action=='approve' and payment['kind']=='topup' else 'paid' if action=='approve' else 'rejected','uz'),reply_markup=contact_markup())
    await call.message.edit_reply_markup(reply_markup=None);await call.answer(text('saved' if changed else 'already','ru'))


@dp.message(Command('support','paysupport'))
async def support(message:Message):
    lang=language(message.from_user);await message.answer(text('support',lang),reply_markup=contact_markup(lang))


@dp.message(Command('balance'))
async def balance(message:Message):
    lang=language(message.from_user);amount=store.state(message.from_user.id)['balance']
    await message.answer(f'{text("balance_info",lang)}: {fmt(amount)} {text("currency",lang)}')


@dp.message(Command('credit'))
async def credit(message:Message,bot:Bot):
    if message.from_user.id!=ADMIN_ID:
        return
    try:
        _,user_id,amount=message.text.split();changed=store.credit(user_id,amount,f'{message.chat.id}:{message.message_id}')
    except (ValueError,ValidationError):
        return await message.answer('/credit TELEGRAM_ID СУММА_В_СУМАХ')
    await message.answer('Баланс пополнен.' if changed else 'Операция уже выполнена.')
    if changed:
        try:
            await bot.send_message(int(user_id),text('credited','uz'))
        except Exception:
            logging.exception('Could not deliver balance notification')


@dp.message(Command('admin'))
async def admin(message:Message):
    if message.from_user.id!=ADMIN_ID:
        return
    with store.connect() as con:
        orders=con.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
        pending=con.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0]
        paid=con.execute("SELECT COUNT(*) FROM payments WHERE status='paid'").fetchone()[0]
    await message.answer(f'Arslan Boost\nЗаказов: {orders}\nОжидают оплаты: {pending}\nОплачено: {paid}\n\n/credit TELEGRAM_ID СУММА — пополнить баланс вручную')


def create_app(bot):
    origin=os.getenv('ALLOWED_ORIGIN','').strip() or (f'{urlsplit(APP_URL).scheme}://{urlsplit(APP_URL).netloc}' if APP_URL else '')

    @web.middleware
    async def middleware(request,handler):
        if request.method=='OPTIONS':
            response=web.Response(status=204)
        else:
            try:
                response=await handler(request)
            except ValidationError as exc:
                response=web.json_response({'error':str(exc)},status=401 if str(exc) in ('unauthorized','session_expired') else 400)
            except (json.JSONDecodeError,UnicodeDecodeError):
                response=web.json_response({'error':'invalid_json'},status=400)
        if origin and request.headers.get('Origin')==origin:
            response.headers['Access-Control-Allow-Origin']=origin;response.headers['Vary']='Origin'
            response.headers['Access-Control-Allow-Headers']='Content-Type, X-Telegram-Init-Data'
            response.headers['Access-Control-Allow-Methods']='GET, POST, OPTIONS'
        response.headers['Cache-Control']='no-store' if request.path.startswith('/api/') else 'no-cache'
        return response

    app=web.Application(middlewares=[middleware],client_max_size=16000)

    async def public_config(request):
        return web.json_response({'arslanBoostApi':True,'supportUrl':admin_link(),
            'botUrl':'https://t.me/'+BOT_USERNAME if BOT_USERNAME else None,
            'starsRate':store.stars_rate,'prices':list(PRICES),'cards':CARDS,'cardHolder':CARD_HOLDER,
            'banners':{'uz':os.getenv('BANNER_URL_UZ') or 'assets/hero-banner-hd.png',
                       'ru':os.getenv('BANNER_URL_RU') or 'assets/hero-banner-hd.png'}})

    def authenticate(request):
        return validate_init_data(request.headers.get('X-Telegram-Init-Data',''),TOKEN)

    async def state_endpoint(request):
        user=authenticate(request);return web.json_response(store.state(user['id']))

    async def profile_endpoint(request):
        user=authenticate(request);data=await request.json()
        if not isinstance(data,dict):
            raise ValidationError('invalid_request')
        return web.json_response(store.profile(user['id'],game_id=data.get('gameId'),lang=data.get('lang')))

    async def checkout(request):
        user=authenticate(request);data=await request.json()
        order,new=store.create_order(user,data);payment=store.payment(order_id=order['id'])
        result={'id':order['id'],'amount':order['amount'],'stars':payment['stars'],'status':order['status']}
        if payment['method']=='stars' and payment['status']=='pending':
            result['invoiceLink']=await bot.create_invoice_link(**invoice_args(payment,order['lang']))
        if new:
            await notify_admin(bot,payment,paid=order['status']=='paid')
        return web.json_response(result)

    async def topup(request):
        user=authenticate(request);data=await request.json()
        if not isinstance(data,dict):
            raise ValidationError('invalid_request')
        payment,new=store.create_topup(user,data)
        result={'id':payment['id'],'amount':payment['amount'],'stars':payment['stars'],'status':payment['status']}
        if payment['method']=='stars' and payment['status']=='pending':
            result['invoiceLink']=await bot.create_invoice_link(**invoice_args(payment,data.get('lang','uz')))
        if new:
            await notify_admin(bot,payment,paid=False)
        return web.json_response(result)

    async def index(request):
        return web.FileResponse(BASE/'index.html')

    async def static_file(request):
        name=request.match_info['name']
        if name not in ('app.js','app.css','config.js'):
            raise web.HTTPNotFound()
        return web.FileResponse(BASE/name)

    app.router.add_get('/api/config',public_config);app.router.add_post('/api/state',state_endpoint)
    app.router.add_post('/api/profile',profile_endpoint)
    app.router.add_post('/api/checkout',checkout);app.router.add_post('/api/topup',topup)
    async def options(request):
        return web.Response(status=204)
    app.router.add_route('OPTIONS','/api/{path:.*}',options)
    app.router.add_get('/',index);app.router.add_get('/index.html',index)
    app.router.add_static('/assets/',BASE/'assets',show_index=False,follow_symlinks=False)
    app.router.add_get('/{name}',static_file)
    return app


async def main():
    global BOT_USERNAME
    if not TOKEN or TOKEN=='PASTE_BOTFATHER_TOKEN_HERE':
        raise RuntimeError('Укажите BOT_TOKEN в .env на сервере')
    bot=Bot(TOKEN);runner=None
    try:
        me=await bot.get_me();BOT_USERNAME=me.username
        if os.getenv('ENABLE_HTTP','1')=='1':
            runner=web.AppRunner(create_app(bot));await runner.setup()
            await web.TCPSite(runner,os.getenv('HTTP_HOST','0.0.0.0'),int(os.getenv('PORT') or os.getenv('HTTP_PORT') or 8080)).start()
        await bot.delete_webhook(drop_pending_updates=False)
        await dp.start_polling(bot,close_bot_session=False)
    finally:
        if runner:
            await runner.cleanup()
        await bot.session.close()


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
