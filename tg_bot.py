from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import filters
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import pickle
import json
import asyncio
import traceback
import random
from config import TOKEN_API


storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)

# путь к файлу с паролем
password_file = r'password.txt'

# путь к файлу со списком с пользователями
ids_file = r'super_ids.dat'

# путь к файлу со словарем с параметрами бота
parameters_file = r'parameters.dat'

# путь к файлу со словарем с пользователями и их настройкой уведомлений on или off
notifications_file = r'notifications.dat'

# путь к файлу со словарем с параметрами бота
data_file = r'data.json'

# путь к файлу со словарем с данными
tg_data_file = r'C:\Users\ivan3\OneDrive\Рабочий стол\lobster\tg_data.json'

# список эмоджи для последних монет
emoji = ['🥥','🧀','🍓','🫐','🍋','🍅','🍔','🍇','🍌','🍣','🦐','🍩','🍫','🫒','🌶','🥒','🍍','🍏','🍰',
         '🍊','🍆','🥑','🍉','🍦','🍪','🥩','🥔','🥝','🥦','🥐','🥕','🌽','🍕','🍟','🐳','🐬','🦈','🍺',
         '🦍','🦄','🐻','🐼','🐨','🦁','🐸','🐧','🐥','🦆','🦅','🦉','🦇','🐺','🐗','🐝','🪱','🐛','🌻',
         '🦋','🐌','🐞','🐜','🪰','🪲','🦟','🕷','🦂','🐢','🐍','🦎','🦕','🐙','🦑','🦞','🦀','🐠','🌹',
         '🐊','🐅','🐆','🦓','🦧','🦣','🐘','🦏','🐫','🦒','🦘','🐄','🐎','🐖','🐏','🦙','🐐','🦌','🍄',
         '🐩','🐈','🐓','🦚','🦜','🦢','🦩','🐇','🦝','🦨','🦫','🐀','🐿','🦔','🐉','🌵','🌲','🌴','🍀',]

# эта функция проверяет строку на числовое значение с плавающей точкой
def is_digit(string):
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False

# эта функция достает текущий пароль из файла password.txt
def get_password():
    file = open(password_file, 'r', encoding='utf8')
    password = file.readline()
    file.close()
    return password

# эта функция изменяет текущий пароль в файле password.txt
def change_password(new_password):
    file = open(password_file, 'w', encoding='utf8')
    file.write(new_password)
    file.close()

# эта функция достает текущий список пользователей с доступом к боту из файла super_ids.txt
def get_ids():
    file = open(ids_file, 'rb')
    try:
        super_ids = pickle.load(file)
    except:
        super_ids = ['1063427532']
        change_ids(super_ids)
    file.close()
    return super_ids

# эта функция изменяет текущий список пользователей с доступом к боту в файле super_ids.dat
def change_ids(new_ids):
    file = open(ids_file, 'wb')
    pickle.dump(new_ids, file)
    file.close()

# эта функция проверяет id пользователя и если он находится в списке то происходит дальнейшая обработка сообщения
# в данной ситуации IDFilter не подходит потомучто он не вызывает функцию в хэндлере при каждом отловленном сообщении, из-за этого если список пользователей изменется, то хэндлер об этом не узнает до перезапуска скрипта
def idfilter(id):
    if str(id) in get_ids():
        return True
    else:
        return False

# эта функция достает словарь с параметрами бота из файла parameters.dat
def get_parameters():
    file = open(parameters_file, 'rb')
    try:
        parameters = pickle.load(file)
    except:
        parameters = dict()
    file.close()
    return parameters

# эта функция изменяет словарь с параметрами бота в файле parameters.dat
def change_parameters(new_parameters):
    file = open(parameters_file, 'wb')
    pickle.dump(new_parameters, file)
    file.close()

# эта функция достает словарь с пользователями и их настройкой уведомлений из файла notifications.dat
def get_notifications():
    file = open(notifications_file, 'rb')
    try:
        notifications = pickle.load(file)
    except:
        notifications = {'1063427532': True}
        change_notifications(notifications)
    file.close()
    return notifications

# эта функция изменяет словарь с пользователями и их настройкой уведомлений в файле notifications.dat
def change_notifications(new_notifications):
    file = open(notifications_file, 'wb')
    pickle.dump(new_notifications, file)
    file.close()

# эта функция присылает всем пользователям (у кого включены) сообщения об изменениях параметров бота
async def send_notifications(message, parametr, new_value):
    for id in get_ids():
        if get_notifications()[id] and id != str(message.from_user.id):  # в первой проверке если по ключу id находится True, то код исполнится          
            if parametr == 'Монету':
                await bot.send_message(chat_id=id, text=f'<b>Продажа 💶</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{new_value}</b>', parse_mode='HTML')
            elif parametr == 'Игнорируемый объем' or parametr == 'Цену покупки':
                if new_value == 'НЕ ЗАДАН':
                    await bot.send_message(chat_id=id, text=f'<b>Продажа 💶</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{new_value}</b>', parse_mode='HTML')
                else:
                    await bot.send_message(chat_id=id, text=f'<b>Продажа 💶</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{float(new_value):,.2f}%</b>', parse_mode='HTML')
            elif parametr == 'status':
                await bot.send_message(chat_id=id, text=f'<b>Продажа 💶</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>{new_value} бота</i>', parse_mode='HTML')
            else:
                if new_value == 'НЕ ЗАДАН':
                    await bot.send_message(chat_id=id, text=f'<b>Продажа 💶</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{new_value}</b>', parse_mode='HTML')
                else:
                    await bot.send_message(chat_id=id, text=f'<b>Продажа 💶</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{float(new_value):,.2f}%</b>', parse_mode='HTML')

# эта функция присылает всем пользователям (у кого включены) сообщения об изменениях параметров бота
async def send_buy_notifications(message, parametr, new_value):
    for id in get_ids():
        if get_notifications()[id] and id != str(message.from_user.id):  # в первой проверке если по ключу id находится True, то код исполнится          
            if parametr == 'Монету':
                await bot.send_message(chat_id=id, text=f'<b>Покупка 🛒</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{new_value}</b>', parse_mode='HTML')
            elif parametr == 'Игнорируемый объем' or parametr == 'Цену покупки':
                if new_value == 'НЕ ЗАДАН':
                    await bot.send_message(chat_id=id, text=f'<b>Покупка 🛒</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{new_value}</b>', parse_mode='HTML')
                else:
                    await bot.send_message(chat_id=id, text=f'<b>Покупка 🛒</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{float(new_value):,}</b>', parse_mode='HTML')
            elif parametr == 'status':
                await bot.send_message(chat_id=id, text=f'<b>Покупка 🛒</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>{new_value} бота</i>', parse_mode='HTML')
            else:
                if new_value == 'НЕ ЗАДАН':
                    await bot.send_message(chat_id=id, text=f'<b>Покупка 🛒</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{new_value}</b>', parse_mode='HTML')
                else:
                    await bot.send_message(chat_id=id, text=f'<b>Покупка 🛒</b>\n<i>Пользователь</i> <b>@{(await bot.get_chat(message.from_user.id))["username"]}</b> <i>изменил</i> <b>{parametr}</b> <i>на</i> <b>{float(new_value):,}</b>', parse_mode='HTML')

# эта функция присылает всем пользователям сообщения об ошибках
async def send_errors(error):
    for id in get_ids():
        if get_notifications()[id]:  # в первой проверке если по ключу id находится True, то код исполнится          
            await bot.send_message(chat_id=id, text=f'{error}', parse_mode='HTML')
            # await bot.send_message(chat_id=id, text='<i>Бот остановлен</i> 🦦', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')

