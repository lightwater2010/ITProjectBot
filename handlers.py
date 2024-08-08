from aiogram.filters import CommandStart
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from keyboards import start_kb

router = Router()

@router.message(CommandStart())
async def start_command(message:Message):
    await message.answer(text="Привет,друг! Этот бот поможет тебе найти интересный IT проект, который тебе по душе или ты можешь найти себе для проекта единомышленников. Решать тебе!\n\n<b>Программист - может искать проект в котором хочет учавствовать</b>\n\n<b>Вакантор - может искать людей для создания своего проекта</b>", reply_markup=start_kb, parse_mode="HTML")