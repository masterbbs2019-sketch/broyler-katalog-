#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import threading
import http.server
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

TOKEN = os.environ.get("TOKEN", "8875573270:AAFGylXSdQVHSVoEXj-vCBKABYtJvXEcIZU")
ADMIN_ID = 772291674
DATA_FILE = "katalog.json"

# Elon yuborish kerak bo'lgan guruh/kanal ID'lari
# Guruh ID'sini olish uchun: @username_to_id_bot dan foydalaning
# Kanal uchun: -100 bilan boshlanadi, masalan: -1001234567890
GURUHLAR = [
    # "-1001234567890",   # 1-guruh yoki kanal ID'sini shu yerga kiriting
    # "-1009876543210",   # 2-guruh yoki kanal ID'sini shu yerga kiriting
]

(MENU, ADMIN_MENU, NARX_KIRIT, ELON_KIRIT, MANZIL_KIRIT, TEL_KIRIT, MALUMOT_KIRIT,
 BUY_ISM, BUY_TEL, BUY_MIQDOR, BUY_MANZIL, LOK_KIRIT,
 GURUH_MENU, GURUH_QOSH, GURUH_OCH) = range(15)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "narx": "Aniqlanmagan",
        "manzil": "Kiritilmagan",
        "telefon": "Kiritilmagan",
        "malumot": "Broyder jo'jalar sotiladi",
        "lokatsiya": None,
        "foydalanuvchilar": [],
        "buyurtmalar": [],
        "guruhlar": []
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def user_keyboard():
    return ReplyKeyboardMarkup([
        ["💰 Bugungi narx", "📍 Manzil"],
        ["📞 Telefon", "ℹ️ Ma'lumot"],
        ["🛒 Buyurtma berish", "📢 E'lonlar"]
    ], resize_keyboard=True)

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["💰 Narx yangilash", "📢 E'lon yuborish"],
        ["📍 Lokatsiya yuborish", "📞 Tel yangilash"],
        ["ℹ️ Ma'lumot yangilash", "👥 Foydalanuvchilar"],
        ["📋 Buyurtmalar", "👥 Guruhlar boshqaruv"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)

def guruh_keyboard():
    return ReplyKeyboardMarkup([
        ["➕ Guruh qo'shish", "📋 Guruhlar ro'yxati"],
        ["🗑 Guruh o'chirish", "🔙 Orqaga"]
    ], resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    if user_id not in data["foydalanuvchilar"]:
        data["foydalanuvchilar"].append(user_id)
        save_data(data)
    await update.message.reply_text(
        "🐣 *Broyder Jo'ja Savdosiga xush kelibsiz!*\n\nQuyidagi ma'lumotlardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=user_keyboard()
    )
    return MENU

async def menu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = load_data()

    if text == "💰 Bugungi narx":
        await update.message.reply_text(
            f"💰 *Bugungi jo'ja narxi:*\n\n🐣 {data['narx']}\n\n_Narx har kuni bozor holatiga qarab o'zgaradi_",
            parse_mode="Markdown", reply_markup=user_keyboard()
        )
    elif text == "📍 Manzil":
        await update.message.reply_text(
            f"📍 *Bizning manzil:*\n\n{data['manzil']}",
            parse_mode="Markdown", reply_markup=user_keyboard()
        )
        if data.get("lokatsiya"):
            await ctx.bot.send_location(
                chat_id=update.effective_chat.id,
                latitude=data["lokatsiya"]["lat"],
                longitude=data["lokatsiya"]["lon"]
            )
    elif text == "📞 Telefon":
        await update.message.reply_text(
            f"📞 *Bog'lanish uchun:*\n\n{data['telefon']}",
            parse_mode="Markdown", reply_markup=user_keyboard()
        )
    elif text == "ℹ️ Ma'lumot":
        await update.message.reply_text(
            f"ℹ️ *Biz haqimizda:*\n\n{data['malumot']}",
            parse_mode="Markdown", reply_markup=user_keyboard()
        )
    elif text == "📢 E'lonlar":
        await update.message.reply_text(
            "📢 E'lonlar hozircha yo'q.",
            reply_markup=user_keyboard()
        )
    elif text == "🛒 Buyurtma berish":
        await update.message.reply_text(
            "📝 Ismingizni kiriting:",
            reply_markup=back_keyboard()
        )
        return BUY_ISM
    elif text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=user_keyboard())
    return MENU

