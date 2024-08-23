from aiogram.types import (KeyboardButton, InlineKeyboardButton,
                           ReplyKeyboardMarkup, InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from orm import get_all_user_projects_names


start_kb = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="Программист", callback_data="programmer"),
    InlineKeyboardButton(text="Вакантор", callback_data="vacancer")
]])

kb_programmier = [
        [InlineKeyboardButton(text="Создать портфолио", callback_data="create_portfolio"),InlineKeyboardButton(text="Назад",callback_data="back")]]
kb_programmer2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Смотреть свое портфолио", callback_data="view_portfolio"), InlineKeyboardButton(text="Смотреть проекты",callback_data="watch_projects")],
    [InlineKeyboardButton(text="Назад",callback_data="back"),InlineKeyboardButton(text='избранные проекты', callback_data='favourite_projects')]
])

keyboard_program = InlineKeyboardMarkup(inline_keyboard=kb_programmier)

keyboard_vacan = [[InlineKeyboardButton(text='Создать проект',callback_data="create_project"), InlineKeyboardButton(text='Список ваших проектов',callback_data="list_projects")],
                  [InlineKeyboardButton(text='Назад',callback_data="back"), InlineKeyboardButton(text='Поиск программистов', callback_data='search_programmers')],
                   [InlineKeyboardButton(text='Избранные программисты', callback_data='favourite_programmiest')]]

kb_vacancer = InlineKeyboardMarkup(inline_keyboard=keyboard_vacan)

kb_edit_info = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Оставить предыдущее значение")]
])

kb_edit_portfolio= InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text='Назад', callback_data='back_to_programmier') ,
                   InlineKeyboardButton(text='Изменить', callback_data='edit_portfolio')]])

kb_edit_project = InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text="Изменить", callback_data="edit_project"), InlineKeyboardButton(text="Удалить", callback_data="delete_project")]])

async def create_list_project_kb(tg_id):
    project_list_builder = ReplyKeyboardBuilder()
    projects_name = await get_all_user_projects_names(tg_id)
    for project_name in projects_name:
        project_button = KeyboardButton(text=project_name)
        project_list_builder.add(project_button)
    project_list_builder.add(KeyboardButton(text="Назад"))
    return project_list_builder.adjust(2).as_markup()

kb_next_programmier = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text="Далее", callback_data="next_programmier"),InlineKeyboardButton(text="Добавить программиста в проект", callback_data="add_programmier_to_project"),
                                                             InlineKeyboardButton(text="Назад в меню", callback_data="back_to_vacanсer")]])

kb_next = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text="Далее", callback_data="next_project"),InlineKeyboardButton(text="Добавить в избранные", callback_data="add_project_to_favourites")],
                                                  [InlineKeyboardButton(text='Назад в меню',callback_data='back_to_programmier')]])