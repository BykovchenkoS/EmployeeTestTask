import json
import mysql.connector

def connect():
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        connection = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        return connection

    except FileNotFoundError:
        print("Файл конфигурации не найден.")
        return None
    except mysql.connector.Error as error:
        print("Ошибка при подключении к базе данных: {}".format(error))
        return None

