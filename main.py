import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

TOKEN = "8930395659:AAFhq__aGB77ewN_op0gAbTv9ERAa1uCUtw"
ADMIN_ID = 1216412017
KARTA_RAQAM = "5614 6819 0849 5173"
STADION_NOMI = "21 Arena"
TELEFON = "+998 90 000 04 21"
NARXLAR = {"kunduz": 100_000, "kechqurun": 150_000}
BOSHLANISH = 9
TUGASH = 26

SANA, VAQT, DAVOMIYLIK, ISM, TELEFON_RAQAM, TOLLOV, CHEK = range(7)
bronlar = {}
logging.basicConfig(level=logging.INFO)

def narx_hisob(soat, davomiylik):
    jami = 0
    for i in range(davomiylik):
        h = (soat + i) % 24
        jami += NARXLAR["kunduz"] if 9 <= h < 17 else NARXLAR["kechqurun"]
    return jami

def band_soatlar(sana):
    band = []
    for bron in bronlar.get(sana, []):
        for i in range(bron[1]):
            band.append(bron[0] + i)
    return band

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Bron qilish", callback_data="bron")],
        [InlineKeyboardButton("💰 Narxlar", callback_data="narxlar")],
        [InlineKeyboardButton("📋 Mening bronlarim", callback_data="mening_bronlarim")],
        [InlineKeyboardButton("📞 Aloqa", callback_data="aloqa")],
    ])

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Barcha bronlar", callback_data="admin_bronlar")],
        [InlineKeyboardButton("📅 Bugungi jadval", callback_data="admin_bugun")],
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stat")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    if user.id == ADMIN_ID:
        await update.message.reply_text(
            f"👋 Xush kelibsiz, Admin!\n🏟 *{STADION_NOMI}* boshqaruv paneli",
            parse_mode="Markdown", reply_markup=admin_menu())
    else:
        await update.message.reply_text(
            f"⚽ *{STADION_NOMI}* ga xush kelibsiz!\n\n🕐 Ish vaqti: 09:00 – 02:00\n📍 Tuman markazi",
            parse_mode="Markdown", reply_markup=main_menu())

async def bosh_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    user = query.from_user
    if user.id == ADMIN_ID:
        await query.edit_message_text(f"👋 Admin paneli — *{STADION_NOMI}*",
            parse_mode="Markdown", reply_markup=admin_menu())
    else:
        await query.edit_message_text(f"⚽ *{STADION_NOMI}*\n\nQuyidagilardan birini tanlang:",
            parse_mode="Markdown", reply_markup=main_menu())
    return ConversationHandler.END

async def narxlar_korsatish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"💰 *{STADION_NOMI} — Narxlar*\n\n"
        f"🌤 Kunduz (09:00–17:00): *{NARXLAR['kunduz']:,} so'm/soat*\n"
        f"🌙 Kechqurun (17:00–02:00): *{NARXLAR['kechqurun']:,} so'm/soat*\n\n"
        f"📌 Minimal bron: 1 soat\n💳 Avans: 50%\n📞 {TELEFON}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📅 Bron qilish", callback_data="bron"),
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")
        ]]))

async def aloqa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        f"📞 *Aloqa*\n\n📱 {TELEFON}\n🏟 {STADION_NOMI}\n🕐 09:00 – 02:00",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")]]))

async def mening_bronlarim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    topildi = [(s, b[0], b[1], b[4]) for s, sb in bronlar.items() for b in sb if b[2] == user_id]
    if not topildi:
        text = "📋 Sizda hech qanday bron yo'q."
    else:
        text = "📋 *Sizning bronlaringiz:*\n\n"
        for sana, soat, davom, tollov in topildi:
            emoji = "💳" if tollov == "avans" else "🤝"
            text += f"📅 {sana} | 🕐 {soat%24:02d}:00–{(soat+davom)%24:02d}:00 {emoji}\n"
    await query.edit_message_text(text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📅 Yangi bron", callback_data="bron"),
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")
        ]]))

