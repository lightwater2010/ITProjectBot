from aiogram.types import KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup


start_kb = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="Программист", callback_data="programmer"),
    InlineKeyboardButton(text="Вакантор", callback_data="vacancer")
]])