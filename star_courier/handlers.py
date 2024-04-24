import json
import random

from alice_sdk import AliceRequest, AliceResponse


def dialog_handler(req: AliceRequest, *context) -> AliceResponse:
    """Основной обработчик запросов пользователя и ответов сервера, принимает на вход request и возвращает response"""

    res = AliceResponse(req)

    try:
        # если пользователь первый раз в игре
        if not req.state:
            return start_handler(res)  # запускаем обработчик start_handler() для приветствия

        if req.is_new_session:
            return new_session_handler(res)

        if req.state['user']['last_response'] == 'restart':
            if 'YANDEX.CONFIRM' in list(req.intents.keys()):
                return new_game(res)  # если подтвердил новую игру
            # else:
            #     res.set_state(req.state.copy())
            #     return intent_handler(res, 'return_game')  # если отказался от новой игры

        # если пользователь просит повторить сообщение
        if req.intents and 'restart' in list(req.intents.keys()):
            return restart(res, req)  # запускаем обработчик restart() для подтверждения новой игры

        # если пользователь просит повторить сообщение
        if req.intents and 'YANDEX.REPEAT' in list(req.intents.keys()):
            for key, item in res['user_state_update']['last_response'].items():
                res.state[key] = item
            return res

        # если сработал интент
        # if req.intents:
        #     for key in list(req.intents.keys()):
        #         if key in intents:  # ищем подходящий интент из списка
        #             if key != 'return_game' or req.state['last_response'] == 'command':
        #                 res.set_state(req.state.copy())
        #                 return intent_handler(res, key)  # запускаем обработчик intent_handler() для ответа на команду

        res.set_state(req.state.copy())
        data = data_handler(req.state['chapter'])

        if req.request['type'] == 'ButtonPressed':  # если пользователь нажал на кнопку
            # запускаем обработчик button_handler() для ответа на кнопку
            res.state['event'] = button_handler(req)

        else:  # если пользователь отправил сообщение
            # запускаем обработчик текста пользователя answer_handler()
            res.state['event'] = answer_handler(req, data['events'][req.state['event']],
                                                req.request['original_utterance'].lower())

        if data['events'][req.state['event']]['last_event']:
            res.state['chapter'] = data['next_chapter']
            data = data_handler(data['next_chapter'])  # переходим в новую главу, если это был последний ивент

        if res.state['event'] != req.state['event'] or req.session['message_id'] == 0:
            # обновляем инвентарь
            state = res.state.copy()
            for item in data['events'][res.state['event']]['items']:
                state['items'].append(item)
            res.set_state(state)

        # возвращаем текст события
        if res.state['event'] == req.state['event'] and req.session['message_id'] != 0:
            # обработка непонятного запроса
            res.set_text(random.choice(MISUNDERSTANDING))
            res.set_tts(res.text)
        else:
            res.set_text(data['events'][res.state['event']]['text'])  # текст
            res.set_tts(data['events'][res.state['event']]['tts'])  # голос
        res.set_buttons(data['events'][res.state['event']]['buttons'])  # кнопки
        if data['events'][res.state['event']]['card']:
            res.set_card(data['events'][res.state['event']]['card'])
        state = res.state.copy()
        state['last_response'] = 'event'
        res.set_state(state)

        return res
    except Exception as e:
        print(e)
        return start_handler(res)


def start_handler(res):
    """Собираем показатели нового игрока и возвращаем приветственное сообщение"""
    res.set_state({
        'chapter': 'start',
        'event': 'greeting',
        'items': [],
        'last_response': 'greeting'
    })
    data = data_handler('start')
    res.set_text(data['events'][res.state['event']]['text'])
    res.set_tts(data['events'][res.state['event']]['tts'])
    res.set_buttons(data['events'][res.state['event']]['buttons'])
    if data['events'][res.state['event']].get('card'):
        res.set_card(data['events'][res.state['event']]['card'])

    return res


def new_session_handler(res):
    return res


def button_handler(req):
    """Обработка кнопок"""
    if req.request['payload']['random']:  # если следующее событие случайное
        return random.choice(req.request['payload']['next_event'])['event']
    else:  # если следующее событие конкретное
        return req.request['payload']['next_event'][0]['event']


def answer_handler(req, events, text):
    """Обработка текстового запроса пользователя"""
    if not text:  # пустое сообщение
        return req.state['event']
    if req.state['chapter'] == 'start':
        for event in events['next_events']:  # поиск ключевых слов в тексте
            if not event['keys']:
                return event['event']
            for word in event['keys']:
                if word in text:
                    return event['event']
    for event in events['next_events']:
        if not event['random']:
            if not event['keys']:
                return event['event']
            for word in event['keys']:
                if word in text:
                    return event['event']
        else:
            if not event['keys']:
                return random.choice(event['event'])
            for word in event['keys']:
                if word in text:
                    return random.choice(event['event'])

    return req.state['event']  # непонятный ответ


def repeat_handler(res, req):
    """Обработчик повторения"""
    data = data_handler(req.state['chapter'])
    res.set_state(req.state.copy())
    res.set_text(data['events'][res.state['event']]['text'])
    res.set_tts(data['events'][res.state['event']]['tts'])
    res.set_buttons(data['events'][res.state['event']]['buttons'])
    if data['events'][res.state['event']].get('card'):
        res.set_card(data['events'][res.state['event']]['card'])
    return res


def restart(res, req):
    """Обработчик запроса новой игры"""
    res.set_state(req.state.copy())
    data = data_handler('commands')
    res.set_text(data['events'][res.state['event']]['text'])
    res.set_tts(res.text)
    res.set_buttons(data['restart']['buttons'])
    state = res.state.copy()
    state['last_response'] = 'restart'
    res.set_state(state)
    return res


def new_game(res):
    """Начинает новую игру, сбрасывает показатели игрока"""
    res.set_state({
        'chapter': 'prologue',
        'event': 'event_0',
        'reputation': 0,
        'mood': 0,
        'karma': 0,
        'items': [],
        'last_response': 'event'
    })
    data = data_handler('prologue')
    res.set_text(data['events'][res.state['event']]['text'])  # текст
    res.set_tts(data['events'][res.state['event']]['tts'])  # голос
    res.set_buttons(data['events'][res.state['event']]['buttons'])  # кнопки
    if data['events'][res['user_state_update']['event']]['card']:
        res.set_card(data['events'][res.state['event']]['card'])

    return res


def data_handler(chapter):
    """Возвращает json-файл с нужной главой"""
    with open(f'data/events/{chapter}.json') as json_file:
        return json.load(json_file)


def save_response(res: dict, text: str, tts: str, buttons: list, card: dict = None) -> dict:
    res['response']['text'] = text
    res['response']['tts'] = tts
    res['response']['buttons'] = buttons.copy()
    res['user_state_update']['last_response'] = {
        'text': text,
        'tts': tts,
        'buttons': buttons.copy()
    }
    if card:
        res['response']['card'] = card.copy()
        res['user_state_update']['last_response']['card'] = card.copy()
    return res