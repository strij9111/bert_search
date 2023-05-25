import re
from datetime import datetime

from behave import *
import requests
import json

# Порог №1 = 90%
THRESHOLD1 = 90

# Порог №2 = 50%
THRESHOLD2 = 50

RANKER = "Combined BERT+Manticore"

# url поискового API
URL = "http://127.0.0.1:8090/search"

headers = {
    'Content-Type': 'application/json',
}


def update_weight(response):
    items = response
    first_weight = items[0]['distance'] if items else 0
    for item in items:
        item['distance'] = item['distance'] / first_weight * 100
    response['distance'] = items
    return response

@given('request with body')
def step_impl(context):
    context.payload = json.loads(context.text)
    context.headers = headers


@given('request with text: "{text}"')
def step_impl(context, text):
    payload = {
        'text': text,
        'ranker': RANKER,
        'limit': 100
    }
    context.headers = headers
    context.payload = payload


@when('send GET request')
def step_impl(context):
    response = requests.get(
        URL, headers=context.headers, json=context.payload)
    context.response = update_weight(response.json())
    items = context.response
    context.top_items = list(filter(lambda x: x['distance'] >= THRESHOLD1, items))
    context.middle_items = list(filter(lambda x: THRESHOLD2 <= x['distance'] < THRESHOLD1, items))
    context.bottom_items = list(filter(lambda x: x['distance'] < THRESHOLD2, items))
    context.items = items
    context.status_code = response.status_code


@then('response is OK')
def step_impl(context):
    assert context.status_code == 200
