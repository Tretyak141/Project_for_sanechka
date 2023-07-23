import aiogram
from aiogram import types,Bot,Dispatcher,executor
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove,KeyboardButtonPollType,InlineKeyboardButton,InlineKeyboardMarkup
import sql_modul as sql3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import os


tok = '***'
bot = Bot(token=tok)
dp = Dispatcher(bot,storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

buttons_admin = [["Создать поиск"],["Список поисков"]]

keyboard_admin = types.ReplyKeyboardMarkup(keyboard=buttons_admin)

buttons_user = [['Список поисков']]
keyboard_user = types.ReplyKeyboardMarkup(keyboard=buttons_user)


@dp.callback_query_handler(lambda c: c.data=="return")
async def ret(callback_query: types.CallbackQuery):
    inlines = InlineKeyboardMarkup(row_width=1)
    data = sql3.array_of_users(callback_query.from_user.id)
    for i in range(len(data)):
        inline_button = InlineKeyboardButton(f'Имя: {data[i][0]}\nГород: {data[i][1]}\nВозраст: {str(data[i][2])}\nДата рождения: {data[i][3]}',callback_data=f'btn{str(i+1)}')
        inlines.add(inline_button)
    await bot.send_message(callback_query.from_user.id,"Выбери нужный поиск",reply_markup=inlines)
    await callback_query.answer(text="Thanks",show_alert=True)

@dp.callback_query_handler(lambda c: c.data.startswith('btn'))
async def menu(callback_query: types.CallbackQuery):
    match sql3.is_admin(callback_query.from_user.id):
        case True:
            num = callback_query.data
            num = int(num.replace('btn','',1))
            inlines = InlineKeyboardMarkup(row_width=1)
            inline_button1 = InlineKeyboardButton("Удалить поиск",callback_data=f"del{str(num)}")
            inline_button2 = InlineKeyboardButton("Вернуться назад",callback_data='return')
            inlines.add(inline_button1)
            inlines.add(inline_button2)
            await bot.send_message(callback_query.from_user.id,"Выберете, что нужно сделать с поиском",reply_markup=inlines)
        case False:
            num = callback_query.data
            num = int(num.replace('btn','',1))
            await bot.send_message(callback_query.from_user.id, "Введите позывной и отправьте файл одним сообщением")
            logs = open(f'users_logs/{callback_query.from_user.id}.txt','w')
            logs.write(sql3.user_wth_num(num))
            logs.close()

@dp.callback_query_handler(lambda c: c.data.startswith('del'))
async def delete(callback_query: types.CallbackQuery):
    num = callback_query.data
    num = int(num.replace('del','',1))
    sql3.del_field(num)
    await bot.send_message(callback_query.from_user.id,"Удаление прошло успешно",reply_markup=keyboard_admin)
    await callback_query.answer(text="Thanks",show_alert=True)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if sql3.is_admin(message.from_user.id):
        await message.answer(f"Hola,admin",reply_markup=keyboard_admin)
    #else:
        #user_activity

@dp.message_handler(content_types=[
    types.ContentType.DOCUMENT,
    types.ContentType.TEXT
])
async def main_handler(message: types.Message):
    match (sql3.is_admin(message.from_user.id)):
        case True:
            match message.text:
                case "Создать поиск":
                    log = open(f'admins_logs/{message.from_user.id}.txt','w')
                    log.write("1")
                    log.close()
                    await message.answer("Введите на разных строках:\n1) Имя\n2) Город\n3) Возраст\n4) Дата рождения")
                    await message.answer("Пример:\n\nИван\nИваново\n18\n01.01.2000")
                case "Список поисков":
                    inlines = InlineKeyboardMarkup(row_width=1)
                    data = sql3.array_of_users(message.from_user.id)
                    for i in range(len(data)):
                        inline_button = InlineKeyboardButton(f'Имя: {data[i][0]}\nГород: {data[i][1]}\nВозраст: {str(data[i][2])}\nДата рождения: {data[i][3]}',callback_data=f'btn{str(i+1)}')
                        inlines.add(inline_button)
                    await message.reply("Выбери нужный поиск",reply_markup=inlines)
                case _:
                    log = open(f'admins_logs/{str(message.from_user.id)}.txt','r+')
                    logger = log.readline()
                    if logger=='1':
                        l = sql3.insert_field(message.text)
                        if l.startswith('un'):
                            await message.answer('Вводите данные корректно',reply_markup=keyboard_admin)
                        else:
                            await message.answer('Данные приняты',reply_markup=keyboard_admin)
                    else:
                        await message.answer('Вводите данные корректно')
                    log.truncate()
                    log.close()
        case False:
            match message.text:
                case 'Список поисков':
                    inlines = InlineKeyboardMarkup(row_width=1)
                    data = sql3.array_of_users(message.from_user.id)
                    for i in range(len(data)):
                        inline_button = InlineKeyboardButton(f'Имя: {data[i][0]}\nГород: {data[i][1]}\nВозраст: {str(data[i][2])}\nДата рождения: {data[i][3]}',callback_data=f'btn{str(i+1)}')
                        inlines.add(inline_button)
                    await message.reply("Выбери нужный поиск",reply_markup=inlines)
                case _:
                    log = open(f'users_logs/{str(message.from_user.id)}.txt','r+')
                    logger = log.read()
                    if logger!='':
                        filename = message.document.file_name
                        fileid = message.document.file_id
                        chanel1 = '*****'#Вот сюда вставишь айди канала ибо мне в падлу чет делать
                        zipp = os.path.splitext(filename)[1]
                        if zipp=='.zip' or zipp=='.plt' or zipp=='.gpx':
                            await bot.send_document(chanel1,fileid,caption=f'{logger}Позывной: {message.text}\nИмя файла: {filename}')
                            await message.answer('Данные приняты',reply_markup=keyboard_user)
                        else:
                            await message.answer('Расширение файла некорректно')
                    else:
                        await message.answer('Я не понимаю, что вы делаете')
                    log.truncate()
                    log.close()

if __name__ =='__main__':
    executor.start_polling(dp)