async def bron_boshlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    bugun = datetime.now().date()
    keyboard = []
    row = []
    for i in range(7):
        sana = bugun + timedelta(days=i)
        nomi = "Bugun" if i == 0 else ("Ertaga" if i == 1 else sana.strftime("%d-%b"))
        row.append(InlineKeyboardButton(nomi, callback_data=f"sana_{sana.strftime('%Y-%m-%d')}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("❌ Bekor", callback_data="bosh")])
    await query.edit_message_text("📅 *Qaysi kunga bron qilmoqchisiz?*",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return SANA

async def sana_tanlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sana_str = query.data.replace("sana_", "")
    context.user_data["sana"] = sana_str
    band = band_soatlar(sana_str)
    keyboard = []
    row = []
    for soat in range(BOSHLANISH, TUGASH):
        soat_nomi = f"{soat%24:02d}:00"
        btn = InlineKeyboardButton(
            f"🔴 {soat_nomi}" if soat in band else f"✅ {soat_nomi}",
            callback_data="band" if soat in band else f"soat_{soat}")
        row.append(btn)
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="bron"),
                     InlineKeyboardButton("❌ Bekor", callback_data="bosh")])
    await query.edit_message_text(
        f"🕐 *{sana_str} — soat tanlang:*\n\n✅ Bo'sh  |  🔴 Band",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return VAQT

async def vaqt_tanlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "band":
        await query.answer("Bu soat band! Boshqa soat tanlang.", show_alert=True)
        return VAQT
    await query.answer()
    soat = int(query.data.replace("soat_", ""))
    context.user_data["soat"] = soat
    sana_str = context.user_data["sana"]
    band = band_soatlar(sana_str)
    keyboard = []
    row = []
    for i in range(1, 5):
        if soat + i > TUGASH or any((soat + j) in band for j in range(i)):
            break
        narx = narx_hisob(soat, i)
        row.append(InlineKeyboardButton(f"{i} soat — {narx:,}", callback_data=f"davom_{i}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data=f"sana_{sana_str}"),
                     InlineKeyboardButton("❌ Bekor", callback_data="bosh")])
    await query.edit_message_text(
        f"⏱ *Necha soat o'ynaysiz?*\n\nBoshlanish: {soat%24:02d}:00",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return DAVOMIYLIK

async def davomiylik_tanlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    davom = int(query.data.replace("davom_", ""))
    context.user_data["davomiylik"] = davom
    soat = context.user_data["soat"]
    sana = context.user_data["sana"]
    narx = narx_hisob(soat, davom)
    avans = narx // 2
    context.user_data["narx"] = narx
    context.user_data["avans"] = avans
    await query.edit_message_text(
        f"👤 *Ismingizni kiriting:*\n\n(Masalan: Jasur Toshmatov)",
        parse_mode="Markdown")
    return ISM

async def ism_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mijoz_ism"] = update.message.text
    await update.message.reply_text(
        f"📱 *Telefon raqamingizni kiriting:*\n\n(Masalan: +998901234567)",
        parse_mode="Markdown")
    return TELEFON_RAQAM

async def telefon_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mijoz_telefon"] = update.message.text
    soat = context.user_data["soat"]
    sana = context.user_data["sana"]
    davom = context.user_data["davomiylik"]
    narx = context.user_data["narx"]
    avans = context.user_data["avans"]
    await update.message.reply_text(
        f"📋 *Bron ma'lumotlari:*\n\n"
        f"👤 Ism: {context.user_data['mijoz_ism']}\n"
        f"📱 Telefon: {context.user_data['mijoz_telefon']}\n"
        f"📅 Sana: {sana}\n"
        f"🕐 Soat: {soat%24:02d}:00 – {(soat+davom)%24:02d}:00\n"
        f"⏱ Davomiylik: {davom} soat\n"
        f"💰 Jami: *{narx:,} so'm*\n"
        f"💳 Avans (50%): *{avans:,} so'm*\n\nTo'lov turini tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Avans to'lash (50%)", callback_data="tollov_avans")],
            [InlineKeyboardButton("🤝 To'lovsiz bron", callback_data="tollov_yoq")],
            [InlineKeyboardButton("❌ Bekor", callback_data="bosh")]
        ]))
    return TOLLOV

async def tollov_tanlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "tollov_avans":
        avans = context.user_data["avans"]
        context.user_data["tollov"] = "avans"
        await query.edit_message_text(
            f"💳 *To'lov ma'lumotlari:*\n\n"
            f"💰 Miqdor: *{avans:,} so'm*\n"
            f"💳 Karta: `{KARTA_RAQAM}`\n\n"
            f"To'lovni amalga oshirib, chek rasmini yuboring yoki tugmani bosing.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ To'lovni amalga oshirdim", callback_data="chek_yuborish")],
                [InlineKeyboardButton("❌ Bekor", callback_data="bosh")]
            ]))
        return CHEK
    else:
        context.user_data["tollov"] = "yoq"
        return await bron_yakunlash(update, context)

async def chek_rasm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["chek_file_id"] = update.message.photo[-1].file_id
    await _saqlash(message=update.message, user=update.effective_user, context=context)
    return ConversationHandler.END

async def bron_yakunlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await _saqlash(query=query, user=query.from_user, context=context)
    return ConversationHandler.END

