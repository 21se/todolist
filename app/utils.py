from json import JSONEncoder, JSONDecoder

import requests


def get_date_fact(day, month):
    response = requests.get(url='http://numbersapi.com/{}/{}/date?json'.format(month, day))

    if response.status_code == 200:
        result = response.json()
        if result['found']:
            return result['text']

    return ''


def translate(texts):
    url = "https://microsoft-translator-text.p.rapidapi.com/translate"

    querystring = {"to": "ru", "api-version": "3.0", "profanityAction": "NoAction", "textType": "plain"}

    json_encoder = JSONEncoder()
    payload = json_encoder.encode([{'Text': text} for text in texts])
    headers = {
        'content-type': "application/json",
        'x-rapidapi-key': "8342c37c96mshb7398e67059cc5ap12c034jsnbc48e2f38e90",
        'x-rapidapi-host': "microsoft-translator-text.p.rapidapi.com"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    if response.status_code == 200:
        json_decoder = JSONDecoder()
        results = json_decoder.decode(response.text)
        return [result['translations'][0]['text'] for result in results]

    return texts
