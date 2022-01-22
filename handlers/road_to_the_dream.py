import asyncio
from datetime import datetime
from pprint import pprint

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from models.road import PomodoroStats
from bot_config import bot, engine
from sqlalchemy.orm import sessionmaker

data = {'msg_if_restart': None}


async def start(message: aiogram.types.Message):
    photo_id = 'AgACAgIAAxkDAALtVWHn3ZZmzpMfA3SI7usT1avw9xrWAALRtjEbe9FASzJZxPBxsVhdAQADAgADeQADIwQ'
    await message.answer_photo(photo_id,
                               caption='Привет <i>%s</i> ты включил модуль 🚀<b>РОД ЗЕ ДРИМ</b>🚀' %
                               message['from']['first_name'])
    buttons = [['Помидор 🕔', 'Трекер привычек']]
    bot.add_keyboard('road_choose', buttons)
    await message.answer('Пожалуйста выберите 🛠 <b>инструмент</b>',
                         reply_markup=bot.keyboards['road_choose'])
    bot.add_state_handler(FSM.choose_tool, choose_tool)
    await FSM.choose_tool.set()


async def choose_tool(message: aiogram.types.Message, state: FSMContext):
    await state.finish()
    await message.delete()
    if message.text == 'Помидор 🕔':
        await pomodoro(message)
    elif message.text == 'Трекер привычек':
        await habit_tracker(message)


async def pomodoro(message: aiogram.types.Message,
                   time_focused: int = 15,
                   time_relax: int = 15):
    await message.answer('Вы включили 🕔 <b>помидор</b>',
                         reply_markup=ReplyKeyboardRemove())

    msg = await message.answer('У вас <i>15</i> минут <b>будьте сконцентрированы</b>')
    await timer(message['from']['id'], time_focused, text='<i>Вжаривай по полной</i>')

    await msg.edit_text('Теперь у вас есть время на отдых <i>15 минут</i>')
    await timer(message['from']['id'], time_relax, text='<i>На чиле</i>')

    Session = sessionmaker(bind=engine)
    with Session.begin() as session:
        user = session.query(PomodoroStats).first()
        user.today_cnt += 1
        cnt = user.today_cnt
    await msg.edit_text('<b>Поздравляю</b> вы получили %s' % ('🍅' * cnt))

    bot.add_keyboard('choose_bool', [['Да', 'Нет']])
    data['msg_if_restart'] = await message.answer('Хотите начать новый помидор?',
                                                  reply_markup=bot.keyboards['choose_bool'])
    bot.add_state_handler(FSM.choose_bool, choose_bool)
    await FSM.choose_bool.set()


async def choose_bool(message: aiogram.types.Message, state: FSMContext):
    await state.finish()
    await message.delete()
    assert data['msg_if_restart'] != None
    await data['msg_if_restart'].delete()
    if message.text == 'Да':
        await pomodoro(message)
    else:
        assert message.text == 'Нет'
        pass


async def timer(chat_id: str, seconds: int,
                text: str = 'Start', delay: int = 1,
                format: str = '%M:%S'):
    msg = await bot.send_message(chat_id, text)
    now = datetime.now().timestamp()
    finish_time = now + seconds
    while True:
        now = datetime.now().timestamp()
        remain_time = finish_time - now
        if now >= finish_time:
            break
        await msg.edit_text(text + ' <b>%s</b>' %
                            datetime.fromtimestamp(
                                remain_time).strftime(format))
        await asyncio.sleep(delay)
    await msg.delete()


async def habit_tracker(message: aiogram.types.Message):
    await message.answer('Вы включили трекер привычек', reply_markup=ReplyKeyboardRemove())
    await message.answer('<b>Поздравляю</b> вы получили 🦣')


class FSM(StatesGroup):
    init = State()
    choose_tool = State()
    pomodoro = State()
    choose_bool = State()