async def buy_ism(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=user_keyboard())
        return MENU
    ctx.user_data["buyurtma"] = {"ism": update.message.text}
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:", reply_markup=back_keyboard())
    return BUY_TEL

async def buy_tel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=user_keyboard())
        return MENU
    ctx.user_data["buyurtma"]["tel"] = update.message.text
    await update.message.reply_text("🐣 Nechta jo'ja kerak (dona):", reply_markup=back_keyboard())
    return BUY_MIQDOR

async def buy_miqdor(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=user_keyboard())
        return MENU
    try:
        ctx.user_data["buyurtma"]["miqdor"] = int(update.message.text)
    except:
        await update.message.reply_text("❌ Faqat son kiriting!")
        return BUY_MIQDOR
    await update.message.reply_text("📍 Manzilingizni kiriting:", reply_markup=back_keyboard())
    return BUY_MANZIL

async def buy_manzil(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=user_keyboard())
        return MENU
    b = ctx.user_data["buyurtma"]
    b["manzil"] = update.message.text
    b["user_id"] = update.effective_user.id
    data = load_data()
    data["buyurtmalar"].append(b)
    save_data(data)
    await update.message.reply_text(
        f"✅ *Buyurtmangiz qabul qilindi!*\n\n"
        f"👤 Ism: {b['ism']}\n"
        f"📞 Tel: {b['tel']}\n"
        f"🐣 Miqdor: {b['miqdor']} ta\n"
        f"📍 Manzil: {b['manzil']}\n\n"
        f"Tez orada siz bilan bog'lanamiz!",
        parse_mode="Markdown",
        reply_markup=user_keyboard()
    )
    try:
        await ctx.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🛒 *Yangi buyurtma!*\n\n"
                 f"👤 Ism: {b['ism']}\n"
                 f"📞 Tel: {b['tel']}\n"
                 f"🐣 Miqdor: {b['miqdor']} ta\n"
                 f"📍 Manzil: {b['manzil']}",
            parse_mode="Markdown"
        )
    except:
        pass
    return MENU

async def admin_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = load_data()

    if text == "💰 Narx yangilash":
        await update.message.reply_text("💰 Yangi narxni kiriting:", reply_markup=back_keyboard())
        return NARX_KIRIT
    elif text == "📢 E'lon yuborish":
        await update.message.reply_text("📢 E'lon matnini kiriting:", reply_markup=back_keyboard())
        return ELON_KIRIT
    elif text == "📍 Lokatsiya yuborish":
        await update.message.reply_text(
            "📍 Lokatsiyangizni yuboring:\n\n📎 Qo'shimcha → Lokatsiya → Ishxona joyi",
            reply_markup=back_keyboard()
        )
        return LOK_KIRIT
    elif text == "📞 Tel yangilash":
        await update.message.reply_text("📞 Yangi telefon raqamini kiriting:", reply_markup=back_keyboard())
        return TEL_KIRIT
    elif text == "ℹ️ Ma'lumot yangilash":
        await update.message.reply_text("ℹ️ Yangi ma'lumotni kiriting:", reply_markup=back_keyboard())
        return MALUMOT_KIRIT
    elif text == "👥 Foydalanuvchilar":
        count = len(data["foydalanuvchilar"])
        await update.message.reply_text(
            f"👥 Jami foydalanuvchilar: *{count} ta*",
            parse_mode="Markdown", reply_markup=admin_keyboard()
        )
    elif text == "📋 Buyurtmalar":
        buyurtmalar = data.get("buyurtmalar", [])
        if not buyurtmalar:
            await update.message.reply_text("📭 Hali buyurtma yo'q.", reply_markup=admin_keyboard())
        else:
            msg = f"📋 *Buyurtmalar ({len(buyurtmalar)} ta):*\n\n"
            for i, b in enumerate(buyurtmalar[-10:], 1):
                msg += f"{i}. *{b['ism']}* — {b['miqdor']} ta\n   📞 {b['tel']}\n   📍 {b['manzil']}\n\n"
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=admin_keyboard())
    elif text == "👥 Guruhlar boshqaruv":
        await update.message.reply_text(
            "👥 *Guruhlar boshqaruvi*\n\nE'lonlar yuboriladigan guruhlar va kanallarni boshqaring:",
            parse_mode="Markdown",
            reply_markup=guruh_keyboard()
        )
        return GURUH_MENU
    elif text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=user_keyboard())
        return MENU
    return ADMIN_MENU

