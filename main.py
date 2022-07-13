import dropbox
import telebot

access_token = "*******************************************************"  # dbx token
client = dropbox.dropbox_client.Dropbox(access_token)

telegram_bot_token = '**************************************'  # tg bot token
bot = telebot.TeleBot(telegram_bot_token)

keyboard_main = telebot.types.ReplyKeyboardMarkup(True)
keyboard_main.row('Информация об аккаунте', 'Узнать кол-во места на диске')
keyboard_main.row('Работа с файлами')

keyboard_files = telebot.types.ReplyKeyboardMarkup(True)
keyboard_files.row('Вывести список объектов корневого каталога')
keyboard_files.row('Получить файл', 'Загрузить файл', 'Удалить объект')
keyboard_files.row('Узнать информацию о файле, который не в корневом каталоге')
keyboard_files.row('Назад')

keyboard_backup = telebot.types.ReplyKeyboardMarkup(True)
keyboard_backup.row('Отмена')


def send(id, text):
    bot.send_message(id, text, reply_markup=keyboard_main)


def send_work(id, text):
    bot.send_message(id, text, reply_markup=keyboard_files)


def send_backup(id, text):
    bot.send_message(id, text, reply_markup=keyboard_backup)


@bot.message_handler(content_types=['text'])
def main(message):
    id = message.chat.id
    msg = message.text
    if msg.lower() == 'привет':
        send(id, 'Привет, ' + client.users_get_current_account().name.display_name)

    if msg.lower() == 'узнать информацию о файле, который не в корневом каталоге':
        send_backup(id, 'Введите путь к файлу на Dropbox')
        bot.register_next_step_handler(message, check)

    if msg[0] == '/':
        try:
            name_path = msg
            print(name_path)
            msg_path = name_path
            if msg_path != '':
                response = client.files_list_folder(path=msg_path)
                for file in response.entries:
                    send_work(id, file.name)
        except dropbox.exceptions.ApiError as e:
            send_work(id, 'Такой папки нет')
            print(e)

    if msg.find('.') != -1:
        try:
            f_name = msg
            response = client.files_list_folder(path='')
            for file in response.entries:
                if file.name == f_name:
                    send_work(id, 'Название файла: ' + str(file.name) +
                              '\nДоступность для загрузки: ' + str(file.is_downloadable) +
                              '\nПуть: ' + str(file.path_display) +
                              '\nРазмер: ' + str(file.size) + ' байт' +
                              '\nДата изменения: ' + str(file.client_modified))
        except dropbox.exceptions.ApiError as e:
            send_work(id, 'Такого файла нет')
            print(e)
        except dropbox.exceptions.BadInputError as e:
            send_work(id, 'Такого файла нет')
            print(e)

    if msg.lower() == 'информация об аккаунте':
        account_information = client.users_get_current_account()
        send(id, 'Регион: ' + account_information.country +
             '\nПочта: ' + account_information.email +
             '\nПодтверждена ли почта: ' + str(account_information.email_verified) +
             '\nФото профиля: ' + str(account_information.profile_photo_url))

    if msg.lower() == 'узнать кол-во места на диске':
        storage_information = client.users_get_space_usage()
        allocate_space = storage_information.allocation.get_individual().allocated
        used_space = storage_information.used
        available_space = allocate_space - used_space
        send(id, 'Всего: ' + str(allocate_space) + ' байт' +
             '\nИспользовано: ' + str(used_space) + ' байт' +
             '\nДоступно: ' + str(available_space) + ' байт')

    if msg.lower() == 'работа с файлами' or msg.lower() == 'главное меню':
        send_work(id, 'Что необходимо сделать?')

    if msg.lower() == 'вывести список объектов корневого каталога':
        response = client.files_list_folder(path='')
        for file in response.entries:
            send_work(id, file.name)

    if msg.lower() == 'назад':
        send(id, 'Необходимо выбрать функцию')

    if msg.lower() == 'получить файл':
        send_backup(id, 'Введите путь к файлу на Dropbox')
        bot.register_next_step_handler(message, download_from)

    if msg.lower() == 'загрузить файл':
        send_backup(id, 'Введите локальный путь к файлу')
        bot.register_next_step_handler(message, download_to)

    if msg.lower() == 'удалить объект':
        send_backup(id, 'Введите путь к объекту на Dropbox')
        bot.register_next_step_handler(message, delete_obj)


def check(message):
    if message.text.lower() == 'отмена':
        send_work(message.chat.id, 'Что необходимо сделать?')
    else:
        try:
            full_path = message.text
            file_name = full_path.split("/")[-1]
            path = ''.join(full_path.rsplit(file_name))
            response = client.files_list_folder(path=path)
            for file in response.entries:
                if file.name == file_name:
                    send_work(message.chat.id, 'Название файла: ' + str(file.name) +
                              '\nДоступность для загрузки: ' + str(file.is_downloadable) +
                              '\nПуть: ' + str(file.path_display) +
                              '\nРазмер: ' + str(file.size) + ' байт' +
                              '\nДата изменения: ' + str(file.client_modified))
        except dropbox.exceptions.ApiError as e:
            send_work(message.chat.id, 'Такого файла нет, либо неверно указан путь')
            print(e)
        except dropbox.exceptions.BadInputError as e:
            send_work(message.chat.id, 'Такого файла нет, либо неверно указан путь')
            print(e)


def download_from(message):
    if message.text.lower() == 'отмена':
        send_work(message.chat.id, 'Что необходимо сделать?')
    else:
        path = message.text
        try:
            file_name = path.split("/")[-1]
            print(file_name)
            with open(file_name, "wb") as f:
                metadata, res = client.files_download(path=path)
                f.write(res.content)
            d = open('D:\\PycharmProjects\\pythonProject\\' + file_name, 'rb')
            send_work(message.chat.id, 'Отправляю файл')
            bot.send_document(message.chat.id, d)
        except dropbox.exceptions.ApiError as e:
            send_work(message.chat.id, 'Такого файла нет, либо неверно указан путь')
            print(e)


def download_to(message):
    if message.text.lower() == 'отмена':
        send_work(message.chat.id, 'Что необходимо сделать?')
    else:
        local_path = message.text
        try:
            file_name = '/' + local_path.split("/")[-1]
            print(file_name)
            with open(local_path, 'rb') as file:
                response = client.files_upload(file.read(), file_name)
                send_work(message.chat.id, 'Файл загружен')
        except OSError as e:
            send_work(message.chat.id, 'Такого файла нет, либо неверно указан локальный путь')
            print(e)


def delete_obj(message):
    if message.text.lower() == 'отмена':
        send_work(message.chat.id, 'Что необходимо сделать?')
    else:
        path = message.text
        try:
            client.files_delete_v2(path)
            send_work(message.chat.id, 'Объект удален')
        except dropbox.exceptions.ApiError as e:
            send_work(message.chat.id, 'Такого файла нет, либо неверно указан путь')
            print(e)


bot.polling(none_stop=True)
