import asyncio
from aiogram.filters import CommandStart, Command
from aiogram import F, Router, types, Bot
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, BotCommand, BotCommandScopeDefault, message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Text
from itertools import cycle
import re

from sqlalchemy.util import await_only

from config import token
from keyboards import (start_kb, keyboard_program, kb_vacancer, kb_programmer2, kb_edit_portfolio,
                       create_list_project_kb, kb_edit_info, kb_edit_project,kb_next, kb_next_programmier)
from orm import set_programmer, set_project, check_programmer_in_db, get_programmer, get_user_project, edit_programmer, \
    edit_project, get_all_user_projects_names, delete_project, get_all_projects_in_db, get_all_programmers, \
    add_project_to_favourites

bot = Bot(token)
router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(text="Привет,друг!"
                              " Этот бот поможет тебе найти интересный IT проект,"
                              " который тебе по душе или ты можешь найти себе для проекта единомышленников. Решать тебе!"
                              "\n\n<b>Программист - может искать проект в котором хочет учавствовать</b>\n\n<b>"
                              "Вакантор - может искать людей для создания своего проекта</b>",
                         reply_markup=start_kb, parse_mode="HTML")

@router.callback_query(F.data == 'programmer')
async def kb_for_programmer(callback: CallbackQuery):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer("")
    programmer_check = await check_programmer_in_db(callback.from_user.id)
    if programmer_check == "this programmer in db":
        await callback.bot.send_message(callback.from_user.id,"Вы выбрали программиста! Выберите следующие действия:",
                                        reply_markup=kb_programmer2)
    else:
        await callback.bot.send_message(callback.from_user.id, "Вы выбрали программиста! Выберите следующие действия:",
                                        reply_markup=keyboard_program)

@router.callback_query(F.data == "back")
async def back_to_start(callback: CallbackQuery):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer("")
    await bot.send_message(callback.from_user.id, "Вы возвращены на начальное меню. Выберите кем хотите быть:", reply_markup=start_kb)

@router.callback_query(F.data == "back_to_vacanсer")
async def back_to_vacantor_menu(callback:CallbackQuery):
    await callback.answer("")
    await bot.send_message(callback.from_user.id, "Вы возвращены на меню вакантора. Выберите следущие действия:", reply_markup=kb_vacancer)

@router.message(F.text == 'Назад')
async def reply_message(message:Message):
    await bot.send_message(message.from_user.id,"...", reply_markup=types.ReplyKeyboardRemove())
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await bot.send_message(message.from_user.id, "Вы возвращены на меню вакантора. Выберите следущие действия:",
                           reply_markup = kb_vacancer)


@router.callback_query(F.data == "back_to_programmier")
async def bac_to_start(callback: CallbackQuery):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer("")
    await bot.send_message(callback.from_user.id, "Вы были возвращены на меню программиста. Выберите действие ниже:",
                           reply_markup=kb_programmer2)

@router.callback_query(F.data == 'vacancer')
async def kb_for_vacancer(callback: CallbackQuery):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer("")
    await callback.bot.send_message(callback.from_user.id,
                                    "Вы выбрали Вакантора! Выберите следующие действия:",
                                    reply_markup=kb_vacancer)



