'use strict';
(() => {
  const tg = window.Telegram?.WebApp;
  try { tg?.ready(); tg?.expand(); tg?.setHeaderColor?.('#06101e'); tg?.setBackgroundColor?.('#06101e'); } catch {}
  const $ = s => document.querySelector(s);
  const all = s => [...document.querySelectorAll(s)];
  const storage = {get(k) { try { return localStorage.getItem(k); } catch { return null; } }, set(k,v) { try { localStorage.setItem(k,v); } catch {} }};
  const config = {...window.ARSLAN_CONFIG};
  const ranks = ['Calibration','Bronze','Silver','Gold','Phoenix','Ranger','Champion','Master','Elite','The Legend'];
  let prices = [0,3000,4000,6000,9000,13000,18000,25000,35000,50000];
  const rankCenters = [null,[214,174],[380,174],[546,174],[723,174],[723,317],[723,460],[905,174],[905,317],[1095,174]];
  const dictionaries = {
    ru: {
      miniApp:'мини-приложение',balance:'Баланс',promo:'Промокод',support:'Поддержка',chooseMode:'Выберите режим',
      currentRank:'Текущий ранг',targetRank:'Желаемый ранг',gameId:'Игровой ID или ник',orderPrice:'Стоимость заказа',order:'Заказать',
      history:'История',orders:'Заказы',payments:'Платежи',all:'Все',completed:'Оплачено',pending:'Ожидают',cancelled:'Отклонено',
      emptyHistory:'Пока нет операций',appUser:'Пользователь Mini App',balanceCaption:'БАЛАНС',cashback:'КЕШБЭК',settings:'Настройки',language:'ЯЗЫК',settingsCaption:'НАСТРОЙКИ',
      profile:'Данные профиля',profileDesc:'Ваш профиль и личные данные',orderHistory:'История заказов',historyDesc:'Все заказы и их статусы',
      promoCodes:'Промокоды',promoDesc:'Промокоды и бонусы',supportDesc:'Помощь с заказами и оплатой',animations:'Анимации',motionDesc:'Уменьшить анимации приложения',
      security:'Безопасность',securityDesc:'Не отправляйте пароль от аккаунта боту',about:'О приложении',aboutDesc:'Arslan Boost · повышение ранга Standoff 2',home:'Главная',skip:'Пропустить',
      priceNote:'Цена складывается из выбранных ступеней ранга. Способ оплаты можно выбрать при заказе — пополнять баланс заранее не обязательно.',
      selectedMode:'Выбранный режим',wing:'Напарники',comp:'Сорев',duel:'Дуэль',calibration:'Калибровка',currency:'сум',steps:'ступеней',idPlaceholder:'Например: 12345678 или Player',
      invalidId:'Введите игровой ID или ник',choosePayment:'Способ оплаты',topup:'Пополнить баланс',topupAmount:'Сумма пополнения, сум',amountPlaceholder:'Например: 30000',
      invalidAmount:'Введите сумму пополнения от 1 до 100 000 000 сум',method_humo:'HUMO',method_uzcard:'UZCARD',method_terminal:'Банкомат / терминал',method_stars:'Telegram Stars',method_balance:'С баланса',
      manualHint:'Заявка администратору с расчётом суммы',starsHint:'Счёт в Telegram Stars',balanceHint:'Доступно: {amount}',notEnough:'На балансе недостаточно средств',
      admin:'Перейти к администратору',copy:'Скопировать сообщение',copied:'Сообщение скопировано',copyHint:'Выделите и скопируйте сообщение ниже',back:'К способам оплаты',close:'Закрыть',
      payment:'Оплата',total:'Итого',calculation:'Расчёт',paymentMethod:'Способ оплаты',topupRequest:'Заявка на пополнение баланса',orderRequest:'Заявка на буст Standoff 2',
      adminMissing:'Администратор пока не подключён. Сообщение с расчётом можно скопировать.',botMissing:'Бот для оплаты Stars пока не подключён.',
      starsNotConfigured:'Стоимость в Stars ещё не задана владельцем.',openBot:'Открыть счёт в боте',payStars:'Оплатить {stars} ⭐',confirming:'Проверяем подтверждение платежа…',paid:'Оплата подтверждена',
      invoiceClosed:'Оплата не завершена',pendingStatus:'Ожидает оплаты',paidStatus:'Оплачено',rejectedStatus:'Отклонено',unknownStatus:'На проверке',orderNumber:'Заказ',paymentNumber:'Платёж',
      processing:'Подождите…',submitted:'Заявка сохранена',connectionError:'Не удалось связаться с ботом. Попробуйте ещё раз.',sessionExpired:'Откройте Mini App заново через Telegram',
      profileText:'Профиль загружается из Telegram.',securityText:'Не вводите пароль от игры и SMS-коды в Mini App. Детали буста согласуйте с администратором.',
      aboutText:'Arslan Boost — повышение ранга в Standoff 2.',promoText:'Введите промокод, чтобы уточнить условия у администратора.',promoPlaceholder:'Промокод',promoAction:'Уточнить промокод',
      supportText:'Вопросы по заказу, балансу и оплате можно отправить администратору.',noAutoCredit:'Пополнение появится на балансе после подтверждения оплаты.',
      orderSent:'Оплаченный заказ передан администратору.',paymentConfirmedText:'Оплата подтверждена сервером.',selectRank:'Выберите ранг',userId:'Telegram ID',receiptText:'Хочу оформить заказ. Подскажите реквизиты и условия оплаты.',
      topupText:'Хочу пополнить баланс. Подскажите реквизиты и условия оплаты.',requestId:'Заявка',draftHint:'Текст откроется в чате администратора. Отправьте его, чтобы оформить заявку.'
    },
    uz: {
      miniApp:'mini-ilova',balance:'Balans',promo:'Promo kod',support:'Texnik yordam',chooseMode:'Rejimni tanlang',currentRank:'Hozirgi rankingiz',targetRank:'Maqsad rank',gameId:'O‘yin ID yoki nick',
      orderPrice:'Buyurtma narxi',order:'Buyurtma berish',history:'Tarix',orders:'Buyurtmalar',payments:'To‘lovlar',all:'Barchasi',completed:'To‘langan',pending:'Kutilmoqda',cancelled:'Rad etilgan',
      emptyHistory:'Hozircha operatsiyalar yo‘q',appUser:'Mini App foydalanuvchisi',balanceCaption:'BALANS',cashback:'KESHBEK',settings:'Sozlamalar',language:'TIL',settingsCaption:'SOZLAMALAR',
      profile:'Profil ma’lumotlari',profileDesc:'Profilingiz va shaxsiy ma’lumotlar',orderHistory:'Buyurtmalar tarixi',historyDesc:'Barcha buyurtmalar va ularning holati',promoCodes:'Promo kodlar',
      promoDesc:'Promo kodlar va bonuslar',supportDesc:'Buyurtma va to‘lov bo‘yicha yordam',animations:'Animatsiyalar',motionDesc:'Ilova animatsiyalarini kamaytirish',security:'Xavfsizlik',
      securityDesc:'Akkaunt parolini botga yubormang',about:'Ilova haqida',aboutDesc:'Arslan Boost · Standoff 2 rank boost',home:'Bosh sahifa',skip:'O‘tkazish',
      priceNote:'Narx tanlangan rank bosqichlari bo‘yicha hisoblanadi. To‘lov usulini buyurtma paytida tanlang — balansni oldindan to‘ldirish shart emas.',
      selectedMode:'Tanlangan rejim',wing:'Naparniklar',comp:'Raqobat',duel:'Duel',calibration:'Kalibrlash',currency:'so‘m',steps:'ta bosqich',idPlaceholder:'Masalan: 12345678 yoki Player',
      invalidId:'O‘yin ID yoki nickni kiriting',choosePayment:'To‘lov usuli',topup:'Balansni to‘ldirish',topupAmount:'To‘ldirish summasi, so‘m',amountPlaceholder:'Masalan: 30000',
      invalidAmount:'1 dan 100 000 000 so‘mgacha summa kiriting',method_humo:'HUMO',method_uzcard:'UZCARD',method_terminal:'Bankomat / terminal',method_stars:'Telegram Stars',method_balance:'Balansdan',
      manualHint:'Administratorga summa hisobi bilan murojaat',starsHint:'Telegram Stars orqali hisob',balanceHint:'Mavjud: {amount}',notEnough:'Balansda mablag‘ yetarli emas',
      admin:'Administratorga o‘tish',copy:'Xabarni nusxalash',copied:'Xabar nusxalandi',copyHint:'Quyidagi xabarni belgilang va nusxalang',back:'To‘lov usullariga',close:'Yopish',
      payment:'To‘lov',total:'Jami',calculation:'Hisob',paymentMethod:'To‘lov usuli',topupRequest:'Balansni to‘ldirish uchun ariza',orderRequest:'Standoff 2 boost buyurtmasi',
      adminMissing:'Administrator hali ulanmagan. Hisoblangan xabarni nusxalashingiz mumkin.',botMissing:'Stars uchun to‘lov boti hali ulanmagan.',starsNotConfigured:'Stars narxi hali belgilanmagan.',
      openBot:'Hisobni botda ochish',payStars:'{stars} ⭐ to‘lash',confirming:'To‘lov tasdig‘i tekshirilmoqda…',paid:'To‘lov tasdiqlandi',invoiceClosed:'To‘lov yakunlanmadi',
      pendingStatus:'To‘lov kutilmoqda',paidStatus:'To‘langan',rejectedStatus:'Rad etilgan',unknownStatus:'Tekshirilmoqda',orderNumber:'Buyurtma',paymentNumber:'To‘lov',processing:'Kuting…',submitted:'Ariza saqlandi',
      connectionError:'Botga ulanish amalga oshmadi. Qayta urinib ko‘ring.',sessionExpired:'Mini App’ni Telegram orqali qayta oching',profileText:'Profil Telegram orqali yuklanadi.',
      securityText:'O‘yin paroli va SMS-kodlarni Mini App’ga kiritmang. Boost tafsilotlarini administrator bilan kelishing.',aboutText:'Arslan Boost — Standoff 2 rank oshirish xizmati.',
      promoText:'Shartlarni administratordan bilish uchun promo kodni kiriting.',promoPlaceholder:'Promo kod',promoAction:'Promo kodni tekshirish',supportText:'Buyurtma, balans va to‘lov bo‘yicha administratorga yozing.',
      noAutoCredit:'Mablag‘ to‘lov tasdiqlanganidan keyin balansda ko‘rinadi.',orderSent:'To‘langan buyurtma administratorga yuborildi.',paymentConfirmedText:'To‘lov server orqali tasdiqlandi.',
      selectRank:'Rankni tanlang',userId:'Telegram ID',receiptText:'Buyurtma bermoqchiman. Rekvizit va to‘lov shartlarini yuboring.',topupText:'Balansni to‘ldirmoqchiman. Rekvizit va to‘lov shartlarini yuboring.',requestId:'Ariza',
      draftHint:'Xabar administrator chatida ochiladi. Arizani rasmiylashtirish uchun uni yuboring.'
    }
  };
  Object.assign(dictionaries.ru,{pay_uzcard:'✅ Оплачу на UZCARD',pay_humo:'✅ Оплачу на HUMO',pay_terminal:'✅ Оплачу через терминал',pay_stars:'✅ Оплачу в Telegram Stars',cardNumber:'Номер карты',cardHolder:'Получатель',copyCard:'Нажмите, чтобы скопировать номер'});
  Object.assign(dictionaries.uz,{pay_uzcard:'✅ UZCARD orqali to‘layman',pay_humo:'✅ HUMO orqali to‘layman',pay_terminal:'✅ Terminal orqali to‘layman',pay_stars:'✅ Telegram Stars orqali to‘layman',cardNumber:'Karta raqami',cardHolder:'Karta egasi',copyCard:'Nusxalash uchun karta raqamiga bosing'});
  const state = {lang:storage.get('ab-lang') === 'ru' ? 'ru':'uz', mode:'wing', balance:0, orders:[], payments:[], historyTab:'orders', filter:'all', sheet:null, context:null, service:false, busy:false, keys:new Map()};
  const t = (key, values={}) => Object.entries(values).reduce((s,[k,v])=>s.replaceAll('{'+k+'}',v),dictionaries[state.lang][key] ?? key);
  const money = n => new Intl.NumberFormat('ru-RU').format(n).replace(/\u00a0/g,' ');
  const sum = n => money(n)+' '+t('currency');
  const escape = text => String(text ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const rankName = index => +index === 0 ? t('calibration') : state.lang==='uz'?(['Kalibrlash','Bronza','Kumush','Oltin','Phoenix','Ranger','Champion','Master','Elite','The Legend'][+index]):ranks[+index];
  const from=$('#from-rank'), to=$('#to-rank'), gameId=$('#game-id'), orderBtn=$('#order-btn');
  ranks.forEach((r,i)=>{if(i<ranks.length-1)from.add(new Option(r,i));if(i>0)to.add(new Option(r,i));});
  from.value='0';to.value='1';
  const overlay=$('#overlay'),title=$('#sheet-title'),body=$('#sheet-body');
  let returnFocus=null,toastTimer;
  function toast(text){clearTimeout(toastTimer);$('#toast').textContent=text;$('#toast').classList.add('show');toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),3000);}
  function icon(index){const center=rankCenters[+index];return center?`<span class="rank-icon" aria-hidden="true" style="background-position:${19-center[0]*.24}px ${19-center[1]*.24}px"></span>`:'<span aria-hidden="true">♢</span>';}
  function calculation(order){const terms=prices.slice(order.fromIndex+1,order.toIndex+1);return terms.map(money).join(' + ')+' = '+sum(terms.reduce((a,b)=>a+b,0));}
  function currentOrder(){return {type:'boost_order',mode:state.mode,fromIndex:+from.value,toIndex:+to.value,gameId:gameId.value.trim(),lang:state.lang,amount:prices.slice(+from.value+1,+to.value+1).reduce((a,b)=>a+b,0)};}
  function validId(){const value=gameId.value.trim();return [...value].length>0&&[...value].length<=32&&!/[\p{C}\p{Zl}\p{Zp}<>]/u.test(value);}
  function updatePrice(){
    const a=+from.value;
    [...to.options].forEach(option=>option.disabled=+option.value<=a);
    if(+to.value<=a)to.value=String(a+1);
    const order=currentOrder();
    $('#amount').textContent=sum(order.amount);$('#formula').textContent=calculation(order);const count=order.toIndex-order.fromIndex;const ending=state.lang==='uz'?'ta bosqich':count%100>=11&&count%100<=14?'ступеней':count%10===1?'ступень':count%10>=2&&count%10<=4?'ступени':'ступеней';$('#steps').textContent=count+' '+ending;
    [from,to].forEach(select=>{select.closest('.field').querySelector('.rank-mark').innerHTML=icon(select.value);$('#'+select.id+'-trigger').textContent=rankName(select.value);[...select.options].forEach(option=>option.textContent=rankName(option.value));});
    orderBtn.disabled=!validId()||order.amount<=0;orderBtn.setAttribute('aria-disabled',String(orderBtn.disabled));
  }
  function nav(page){closeSheet();all('.page').forEach(x=>x.classList.toggle('active',x.id===page));all('.nav').forEach(x=>x.classList.toggle('active',x.dataset.page===page));window.scrollTo({top:0,behavior:document.body.classList.contains('reduce-motion')?'auto':'smooth'});if(page==='history'||page==='settings')syncState();}
  function showSheet(name,html,heading){if(!overlay.classList.contains('open'))returnFocus=document.activeElement;state.sheet=name;title.textContent=heading;body.innerHTML=html;overlay.classList.add('open');document.querySelector('.sheet').focus({preventScroll:true});}
  function closeSheet(){overlay.classList.remove('open');state.sheet=null;returnFocus?.focus?.({preventScroll:true});}
  function openRanks(which){const select=which==='from'?from:to;const choices=ranks.map((_,i)=>i).filter(i=>which==='from'?i<ranks.length-1:i>+from.value);showSheet('rank:'+which,`<div class="rank-options" role="listbox" aria-label="${escape(t('selectRank'))}">${choices.map(i=>`<button class="rank-option" role="option" aria-selected="${+select.value===i}" data-rank="${i}">${icon(i)}<span>${escape(rankName(i))}</span></button>`).join('')}</div>`,t(which==='from'?'currentRank':'targetRank'));all('[data-rank]').forEach(button=>button.onclick=()=>{select.value=button.dataset.rank;updatePrice();closeSheet();});}
  function statusName(status){return t(status==='paid'||status==='approved'?'paidStatus':status==='rejected'?'rejectedStatus':status==='pending'?'pendingStatus':'unknownStatus');}
  function renderHistory(){
    $('#filters').style.display=state.historyTab==='orders'?'flex':'none';
    const entries=(state.historyTab==='orders'?state.orders:state.payments).filter(item=>state.filter==='all'||state.historyTab!=='orders'||(state.filter==='completed'?['paid','approved'].includes(item.status):state.filter==='cancelled'?item.status==='rejected':item.status==='pending'));
    $('#history-content').innerHTML=entries.length?entries.map(item=>{const isOrder=state.historyTab==='orders';const desc=isOrder?`${rankName(item.current_rank)} → ${rankName(item.target_rank)}`:t('method_'+item.method);const date=new Date(item.created_at).toLocaleString(state.lang==='ru'?'ru-RU':'uz-UZ');return `<div class="txn"><div class="txn-icon">${isOrder?'♢':'▤'}</div><div>${escape(t(isOrder?'orderNumber':'paymentNumber'))} #${item.id}<small>${escape(desc)}</small><small>${escape(statusName(item.status))} · ${escape(date)}</small></div><strong>${escape(sum(item.amount))}</strong></div>`;}).join(''):`<div class="empty">${escape(t('emptyHistory'))}</div>`;
  }
  function applyLanguage(){
    document.documentElement.lang=state.lang;all('[data-i18n]').forEach(x=>x.textContent=t(x.dataset.i18n));all('[data-lang]').forEach(b=>b.classList.toggle('active',b.dataset.lang===state.lang));
    gameId.placeholder=t('idPlaceholder');gameId.setAttribute('aria-label',t('gameId'));$('#close-sheet').setAttribute('aria-label',t('close'));
    const banner=config.banners?.[state.lang];if(banner){try{const url=new URL(banner,document.baseURI);if(['https:','http:'].includes(url.protocol))$('.hero').style.backgroundImage=`url(${JSON.stringify(url.href)})`;}catch{}}
    all('[data-mode]').forEach(button=>button.textContent=t(button.dataset.mode));$('#mode-label').textContent=t('selectedMode')+': '+t(state.mode);
    $('#quick-balance').textContent=sum(state.balance);$('#setting-balance').textContent=sum(state.balance);updatePrice();renderHistory();
    const sheet=state.sheet;if(sheet?.startsWith('rank:'))openRanks(sheet.split(':')[1]);else if(sheet==='checkout'||sheet==='topup')renderPayments();else if(sheet==='payment')renderPayment();else if(sheet)openInfo(sheet);
  }
  const methods=['humo','uzcard','terminal','stars'];
  function orderSummary(context){if(context.kind==='topup')return `<div class="checkout-summary"><strong>${escape(t('topup'))}</strong><br>${escape(t('total'))}: <strong>${escape(sum(context.amount||0))}</strong></div>`;const order=context.order;return `<div class="checkout-summary">🎮 ${escape(t(order.mode))}<br>🏅 ${escape(rankName(order.fromIndex))} → ${escape(rankName(order.toIndex))}<br>🆔 ${escape(order.gameId)}<div class="formula">${escape(calculation(order))}</div><strong>${escape(t('total'))}: ${escape(sum(order.amount))}</strong></div>`;}
  function renderPayments(){
    const context=state.context;
    const topup=context.kind==='topup';
    const available=topup?methods:[...methods,'balance'];
    const amount=topup?context.amount:context.order.amount;
    showSheet(topup?'topup':'checkout',`${topup?`<label for="topup-amount">${escape(t('topupAmount'))}</label><input id="topup-amount" inputmode="numeric" autocomplete="off" placeholder="${escape(t('amountPlaceholder'))}" value="${escape(context.amount||'')}">`:orderSummary(context)}<div class="payment-options">${available.map(method=>`<button class="payment-method" data-payment="${method}" ${method==='balance'&&(!state.service||state.balance<amount)?'disabled':''}><span class="sicon">${method==='stars'?'★':method==='terminal'?'▤':method==='balance'?'◉':'▱'}</span><span><strong>${escape(t('method_'+method))}</strong><small>${escape(method==='balance'?t('balanceHint',{amount:sum(state.balance)}):method==='stars'?config.starsRate?`${Math.ceil((amount||0)/config.starsRate)} ⭐`:t('starsHint'):t('manualHint'))}</small></span><span class="arrow">›</span></button>`).join('')}</div><p class="notice">${escape(t(topup?'noAutoCredit':'priceNote'))}</p>`,t(topup?'topup':'choosePayment'));
    if(topup){const input=$('#topup-amount');const update=()=>{context.amount=Number(input.value.replace(/\s/g,''));all('[data-payment]').forEach(button=>button.disabled=!Number.isSafeInteger(context.amount)||context.amount<1||context.amount>100000000);};input.addEventListener('input',update);update();}
    all('[data-payment]').forEach(button=>button.onclick=()=>startPayment(button.dataset.payment));
  }
  function validTelegramUrl(value){try{const u=new URL(value);return u.protocol==='https:'&&u.hostname==='t.me'&&/^\/[A-Za-z0-9_]{3,32}\/?$/.test(u.pathname)?u:null;}catch{return null;}}
  function adminUrl(text){const url=validTelegramUrl(config.supportUrl);if(!url)return null;url.search='';if(text)url.searchParams.set('text',text);return url.href;}
  function openTelegram(url){if(!url)return;try{if(tg?.initData&&tg.openTelegramLink)tg.openTelegramLink(url);else window.location.assign(url);}catch{toast(t('connectionError'));}}
  function requestId(context,method){const fields=context.kind==='topup'?{kind:'topup',amount:context.amount,method}:{...context.order,method,lang:undefined};const key=JSON.stringify(fields);if(!state.keys.has(key))state.keys.set(key,crypto.randomUUID?.().replaceAll('-','').slice(0,12)||Math.random().toString(36).slice(2,14));return state.keys.get(key);}
  function buildMessage(context=state.context){
    const isTopup=context.kind==='topup',order=context.order;
    const uzRanks=['Kalibrlash','Bronza','Kumush','Oltin','Phoenix','Ranger','Champion','Master','Elite','The Legend'];
    const lines=[isTopup?'Assalomu alaykum! Arslan Boost balansimni to‘ldirmoqchiman.':'Assalomu alaykum! Arslan Boost orqali buyurtma bermoqchiman.'];
    if(context.serverId)lines.push((isTopup?'To‘lov':'Buyurtma')+' №'+context.serverId);
    if(!isTopup)lines.push('Rejim: '+({wing:'Напарники',comp:'Сорев',duel:'Дуэль'}[order.mode]),'O‘yin ID yoki nick: '+order.gameId,'Rank: '+uzRanks[order.fromIndex]+' → '+uzRanks[order.toIndex],'Hisob: '+prices.slice(order.fromIndex+1,order.toIndex+1).map(money).join(' + ')+' = '+money(order.amount)+' so‘m');
    lines.push('Narxi: '+money(isTopup?context.amount:order.amount)+' so‘m','To‘lov turi: #'+context.method);
    const user=tg?.initDataUnsafe?.user;if(user?.id)lines.push(t('userId')+': '+user.id);if(user?.username)lines.push('@'+user.username);
    const triggers={uzcard:'Оплачу на узкард',humo:'Оплачу на хумо',stars:'Оплачу на тг старс',terminal:'Оплачу на терминал',balance:'Оплачу с баланса'};
    lines.push('',triggers[context.method]);return lines.join('\n');
  }
  async function copyMessage(text){try{await navigator.clipboard.writeText(text);toast(t('copied'));}catch{body.querySelector('textarea')?.remove();const textarea=document.createElement('textarea');textarea.value=text;textarea.readOnly=true;body.append(textarea);textarea.focus();textarea.select();toast(t('copyHint'));}}
  function botDeepLink(){
    const bot=validTelegramUrl(config.botUrl||config.orderBotUrl);if(!bot)return null;
    const c=state.context,method={humo:'h',uzcard:'u',terminal:'t',stars:'s',balance:'b'}[c.method],lang=state.lang==='ru'?'r':'u';
    const key=requestId(c,c.method);const parts=c.kind==='topup'?['t',c.amount,method,lang,key]:['o',{wing:'w',comp:'c',duel:'d'}[c.order.mode],c.order.fromIndex,c.order.toIndex,method,lang,key,c.order.gameId];
    const payload='ab_'+btoa(String.fromCharCode(...new TextEncoder().encode(parts.join(',')))).replaceAll('+','-').replaceAll('/','_').replaceAll('=','');if(payload.length>64)return null;bot.search='';bot.searchParams.set('start',payload);return bot.href;
  }
  function renderPayment(){
    const c=state.context,stars=c.method==='stars',balance=c.method==='balance',message=buildMessage(c),admin=adminUrl(message),bot=botDeepLink();
    let notice=stars?(!config.starsRate?t('starsNotConfigured'):!state.service&&!bot?t('botMissing'):t('starsHint')):balance?t('orderSent'):admin?t('draftHint'):t('adminMissing');
    let cardHtml='';const card=config.cards?.[c.method];if(card){cardHtml=`<div class="checkout-summary"><small>${escape(t('cardNumber'))}</small><button type="button" class="card-number" id="copy-card">${escape(card)}</button>${config.cardHolder?`<div>${escape(t('cardHolder'))}: ${escape(config.cardHolder)}</div>`:''}<small>${escape(t('copyCard'))}</small></div>`;}
    const actionHtml=!balance?`<button class="${stars?'secondary':'action'}" id="admin-contact" ${admin?'':'disabled'}>${escape(t('pay_'+c.method))}</button><button class="secondary" id="copy-order">${escape(t('copy'))}</button>`:'';
    showSheet('payment',`${orderSummary(c)}${cardHtml}<p>${escape(notice)}</p>${c.confirmed?`<p>${escape(t('paymentConfirmedText'))}</p>`:''}${stars?`<button class="action" id="pay-stars" ${!c.invoiceLink&&!bot?'disabled':''}>${escape(c.invoiceLink?t('payStars',{stars:c.stars}):t('openBot'))}</button>`:''}${actionHtml}<button class="secondary" id="payment-back">${escape(t('back'))}</button>`,t('method_'+c.method));
    $('#copy-card')?.addEventListener('click',()=>copyMessage(card));
    $('#admin-contact')?.addEventListener('click',()=>openTelegram(admin));$('#copy-order')?.addEventListener('click',()=>copyMessage(message));$('#payment-back').onclick=()=>{c.invoiceLink=null;renderPayments();};
    $('#pay-stars')?.addEventListener('click',()=>{if(c.invoiceLink&&tg?.initData&&tg.openInvoice){tg.openInvoice(c.invoiceLink,status=>{if(status==='paid'){toast(t('confirming'));confirmPayment(c);}else toast(t('invoiceClosed'));});}else openTelegram(c.invoiceLink||bot);});
  }
  function apiUrl(path){return config.apiBaseUrl?config.apiBaseUrl.replace(/\/$/,'')+'/api/'+path:new URL('api/'+path,document.baseURI).href;}
  async function api(path,data){
    const response=await fetch(apiUrl(path),{method:'POST',headers:{'Content-Type':'application/json','X-Telegram-Init-Data':tg?.initData||''},body:JSON.stringify(data||{}),signal:AbortSignal.timeout(15000)});
    const result=await response.json();if(!response.ok)throw new Error(result.error||'connection_error');return result;
  }
  async function syncState(){if(!state.service||!tg?.initData)return;try{const result=await api('state');if(!gameId.value&&result.gameId){gameId.value=result.gameId;updatePrice();}state.balance=result.balance;state.orders=result.orders;state.payments=result.payments;$('#quick-balance').textContent=sum(state.balance);$('#setting-balance').textContent=sum(state.balance);renderHistory();return result;}catch{return null;}}
  async function confirmPayment(context){for(let i=0;i<5;i++){const result=await syncState();const found=(context.kind==='topup'?result?.payments:result?.orders)?.find(item=>item.id===context.serverId);if(found?.status==='paid'){context.confirmed=true;if(state.context===context&&state.sheet==='payment')renderPayment();toast(t('paid'));return;}await new Promise(resolve=>setTimeout(resolve,1000));}toast(t('confirming'));}
  function errorMessage(error){const mapping={invalid_game_id:'invalidId',insufficient_balance:'notEnough',stars_not_configured:'starsNotConfigured',unauthorized:'sessionExpired',session_expired:'sessionExpired'};return t(mapping[error.message]||'connectionError');}
  async function startPayment(method){
    if(state.busy)return;const c=state.context;if(c.kind==='topup'&&(!Number.isSafeInteger(c.amount)||c.amount<1||c.amount>100000000)){toast(t('invalidAmount'));return;}
    c.method=method;c.confirmed=false;c.invoiceLink=null;c.serverId=null;
    if(state.service&&tg?.initData){
      state.busy=true;all('[data-payment]').forEach(b=>b.disabled=true);
      try{const payload=c.kind==='topup'?{amount:c.amount}:{...c.order,lang:state.lang};const result=await api(c.kind==='topup'?'topup':'checkout',{...payload,paymentMethod:method,requestId:requestId(c,method)});c.serverId=result.id;c.invoiceLink=result.invoiceLink;c.stars=result.stars;c.confirmed=result.status==='paid';await syncState();}
      catch(error){toast(errorMessage(error));renderPayments();return;}finally{state.busy=false;}
    }else if(method==='balance'){toast(t('notEnough'));return;}
    renderPayment();
    if(method==='terminal'){const link=adminUrl(buildMessage(c));if(link)openTelegram(link);}
  }
  function openInfo(name){
    if(name==='balance'){state.context={kind:'topup',amount:null};renderPayments();return;}
    const textKey={support:'supportText',profile:'profileText',security:'securityText',about:'aboutText',promo:'promoText'}[name]||'aboutText';
    const user=tg?.initDataUnsafe?.user;
    let html=`<p>${escape(t(textKey))}</p>`;
    if(name==='profile')html+=`<div class="checkout-summary">${escape([user?.first_name,user?.last_name].filter(Boolean).join(' ')||t('appUser'))}${user?.id?'<br>ID: '+escape(user.id):''}</div>`;
    if(name==='promo')html+=`<input id="promo-input" maxlength="64" placeholder="${escape(t('promoPlaceholder'))}"><button class="action" id="promo-submit">${escape(t('promoAction'))}</button>`;
    if(name==='support'){html+=`<button class="action" id="support-contact" ${adminUrl()?'':'disabled'}>${escape(t('admin'))}</button>`;if(!adminUrl())html+=`<p class="notice">${escape(t('adminMissing'))}</p>`;}
    showSheet(name,html,t(name));
    $('#support-contact')?.addEventListener('click',()=>openTelegram(adminUrl()));$('#promo-submit')?.addEventListener('click',()=>{const code=$('#promo-input').value.trim();if(!code){$('#promo-input').focus();return;}const message=t('promo')+': '+code;const link=adminUrl(message);if(link)openTelegram(link);else toast(t('adminMissing'));});
  }
  all('.nav').forEach(button=>button.onclick=()=>nav(button.dataset.page));all('[data-nav]').forEach(button=>button.onclick=()=>nav(button.dataset.nav));all('[data-sheet]').forEach(button=>button.onclick=()=>openInfo(button.dataset.sheet));
  all('.mode').forEach(button=>button.onclick=()=>{state.mode=button.dataset.mode;all('.mode').forEach(b=>b.classList.toggle('selected',b===button));$('#mode-label').textContent=t('selectedMode')+': '+t(state.mode);});
  $('#from-rank-trigger').onclick=()=>openRanks('from');$('#to-rank-trigger').onclick=()=>openRanks('to');from.onchange=updatePrice;to.onchange=updatePrice;let profileTimer;gameId.value=storage.get('ab-game-id')||'';gameId.addEventListener('input',()=>{updatePrice();clearTimeout(profileTimer);storage.set('ab-game-id',gameId.value);if(validId()&&state.service&&tg?.initData)profileTimer=setTimeout(()=>api('profile',{gameId:gameId.value.trim(),lang:state.lang}).catch(()=>{}),500);});
  orderBtn.onclick=()=>{if(!validId()||orderBtn.disabled){gameId.focus();toast(t('invalidId'));return;}gameId.blur();state.context={kind:'order',order:currentOrder()};renderPayments();};
  $('#close-sheet').onclick=closeSheet;overlay.onclick=e=>{if(e.target===overlay)closeSheet();};document.addEventListener('keydown',event=>{if(!overlay.classList.contains('open'))return;if(event.key==='Escape')closeSheet();if(event.key==='Tab'){const focusable=[...overlay.querySelectorAll('button:not([disabled]),input,textarea,[tabindex="0"]')];const first=focusable[0],last=focusable.at(-1);if(event.shiftKey&&document.activeElement===first){last?.focus();event.preventDefault();}else if(!event.shiftKey&&document.activeElement===last){first?.focus();event.preventDefault();}}});
  all('[data-lang]').forEach(button=>button.onclick=()=>{state.lang=button.dataset.lang;storage.set('ab-lang',state.lang);applyLanguage();if(state.service&&tg?.initData)api('profile',{lang:state.lang}).catch(()=>{});});
  all('[data-history]').forEach(button=>button.onclick=()=>{state.historyTab=button.dataset.history;all('[data-history]').forEach(b=>b.classList.toggle('active',b===button));renderHistory();syncState();});
  all('#filters .chip').forEach((button,i)=>{button.onclick=()=>{state.filter=['all','completed','pending','cancelled'][i];all('#filters .chip').forEach(b=>b.classList.toggle('active',b===button));renderHistory();};});
  function setMotion(reduced){document.body.classList.toggle('reduce-motion',reduced);$('#motion-toggle').classList.toggle('on',reduced);storage.set('ab-reduced-motion',String(reduced));}
  $('#motion-row').onclick=()=>setMotion(!document.body.classList.contains('reduce-motion'));if(storage.get('ab-reduced-motion')==='true')setMotion(true);
  const user=tg?.initDataUnsafe?.user;if(user){$('#username').textContent=[user.first_name,user.last_name].filter(Boolean).join(' ')||t('appUser');$('#telegram-id').textContent=user.username?'@'+user.username:'ID: '+user.id;$('.avatar').textContent=(user.first_name||'A').slice(0,1);}
  $('.tg-icon.left').onclick=()=>{if(overlay.classList.contains('open'))closeSheet();else nav('home');};$('.tg-icon.right').onclick=()=>openInfo('about');
  window.visualViewport?.addEventListener('resize',()=>document.body.classList.toggle('keyboard-open',window.innerHeight-window.visualViewport.height>140));
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')syncState();});
  applyLanguage();
  (async()=>{try{const response=await fetch(apiUrl('config'),{signal:AbortSignal.timeout(5000)});if(!response.ok)return;const server=await response.json();if(!server.arslanBoostApi)return;for(const key of ['supportUrl','botUrl','starsRate','cards','cardHolder','banners'])if(server[key])config[key]=server[key];if(Array.isArray(server.prices)&&server.prices.length===prices.length)prices=server.prices;state.service=true;updatePrice();await syncState();}catch{}})();
  const intro=$('#intro'),video=$('#intro-video');let introTimeout;function finishIntro(){clearTimeout(introTimeout);intro.classList.remove('show');try{video.pause();video.currentTime=0;}catch{}}
  $('#skip').onclick=finishIntro;video.addEventListener('ended',finishIntro);video.addEventListener('error',finishIntro);
  if(storage.get('ab-reduced-motion')!=='true'&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){intro.classList.add('show');video.addEventListener('playing',()=>{introTimeout=setTimeout(finishIntro,3000);},{once:true});video.play().catch(finishIntro);}
})();
