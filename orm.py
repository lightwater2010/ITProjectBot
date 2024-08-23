from itertools import cycle
from typing import cast

from greenlet import greenlet
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_engine, async_session
from models import Base, Programmer, Project
from sqlalchemy import select, update, delete
import asyncio


async def create_tables():
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

async def set_programmer(name, description, exception, user_name, tg_id):
    async with async_session() as session:
        programmer = await session.scalar(select(Programmer).where(Programmer.tg_id==tg_id))
        if not programmer:
            programmer_ = Programmer(name=name, description=description, exception=exception, user_name=user_name, tg_id=tg_id )
            session.add(programmer_)
            await session.commit()
async def check_programmer_in_db(tg_id):
    async with async_session() as session:
        programmer = await session.scalar(select(Programmer).where(Programmer.tg_id == tg_id))
        if programmer:
            return "this programmer in db"
        return "this programmer isn't in db"
async def get_all_programmers(tg_id):
    async with async_session() as session:
        result = await session.execute(select(Programmer).where(Programmer.tg_id != tg_id))
        programmers = result.scalars().all()
        programmers_list = []
        for programmer in programmers:
            programmers_list.append(programmer)
        return programmers_list

async def get_programmer(tg_id):
    async with async_session() as session:
        programmer = await session.scalar(select(Programmer).where(Programmer.tg_id == tg_id))
        if programmer:
            programmer_info = [programmer.name, programmer.description, programmer.exception, programmer.user_name]
            return programmer_info
async def edit_programmer(new_name, new_description, new_exception, new_user_name, tg_id):
    async with async_session() as session:
        programmer = await session.scalar(select(Programmer).where(Programmer.tg_id == tg_id))
        programmer.name = new_name
        programmer.description = new_description
        programmer.exception = new_exception
        programmer.user_name = new_user_name
        await session.commit()

async def delete_portfolio(tg_id):
    session: AsyncSession
    async with async_session() as session:
        programmer = await session.scalar(select(Programmer).where(Programmer.tg_id == tg_id))
        await session.delete(programmer)
        await session.commit()
async def set_project(name, description, places, occupied_places, skills, user_name, tg_id):
    async with async_session() as session:
        free_places = places-occupied_places
        project_ = Project(project_name=name, description=description, places=places, occupied_places=occupied_places, free_places=free_places, required_skills=skills, user_name=user_name, tg_id=tg_id)
        session.add(project_)
        await session.commit()
async def get_all_user_projects_names(tg_id):
    async with async_session() as session:
        result = await session.execute(select(Project).where(Project.tg_id == tg_id))
        projects = result.scalars().all()
        projects_list = []
        for project in projects:
            projects_list.append(project.project_name)
        return projects_list
async def get_user_project(tg_id, project_name):
    async with async_session() as session:
        project = await session.scalar(select(Project).where(Project.tg_id == tg_id).where(Project.project_name == project_name))
        project_info = [project.project_name, project.description, project.places, project.occupied_places, project.free_places, project.required_skills, project.user_name]
        return project_info


async def get_all_projects_in_db(tg_id):
    async with (async_session() as session):
        projects = await session.execute(select(Project).where(Project.tg_id == tg_id))
        projects_result = projects.scalars().all()
        projects_list = []
        for project in projects_result:
            projects_list.append(project)
        return projects_list
async def edit_project(new_name, new_description, new_places, new_occupied_places, new_skills, new_user_name, tg_id, project_name):
    async with async_session() as session:
        project = await session.scalar(select(Project).where(Project.tg_id == tg_id).where(Project.project_name == project_name))
        project.project_name = new_name
        project.description = new_description
        project.places = new_places
        project.occupied_places = new_occupied_places
        project.free_places = new_places - new_occupied_places
        project.required_skills = new_skills
        project.user_name = new_user_name
        await session.commit()
async def delete_project(tg_id, name):
    session: AsyncSession
    async with async_session() as session:
        project_to_delete = await session.scalar(select(Project).where(Project.tg_id == tg_id).where(Project.project_name == name))
        if project_to_delete:
            await session.delete(project_to_delete)
        await session.commit()



# async def add_to_favorite_projects(tg_id, project):
#     session: AsyncSession
#     async with (async_session() as session):
#         g = greenlet(session.scalar)
#         result = g.switch(f'SELECT programmer FROM programmers WHERE programmer.tg_id =={tg_id}')
#         # programmer = await session.scalar(select(Programmer).where(Programmer.tg_id == tg_id))
#         print(result)
#
#         await session.commit()

async def add_project_to_favourites(tg_id, project):
    async with async_session() as session:
        async with session.begin():
            programmer = await session.scalar(select(Programmer).where(Programmer.tg_id == tg_id))
            programmer.projects.append(project)
            await session.commit()

async def add_to_project_team(tg_id, project_name, programmer):
    session: AsyncSession
    async with async_session() as session:
        project = await session.scalar(select(Project).where(Project.tg_id == tg_id).where(Project.project_name == project_name))
        project.programmers.append(programmer)
        await session.commit()

# asyncio.run(create_tables())






