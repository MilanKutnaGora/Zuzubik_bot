import os
import pandas as pd
import sqlite3
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройки базы данных
DB_NAME = 'zuzubik_data.db'

# Создание таблицы, если она не существует
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            xpath TEXT,
            price REAL
        )
    ''')
    conn.commit()
    conn.close()

# Функция для обработки загрузки файла
def handle_document(update: Update, context: CallbackContext):
    file = update.message.document.get_file()
    file.download('uploaded_file.xlsx')

    # Открываем файл с помощью pandas
    df = pd.read_excel('uploaded_file.xlsx')

    # Выводим содержимое в ответ пользователю
    update.message.reply_text(f"Содержимое файла:\n{df.to_string(index=False)}")

    # Сохраняем данные в локальную БД
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        title = row['title']
        url = row['url']
        xpath = row['xpath']
        cursor.execute('INSERT INTO products (title, url, xpath) VALUES (?, ?, ?)', (title, url, xpath))

    conn.commit()
    conn.close()

    update.message.reply_text("Данные успешно сохранены в базе данных.")

# Основная функция для запуска бота
def main():
    create_table()
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), handle_document))

    updater.start_polling()
    updater.idle()


# Задание со звездочкой

#Для реализации парсинга и вычисления средней цены по каждому сайту

def parse_and_calculate_average():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT url FROM products')
    urls = cursor.fetchall()

    averages = {}
    for (url,) in urls:
        cursor.execute('SELECT price FROM products WHERE url = ?', (url,))
        prices = cursor.fetchall()
        if prices:
            prices = [price[0] for price in prices]
            avg_price = sum(prices) / len(prices)
            averages[url] = avg_price

    conn.close()
    return averages

if __name__ == '__main__':
    main()