#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

TOKEN = os.environ.get("TOKEN", "8875573270:AAFGylXSdQVHSVoEXj-vCBKABYtJvXEcIZU")
ADMIN_ID = 772291674
DATA_FILE = "katalog.json"

(MENU, ADMIN_MENU, NARX_KIRIT, ELON_KIRIT, MANZIL_KIRIT, TEL_KIRIT, MALUMOT_KIRIT) = range(7)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "narx": "Aniqlanmagan",
        "manzil": "Kiritilmagan",
        "telefon": "Kiritilmagan",
        "malumot": "Broyder jo'jalar sotiladi",
        "foydalanuvchilar": []
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def user_keyboard():
    return ReplyKeyboardMarkup([
        ["💰 Bugungi narx", "📍 Manzil"],
        ["📞 Telefon", "ℹ️ Ma'lumot"],
        ["📢 E'lonlar"]
    ], resize_keyboard=True)

def admin_keyboard():
    return ReplyKeyboardMarkup([
        ["💰 Narx yangilash", "📢 E'lon yuborish"],
        ["📍 Manzil yangilash", "📞 Tel yangilash"],
        ["ℹ️ Ma'lumot yangilash", "👥 Foydalanuvchilar"],
        ["🔙 Orqaga"]
    ], resize_keyboard=True)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    
    # Foydalanuvchini saqlash
    if user_id not in data["foydalanuvchilar"]:
        data["foydalanuvchilar"].append(user_id)
        save_data(data)
    
    await update.message.reply_text(
        "🐣 *Broyder Jo'ja Savdosiga xush kelibsiz!*\n\n"
        "Quyidagi ma'lumotlardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=user_keyboard()
    )
    return MENU

async def menu_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    data = load_data()

    if text == "💰 Bugungi narx":
        await update.message.reply_text(
            f"💰 *Bugungi jo'ja narxi:*\n\n"
            f"🐣 {data['narx']}\n\n"
            f"_Narx har kuni bozor holatiga qarab o'zgaradi_",
            parse_mode="Markdown",
            reply_markup=user_keyboard()
        )

    elif text == "📍 Manzil":
        await update.message.reply_text(
            f"📍 *Bizning manzil:*\n\n{data['manzil']}",
            parse_mode="Markdown",
            reply_markup=user_keyboard()
        )

    elif text == "📞 Telefon":
        await update.message.reply_text(
            f"📞 *Bog'lanish uchun:*\n\n{data['telefon']}",
            parse_mode="Markdown",
            reply_markup=user_keyboard()
        )

    elif text == "ℹ️ Ma'lumot":
        await update.message.reply_text(
            f"ℹ️ *Biz haqimizda:*\n\n{data['malumot']}",
            parse_mode="Markdown",
            reply_markup=user_keyboard()
        )

    elif text == "📢 E'lonlar":
        await update.message.reply_text(
            "📢 E'lonlar hozircha yo'q.",
            reply_markup=user_keyboard()
        )

    elif text == "🔑 Admin" and user_id == ADMIN_ID:
        await update.message.reply_text(
            "👑 *Admin paneliga xush kelibsiz!*",
            parse_mode="Markdown",
            reply_markup=admin_keyboard()
        )
        return ADMIN_MENU

    return MENU

async def admin_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = load_data()

    if text == "💰 Narx yangilash":
        await update.message.reply_text(
            "💰 Yangi narxni kiriting:\nMasalan: 1 dona = 15,000 so'm",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return NARX_KIRIT

    elif text == "📢 E'lon yuborish":
        await update.message.reply_text(
            "📢 E'lon matnini kiriting:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return ELON_KIRIT

    elif text == "📍 Manzil yangilash":
        await update.message.reply_text(
            "📍 Yangi manzilni kiriting:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return MANZIL_KIRIT

    elif text == "📞 Tel yangilash":
        await update.message.reply_text(
            "📞 Yangi telefon raqamini kiriting:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return TEL_KIRIT

    elif text == "ℹ️ Ma'lumot yangilash":
        await update.message.reply_text(
            "ℹ️ Yangi ma'lumotni kiriting:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
        )
        return MALUMOT_KIRIT

    elif text == "👥 Foydalanuvchilar":
        count = len(data["foydalanuvchilar"])
        await update.message.reply_text(
            f"👥 Jami foydalanuvchilar: *{count} ta*",
            parse_mode="Markdown",
            reply_markup=admin_keyboard()
        )

    elif text == "🔙 Orqaga":
        await update.message.reply_text(
            "🏠 Asosiy menyu:",
            reply_markup=user_keyboard()
        )
        return MENU

    return ADMIN_MENU

async def narx_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    data["narx"] = update.message.text
    save_data(data)
    await update.message.reply_text(
        f"✅ Narx yangilandi: *{data['narx']}*",
        parse_mode="Markdown",
        reply_markup=admin_keyboard()
    )
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
            await ctx.bot.send_message(
                chat_id=user_id,
                text=f"📢 *E'lon:*\n\n{elon}",
                parse_mode="Markdown"
            )
            yuborildi += 1
        except:
            pass
    await update.message.reply_text(
        f"✅ E'lon {yuborildi} ta foydalanuvchiga yuborildi!",
        reply_markup=admin_keyboard()
    )
    return ADMIN_MENU

async def manzil_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    data["manzil"] = update.message.text
    save_data(data)
    await update.message.reply_text(
        f"✅ Manzil yangilandi!",
        reply_markup=admin_keyboard()
    )
    return ADMIN_MENU

async def tel_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    data["telefon"] = update.message.text
    save_data(data)
    await update.message.reply_text(
        f"✅ Telefon yangilandi!",
        reply_markup=admin_keyboard()
    )
    return ADMIN_MENU

async def malumot_kirit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("Admin menyu:", reply_markup=admin_keyboard())
        return ADMIN_MENU
    data = load_data()
    data["malumot"] = update.message.text
    save_data(data)
    await update.message.reply_text(
        f"✅ Ma'lumot yangilandi!",
        reply_markup=admin_keyboard()
    )
    return ADMIN_MENU

async def admin_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(
            "👑 *Admin paneliga xush kelibsiz!*",
            parse_mode="Markdown",
            reply_markup=admin_keyboard()
        )
        return ADMIN_MENU
    return MENU

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("admin", admin_command)
        ],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
            ADMIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_handler)],
            NARX_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, narx_kirit)],
            ELON_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, elon_kirit)],
            MANZIL_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, manzil_kirit)],
            TEL_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, tel_kirit)],
            MALUMOT_KIRIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, malumot_kirit)],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("admin", admin_command)
        ],
    )
    app.add_handler(conv)
    print("Katalog bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
