from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from el_pagination.decorators import page_template

from .models import NewsItem


@page_template('newsfeed/_news_items.html')
def newsitem_list(request, template_name="newsfeed/newsfeed.html", extra_context=None):
    objects = NewsItem.published.all()
    context = {
        'objects': objects,
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, template_name, context)