# эта функция достает словарь с параметрами бота из файла data.json
def get_data():
    file = open(data_file, 'r', encoding='utf-8')
    try:
        data = json.load(file)
    except:
        data = {'take profit': 0,
                'stop loss': 0,
                'volume': 100,
                'buy_price': 0,
                'assetsell': 'AURAX',
                'assetAddress': 'GAH75KLFPTYUGODDM6ETHNZUU2W3VNRPICPGQ5SDZ2KHOUXESA3WSAQ6',
                'status': False,
                'errors': [],
                'not_trigger': 0,
                'purchase_price': 0,
                'buy_volume': 100,
                'buy_status': False,
                'buy_not_trigger': 0}
        change_data(data)
    file.close()
    return data

# эта функция достает словарь с данными о тг боте из файла tg_data.json
def get_tg_data():
    file = open(tg_data_file, 'r', encoding='utf-8')
    try:
        data = json.load(file)
        if data == {}:
            data = {'coins':{}}         
    except:
        print('tg_data не считывается')
        data = {'coins':{}}
        
    file.close()
    return data

# эта функция изменяет словарь с параметрами бота в data.json
def change_data(new_data):
    file = open(data_file, 'w')
    json.dump(new_data, file, indent=4)
    file.close()

# эта функция изменяет словарь с данными о тг боте в tg_data.json
def change_tg_data(new_data):
    file = open(tg_data_file, 'w')
    json.dump(new_data, file, indent=4)
    file.close()

# эта функция добавляет новую монету в tg_data.json или изменяет порядок
def coins_sort(new_assetsell, new_assetAddress):
    data = get_tg_data()
    try:
        for number in list(data['coins']):
            data['coins'][int(number) + 1] = data['coins'].pop(number)
        del data['coins'][10]
    except:
        pass
    
    data['coins'][1] = {'assetsell':new_assetsell, 'assetAddress':new_assetAddress, 'emoji':random.choice(emoji)}
    change_tg_data(data)
       




# стартовая клавиатура которая показывается только пользователям с доступом к боту
def start_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Продажа💶'),KeyboardButton('Покупка🛒'), KeyboardButton('Пользователи👥'))
    return kb

# стартовая клавиатура которая показывается всем кроме пользователей бота
def id_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Показать мой ID❇️'))
    return kb

# клавиатура которая открывает меню Продажа и показывается только пользователям с доступом к боту
def sell_exchange_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    try:                                            # обработчик try проверяет наличие ключа 'status', если его нет, то запускается клавиатура с кнопкой запуска бота
        status = get_data()['status']
        if status:
            kb.add(KeyboardButton('➡️')).add(KeyboardButton('Параметры бота📊'), KeyboardButton('Цена покупки💳')).add(KeyboardButton('Take Profit💸'), KeyboardButton('Stop Loss📉')).add(KeyboardButton('Выбрать объем💰'), KeyboardButton('Игнор объема🗿')).add(KeyboardButton('Выбрать монету🪙'), KeyboardButton('Выключить бота💤')).add(KeyboardButton('Главное меню🏠'))
        else:
            kb.add(KeyboardButton('➡️')).add(KeyboardButton('Параметры бота📊'), KeyboardButton('Цена покупки💳')).add(KeyboardButton('Take Profit💸'), KeyboardButton('Stop Loss📉')).add(KeyboardButton('Выбрать объем💰'), KeyboardButton('Игнор объема🗿')).add(KeyboardButton('Выбрать монету🪙'), KeyboardButton('Включить бота⚡️')).add(KeyboardButton('Главное меню🏠'))
    except:
        kb.add(KeyboardButton('➡️')).add(KeyboardButton('Параметры бота📊'), KeyboardButton('Цена покупки💳')).add(KeyboardButton('Take Profit💸'), KeyboardButton('Stop Loss📉')).add(KeyboardButton('Выбрать объем💰'), KeyboardButton('Игнор объема🗿')).add(KeyboardButton('Выбрать монету🪙'), KeyboardButton('Включить бота⚡️')).add(KeyboardButton('Главное меню🏠'))
    return kb

# клавиатура которая открывает меню Покупка и показывается только пользователям с доступом к боту
def buy_exchange_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    try:                                            # обработчик try проверяет наличие ключа 'buy_status', если его нет, то запускается клавиатура с кнопкой запуска бота
        status = get_data()['buy_status']
        if status:
            kb.add(KeyboardButton('⬅️')).add(KeyboardButton('Параметры бота🧭'), KeyboardButton('Выбрать объем🥤')).add(KeyboardButton('Игнор объема🏝'), KeyboardButton('Остановить бота⚓️')).add(KeyboardButton('Главное меню🏠'))
        else:
            kb.add(KeyboardButton('⬅️')).add(KeyboardButton('Параметры бота🧭'), KeyboardButton('Выбрать объем🥤')).add(KeyboardButton('Игнор объема🏝'), KeyboardButton('Запустить бота🎳')).add(KeyboardButton('Главное меню🏠'))
    except:
        kb.add(KeyboardButton('⬅️')).add(KeyboardButton('Параметры бота🧭'), KeyboardButton('Выбрать объем🥤')).add(KeyboardButton('Игнор объема🏝'), KeyboardButton('Запустить бота🎳')).add(KeyboardButton('Главное меню🏠'))
    return kb

# клавиатура которая открывает меню с пользователями и показывается только пользователям с доступом к боту
def users_keyboard(id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    if get_notifications()[id]: 
        kb.add(KeyboardButton('Выключить уведомления🔕')).add(KeyboardButton('Показать всех пользователей👨‍👨‍👦‍👦'), KeyboardButton('Сменить пароль🔐')).add(KeyboardButton('Добавить пользователя🟢'), KeyboardButton('Удалить пользователя🔴')).add(KeyboardButton('Главное меню🏠'))
    else:
        kb.add(KeyboardButton('Включить уведомления🔔')).add(KeyboardButton('Показать всех пользователей👨‍👨‍👦‍👦'), KeyboardButton('Сменить пароль🔐')).add(KeyboardButton('Добавить пользователя🟢'), KeyboardButton('Удалить пользователя🔴')).add(KeyboardButton('Главное меню🏠'))
    return kb

# клавиатура отмены
def cancel_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Отмена🚫'))
    return kb

# клавиатура отмены специально для take profit и stop loss
def cancel_tp_sl_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Не задавать ничего🙈'), KeyboardButton('Отмена🚫'))
    return kb

# клавиатура отмены специально для Игнор объема
def cancel_not_trigger_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('Реагировать на любой объем👹'), KeyboardButton('Отмена🚫'))
    return kb

# инлайн клавиатура для подтверждения включения бота
def status_on_inline_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Да✅',callback_data='on'), InlineKeyboardButton('Нет⛔️',callback_data='cancel'))

# инлайн клавиатура для подтверждения выключения бота
def status_off_inline_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Да✅',callback_data='off'), InlineKeyboardButton('Нет⛔️',callback_data='cancel'))

# инлайн клавиатура для подтверждения включения бота
def buy_status_on_inline_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Да✅',callback_data='on'), InlineKeyboardButton('Нет⛔️',callback_data='cancel'))

# инлайн клавиатура для подтверждения выключения бота
def buy_status_off_inline_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Да✅',callback_data='off'), InlineKeyboardButton('Нет⛔️',callback_data='cancel'))

# инлайн клавиатура для подтверждения включения уведомлений
def notification_on_inline_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Да👍🏻',callback_data='on'), InlineKeyboardButton('Нет👎🏻',callback_data='cancel'))

# инлайн клавиатура для подтверждения выключения уведомлений
def notification_off_inline_keyboard():
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Да👍🏻',callback_data='off'), InlineKeyboardButton('Нет👎🏻',callback_data='cancel'))