@router.message(Command("developers_info"))
async def cmd_info(message: Message):
    await bot.send_message(message.from_user.id, "Над созданием проекта работали(Github разработчиков)\n"
                                                 "<i>lightwater2010 и Dangersnegggg</i>.", parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await bot.send_message(message.from_user.id, "Команды:\n/start - начать\n"
                                                 "/developers_info - информация о разработчиках"
                                                 "\n/help - помощь")


@router.message(Command("info"))
async def cmd_info(message: Message):
    await bot.send_message(message.from_user.id, "Проект создан для не коммерческий организаций!")


async def setup_bot_commands():
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Получить помощь"),
        BotCommand(command="/info", description="Информация о проекте"),
        BotCommand(command="/developers_info", description="Информация о разработчиках"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


class ProgrammerForm(StatesGroup):
    name = State()
    description = State()
    expectations = State()
    user_name = State()


class ProjectForm(StatesGroup):
    project_name = State()
    description = State()
    places = State()
    occupied_places = State()
    required_skills = State()
    user_name = State()


@router.callback_query(F.data == 'create_portfolio')
async def programmer_form_fsm(callback: CallbackQuery, state: FSMContext):
    await callback.bot.send_message(callback.from_user.id, "Введите ваше имя:")
    await state.set_state(ProgrammerForm.name)

edit_portfolio = False

@router.callback_query(F.data == "edit_portfolio")
async def edit_programmer_fsm(callback: CallbackQuery, state: FSMContext):
    global edit_portfolio
    await callback.bot.send_message(callback.from_user.id, "Введите ваше новое имя:", reply_markup=kb_edit_info)
    edit_portfolio = True
    await state.set_state(ProgrammerForm.name)


@router.callback_query(F.data == "view_portfolio")
async def portfolio_form(callback:CallbackQuery):
    tg_id = callback.from_user.id
    portfolio_info = await get_programmer(tg_id)
    name_programmier = portfolio_info[0]
    description_programmier = portfolio_info[1]
    expectations_programmier = portfolio_info[2]
    user_name_programmier = portfolio_info[3]
    await bot.send_message(callback.from_user.id, f"Ваше имя: {name_programmier}\n"
                                                    f"Информация о вас: {description_programmier}\n"
                                                    f"Ваше ожидания от проекта: {expectations_programmier}\n"
                                                    f"Ваше имя пользователя: {user_name_programmier}\n"
                                                    ,reply_markup=kb_edit_portfolio)



@router.message(ProgrammerForm.name)
async def process_name(message: types.Message, state: FSMContext):
    if message.text == "Оставить предыдущее значение":
        programmer_name = await get_programmer(message.from_user.id)
        programmer_name_result = programmer_name[0]
        await state.update_data(name=programmer_name_result)
        await state.set_state(ProgrammerForm.description)
        await bot.send_message(message.from_user.id, "Введите новую информацию про себя (навыки и знания):")
    else:
        await state.update_data(name=message.text)
        #await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await state.set_state(ProgrammerForm.description)
        await bot.send_message(message.from_user.id, "Введите информацию про себя (навыки и знания):")


@router.message(ProgrammerForm.description)
async def process_description(message: types.Message, state: FSMContext):
    if message.text == "Оставить предыдущее значение":
        programmer_description = await get_programmer(message.from_user.id)
        programmer_description_result = programmer_description[1]
        await state.update_data(description=programmer_description_result)
        await state.set_state(ProgrammerForm.expectations)
        await bot.send_message(message.from_user.id, "Введите новые ожидания от проекта которого хотите найти")
    else:
        await state.update_data(description=message.text)
        await state.set_state(ProgrammerForm.expectations)
        await bot.send_message(message.from_user.id, "Введите ожидания от проекта которого хотите найти:")


@router.message(ProgrammerForm.expectations)
async def process_expectations(message: types.Message, state: FSMContext):
    await state.update_data(expectations=message.text)
    if message.text == "Оставить предыдущее значение":
        programmer_expectations = await get_programmer(message.from_user.id)
        programmer_expectations_result = programmer_expectations[2]
        await state.update_data(expectations=programmer_expectations_result)
        await state.set_state(ProgrammerForm.user_name)
        await bot.send_message(message.from_user.id, "Введите ваше новое имя пользователя в телеграмме:")
    else:
        await state.update_data(expectations=message.text)
        await state.set_state(ProgrammerForm.user_name)
        await bot.send_message(message.from_user.id, "Введите ваше имя пользователя в телеграмме:")


@router.message(ProgrammerForm.user_name)
async def process_user_name(message: types.Message, state: FSMContext):
    global edit_portfolio
    user_name_text = message.text
    is_correct_user_name = bool(re.fullmatch(r'[@A-Za-z0-9_]+', user_name_text))
    global project_name_global
    if (len(user_name_text) > 5 and is_correct_user_name) or user_name_text == "Оставить предыдущее значение":
        if message.text == "Оставить предыдущее значение":
            programmer_user_name = await get_programmer(message.from_user.id)
            programmer_user_name_result = programmer_user_name[3]
            await state.update_data(user_name=programmer_user_name_result)
        else:
            await state.update_data(user_name=message.text)
        programmer_data = await state.get_data()
        programmer_name = programmer_data['name']
        programmer_description = programmer_data['description']
        programmer_expectations = programmer_data['expectations']
        programmer_user_name = programmer_data['user_name']
        tg_id = message.from_user.id
        if edit_portfolio:
            await message.answer("...", reply_markup=types.ReplyKeyboardRemove())
            await bot.send_message(message.from_user.id, "Ваше портфолио изменено", reply_markup=kb_programmer2)
            await edit_programmer(programmer_name, programmer_description, programmer_expectations, programmer_user_name,
                              tg_id)
        else:
            await bot.send_message(message.from_user.id, "Ваше портфолио создано", reply_markup=kb_programmer2)
            await set_programmer(programmer_name, programmer_description, programmer_expectations, programmer_user_name,
                              tg_id)
        await state.clear()

    else:
        await state.set_state(ProgrammerForm.user_name)
        await bot.send_message(message.from_user.id, "Вы неправильно ввели ваше имя пользователя. Введите ваше имя пользователя заново:")


@router.callback_query(F.data == "create_project")
async def project_form(callback: CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.bot.send_message(callback.from_user.id, "Введите название вашего проекта:")
    await state.set_state(ProjectForm.project_name)

project_info_from_db_for_users = {}
edit_project_ = False

@router.callback_query(F.data == "edit_project")
async def edit_project_form(callback: CallbackQuery, state: FSMContext):
    global edit_project_
    edit_project_ = True
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.bot.send_message(callback.from_user.id, "Введите новое название проекта:", reply_markup=kb_edit_info)
    await state.set_state(ProjectForm.project_name)

projects_names = []
@router.callback_query(F.data == "list_projects")
async def watch_projects(callback: CallbackQuery):
    global projects_names
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    projects_kb = await create_list_project_kb(callback.from_user.id)
    projects_names = [button.text for row in projects_kb.keyboard for button in row]
    await callback.bot.send_message(callback.from_user.id, f"Выберите ваш проект, который хотите удалить или изменить:", reply_markup=projects_kb)

@router.callback_query(F.data == "delete_project")
async def process_delete_project(callback:CallbackQuery):
    global project_info_from_db_for_users
    project_name_to_delete = project_info_from_db_for_users[callback.from_user.id][0]
    await bot.send_message(callback.from_user.id, f"Проект под названием {project_name_to_delete} был успешно удалён!", reply_markup=kb_vacancer)
    await delete_project(callback.from_user.id, project_name_to_delete)
    await bot.send_message(callback.from_user.id, "...", reply_markup=types.ReplyKeyboardRemove())


@router.message(ProjectForm.project_name)
async def process_project_name(message: types.Message, state: FSMContext):
    global project_info_from_db_for_users
    user_projects_names = await get_all_user_projects_names(message.from_user.id)
    if message.text not in user_projects_names or message.text == "Оставить предыдущее значение":
        if message.text == "Оставить предыдущее значение":
            project_name_result = project_info_from_db_for_users[message.from_user.id][0]
            await state.update_data(project_name=project_name_result)
            await state.set_state(ProjectForm.description)
            await bot.send_message(message.from_user.id, "Введите новое описание вашего проекта:")
        else:
            await state.update_data(project_name=message.text)
            await state.set_state(ProjectForm.description)
            await bot.send_message(message.from_user.id, "Введите описание вашего проекта:")
    else:
        await bot.send_message(message.from_user.id, 'У вас уже есть проект с таким именем. Введите другое название вашего проекта')
        await state.set_state(ProjectForm.project_name)

@router.message(ProjectForm.description)
async def process_project_description(message: types.Message, state: FSMContext):
    if message.text == "Оставить предыдущее значение":
        project_description_result = project_info_from_db_for_users[message.from_user.id][1]
        await state.update_data(description=project_description_result)
        await state.set_state(ProjectForm.places)
        await bot.send_message(message.from_user.id, "Введите новое кол-во мест разработчиков в вашем проекте:")
    else:
        await state.update_data(description=message.text)
        await state.set_state(ProjectForm.places)
        await bot.send_message(message.from_user.id, "Введите кол-во мест разработчиков в вашем проекте:")


@router.message(ProjectForm.places)
async def process_project_places(message: types.Message, state: FSMContext):
    if message.text.isdigit() or message.text == "Оставить предыдущее значение":
        if message.text == "Оставить предыдущее значение":
            project_places_result = project_info_from_db_for_users[message.from_user.id][2]
            await state.update_data(places=project_places_result)
            await state.set_state(ProjectForm.occupied_places)
            await bot.send_message(message.from_user.id, "Введите новые занятые места разработчиков в проекте:")
        else:
            await state.update_data(places=message.text)
            await state.set_state(ProjectForm.occupied_places)
            await bot.send_message(message.from_user.id, "Введите занятые места разработчиков в проекте:")
    else:
        await state.set_state(ProjectForm.places)
        await bot.send_message(message.from_user.id,"Вам нужно ввести число а не строку! Введите кол-во мест разработчиков в вашем проекте заново: " )


@router.message(ProjectForm.occupied_places)
async def process_occupied_places(message: types.Message, state: FSMContext):
    project_data = await state.get_data()
    project_places = project_data['places']
    if message.text.isdigit() and int(project_places) > int(message.text) or message.text == "Оставить предыдущее значение":
        if message.text == "Оставить предыдущее значение":
            project_occupied_places_result = project_info_from_db_for_users[message.from_user.id][3]
            if int(project_places) > int(project_occupied_places_result):
                await state.update_data(occupied_places=project_occupied_places_result)
                await state.set_state(ProjectForm.required_skills)
                await bot.send_message(message.from_user.id, "Введите новые требуемые навыки разработчиков(языки программирования, фреймворки):")
            else:
                await state.set_state(ProjectForm.occupied_places)
                await bot.send_message(message.from_user.id,
                                       "Количество занятых мест разработчиков должно быть меньше чем всего мест разработчиков.\n"
                                       "Введите занятые места разработчиков в проекте заново:")
        else:
            await state.update_data(occupied_places=message.text)
            await state.set_state(ProjectForm.required_skills)
            await bot.send_message(message.from_user.id, "Введите требуемые навыки разработчиков:")
    else:
        await state.set_state(ProjectForm.occupied_places)
        await bot.send_message(message.from_user.id, "Количество занятых мест разработчиков должно быть меньше чем всего мест разработчиков.\n"
                                                     "Введите занятые места разработчиков в проекте заново: ")


@router.message(ProjectForm.required_skills)
async def process_required_skills(message: types.Message, state: FSMContext):
    if message.text == "Оставить предыдущее значение":
        project_required_skills_result = project_info_from_db_for_users[message.from_user.id][5]
        await state.update_data(required_skills=project_required_skills_result)
        await state.set_state(ProjectForm.user_name)
        await bot.send_message(message.from_user.id, "Введите ваше новое имя пользователя в телеграмме:")
    else:
        await state.update_data(required_skills=message.text)
        await state.set_state(ProjectForm.user_name)
        await bot.send_message(message.from_user.id, "Введите ваше имя пользователя в телеграмме:")


@router.message(ProjectForm.user_name)
async def process_user_name(message: types.Message, state: FSMContext):
    global edit_project_
    user_name_text = message.text
    is_correct_letters = bool(re.fullmatch(r'[@A-Za-z0-9_]+', user_name_text))
    if (len(user_name_text) > 5 and is_correct_letters) or user_name_text == "Оставить предыдущее значение":
        if message.text == "Оставить предыдущее значение":
            project_user_name_result = project_info_from_db_for_users[message.from_user.id][6]
            await state.update_data(user_name=project_user_name_result)
        else:
            await state.update_data(user_name=message.text)
        project_data = await state.get_data()
        project_name = project_data['project_name']
        project_description = project_data['description']
        project_places = int(project_data['places'])
        project_occupied_places = int(project_data['occupied_places'])
        project_required_skills = project_data['required_skills']
        project_user_name = project_data['user_name']
        tg_id = message.from_user.id
        if edit_project_:
            await message.answer("...", reply_markup=types.ReplyKeyboardRemove())
            await bot.send_message(message.from_user.id, "Ваш проект был изменён! Выберите проект который тоже хотите изменить или удалить", reply_markup=kb_vacancer)
            await edit_project(project_name, project_description, project_places, project_occupied_places,
                            project_required_skills, project_user_name, tg_id, project_info_from_db_for_users[message.from_user.id][0])
        else:
            await bot.send_message(message.from_user.id, "Ваш проект был создан!", reply_markup=kb_vacancer)
            await set_project(project_name, project_description, project_places, project_occupied_places,
                              project_required_skills, project_user_name, tg_id)
        await state.clear()
    else:
        await state.set_state(ProjectForm.user_name)
        await bot.send_message(message.from_user.id,
                               text="Вы неправильно ввели ваше имя пользователя. Введите имя пользователя заново:")


@router.message(lambda message: message.text in projects_names)
async def project_in_db(message: Message):
    project_info = await get_user_project(message.from_user.id, message.text)
    project_info_from_db_for_users[message.from_user.id] = project_info
    await bot.send_message(message.from_user.id, f"<b>Название вашего проекта</b>: <i>{project_info[0]}</i>\n\n"
                                                             f"<b>Описание вашего проекта</b>: <i>{project_info[1]}</i>\n\n"
                                                             f"<b>Кол-во программистов в вашем проекте</b>: <i>{project_info[2]} человек</i>\n\n"
                                                             f"<b>Занятые места программистов в вашем проекте</b>: <i>{project_info[3]} человек</i>\n\n"
                                                             f"<b>Свободные места программистов в вашем проекте</b>: <i>{project_info[4]} человек</i>\n\n"
                                                             f"<b>Требуемые навыки программистов</b>: <i>{project_info[5]}</i>\n\n"
                                                             f"<b>Ваше имя пользователя:</b>: {project_info[6]}", reply_markup=kb_edit_project, parse_mode="HTML")
projects_for_users = {}

project_to_favourite = ...

@router.callback_query(F.data == "watch_projects")
async def return_project(callback:CallbackQuery):
    global projects_for_users
    global project_to_favourite
    projects_list_in_db = cycle(await get_all_projects_in_db(callback.from_user.id))
    if projects_list_in_db:
        projects_for_users[callback.from_user.id] = projects_list_in_db
        project = next(projects_list_in_db)
        project_to_favourite = project
        await bot.send_message(callback.from_user.id, f"<b>Название проекта</b>: <i>{project.project_name}</i>\n\n"
                                                      f"<b>Описание проекта</b>: <i>{project.description}</i>\n\n"
                                                      f"<b>Кол-во программистов в проекте</b>: <i>{project.places}</i> человек\n\n"
                                                      f"<b>Занятые места программистов в проекте</b>: <i>{project.occupied_places}</i> человек\n\n"
                                                      f"<b>Свободные места программистов в проекте</b>: <i>{project.free_places}</i> человек\n\n"
                                                      f"<b>Требуемые навыки программистов</b>: <i>{project.required_skills}</i>\n\n"
                                                      f"<b>Связаться с вакантором</b>: <i>{project.user_name}</i>",
                               reply_markup=kb_next, parse_mode="HTML")
    else:
        await bot.send_message(callback.from_user.id, "Проектов в базе данных нет!")
    await callback.answer()

@router.callback_query(F.data == "next_project")
async def return_next_project(callback:CallbackQuery):
    global project_to_favourite
    project = next(projects_for_users[callback.from_user.id])
    project_to_favourite = project
    await bot.send_message(callback.from_user.id, f"<b>Название проекта</b>: <i>{project.project_name}</i>\n\n"
                                                  f"<b>Описание проекта</b>: <i>{project.description}</i>\n\n"
                                                  f"<b>Кол-во программистов в проекте</b>: <i>{project.places}</i> человек\n\n"
                                                  f"<b>Занятые места программистов в проекте</b>: <i>{project.occupied_places}</i> человек\n\n"
                                                  f"<b>Свободные места программистов в проекте</b>: <i>{project.free_places}</i> человек\n\n"
                                                  f"<b>Требуемые навыки программистов</b>: <i>{project.required_skills}</i>\n\n"
                                                  f"<b>Связаться с вакантором</b>: <i>{project.user_name}</i>",
                           reply_markup=kb_next, parse_mode="HTML")


programmers_for_users = {}

@router.callback_query(F.data == "search_programmers")
async def return_programmier(callback:CallbackQuery):
    global programmers_for_users
    programmers_from_db = cycle(await get_all_programmers(callback.from_user.id))
    if programmers_from_db:
        programmers_for_users[callback.from_user.id] = programmers_from_db
        programmier = next(programmers_from_db)
        await bot.send_message(callback.from_user.id, f"<b>Имя</b>: <i>{programmier.name}</i>\n\n"
                                                  f"<b>Информация о программисте(навыки и знания)</b>: <i>{programmier.description}</i>\n\n"
                                                  f"<b>Ожидание программиста от проекта которого он хочет найти</b>: <i>{programmier.exception}</i>\n\n"
                                                  f"<b>Имя пользователя программиста в телеграмме</b>: <i>{programmier.user_name}</i>",
                                                    reply_markup=kb_next_programmier, parse_mode="HTML")
    else:
        await bot.send_message(callback.from_user.id, "Нет программистов в базе данных")

@router.callback_query(F.data == "next_programmier")
async def return_next_programmier(callback:CallbackQuery):
    programmier = next(programmers_for_users[callback.from_user.id])
    await bot.send_message(callback.from_user.id, f"<b>Имя</b>: <i>{programmier.name}</i>\n\n"
                                                  f"<b>Информация о программисте(навыки и знания)</b>: <i>{programmier.description}</i>\n\n"
                                                  f"<b>Ожидание программиста от проекта которого он хочет найти</b>: <i>{programmier.exception}</i>\n\n"
                                                  f"<b>Имя пользователя программиста в телеграмме</b>: <i>{programmier.user_name}</i>",
                                                    parse_mode="HTML", reply_markup=kb_next_programmier)


@router.callback_query(F.data == 'favourite_projects')
async def list_favourite_projects(callback:CallbackQuery):
    await bot.send_message(callback.from_user.id, "проверка")

@router.callback_query(F.data == 'favourite_programmiest')
async def list_favourite_projects(callback:CallbackQuery):
    await bot.send_message(callback.from_user.id, "проверка программистов")



@router.callback_query(F.data == "add_project_to_favourites")
async def add_favourite_project(callback:CallbackQuery):
    print(project_to_favourite.project_name)
    await add_project_to_favourites(callback.from_user.id, project_to_favourite)
    await bot.send_message(callback.from_user.id, "Проект был добавлен в Избранные")

@router.callback_query(F.data == "add_programmier_to_favourites")
async def add_favourite_programmier(callback:CallbackQuery):
    await bot.send_message(callback.from_user.id , "Программист был добавлен в избранные проекта")
    # programmier = next(programmers_for_users[callback.from_user.id])