# ===================== GURUH BOSHQARUVI =====================

async def guruh_menu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = load_data()
    if "guruhlar" not in data:
        data["guruhlar"] = []

    if text == "➕ Guruh qo'shish":
        await update.message.reply_text(
            "➕ *Guruh yoki kanal ID'sini kiriting:*\n\n"
            "📌 ID olish usuli:\n"
            "1️⃣ Botni guruhga qo'shing\n"
            "2️⃣ @username_to_id_bot ga guruh nomini yuboring\n"
            "3️⃣ Yoki @RawDataBot ni guruhga qo'shing\n\n"
            "Misol: `-1001234567890`",
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )
        return GURUH_QOSH
    elif text == "📋 Guruhlar ro'yxati":
        # Kodda yozilgan + bazadagi guruhlarni birlashtir
        barcha = list(set([str(g) for g in GURUHLAR] + data["guruhlar"]))
        if not barcha:
            await update.message.reply_text(
                "📭 Hali hech qanday guruh qo'shilmagan.\n\n"
                "➕ Guruh qo'shish tugmasini bosing.",
                reply_markup=guruh_keyboard()
            )
        else:
            msg = f"📋 *Guruhlar ro'yxati ({len(barcha)} ta):*\n\n"
            for i, g in enumerate(barcha, 1):
                msg += f"{i}. `{g}`\n"
            msg += "\n💡 E'lon yuborganda barchaga ketadi."
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=guruh_keyboard())
    elif text == "🗑 Guruh o'chirish":
        barcha = data["guruhlar"]
        if not barcha:
            await update.message.reply_text("📭 O'chiriladigan guruh yo'q.", reply_markup=guruh_keyboard())
        else:
            msg = "🗑 *O'chirish uchun guruh ID'sini kiriting:*\n\n"
            for i, g in enumerate(barcha, 1):
                msg += f"{i}. `{g}`\n"
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())
            return GURUH_OCH
    elif text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    return GURUH_MENU

