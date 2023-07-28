from aiogram import Bot, types, Dispatcher, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlite import db_start, create_profile, edit_profile_back_call, edit_profile_currently

storage = MemoryStorage()
bot = Bot('###')
dp = Dispatcher(bot, storage=MemoryStorage())


async def on_startup(_):
    await db_start()


class ProfileStatesGroup(StatesGroup):   # names states
    name = State()
    phone = State()
    time = State()
    cur_name = State()
    cur_phone = State()
    cur_time = State()


def get_ikb_start():    # start function where the user selects action type
    ikb_start = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Запись', callback_data='record'),
         InlineKeyboardButton('Контакты', callback_data='contacts')],
        [InlineKeyboardButton('О нас', callback_data='about')]
    ])

    return ikb_start


def get_ikb_appointment_type():    # function where the user selects comfortable type of make an appointment
    ikb_appointment = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Обратный звонок', callback_data='call'),
         InlineKeyboardButton('Записаться сейчас', callback_data='currently')],
        [InlineKeyboardButton('Назад', callback_data='cancel')]
    ])

    return ikb_appointment


def cancel_kb():    # this keyboard function for exit
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Отмена'))

    return kb


@dp.callback_query_handler(lambda c: c.data == 'cancel')   # handling the cancel function
# and output start inline keyboard
async def get_info(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Вы прервали процесс записи\n Выберите пожалуйста, что Вас интересует',
                           reply_markup=get_ikb_start())


@dp.message_handler(commands=['start'])    # handling the start command
async def cmd_start(message: types.Message):
    await message.answer(f"Добро пожаловать! \nВыберите пожалуйста необходимую для Вас функцию: ",
                         reply_markup=get_ikb_start())
    await create_profile(user_id=message.from_user.id)    # added in database user id


@dp.callback_query_handler(lambda c: c.data == 'record')    # handling answer 'запись'
async def get_record(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Выберите удобный для Вас вариант записи',
                           reply_markup=get_ikb_appointment_type())


@dp.callback_query_handler(lambda c: c.data == 'call')    # handling request 'обратный звонок'
async def get_call(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["data_call"] = callback_query.data    # added data for next work with it

    await bot.send_message(callback_query.from_user.id, text='Введите пожалуйста Ваше имя и фамилию',
                           reply_markup=cancel_kb())
    await ProfileStatesGroup.next()    # end with this handler and waiting the next action


@dp.message_handler(lambda message: not message.text.isdigit(), state=ProfileStatesGroup.phone)    # handling answer
# for phone
async def check_phone(message: types.Message):
    await message.reply('Вы ввели некорректный номер телефона, попробуйте снова',    # error if user has written
                        # incorrect number
                        reply_markup=cancel_kb())


@dp.message_handler(state=ProfileStatesGroup.name)   # handling name
async def get_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text

    await message.reply("Введите пожалуйста Ваш номер телефона (без знака + и пробелов)",    # check correct number
                        reply_markup=cancel_kb())
    await ProfileStatesGroup.next()    # end with this handler and waiting the next action


@dp.message_handler(state=ProfileStatesGroup.phone)    # handling for getting user number
async def get_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["phone"] = message.text

    await message.answer("Укажите пожалуйста удобное время для звонка",
                         reply_markup=cancel_kb())
    await ProfileStatesGroup.next()    # end with this handler and waiting the next action


@dp.message_handler(state=ProfileStatesGroup.time)    # handling request time
async def get_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["time"] = message.text
    await edit_profile_back_call(state, user_id=message.from_user.id)
    await message.answer('Ваша заявка успешно создана, мы свяжемся с Вами в ближайшее время')    # the last message
    # after getting information
    await state.finish()    # end process


@dp.callback_query_handler(lambda c: c.data == 'contacts')    # handling request 'контакты'
async def get_contacts(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Наш телефон: ...\n ВК: ...',    # output contacts info
                           reply_markup=get_ikb_start())


@dp.callback_query_handler(lambda c: c.data == 'about')    # handling request 'о нас'
async def get_info(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мы занимаемся ....',    # output info
                           reply_markup=get_ikb_start())


@dp.callback_query_handler(lambda c: c.data == 'currently')    # handling request 'записаться сейчас'
async def get_currently(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["currently"] = callback_query.data

    await bot.send_message(callback_query.from_user.id, text='Введите пожалуйста Ваше имя и фамилию',
                           reply_markup=cancel_kb())
    await ProfileStatesGroup.next()    # end with this handler and waiting the next action


@dp.message_handler(lambda message: not message.text.isdigit(), state=ProfileStatesGroup.phone)    # check user number
async def check_cur_phone(message: types.Message):
    await message.reply('Вы ввели некорректный номер телефона, попробуйте снова',    # error if user has written
                        # incorrect number
                        reply_markup=cancel_kb())


@dp.message_handler(state=ProfileStatesGroup.cur_name)    # handling request name
async def get_currently_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["cur_name"] = message.text

    await message.answer('Введите пожалуйста Ваш номер (без знака + и пробелов)',
                         reply_markup=cancel_kb())
    await ProfileStatesGroup.next()


@dp.message_handler(state=ProfileStatesGroup.cur_phone)    # handling request number
async def get_cur_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["cur_phone"] = message.text

    await message.answer("Укажите пожалуйста удобное время для записи на прием",
                         reply_markup=cancel_kb())
    await ProfileStatesGroup.next()


@dp.message_handler(state=ProfileStatesGroup.cur_time)    # handling request time
async def get_cur_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["cur_time"] = message.text
    await edit_profile_currently(state, user_id=message.from_user.id)
    await message.reply('Ваша заявка на прием была успешно сохранена, мы свяжемся с Вами в ближайшее время',)   # the
    # last message after getting information
    await state.finish()   # end the process


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)