async def _saqlash(context, user, query=None, message=None):
    d = context.user_data
    sana, soat, davom = d["sana"], d["soat"], d["davomiylik"]
    narx, avans, tollov = d["narx"], d["avans"], d.get("tollov", "yoq")
    bron_id = f"{sana}_{soat}_{user.id}"
    if sana not in bronlar:
        bronlar[sana] = []
    bronlar[sana].append((soat, davom, user.id, user.full_name, tollov, bron_id))
    tollov_text = f"💳 Avans: {avans:,} so'm" if tollov == "avans" else "🤝 To'lovsiz (joyda to'lanadi)"
    text = (
        f"✅ *Bron tasdiqlandi!*\n\n"
        f"📅 {sana}\n🕐 {soat%24:02d}:00 – {(soat+davom)%24:02d}:00\n"
        f"💰 {narx:,} so'm\n{tollov_text}\n\n📞 {TELEFON}\n⚽ O'yningiz xayrli bo'lsin!"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Bosh menyu", callback_data="bosh")]])
    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    admin_text = (
        f"🔔 *Yangi bron!*\n\n👤 {d.get('mijoz_ism', user.full_name)}\n"
        f"📱 {d.get('mijoz_telefon', 'Noma\'lum')}\n"
        f"🆔 Telegram: {user.id}\n"
        f"📅 {sana}\n🕐 {soat%24:02d}:00–{(soat+davom)%24:02d}:00\n"
        f"💰 {narx:,} so'm\n💳 {'Avans: '+str(avans)+' so\'m' if tollov=='avans' else 'To\'lovsiz'}"
    )
    admin_kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{bron_id}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"rad_{bron_id}")
    ]])
    try:
        if d.get("chek_file_id"):
            await context.bot.send_photo(ADMIN_ID, d["chek_file_id"],
                caption=admin_text, parse_mode="Markdown", reply_markup=admin_kb)
        else:
            await context.bot.send_message(ADMIN_ID, admin_text,
                parse_mode="Markdown", reply_markup=admin_kb)
    except Exception as e:
        print(f"Admin xabar xatosi: {e}")
    context.user_data.clear()

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ Ruxsat yo'q!", show_alert=True)
        return
    data = query.data
    back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_menu")]])
    if data == "admin_bronlar":
        if not bronlar:
            text = "📋 Hozircha bron yo'q."
        else:
            text = "📋 *Barcha bronlar:*\n\n"
            for sana, sb in sorted(bronlar.items()):
                text += f"📅 *{sana}:*\n"
                for b in sb:
                    t = "💳" if b[4] == "avans" else "🤝"
                    text += f"  {b[0]%24:02d}:00–{(b[0]+b[1])%24:02d}:00 | {b[3]} {t}\n"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb)
    elif data == "admin_bugun":
        bugun = datetime.now().date().strftime("%Y-%m-%d")
        text = f"📅 *Bugun ({bugun}):*\n\n"
        band = bronlar.get(bugun, [])
        text += "\n".join(
            f"🕐 {b[0]%24:02d}:00–{(b[0]+b[1])%24:02d}:00 | {b[3]} {'💳' if b[4]=='avans' else '🤝'}"
            for b in sorted(band, key=lambda x: x[0])
        ) if band else "Bugun bron yo'q."
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_kb)
    elif data == "admin_stat":
        jami = sum(len(v) for v in bronlar.values())
        daromad = sum(narx_hisob(b[0], b[1]) for sb in bronlar.values() for b in sb)
        await query.edit_message_text(
            f"📊 *Statistika:*\n\n📋 Jami: {jami} ta bron\n💰 Daromad: {daromad:,} so'm",
            parse_mode="Markdown", reply_markup=back_kb)
    elif data == "admin_menu":
        await query.edit_message_text(f"👋 Admin paneli — *{STADION_NOMI}*",
            parse_mode="Markdown", reply_markup=admin_menu())
    elif data.startswith("ok_"):
        await query.edit_message_reply_markup(None)
        await query.message.reply_text("✅ Bron tasdiqlandi!")
    elif data.startswith("rad_"):
        bron_id = data.replace("rad_", "")
        sana = "_".join(bron_id.split("_")[:3])
        if sana in bronlar:
            bronlar[sana] = [b for b in bronlar[sana] if b[5] != bron_id]
        await query.edit_message_reply_markup(None)
        await query.message.reply_text("❌ Bron rad etildi!")

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(bron_boshlash, pattern="^bron$")],
        states={
            SANA: [CallbackQueryHandler(sana_tanlash, pattern="^sana_")],
            VAQT: [
                CallbackQueryHandler(vaqt_tanlash, pattern="^(soat_|band)"),
                CallbackQueryHandler(bron_boshlash, pattern="^bron$")
            ],
            DAVOMIYLIK: [CallbackQueryHandler(davomiylik_tanlash, pattern="^davom_")],
            ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ism_qabul)],
            TELEFON_RAQAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, telefon_qabul)],
            TOLLOV: [CallbackQueryHandler(tollov_tanlash, pattern="^tollov_")],
            CHEK: [
                CallbackQueryHandler(bron_yakunlash, pattern="^chek_yuborish$"),
                MessageHandler(filters.PHOTO, chek_rasm)
            ],
        },
        fallbacks=[CallbackQueryHandler(bosh_menu, pattern="^bosh$")],
        per_user=True,
        allow_reentry=True
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(narxlar_korsatish, pattern="^narxlar$"))
    app.add_handler(CallbackQueryHandler(aloqa, pattern="^aloqa$"))
    app.add_handler(CallbackQueryHandler(mening_bronlarim, pattern="^mening_bronlarim$"))
    app.add_handler(CallbackQueryHandler(bosh_menu, pattern="^bosh$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(admin_|ok_|rad_)"))
    print("✅ Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
