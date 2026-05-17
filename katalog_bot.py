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

(MENU, ADMIN_MENU, NARX_KIRIT, ELON_KIRIT, MANZIL_KIRIT, TEL_KIRIT, MALUMOT_KIRIT,
 BUY_ISM, BUY_TEL, BUY_MIQDOR, BUY_MANZIL, LOK_KIRIT) = range(12)

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
        "buyurtmalar": []
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
        ["📋 Buyurtmalar", "🔙 Orqaga"]
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
    elif text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=user_keyboard())
        return MENU
    return ADMIN_MENU

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

async def elon_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    elon = update.message.text
    yuborildi = 0
    for user_id in data["foydalanuvchilar"]:
        try:
            await ctx.bot.send_message(chat_id=user_id, text=f"📢 *E'lon:*\n\n{elon}", parse_mode="Markdown")
            yuborildi += 1
        except:
            pass
    await update.message.reply_text(f"✅ E'lon {yuborildi} ta foydalanuvchiga yuborildi!", reply_markup=admin_keyboard())
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
