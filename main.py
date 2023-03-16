from config import API_TOKEN, tags
import logging
import psycopg2
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Task(StatesGroup):
    tag = State()
    difficulty = State()
    checks_tag = State()
    checks_difficulty = State()


conn = psycopg2.connect(dbname='tasks', user='postgres', password='7355608k', host='localhost')
cur = conn.cursor()
cur.execute("SELECT tag_name FROM tags ORDER BY tag_name")
tags_list = cur.fetchall()
for i in range(len(tags_list)):
    tags_list[i] = str(tags_list[i])
    tags_list[i] = tags_list[i][2:-3]

keyboard_start = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_start.add(KeyboardButton('/help'), KeyboardButton('/tag_list'), KeyboardButton('/task'))


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет! Я - бот, который поможет тебе подбирать задачки по программированию.\n "
        "Напиши /help чтобы увидеть список всех команд",
        reply_markup=keyboard_start)


@dp.message_handler(commands=['help'])
async def get_help(message: types.Message):
    await message.reply("/help - список всех команд\n"
                        "/task - вывести список из 10 задач с заданными темой и сложностью\n"
                        "/tag_list - вывести список всех тем задач")


@dp.message_handler(commands=['tag_list'])
async def tag_list(message: types.Message):
    await message.reply(tags, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['task'])
async def get_tag(message: types.Message):
    await message.reply("Введите тему задачи(на английском)\nДля получения списка задач, введите /tag_list")
    await Task.checks_tag.set()


@dp.message_handler(state=Task.checks_tag)
async def checks_tags(message: types.Message, state: FSMContext):
    user_answer = message.text
    if user_answer not in tags_list:
        await message.reply("Пожалуйста, введите тему корректно")
        await get_tag(user_answer)
    await state.update_data(tag=user_answer)
    await Task.tag.set()


@dp.message_handler(state=Task.tag)
async def get_difficulty(message: types.Message, state: FSMContext):
    await message.reply(
        "Теперь введите сложность задачи (от 800 до 3500 и кратно 100, где 800 - это самая легкая задача, а 3500 - самая сложная)")
    await Task.checks_difficulty.set()


@dp.message_handler(state=Task.checks_difficulty)
async def checks_difficulty(message: types.Message, state: FSMContext):
    user_answer = int(message.text)
    if (user_answer < 799) and (user_answer > 3501) and (user_answer % 100 != 0):
        await message.reply("Пожалуйста, введите сложность корректно")
        await get_difficulty(user_answer)
    await state.update_data(difficulty=user_answer)
    await Task.difficulty.set()


@dp.message_handler(state=Task.difficulty)
async def get_data(message: types.Message, state: FSMContext):
    await state.update_data(difficulty=message.text)
    data = await state.get_data()
    cur.execute(
        f"SELECT * FROM tasks "
        f"JOIN tasks_tags ON tasks.num = tasks_tags.task_num "
        f"JOIN tags ON tasks_tags.tag_id = tags.tag_id "
        f"WHERE (tags.tag_name = '{data['tag']}') AND (tasks.difficulty = '{data['difficulty']}') ORDER BY RANDOM() LIMIT 10")
    rows = cur.fetchall()
    result = ""
    for row in rows:
        result += f"Number: {row[0]},  Name: {row[1]},  Tag: {row[6]},  Difficulty: {row[2]},  Times Solved: {row[3]} , Link: {row[4]}\n"
    if len(result) != 0:
        await message.reply(result)
    else:
        await message.reply(
            "Извините, не могу найти такие задачи\nПожалуйста, проверьте, правильно ли вы написали тему")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