async def guruh_qosh(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("👥 Guruhlar:", reply_markup=guruh_keyboard())
        return GURUH_MENU
    guruh_id = update.message.text.strip()
    data = load_data()
    if "guruhlar" not in data:
        data["guruhlar"] = []

    if guruh_id in data["guruhlar"] or guruh_id in [str(g) for g in GURUHLAR]:
        await update.message.reply_text("⚠️ Bu guruh allaqachon mavjud!", reply_markup=guruh_keyboard())
        return GURUH_MENU

    # Guruh mavjudligini tekshirish
    try:
        chat = await ctx.bot.get_chat(guruh_id)
        data["guruhlar"].append(guruh_id)
        save_data(data)
        await update.message.reply_text(
            f"✅ *Guruh muvaffaqiyatli qo'shildi!*\n\n"
            f"📛 Nomi: {chat.title}\n"
            f"🆔 ID: `{guruh_id}`\n\n"
            f"Endi e'lonlar bu guruhga ham yuboriladi.",
            parse_mode="Markdown",
            reply_markup=guruh_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ *Xato!* Guruh topilmadi.\n\n"
            f"Tekshiring:\n"
            f"• Bot guruhga qo'shilganmi?\n"
            f"• ID to'g'rimi? (manfiy son bo'lishi kerak)\n\n"
            f"Xato: `{str(e)[:100]}`",
            parse_mode="Markdown",
            reply_markup=guruh_keyboard()
        )
    return GURUH_MENU

async def guruh_och(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("👥 Guruhlar:", reply_markup=guruh_keyboard())
        return GURUH_MENU
    guruh_id = update.message.text.strip()
    data = load_data()
    if guruh_id in data.get("guruhlar", []):
        data["guruhlar"].remove(guruh_id)
        save_data(data)
        await update.message.reply_text(f"✅ Guruh o'chirildi: `{guruh_id}`", parse_mode="Markdown", reply_markup=guruh_keyboard())
    else:
        await update.message.reply_text("❌ Bunday guruh topilmadi.", reply_markup=guruh_keyboard())
    return GURUH_MENU

# ===================== E'LON YUBORISH =====================

async def elon_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    elon = update.message.text

    # Foydalanuvchilarga yuborish
    user_yuborildi = 0
    for user_id in data["foydalanuvchilar"]:
        try:
            await ctx.bot.send_message(chat_id=user_id, text=f"📢 *E'lon:*\n\n{elon}", parse_mode="Markdown")
            user_yuborildi += 1
        except:
            pass

    # Guruhlarga yuborish (kodda yozilgan + bazadagi)
    if "guruhlar" not in data:
        data["guruhlar"] = []
    barcha_guruhlar = list(set([str(g) for g in GURUHLAR] + data["guruhlar"]))

    guruh_yuborildi = 0
    guruh_xato = 0
    for guruh_id in barcha_guruhlar:
        try:
            await ctx.bot.send_message(chat_id=guruh_id, text=f"📢 *E'lon:*\n\n{elon}", parse_mode="Markdown")
            guruh_yuborildi += 1
        except Exception as e:
            guruh_xato += 1

    xabar = (
        f"✅ *E'lon muvaffaqiyatli yuborildi!*\n\n"
        f"👥 Foydalanuvchilar: *{user_yuborildi} ta*\n"
        f"👥 Guruhlar: *{guruh_yuborildi} ta*"
    )
    if guruh_xato > 0:
        xabar += f"\n⚠️ Yuborilmadi (xato): *{guruh_xato} ta guruh*"

    await update.message.reply_text(xabar, parse_mode="Markdown", reply_markup=admin_keyboard())
    return ADMIN_MENU

# ===================== QOLGAN HANDLERLAR =====================

async def lok_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    if update.message.location:
        data = load_data()
        data["lokatsiya"] = {
            "lat": update.message.location.latitude,
            "lon": update.message.location.longitude
        }
        save_data(data)
        await update.message.reply_text(
            "✅ Lokatsiya saqlandi!\n\nEndi manzil matnini kiriting:\nMasalan: Samarqand, Mirankul qishlog'i",
            reply_markup=back_keyboard()
        )
        return MANZIL_KIRIT
    await update.message.reply_text("❌ Iltimos lokatsiya yuboring!")
    return LOK_KIRIT

async def manzil_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    data["manzil"] = update.message.text
    save_data(data)
    await update.message.reply_text(
        f"✅ Manzil yangilandi: *{data['manzil']}*",
        parse_mode="Markdown",
        reply_markup=admin_keyboard()
    )
    return ADMIN_MENU

async def narx_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    data["narx"] = update.message.text
    save_data(data)
    await update.message.reply_text(f"✅ Narx yangilandi: *{data['narx']}*", parse_mode="Markdown", reply_markup=admin_keyboard())
    return ADMIN_MENU

async def tel_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    data["telefon"] = update.message.text
    save_data(data)
    await update.message.reply_text("✅ Telefon yangilandi!", reply_markup=admin_keyboard())
    return ADMIN_MENU

async def malumot_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    data["malumot"] = update.message.text
    save_data(data)
    await update.message.reply_text("✅ Ma'lumot yangilandi!", reply_markup=admin_keyboard())
    return ADMIN_MENU

async def admin_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("👑 *Admin paneliga xush kelibsiz!*", parse_mode="Markdown", reply_markup=admin_keyboard())
        return ADMIN_MENU
    return MENU

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("admin", admin_command)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
            ADMIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler)],
            NARX_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, narx_kirit)],
            ELON_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, elon_kirit)],
            MANZIL_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, manzil_kirit)],
            TEL_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, tel_kirit)],
            MALUMOT_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, malumot_kirit)],
            BUY_ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_ism)],
            BUY_TEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_tel)],
            BUY_MIQDOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_miqdor)],
            BUY_MANZIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_manzil)],
            LOK_KIRIT: [MessageHandler(filters.ALL, lok_kirit)],
            GURUH_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, guruh_menu_handler)],
            GURUH_QOSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, guruh_qosh)],
            GURUH_OCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, guruh_och)],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("admin", admin_command)],
    )
    app.add_handler(conv)
    print("Katalog bot ishga tushdi!")
    def run_server():
        server = http.server.HTTPServer(('0.0.0.0', 10000), http.server.BaseHTTPRequestHandler)
        server.serve_forever()
    threading.Thread(target=run_server, daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
    