# клавиатура которая показывает последние введенные монеты
def last_coins_inline_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    coins = get_tg_data()['coins']
    buttons = dict()
    for number in coins:        
        buttons[number] = InlineKeyboardButton(f'{coins[number]["assetsell"]} {coins[number]["emoji"]}', callback_data=number)
    if len(buttons) == 9:
        keyboard.add(buttons['1'], buttons['2'], buttons['3'], buttons['4'], buttons['5'], buttons['6'], buttons['7'], buttons['8'], buttons['9'])
    if len(buttons) == 8:
        keyboard.add(buttons['1'], buttons['2'])
        keyboard.add(buttons['3'], buttons['4'])
        keyboard.add(buttons['5'], buttons['6'])
        keyboard.add(buttons['7'], buttons['8'])
    if len(buttons) == 7:
        keyboard.add(buttons['1'], buttons['2'])
        keyboard.add(buttons['3'], buttons['4'])
        keyboard.add(buttons['5'], buttons['6'])
        keyboard.add(buttons['7'])
    if len(buttons) == 6:
        keyboard.add(buttons['1'], buttons['2'])
        keyboard.add(buttons['3'], buttons['4'])
        keyboard.add(buttons['5'], buttons['6'])
    if len(buttons) == 5:
        keyboard.add(buttons['1'], buttons['2'])
        keyboard.add(buttons['3'], buttons['4'])
        keyboard.add(buttons['5'])
    if len(buttons) == 4:
        keyboard.add(buttons['1'], buttons['2'])
        keyboard.add(buttons['3'], buttons['4'])
    if len(buttons) == 3:
        keyboard.add(buttons['1'], buttons['2'], buttons['3'])   
    if len(buttons) == 2:
        keyboard.add(buttons['1'], buttons['2'])
    if len(buttons) == 1:
        keyboard.add(buttons['1'])
    return keyboard





