import logging
import re
import paramiko
import psycopg2
from psycopg2 import Error
import os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler,CallbackContext

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN ="token_cifr"
RM_HOST="192.168.217.154"
RM_PORT="22"
RM_USER="kali"
RM_PASSWORD="kali"

DB_USER="postgres"
DB_PASSWORD="Qq12345"
DB_HOST="192.168.217.154"
DB_PORT="5432"
DB_DATABASE="labdatabase"


def find_email_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')
    return 'find_email'


def find_email(update: Update, context):
    user_input = update.message.text
    context.user_data['user_input'] = user_input
    email_regex = re.compile(r'[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,}')
    email_list = email_regex.findall(user_input)
    if not email_list:
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END

    try:
        conn = psycopg2.connect(dbname=DB_DATABASE, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor = conn.cursor()
        for email in email_list:
            cursor.execute("SELECT * FROM emails WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result:
                update.message.reply_text(f'emails {email} уже есть в базе данных.')
                email_list.remove(email)
    except Exception as e:
        update.message.reply_text(f"Ошибка при работе с базой данных: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            cursor.close()

    emails = '\n'.join(email_list)
    update.message.reply_text(emails)
    update.message.reply_text('Хотите занести найденные email-адреса в базу данных? (Да/Нет)')
    return 'add_emails_to_db'




def add_emails_to_db(update: Update, context):
    user_response = update.message.text.lower()
    try:
        conn = psycopg2.connect(dbname=DB_DATABASE, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor = conn.cursor()

        email_list = re.findall(r'[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,}', context.user_data['user_input'])
        for email in email_list:
            cursor.execute("INSERT INTO emails (email) VALUES (%s) ON CONFLICT DO NOTHING", (email,))

        if user_response == 'да':
            conn.commit()
            update.message.reply_text('Email-адреса успешно добавлены в базу данных.')
        elif user_response == 'нет':
            update.message.reply_text('Данные не будут добавлены в базу данных.')
        else:
            update.message.reply_text('Пожалуйста ответьте "Да" или "Нет".')

    except Exception as e:
        update.message.reply_text(f"Ошибка при работе с базой данных: {e}")

    finally:
        if 'conn' in locals():
            conn.close()
            cursor.close()

    return ConversationHandler.END


# Команда для поиска телефонных номеров в тексте.
def find_phone_number_command(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'


# Поиск и вывод телефонных номеров из текста.
def find_phone_number(update: Update, context):
    user_input = update.message.text
    context.user_data['user_input'] = user_input
    phone_regex = re.compile(r'(?:8|\+7)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}')
    phone_list = phone_regex.findall(user_input)
    if not phone_list:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    try:
        conn = psycopg2.connect(dbname=DB_DATABASE, 
                                user=DB_USER, 
                                password=DB_PASSWORD, 
                                host=DB_HOST, 
                                port=DB_PORT)
        cursor = conn.cursor()
        for phone in phone_list:
            cursor.execute("SELECT * FROM phone WHERE phone_number = %s", (phone,))
            result = cursor.fetchone()
            if result:
                update.message.reply_text(f'Номер телефона {phone} уже есть в базе данных.')
                phone_list.remove(phone)
    except Exception as e:
        update.message.reply_text(f"Ошибка при работе с базой данных: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            cursor.close()
    phone = '\n'.join(phone_list)
    update.message.reply_text(phone)

    # Предложение занести данные в базу данных
    update.message.reply_text('Хотите занести найденные телефонные номера в базу данных? (Да/Нет)')
    return 'add_phone_numbers_to_db'


# Добавление телефонных номеров в базу данных.
def add_phone_numbers_to_db(update: Update, context):
    user_response = update.message.text.lower()
    try:
        conn = psycopg2.connect(dbname=DB_DATABASE, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor = conn.cursor()
        phone_list = [match for match in re.findall(r'(?:8|\+7)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}', context.user_data['user_input'])]
        
        for phone in phone_list:
            cursor.execute("INSERT INTO phone (phone_number) VALUES (%s) ON CONFLICT DO NOTHING", (phone,))
            
        if user_response == 'да':
            conn.commit()
            update.message.reply_text('Телефонные номера успешно добавлены в базу данных.')
        elif user_response == 'нет':
            update.message.reply_text('Хорошо, данные не будут добавлены в базу данных.')
        else:
            update.message.reply_text('Пожалуйста, ответьте "Да" или "Нет".')
    except Exception as e:
        update.message.reply_text(f"Ошибка при добавлении в базу данных: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
        cursor.close()
        
        return ConversationHandler.END
def get_release(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('lsb_release -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def get_repl_logs(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command(f'echo {RM_PASSWORD} | sudo -S docker logs db_container | grep repl_user')
    data = stdout.read() + stderr.read()
    client.close()
    data = data.decode('utf-8')
    update.message.reply_text(data)
def get_uname(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('uname -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def get_uptime(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_df(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('df')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def get_free(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('free')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def get_mpstat(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def get_w(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def get_auths(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('last -n 10')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def get_critical(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('journalctl -p crit -n 5')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def get_ps(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def get_ss(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('ss -s')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)


def get_apt_list(update, context):
    text = update.message.text.split()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    if len(text) > 1:
        package_name = " ".join(text[1:])
        stdin, stdout, stderr = client.exec_command(f'apt list {package_name}')
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data)
    else:
        stdin, stdout, stderr = client.exec_command('apt list --installed | head')
        data = stdout.read() + stderr.read()
        client.close()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        update.message.reply_text(data)
def get_services(update, context):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command('service --status-all')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    help_text = "Доступные команды:\n"
    help_text += "/start - Начать диалог\n"
    help_text += "/help - Получить справку о доступных командах\n"
    help_text += "/findemailaddress - Найти email-адреса в тексте\n"
    help_text += "/findPhoneNumbers - Найти телефонные номера в тексте\n"
    help_text += "/verify_password - Проверить сложность пароля\n"
    help_text += "/get_release - Получить информацию о релизе Linux системы\n"
    help_text += "/get_uname - Получить информацию об архитектуре процессора, имени хоста системы и версии ядра\n"
    help_text += "/get_uptime - Получить информацию о времени работы системы\n"
    help_text += "/get_df - Получить информацию о состоянии файловой системы\n"
    help_text += "/get_free - Получить информацию о состоянии оперативной памяти\n"
    help_text += "/get_mpstat - Получить информацию о производительности системы\n"
    help_text += "/get_w - Получить информацию о работающих пользователях\n"
    help_text += "/get_auths - Получить последние 10 входов в систему\n"
    help_text += "/get_critical - Получить последние 5 критических событий\n"
    help_text += "/get_ps - Получить информацию о запущенных процессах\n"
    help_text += "/get_ss - Получить информацию об используемых портах\n"
    help_text += "/get_apt_list - Получить список установленных пакетов или информацию о конкретном пакете\n"
    help_text += "/get_services - Получить информацию о запущенных сервисах\n"
    help_text += "/get_repl_logs - Получить информацию о репликации PostgreSQL\n"
    help_text += "/find_email - Вывести список email-адресов из базы данных\n"
    help_text += "/find_phone_number - Вывести список телефонных номеров из базы данных\n"
    update.message.reply_text(help_text)

def findemailaddressCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email адреса: ')
    return 'findemailaddress'

def findemailaddress(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) электронные адресса

    emailaddressregex = re.compile(r'[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,}', re.IGNORECASE)


    emailaddressList = emailaddressregex.findall(user_input)
    if not emailaddressList:
        update.message.reply_text('Электронные адреса не найдены')
        return ConversationHandler.END

    emailadress = ''
    for i in range(len(emailaddressList)):
        emailadress += f'{i + 1}. {emailaddressList[i]}\n'

    update.message.reply_text(emailadress)

    return ConversationHandler.END
def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:8|\+7)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}')

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль: ')

    return 'verify_password'

def verify_password(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    PasswordNumRegex = re.compile(r'(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}')

    PasswordNumList = PasswordNumRegex.findall(user_input)  # Ищем номера телефонов

    if PasswordNumRegex.match(user_input):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Пароль сложный')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Пароль простой')

    return ConversationHandler.END



def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    ConvHandlerPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )
    ConvHandlerFindEmailAddress = ConversationHandler(
    entry_points = [CommandHandler('findemailaddress', findemailaddressCommand)],
    states = {
        'findemailaddress': [MessageHandler(Filters.text & ~Filters.command, findemailaddress)],
    },
    fallbacks = []
    )
    
    conv_handler_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_command)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'add_emails_to_db': [MessageHandler(Filters.text & ~Filters.command, add_emails_to_db)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler_email)

    conv_handler_phone = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_number_command)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'add_phone_numbers_to_db': [MessageHandler(Filters.text & ~Filters.command, add_phone_numbers_to_db)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler_phone)
    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(ConvHandlerPassword)
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(ConvHandlerFindEmailAddress)
    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(CommandHandler('get_release', get_release))
    dp.add_handler(CommandHandler('get_uname', get_uname))
    dp.add_handler(CommandHandler('get_uptime', get_uptime))
    dp.add_handler(CommandHandler('get_df', get_df))
    dp.add_handler(CommandHandler('get_free', get_free ))
    dp.add_handler(CommandHandler('get_mpstat', get_mpstat ))
    dp.add_handler(CommandHandler('get_w', get_w ))
    dp.add_handler(CommandHandler('get_auths', get_auths ))
    dp.add_handler(CommandHandler('get_critical', get_critical ))
    dp.add_handler(CommandHandler('get_ps', get_ps ))
    dp.add_handler(CommandHandler('get_ss', get_ss ))
    dp.add_handler(CommandHandler('get_apt_list', get_apt_list ))
    dp.add_handler(CommandHandler('get_services', get_services ))
    dp.add_handler(CommandHandler('get_repl_logs', get_repl_logs))
    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
