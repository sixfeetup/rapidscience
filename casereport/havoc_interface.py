__author__ = 'yaseen'

import requests
from django.conf import settings


HAVOC_USER = settings.HAVOC_USER
HAVOC_TOKEN = settings.HAVOC_TOKEN
HAVOC_BASE_URL = settings.HAVOC_BASE_URL
VOCABS = settings.VOCABS


def havoc_results(api, term, vocab=None, partial=None):
    if api == 'concepts':
        result_api = get_havoc_url(name='concepts', term=term)
        if partial:
            if vocab == 'hgnc':
                result_api += '&partial=1&tty=ACR'
            else:
                result_api += '&partial=1&tty=PT'

    elif api == 'concepts_bulk':
        result_api = get_havoc_url(name='concepts_bulk', terms=term)
    elif api == 'synonyms':
        result_api = get_havoc_url(name='synonyms', cui=term)
    result_api += '&user=' + HAVOC_USER + '&token=' + HAVOC_TOKEN
    if vocab:
        result_api += '&sabs=' + VOCABS.get(vocab)
    havoc_url = HAVOC_BASE_URL + result_api
    resp = requests.get(havoc_url)
    if api == 'synonyms':
        return resp.json()
    return format_results(resp.json())


def format_results(data):
    dict_list = []
    for res in data:
        if res.get('terms'):
            dict_list.append(dict(value=res.get('terms')[0], cui=res.get('cui'))) # appending first preffered term only
    return dict_list


def get_all_synonyms(terms):
    cui_list = []
    synonyms = []
    data = havoc_results(api='concepts_bulk', term=terms)
    for term in data:
        if term.get('cui') not in cui_list:
            cui_list.append(term.get('cui'))
    for cui in cui_list:
        synons = havoc_results(api='synonyms', term=cui)
        synonyms.extend(synons)
    synonyms = list(set(synonyms))
    return synonyms


def get_havoc_url(name, **kwargs):
    havoc_apis = {
        "concepts": "concepts?term={term}",
        "concepts_bulk": "concepts_bulk?terms={terms}",
        "synonyms": "concepts/{cui}/synonyms?",
    }
    url = havoc_apis[name].format(**kwargs)
    return url
