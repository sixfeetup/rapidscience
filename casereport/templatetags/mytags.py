__author__ = 'asreedh'

import re
import urllib.parse
import mimetypes


from django import template

register = template.Library()

RETURN_VALUES = {'gender': 'checked',
                 'molecular_abberations': 'selected',
                 'treatments': 'selected',
                 'cr_tests': 'selected',
                 'treatment_type': 'selected',
                 'country': 'selected',
                 'primary_physician': 'checked'}

@register.simple_tag
def check_value_is_active(field, value, url):
    url_value = urllib.parse.parse_qs(url)
    current_value = '{0}:{1}'.format(field, value)
    if url_value:
        facets = [x.lower() for x in url_value.get('selected_facets', None)]
        if current_value.lower() in facets:
            return RETURN_VALUES[field]
    if field == 'gender' and 'gender' not in url:
        # display gender fields as checked if gender not in query
        return RETURN_VALUES[field]
    return ''


@register.simple_tag
def check_treatment_active(field, value, url):
    url_value = urllib.parse.parse_qs(url)
    current_value = '%s_exact:%s' %(field, value)
    selected_facets = url_value.get('selected_facets', None)
    if selected_facets:
        return "selected"
    return ''


@register.simple_tag
def get_pagination_url(url, page_number):
    actual_url = url.split('&page')[0]
    if actual_url.rfind('?') < 0:
        actual_url += '?'
    return '%s&page=%s' %(actual_url, page_number)


@register.filter()
def check_is_image(name):
    type = mimetypes.guess_type(name)
    if 'image' in type[0].lower():
        return True
    return False

@register.simple_tag
def age_range(url, facet_ages):
    try:
        age = re.findall('[0-9]*TO[0-9]*', url)[0]
        min_age, max_age = age.split('TO')
    except:
        if not facet_ages:
            return '0-100'
        min_age, max_age = facet_ages[0][0], facet_ages[-1][0]
    return '%s-%s' %(min_age, max_age)