# основная часть бота
async def tg_bot():

    # группа состояний для изменения параметров бота на прожажу
    class SellParametersChange(StatesGroup):
        take_profit = State()
        stop_loss = State()
        choose_volume = State()
        choose_coin = State()
        work_status = State()
        not_trigger = State()
        purchase_price = State()

    # группа состояний для изменения параметров бота на покупку
    class BuyParametersChange(StatesGroup):
        buy_volume = State()
        buy_status = State()
        buy_not_trigger = State()

    # группа состояний для изменения списка пользователей
    class UsersChange(StatesGroup):
        append_password = State()
        append_users = State()
        delete_password = State()
        delete_users = State()

    # группа состояний для смены пароля
    class PasswordChange(StatesGroup):
        current_password = State()
        create_new_password = State()
        repeat_new_password = State()

    # группа состояний запуска бота через инлайн кнопку
    class BotStatus(StatesGroup):
        status_on = State()
        status_off = State()
        buy_status_on = State()
        buy_status_off = State()        
        notifications_on = State()
        notifications_off = State()

    

    # эта функция отлавливает монету в предложенных монетах в inline клавиатуре, задает новое значение ключам assetsell и assetAddress, а также сбрасывает состояние
    @dp.callback_query_handler(state=SellParametersChange.choose_coin)
    async def callback_choose_coin_command(callback: types.CallbackQuery, state: FSMContext):
        coins = get_tg_data()['coins']
        data = get_data()
        data['assetsell'] = coins[callback.data]['assetsell']
        data['assetAddress'] = coins[callback.data]['assetAddress']
        change_data(data)
        await bot.send_message(callback.from_user.id, text=f'<i>Вы выбрали </i><b>{coins[callback.data]["assetsell"]}</b><i>\nТеперь это новый параметр монеты</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
        await callback.answer(text=f'{coins[callback.data]["assetsell"]} {coins[callback.data]["emoji"]}')
        await state.reset_state()
        await send_notifications(callback, 'Монету', coins[callback.data]['assetsell'])

    # эта функция сохраняет статаус бота в словарь, удаляет сообщение с inline клавиатурой, сбрасывает состояние и обновляет основную клавиатуру
    @dp.callback_query_handler(text='on', state=BotStatus.status_on)
    async def callback_on_status_command(callback: types.CallbackQuery, state: FSMContext):
        data = get_data()
        data['status'] = True
        change_data(data)
        async with state.proxy() as memory:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=memory['message'])
        await state.reset_state()
        await bot.send_message(callback.from_user.id, text='<i>Бот успешно запущен</i> 💫', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
        await send_notifications(callback, 'status', 'запустил')


    # эта функция сохраняет статаус бота в словарь, удаляет сообщение с inline клавиатурой, сбрасывает состояние и обновляет основную клавиатуру
    @dp.callback_query_handler(text='off', state=BotStatus.status_off)
    async def callback_off_status_command(callback: types.CallbackQuery, state: FSMContext):
        data = get_data()
        data['status'] = False
        change_data(data)
        async with state.proxy() as memory:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=memory['message'])
        await state.reset_state()
        await bot.send_message(callback.from_user.id, text='<i>Бот остановлен</i> 🦦', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
        await send_notifications(callback, 'status', 'остановил')

    # эта функция сохраняет статаус бота на продажу в словарь, удаляет сообщение с inline клавиатурой, сбрасывает состояние и обновляет основную клавиатуру
    @dp.callback_query_handler(text='on', state=BotStatus.buy_status_on)
    async def callback_on_buy_status_command(callback: types.CallbackQuery, state: FSMContext):
        data = get_data()
        data['buy_status'] = True
        change_data(data)
        async with state.proxy() as memory:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=memory['message'])
        await state.reset_state()
        await bot.send_message(callback.from_user.id, text='<i>Бот успешно запущен</i> 🌟', reply_markup=buy_exchange_keyboard(), parse_mode='HTML')
        await send_buy_notifications(callback, 'status', 'запустил')


    # эта функция сохраняет статаус бота на продажу в словарь, удаляет сообщение с inline клавиатурой, сбрасывает состояние и обновляет основную клавиатуру
    @dp.callback_query_handler(text='off', state=BotStatus.buy_status_off)
    async def callback_off_buy_status_command(callback: types.CallbackQuery, state: FSMContext):
        data = get_data()
        data['buy_status'] = False
        change_data(data)
        async with state.proxy() as memory:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=memory['message'])
        await state.reset_state()
        await bot.send_message(callback.from_user.id, text='<i>Бот остановлен</i> 🦥', reply_markup=buy_exchange_keyboard(), parse_mode='HTML')
        await send_buy_notifications(callback, 'status', 'остановил')

    # эта функция сохраняет статаус уведомлений в словарь, удаляет сообщение с inline клавиатурой, сбрасывает состояние и обновляет основную клавиатуру
    @dp.callback_query_handler(text='on', state=BotStatus.notifications_on)
    async def callback_on_notifications_command(callback: types.CallbackQuery, state: FSMContext):
        notifications = get_notifications()
        notifications[str(callback.from_user.id)] = True
        change_notifications(notifications)
        async with state.proxy() as memory:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=memory['message'])
        await state.reset_state()
        await bot.send_message(callback.from_user.id, text='<i>Уведомления включены</i> 🔊', reply_markup=users_keyboard(str(callback.from_user.id)), parse_mode='HTML')

    # эта функция сохраняет статаус уведомлений в словарь, удаляет сообщение с inline клавиатурой, сбрасывает состояние и обновляет основную клавиатуру
    @dp.callback_query_handler(text='off', state=BotStatus.notifications_off)
    async def callback_off_notifications_command(callback: types.CallbackQuery, state: FSMContext):
        notifications = get_notifications()
        notifications[str(callback.from_user.id)] = False
        change_notifications(notifications)
        async with state.proxy() as memory:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=memory['message'])
        await state.reset_state()
        await bot.send_message(callback.from_user.id, text='<i>Уведомления выключены</i> 🔇', reply_markup=users_keyboard(str(callback.from_user.id)), parse_mode='HTML')


    # удаляет сообщение с inline клавиатурой, сбрасывает состояние и выводит соответствующий callback message
    @dp.callback_query_handler(text='cancel', state=BotStatus)
    async def callback_cancel_command(callback: types.CallbackQuery, state: FSMContext):
        await callback.answer('Операция отменена')
        async with state.proxy() as memory:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=memory['message'])
        await state.reset_state()







    # обработка команды /start только для пользователей с доступом
    @dp.message_handler(commands=['start'])
    async def start_menu_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text=f'<i><b>Здравствуй, мамкин ботовод</b></i> 🤑', reply_markup=start_keyboard(), parse_mode='HTML')
        else:
            await bot.send_message(message.from_user.id, text=f'Привет <b>@{message.from_user.username}</b>\n<i>К сожалению, у тебя нет доступа к функциям этого бота 😢\nЧтобы узнать на что он способен, свяжись с админом</i> ✨', reply_markup=id_keyboard(), parse_mode='HTML')

    # эта функция показывает твой id
    @dp.message_handler(lambda message: message.text.lower() == 'показать мой id❇️' or message.text.lower() == 'показать мой id')
    async def id_command(message: types.Message):
        await bot.send_message(message.from_user.id, text=f'Твой ID: <b>{message.from_user.id}</b>\n<i>Отправь его админу</i> 👾', parse_mode='HTML')

    # эта функция открывает меню "Продажа"
    @dp.message_handler(lambda message: message.text.lower() == 'продажа💶' or message.text.lower() == 'продажа')
    async def sell_open_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Меню</i> <b>Продажа💶</b> <i>открыто</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')

    # эта функция открывает меню "Покупка"
    @dp.message_handler(lambda message: message.text.lower() == 'покупка🛒' or message.text.lower() == 'покупка')
    async def buy_open_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Меню</i> <b>Покупка🛒</b> <i>открыто</i>', reply_markup=buy_exchange_keyboard(), parse_mode='HTML')

    # эта функция открывает меню "Покупка"
    @dp.message_handler(lambda message: message.text.lower() == '➡️')
    async def buy_open_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.delete_message(message.from_user.id, message.message_id)      # удаляет сообщение пользователя со стрелочкой
            await bot.send_message(message.from_user.id, text='<i>Меню</i> <b>Покупка🛒</b> <i>открыто</i>', reply_markup=buy_exchange_keyboard(), parse_mode='HTML')

    # эта функция открывает меню "Продажа"
    @dp.message_handler(lambda message: message.text.lower() == '⬅️')
    async def sell_open_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.delete_message(message.from_user.id, message.message_id)      # удаляет сообщение пользователя со стрелочкой
            await bot.send_message(message.from_user.id, text='<i>Меню</i> <b>Продажа💶</b> <i>открыто</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')

    # эта функция открывает меню "Пользователи"
    @dp.message_handler(lambda message: message.text.lower() == 'пользователи👥' or message.text.lower() == 'пользователи')
    async def users_open_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Меню</i> <b>Пользователи👥</b> <i>открыто</i>', reply_markup=users_keyboard(str(message.from_user.id)), parse_mode='HTML')

    # эта функция возвращает в главное меню
    @dp.message_handler(lambda message: message.text.lower() == 'главное меню🏠' or message.text.lower() == 'главное меню')
    async def main_menu_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Вы вернулись в</i> <b>Главное меню</b> 🏠', reply_markup=start_keyboard(), parse_mode='HTML')

    # эта функция показывает список всех пользователей с доступом
    @dp.message_handler(lambda message: message.text.lower() == 'показать всех пользователей👨‍👨‍👦‍👦' or message.text.lower() == 'показать всех пользователей')
    async def show_ids_command(message: types.Message):
        if idfilter(message.from_user.id):
            text = ''
            for i in get_ids():
                try:
                    text += f'<b>@{(await bot.get_chat(i))["username"]} - {i}\n</b>'
                except:
                    text += f'Noname<b> - {i}\n</b>'
            await bot.send_message(message.from_user.id, text=text, reply_markup=users_keyboard(str(message.from_user.id)), parse_mode='HTML')





    # эта функция показывает все параметры бота покупки
    @dp.message_handler(lambda message: message.text.lower() == 'параметры бота🧭')
    async def show_buy_parameters_command(message: types.Message):
        if idfilter(message.from_user.id):
            text = ''
            tg_data = get_tg_data()
            data = get_data()
            if 'assetsell' in data:
                try:
                    for number in tg_data['coins']:
                        if tg_data['coins'][number]['assetAddress'] == data['assetAddress']:
                            emoji = tg_data['coins'][number]['emoji']
                    text += f'<i>Название монеты: </i><b>{data["assetsell"]} {emoji}</b>\n'
                except:
                    text += f'<i>Название монеты: </i><b>{data["assetsell"]}</b>\n'
            else:
                text += f'<i>Название монеты: </i><b>НЕ ЗАДАН</b>\n'
            if 'assetAddress' in data:
                text += f'<i>Адрес монеты: </i><b>{data["assetAddress"]}</b>\n'
            else:
                text += f'<i>Адрес монеты: </i><b>НЕ ЗАДАН</b>\n'
            text += f'<b>\nПродажа 💶</b>\n'
            if 'purchase_price' in data:
                if data['purchase_price'] == 0:
                    text += f'<i>Цена покупки: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Цена покупки: </i><b>{data["purchase_price"]:,}</b>\n'
            if 'take profit' in data:
                if data['take profit'] == 0:
                    text += f'<i>Take Profit: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Take Profit: </i><b>{data["take profit"]:,.2f}</b>%\n'
            else:
                text += f'<i>Take Profit: </i><b>НЕ ЗАДАН</b>\n'
            if 'stop loss' in data:
                if data['stop loss'] == 0:
                    text += f'<i>Stop Loss: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Stop Loss: </i><b>{data["stop loss"]:,.2f}</b>%\n'
            else:
                text += f'<i>Stop Loss: </i><b>НЕ ЗАДАН</b>\n'
            if 'not_trigger' in data:
                if data['not_trigger'] == 0:
                    text += f'<i>Игнорируемый объем: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Игнорируемый объем: </i><b>{data["not_trigger"]:,}</b>\n'
            else:
                text += f'<i>Игнорируемый объем: </i><b>НЕ ЗАДАН</b>\n'
            if 'volume' in data:
                text += f'<i>Объем торговли: </i><b>{data["volume"]:,.2f}</b>%\n'
            else:
                text += f'<i>Объем торговли: </i><b>НЕ ЗАДАН</b>\n'
            if 'status' in data:
                if data['status'] == True:
                    text += f'<i>Состояние бота: </i><b>работает</b> 🟢\n'
                else:
                    text += f'<i>Состояние бота: </i><b>временно чиллит</b> 🔴\n'
            else:
                text += f'<i>Состояние бота: </i><b>временно чиллит</b> 🔴\n'
            text += f'\n<b>Покупка 🛒</b>\n'
            if 'buy_not_trigger' in data:
                if data['buy_not_trigger'] == 0:
                    text += f'<i>Игнорируемый объем: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Игнорируемый объем: </i><b>{data["buy_not_trigger"]:,}</b>\n'
            else:
                text += f'<i>Игнорируемый объем: </i><b>НЕ ЗАДАН</b>\n'
            if 'buy_volume' in data:
                text += f'<i>Объем торговли: </i><b>{data["buy_volume"]:,}</b>\n'
            else:
                text += f'<i>Объем торговли: </i><b>НЕ ЗАДАН</b>\n'
            if 'buy_status' in data:
                if data['buy_status'] == True:
                    text += f'<i>Состояние бота: </i><b>работает</b> 🟢\n'
                else:
                    text += f'<i>Состояние бота: </i><b>временно чиллит</b> 🔴\n'
            else:
                text += f'<i>Состояние бота: </i><b>временно чиллит</b> 🔴\n'
            await bot.send_message(message.from_user.id, text=text, reply_markup=buy_exchange_keyboard(), parse_mode='HTML')

    # эта функция отменяет изменение параметров бота на покупку на любой стадии
    @dp.message_handler(lambda message: message.text.lower() == 'отмена🚫' or message.text.lower() == 'отмена', state=BuyParametersChange)
    async def buy_parameters_cancel_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Изменения параметров покупки отменено ❌</i>', reply_markup=buy_exchange_keyboard(), parse_mode='HTML')
            await state.reset_state()

    # эта функция отлавливает текст 'игнор объема' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки нового параметра - Игнорируемый объем для покупки
    @dp.message_handler(lambda message: message.text.lower() == 'игнор объема🏝')
    async def buy_not_trigger_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>Игнорируемый объем</b> <i>в текущей монете 🏔\nВ качестве разделителя целого числа и дробной части используйте</i> <b>точку</b>❗️', reply_markup=cancel_not_trigger_keyboard(), parse_mode='HTML')
            await BuyParametersChange.buy_not_trigger.set()

    # эта функция принимает сообщение 'реагировать на любой объем' и задает ключу 'buy_not_trigger' значение 0, потом посылает сигнал на биржу 
    @dp.message_handler(lambda message: message.text.lower() == 'реагировать на любой объем👹' or message.text.lower() == 'реагировать на любой объем', state=BuyParametersChange.buy_not_trigger)
    async def buy_not_trigger_cancel_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            data = get_data()
            data['buy_not_trigger'] = 0
            change_data(data)
            await bot.send_message(message.from_user.id, text='<i>Параметр Игнорируемый объем</i> <b>НЕ ЗАДАН</b>', reply_markup=buy_exchange_keyboard(), parse_mode='HTML')
            await state.reset_state()
            await send_buy_notifications(message, 'Игнорируемый объем', 'НЕ ЗАДАН')

    # эта функция принимает Игнорируемый объем в текущей монете, сохраняет это значение в словарь, подает сигнал для бота на бирже и меняет состояние на None
    @dp.message_handler(state=BuyParametersChange.buy_not_trigger)
    async def buy_not_trigger_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            if is_digit(message.text):
                data = get_data()
                data['buy_not_trigger'] = float(message.text)
                change_data(data)
                await bot.send_message(message.from_user.id, text='<i>Новый параметр Игнорируемого объема установлен</i>', reply_markup=buy_exchange_keyboard(), parse_mode='HTML')
                await state.reset_state()
                await send_buy_notifications(message, 'Игнорируемый объем', message.text)
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели не числовое значение</i> ‼️', parse_mode='HTML')

    # эта функция отлавливает текст 'выбрать обьем' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки нового параметра - обьема на покупку
    @dp.message_handler(lambda message: message.text.lower() == 'выбрать объем🥤')
    async def choose_buy_volume_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>Объем</b> <i>в текущей монете 💵\nВ качестве разделителя целого числа и дробной части используйте</i> <b>точку</b>❗️', reply_markup=cancel_keyboard(), parse_mode='HTML')
            await BuyParametersChange.buy_volume.set()

    # эта функция принимает обьем в текущуй монете, сохраняет это значение в словарь, подает сигнал для бота на бирже и меняет состояние на None
    @dp.message_handler(state=BuyParametersChange.buy_volume)
    async def choose_buy_volume_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            if is_digit(message.text):
                data = get_data()
                data['buy_volume'] = float(message.text)
                change_data(data)
                await bot.send_message(message.from_user.id, text='<i>Новый параметр Обьема установлен</i>', reply_markup=buy_exchange_keyboard(), parse_mode='HTML')
                await state.reset_state()
                await send_buy_notifications(message, 'Объем торговли', message.text)
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели не числовое значение</i> ‼️', parse_mode='HTML')

    # эта функция отлавливает текст 'запустить бота', сохраняет в MemoryStorage id сообщения для дальнейшего его удаления в callback hendler, вызывает состояние и inline клавиатуру
    @dp.message_handler(lambda message: message.text.lower() == 'запустить бота🎳' or message.text.lower() == 'запустить бота')
    async def work_buy_status_on_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await BotStatus.buy_status_on.set()
            async with state.proxy() as memory:
                memory['message'] = message.message_id + 1
            await bot.send_message(message.from_user.id, text='<b>Вы уверены что хотите запустить бота</b>❓\n<i>Бот сразу выставит ордер по текущим параметрам🔹\nЖелательно убедиться в актуальности текущих параметров</i>🔹', reply_markup=buy_status_on_inline_keyboard(), parse_mode='HTML')

    # эта функция отлавливает текст 'остановить бота', сохраняет в MemoryStorage id сообщения для дальнейшего его удаления в callback hendler, вызывает состояние и inline клавиатуру
    @dp.message_handler(lambda message: message.text.lower() == 'остановить бота⚓️' or message.text.lower() == 'остановить бота')
    async def work_buy_status_off_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await BotStatus.buy_status_off.set()
            async with state.proxy() as memory:
                memory['message'] = message.message_id + 1
            await bot.send_message(message.from_user.id, text='<b>Вы уверены что хотите остановить бота</b> ⁉️\n<i>Бот прекратит поддерживать первую строчку в стакане, но не отменит текущий ордер🔹\nЕсли вы хотите отменить ордер, сделайте это через биржу</i>🔹', reply_markup=buy_status_off_inline_keyboard(), parse_mode='HTML')





    # эта функция отменяет изменение параметров бота на продажу на любой стадии
    @dp.message_handler(lambda message: message.text.lower() == 'отмена🚫' or message.text.lower() == 'отмена', state=SellParametersChange)
    async def sell_parameters_cancel_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Изменения параметров продажи отменено ❌</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
            await state.reset_state()

    # эта функция показывает все параметры бота продажи
    @dp.message_handler(lambda message: message.text.lower() == 'параметры бота📊')
    async def show_parameters_command(message: types.Message):
        if idfilter(message.from_user.id):
            text = ''
            tg_data = get_tg_data()
            data = get_data()
            if 'assetsell' in data:
                try:
                    for number in tg_data['coins']:
                        if tg_data['coins'][number]['assetAddress'] == data['assetAddress']:
                            emoji = tg_data['coins'][number]['emoji']
                    text += f'<i>Название монеты: </i><b>{data["assetsell"]} {emoji}</b>\n'
                except:
                    text += f'<i>Название монеты: </i><b>{data["assetsell"]}</b>\n'
            else:
                text += f'<i>Название монеты: </i><b>НЕ ЗАДАН</b>\n'
            if 'assetAddress' in data:
                text += f'<i>Адрес монеты: </i><b>{data["assetAddress"]}</b>\n'
            else:
                text += f'<i>Адрес монеты: </i><b>НЕ ЗАДАН</b>\n'
            text += f'\n<b>Продажа 💶</b>\n'
            if 'purchase_price' in data:
                if data['purchase_price'] == 0:
                    text += f'<i>Цена покупки: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Цена покупки: </i><b>{data["purchase_price"]:,}</b>\n'
            if 'take profit' in data:
                if data['take profit'] == 0:
                    text += f'<i>Take Profit: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Take Profit: </i><b>{data["take profit"]:,.2f}</b>%\n'
            else:
                text += f'<i>Take Profit: </i><b>НЕ ЗАДАН</b>\n'
            if 'stop loss' in data:
                if data['stop loss'] == 0:
                    text += f'<i>Stop Loss: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Stop Loss: </i><b>{data["stop loss"]:,.2f}</b>%\n'
            else:
                text += f'<i>Stop Loss: </i><b>НЕ ЗАДАН</b>\n'
            if 'not_trigger' in data:
                if data['not_trigger'] == 0:
                    text += f'<i>Игнорируемый объем: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Игнорируемый объем: </i><b>{data["not_trigger"]:,}</b>\n'
            else:
                text += f'<i>Игнорируемый объем: </i><b>НЕ ЗАДАН</b>\n'
            if 'volume' in data:
                text += f'<i>Объем торговли: </i><b>{data["volume"]:,.2f}</b>%\n'
            else:
                text += f'<i>Объем торговли: </i><b>НЕ ЗАДАН</b>\n'
            if 'status' in data:
                if data['status'] == True:
                    text += f'<i>Состояние бота: </i><b>работает</b> 🟢\n'
                else:
                    text += f'<i>Состояние бота: </i><b>временно чиллит</b> 🔴\n'
            else:
                text += f'<i>Состояние бота: </i><b>временно чиллит</b> 🔴\n'
            text += f'\n<b>Покупка 🛒</b>\n'
            if 'buy_not_trigger' in data:
                if data['buy_not_trigger'] == 0:
                    text += f'<i>Игнорируемый объем: </i><b>НЕ ЗАДАН</b>\n'
                else:
                    text += f'<i>Игнорируемый объем: </i><b>{data["buy_not_trigger"]:,}</b>\n'
            else:
                text += f'<i>Игнорируемый объем: </i><b>НЕ ЗАДАН</b>\n'
            if 'buy_volume' in data:
                text += f'<i>Объем торговли: </i><b>{data["buy_volume"]:,}</b>\n'
            else:
                text += f'<i>Объем торговли: </i><b>НЕ ЗАДАН</b>\n'
            if 'buy_status' in data:
                if data['buy_status'] == True:
                    text += f'<i>Состояние бота: </i><b>работает</b> 🟢\n'
                else:
                    text += f'<i>Состояние бота: </i><b>временно чиллит</b> 🔴\n'
            else:
                text += f'<i>Состояние бота: </i><b>временно чиллит</b> 🔴\n'
            await bot.send_message(message.from_user.id, text=text, reply_markup=sell_exchange_keyboard(), parse_mode='HTML')

    # эта функция отлавливает текст 'цена покупки' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки нового параметра - Цена покупки
    @dp.message_handler(lambda message: message.text.lower() == 'цена покупки💳' or message.text.lower() == 'цена покупки')
    async def purchase_price_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>Цену покупки</b> <i>в текущей монете ⚖️\nВ качестве разделителя целого числа и дробной части используйте</i> <b>точку</b>❗️', reply_markup=cancel_keyboard(), parse_mode='HTML')
            await SellParametersChange.purchase_price.set()

    # эта функция принимает Цену покупки в текущей монете, сохраняет это значение в словарь, подает сигнал для бота на бирже и меняет состояние на None
    @dp.message_handler(state=SellParametersChange.purchase_price)
    async def purchase_price_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            if is_digit(message.text):
                data = get_data()
                data['purchase_price'] = float(message.text)
                change_data(data)
                await bot.send_message(message.from_user.id, text='<i>Новый параметр Цены покупки установлен</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
                await state.reset_state()
                await send_notifications(message, 'Цену покупки', message.text)
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели не числовое значение</i> ‼️', parse_mode='HTML')

    # эта функция отлавливает текст 'take profit' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки нового параметра - take profit
    @dp.message_handler(lambda message: message.text.lower() == 'take profit💸' or message.text.lower() == 'take profit')
    async def take_profit_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>Take Profit</b> <i>в процентах 🗯\nВ качестве разделителя целого числа и дробной части используйте</i> <b>точку</b>❗️\n<i>Знак процента указывать не надо</i>', reply_markup=cancel_tp_sl_keyboard(), parse_mode='HTML')
            await SellParametersChange.take_profit.set()
            

    # эта функция принимает сообщение 'не задавать ничего' и безопасно удаляет ключ 'take profit' из словаря если он есть, потом посылает сигнал на биржу 
    @dp.message_handler(lambda message: message.text.lower() == 'не задавать ничего🙈' or message.text.lower() == 'не задавать ничего', state=SellParametersChange.take_profit)
    async def take_profit_cancel_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            data = get_data()
            data['take profit'] = 0
            change_data(data)
            await bot.send_message(message.from_user.id, text='<i>Параметр Take Profit</i> <b>НЕ ЗАДАН</b>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
            await state.reset_state()
            await send_notifications(message, 'Take Profit', 'НЕ ЗАДАН')

    # эта функция принимает take profit в процентах, сохраняет это значение в словарь, подает сигнал для бота на бирже и меняет состояние на None
    @dp.message_handler(state=SellParametersChange.take_profit)
    async def take_profit_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            if is_digit(message.text):
                data = get_data()
                data['take profit'] = float(message.text)
                change_data(data)
                await bot.send_message(message.from_user.id, text='<i>Новый параметр Take Profit установлен</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
                await state.reset_state()
                await send_notifications(message, 'Take profit', message.text)
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели не числовое значение</i> ‼️', parse_mode='HTML')

    # эта функция отлавливает текст 'stop loss' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки нового параметра - stop loss
    @dp.message_handler(lambda message: message.text.lower() == 'stop loss📉' or message.text.lower() == 'stop loss')
    async def stop_loss_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>Stop Loss</b> <i>в процентах 💭\nВ качестве разделителя целого числа и дробной части используйте</i> <b>точку</b>❗️\n<i>Знак процента указывать не надо</i>', reply_markup=cancel_tp_sl_keyboard(), parse_mode='HTML')
            await SellParametersChange.stop_loss.set()

    # эта функция принимает сообщение 'не задавать ничего' и безопасно удаляет ключ 'stop loss' из словаря если он есть, потом посылает сигнал на биржу 
    @dp.message_handler(lambda message: message.text.lower() == 'не задавать ничего🙈' or message.text.lower() == 'не задавать ничего', state=SellParametersChange.stop_loss)
    async def stop_loss_cancel_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            data = get_data()
            data['stop loss'] = 0
            change_data(data)
            await bot.send_message(message.from_user.id, text='<i>Параметр Stop Loss</i> <b>НЕ ЗАДАН</b>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
            await state.reset_state()
            await send_notifications(message, 'Stop loss', 'НЕ ЗАДАН')

    # эта функция принимает stop loss в процентах, сохраняет это значение в словарь, подает сигнал для бота на бирже и меняет состояние на None
    @dp.message_handler(state=SellParametersChange.stop_loss)
    async def stop_loss_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            if is_digit(message.text):
                data = get_data()
                data['stop loss'] = float(message.text)
                change_data(data)
                await bot.send_message(message.from_user.id, text='<i>Новый параметр Stop Loss установлен</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
                await state.reset_state()
                await send_notifications(message, 'Stop loss', message.text)
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели не числовое значение</i> ‼️', parse_mode='HTML')

    # эта функция отлавливает текст 'игнор объема' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки нового параметра - Игнорируемый объем
    @dp.message_handler(lambda message: message.text.lower() == 'игнор объема🗿')
    async def not_trigger_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>Игнорируемый объем</b> <i>в текущей монете 🏔\nВ качестве разделителя целого числа и дробной части используйте</i> <b>точку</b>❗️', reply_markup=cancel_not_trigger_keyboard(), parse_mode='HTML')
            await SellParametersChange.not_trigger.set()

    # эта функция принимает сообщение 'реагировать на любой объем' и задает ключу 'not_trigger' значение 0, потом посылает сигнал на биржу 
    @dp.message_handler(lambda message: message.text.lower() == 'реагировать на любой объем👹' or message.text.lower() == 'реагировать на любой объем', state=SellParametersChange.not_trigger)
    async def not_trigger_cancel_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            data = get_data()
            data['not_trigger'] = 0
            change_data(data)
            await bot.send_message(message.from_user.id, text='<i>Параметр Игнорируемый объем</i> <b>НЕ ЗАДАН</b>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
            await state.reset_state()
            await send_notifications(message, 'Игнорируемый объем', 'НЕ ЗАДАН')

    # эта функция принимает Игнорируемый объем в текущей монете, сохраняет это значение в словарь, подает сигнал для бота на бирже и меняет состояние на None
    @dp.message_handler(state=SellParametersChange.not_trigger)
    async def not_trigger_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            if is_digit(message.text):
                data = get_data()
                data['not_trigger'] = float(message.text)
                change_data(data)
                await bot.send_message(message.from_user.id, text='<i>Новый параметр Игнорируемого объема установлен</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
                await state.reset_state()
                await send_notifications(message, 'Игнорируемый объем', message.text)
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели не числовое значение</i> ‼️', parse_mode='HTML')

    # эта функция отлавливает текст 'выбрать обьем' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки нового параметра - обьема на продажу
    @dp.message_handler(lambda message: message.text.lower() == 'выбрать объем💰')
    async def choose_volume_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>Объем</b> <i>в процентах 💵\nВ качестве разделителя целого числа и дробной части используйте</i> <b>точку</b>❗️\n<i>Знак процента указывать не надо</i>', reply_markup=cancel_keyboard(), parse_mode='HTML')
            await SellParametersChange.choose_volume.set()

    # эта функция принимает обьем в процентах, сохраняет это значение в словарь, подает сигнал для бота на бирже и меняет состояние на None
    @dp.message_handler(state=SellParametersChange.choose_volume)
    async def choose_volume_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            if is_digit(message.text):
                data = get_data()
                data['volume'] = float(message.text)
                change_data(data)
                await bot.send_message(message.from_user.id, text='<i>Новый параметр Обьема установлен</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
                await state.reset_state()
                await send_notifications(message, 'Объем торговли', message.text)
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели не числовое значение</i> ‼️', parse_mode='HTML')

    # эта функция отлавливает текст 'выбрать монету' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки нового параметра - названия монеты
    @dp.message_handler(lambda message: message.text.lower() == 'выбрать монету🪙' or message.text.lower() == 'выбрать монету')
    async def choose_coin_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Выберите монету 🌕\nВведите</i> <b>заглавными буквами</b> <i>в данном формате</i>\n<b>НАЗВАНИЕ МОНЕТЫ:АДРЕСС МОНЕТЫ</b>❗️', reply_markup=cancel_keyboard(), parse_mode='HTML')
            if get_tg_data()['coins'] != dict():
                await bot.send_message(message.from_user.id, text='<i>Вы можете выбрать из предложенных ниже монет</i>🔎', reply_markup=last_coins_inline_keyboard(), parse_mode='HTML')
            await SellParametersChange.choose_coin.set()

    # эта функция принимает название монеты, сохраняет это значение в словарь, подает сигнал для бота на бирже и меняет состояние на None
    @dp.message_handler(state=SellParametersChange.choose_coin)
    async def choose_coin_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            if ':' in message.text:
                data = get_data()
                assetsell = message.text.partition(":")[0]
                assetAddress = message.text.partition(":")[2]
                data['assetsell'] = assetsell
                data['assetAddress'] = assetAddress
                change_data(data)
                coins_sort(assetsell, assetAddress)
                await bot.send_message(message.from_user.id, text='<i>Новый параметр названия монеты установлен</i>', reply_markup=sell_exchange_keyboard(), parse_mode='HTML')
                await state.reset_state()
                await send_notifications(message, 'Монету', assetsell)
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели неподходящее значение</i> ‼️', parse_mode='HTML')







    # эта функция отлавливает текст 'включить бота', сохраняет в MemoryStorage id сообщения для дальнейшего его удаления в callback hendler, вызывает состояние и inline клавиатуру
    @dp.message_handler(lambda message: message.text.lower() == 'включить бота⚡️' or message.text.lower() == 'включить бота')
    async def work_status_on_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await BotStatus.status_on.set()
            async with state.proxy() as memory:
                memory['message'] = message.message_id + 1
            await bot.send_message(message.from_user.id, text='<b>Вы уверены что хотите запустить бота</b>❓\n<i>Бот сразу выставит ордер по текущим параметрам🔹\nЖелательно убедиться в актуальности текущих параметров</i>🔹', reply_markup=status_on_inline_keyboard(), parse_mode='HTML')

    # эта функция отлавливает текст 'выключить бота', сохраняет в MemoryStorage id сообщения для дальнейшего его удаления в callback hendler, вызывает состояние и inline клавиатуру
    @dp.message_handler(lambda message: message.text.lower() == 'выключить бота💤' or message.text.lower() == 'выключить бота')
    async def work_status_off_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await BotStatus.status_off.set()
            async with state.proxy() as memory:
                memory['message'] = message.message_id + 1
            await bot.send_message(message.from_user.id, text='<b>Вы уверены что хотите остановить бота</b> ⁉️\n<i>Бот прекратит поддерживать первую строчку в стакане, но не отменит текущий ордер🔹\nЕсли вы хотите отменить ордер, сделайте это через биржу</i>🔹', reply_markup=status_off_inline_keyboard(), parse_mode='HTML')

    # эта функция отлавливает текст 'включить уведомления', сохраняет в MemoryStorage id сообщения для дальнейшего его удаления в callback hendler, вызывает состояние и inline клавиатуру
    @dp.message_handler(lambda message: message.text.lower() == 'включить уведомления🔔' or message.text.lower() == 'включить уведомления')
    async def notifications_on_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await BotStatus.notifications_on.set()
            async with state.proxy() as memory:
                memory['message'] = message.message_id + 1
            await bot.send_message(message.from_user.id, text='<b>Вы уверены что хотите включить уведомления</b>❓\n<i>Вам начнут приходить уведомления об измениях параметров бота от других пользователей</i>🔹', reply_markup=notification_on_inline_keyboard(), parse_mode='HTML')

    # эта функция отлавливает текст 'выключить уведомления', сохраняет в MemoryStorage id сообщения для дальнейшего его удаления в callback hendler, вызывает состояние и inline клавиатуру
    @dp.message_handler(lambda message: message.text.lower() == 'выключить уведомления🔕' or message.text.lower() == 'выключить уведомления')
    async def notifications_off_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await BotStatus.notifications_off.set()
            async with state.proxy() as memory:
                memory['message'] = message.message_id + 1
            await bot.send_message(message.from_user.id, text='<b>Вы уверены что хотите выключить уведомления</b> ⁉️\n<i>Вы не сможете следить за изменениями параметров бота от других пользователей</i>🔹', reply_markup=notification_off_inline_keyboard(), parse_mode='HTML')







    # эта функция отменяет редактирование списка пользователей на любой стадии
    @dp.message_handler(lambda message: message.text.lower() == 'отмена🚫' or message.text.lower() == 'отмена', state=UsersChange)
    async def users_cancel_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Редактирование списка пользователей отменено</i> ❌', reply_markup=users_keyboard(str(message.from_user.id)), parse_mode='HTML')
            await state.reset_state()

    # эта функция отлавливает текст 'добавить пользователя' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки текущего пароля
    @dp.message_handler(lambda message: message.text.lower() == 'добавить пользователя🟢' or message.text.lower() == 'добавить пользователя')
    async def append_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите пароль</i> 🔑', reply_markup=cancel_keyboard(), parse_mode='HTML')
            await UsersChange.append_password.set()

    # эта функция принимает текущий пароль и если он правильный то меняет состояние и просит ввести id пользователя для добавления, в противном случае сообщает о неверном пароле и предлагает ввести его повторно
    @dp.message_handler(state=UsersChange.append_password)
    async def append_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await message.delete()
            if message.text == get_password():
                await bot.send_message(message.from_user.id, text='<i>Введите id пользователя</i>', parse_mode='HTML')
                await UsersChange.append_users.set()
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели неправильный пароль</i> ‼️', parse_mode='HTML')

    # эта функция принимает id пользователя и если он состоит только из цифр то добавляет этот id и сохраняет обновленный список id в super_ids.txt и меняет состояние на None, в противном случае сообщает о невозможном id и предлагает ввести его повторно
    @dp.message_handler(state=UsersChange.append_users)
    async def append_third_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            if is_digit(message.text):
                ids = get_ids()
                ids.append(message.text)
                change_ids(ids)
                await bot.send_message(message.from_user.id, text='<i>Пользователь успешно добавлен</i> 👌🏻', reply_markup=users_keyboard(str(message.from_user.id)), parse_mode='HTML')
                try:    
                    await bot.send_message(message.text, text='<i>Вам открыли доступ к боту!!!</i> 🎉', reply_markup=start_keyboard(), parse_mode='HTML')
                except:
                    await bot.send_message(message.from_user.id, text='<i>Пользователь еще не активировал бота</i> 😕', parse_mode='HTML')
                await state.reset_state()
                notifications = get_notifications()
                if not message.text in notifications.keys():
                    notifications[message.text] = True      # обновляет notifications только если там нету ключа с этим id
                    change_notifications(notifications)
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели неправильный id</i> ‼️', parse_mode='HTML')

    # эта функция отлавливает текст 'удалить пользователя' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки текущего пароля
    @dp.message_handler(lambda message: message.text.lower() == 'удалить пользователя🔴' or message.text.lower() == 'удалить пользователя')
    async def delete_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите пароль</i> 🔑', reply_markup=cancel_keyboard(), parse_mode='HTML')
            await UsersChange.delete_password.set()

    # эта функция принимает текущий пароль и если он правильный то меняет состояние и просит ввести id пользователя для удаления, в противном случае сообщает о неверном пароле и предлагает ввести его повторно
    @dp.message_handler(state=UsersChange.delete_password)
    async def delete_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await message.delete()
            if message.text == get_password():
                await bot.send_message(message.from_user.id, text='<i>Введите id пользователя</i>', parse_mode='HTML')
                await UsersChange.delete_users.set()
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели неправильный пароль</i> ‼️', parse_mode='HTML')

    # эта функция принимает id пользователя и если он находится в то удаляет этот id и сохраняет обновленный список id в super_ids.txt и меняет состояние на None, в противном случае сообщает об отсутствии этого id в списке и предлагает ввести его повторно
    @dp.message_handler(state=UsersChange.delete_users)
    async def delete_third_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            ids = get_ids()
            if message.text in ids:
                ids.remove(message.text)
                change_ids(ids)
                await bot.send_message(message.from_user.id, text='<i>Пользователь успешно удален</i> 🤙🏻', reply_markup=users_keyboard(str(message.from_user.id)), parse_mode='HTML')
                try:
                    await bot.send_message(message.text, text='<i>Вам закрыли доступ к боту</i> 🥺', reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
                except:
                    pass
                await state.reset_state()
            else:
                await bot.send_message(message.from_user.id, text='<i>Такого id не найдено</i> ‼️', parse_mode='HTML')



    # эта функция отлавливает текст 'сменить пароль' в любом регистре только для пользователей с доступом к боту и после устанавливает состояние бота для обработки текущего пароля
    @dp.message_handler(lambda message: message.text.lower() == 'сменить пароль🔐' or message.text.lower() == 'сменить пароль')
    async def password_first_command(message: types.Message):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>текущий</b> <i>пароль</i> 🔑', reply_markup=cancel_keyboard(), parse_mode='HTML')
            await PasswordChange.current_password.set()

    # эта функция отменяет смену пароля на любой стадии
    @dp.message_handler(lambda message: message.text.lower() == 'отмена🚫' or message.text.lower() == 'отмена', state=PasswordChange)
    async def password_cancel_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await bot.send_message(message.from_user.id, text='<i>Смена пароля отменена</i> ❌', reply_markup=users_keyboard(str(message.from_user.id)), parse_mode='HTML')
            await state.reset_state()

    # эта функция принимает текущий пароль и если он правильный то меняет состояние и просит ввести новый, в противном случае сообщает о неверном пароле и предлагает ввести его повторно
    @dp.message_handler(state=PasswordChange.current_password)
    async def password_second_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await message.delete()
            if message.text == get_password():
                await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>новый</b> <i>пароль\nПароль может содержать совершенно любые значения</i> 👁‍🗨', parse_mode='HTML')
                await PasswordChange.next()
            else:
                await bot.send_message(message.from_user.id, text='<i>Вы ввели</i> <b>неверный</b> <i>пароль</i> ‼️', parse_mode='HTML')
                await bot.send_message(message.from_user.id, text='<i>Введите</i> <b>текущий</b> <i>пароль</i> 🔑', parse_mode='HTML')

    # эта функция принимает новый пароль, сохраняет его в MemoryStorage, устанавливает следуещее состояние и просит повторно ввести новый пароль
    @dp.message_handler(state=PasswordChange.create_new_password)
    async def password_third_command(message: types.Message, state: FSMContext):
            await message.delete()
            async with state.proxy() as memory:
                memory['new_password'] = message.text
            await bot.send_message(message.from_user.id, text='<i>Повторите</i> <b>новый</b> <i>пароль</i>', parse_mode='HTML')
            await PasswordChange.next()

    # эта функция просит повторно ввести новый пароль и если два ввода совпадают, то новый пароль записывается в глобальную переменную и состояние меняется на None, в противном случае предлагается заново ввести новый пароль
    @dp.message_handler(state=PasswordChange.repeat_new_password)
    async def password_fourth_command(message: types.Message, state: FSMContext):
        if idfilter(message.from_user.id):
            await message.delete()
            async with state.proxy() as memory:
                if memory['new_password'] == message.text:
                    change_password(memory['new_password'])
                    await bot.send_message(message.from_user.id, text='<i>Пароль успешно изменен</i> 🔄', reply_markup=users_keyboard(str(message.from_user.id)), parse_mode='HTML')
                    await PasswordChange.next()
                else:
                    await bot.send_message(message.from_user.id, text='<i>Вы ввели</i> <b>неверный</b> <i>пароль</i> ‼️', parse_mode='HTML')
                    await bot.send_message(message.from_user.id, text='<i>Повторите</i> <b>новый</b> <i>пароль</i>', parse_mode='HTML')

    # обработчик ошибок в основной части
    @dp.errors_handler()
    async def errors_command(update: types.Update, exception: all):
        error_info = traceback.format_exc()
        await bot.send_message(chat_id=1063427532, text='✉️telegram bot:\n'+error_info)
        return True



# функция которая работает асинхронно с основной частью бота, проверяет ключ 'errors' и если в него передается ошибка, то функция выводит ее в бота и дальше снова присваевает ключу значение None 
async def errors_catch():
    while True:
        await asyncio.sleep(1)      # sleep здесь необходим чтобы задачи работали асинхронно и while True не забирал на себя весь поток
        data = get_data()
        if data['errors'] != []:
            for error in data['errors']:
                try:
                    await send_errors(error)       # отправка сообщения об ошибке в боте на бирже
                except:
                    await bot.send_message(1063427532, '✉️telegram bot:\nОшибка в отправке ошибок с биржи')
            data['errors'] = []
            change_data(data)
        


# здесь создаются две асинхронные задачи
if __name__ == '__main__':          
    
    loop = asyncio.get_event_loop()
    loop.create_task(tg_bot())        # основная часть
    loop.create_task(errors_catch())    # проверка ошибок в бирже боте
    executor.start_polling(dp, loop=loop, skip_updates=True)

# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)         # стандартный запуск бота