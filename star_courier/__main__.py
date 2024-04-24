# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с логами.
import logging

# Импортируем модуль для работы с json
import json

# Импортируем модуль для работы с API Алисы
from alice_sdk import AliceRequest, AliceResponse

# Импортируем модуль с логикой игры
from handlers import dialog_handler

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)


logging.basicConfig(level=logging.INFO)


# Задаем параметры приложения Flask.
@app.route("/alice", methods=["POST"])
def main():

    alice_request = AliceRequest(request.json)
    logging.info("Request: {}".format(alice_request))

    alice_response = dialog_handler(alice_request)

    logging.info("Response: {}".format(alice_response))

    return alice_response.dumps()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)  # запуск
