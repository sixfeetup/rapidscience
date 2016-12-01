__author__ = 'yaseen'

import requests
from crdb.settings import HAVOC_USER
from crdb.settings import HAVOC_TOKEN
from crdb.settings import HAVOC_BASE_URL
from crdb.settings import VOCABS
from crdb.settings import get_havoc_url


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

