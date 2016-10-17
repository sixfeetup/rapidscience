from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(request, object_list, per_page=20, orphans=0, allow_empty_first_page=True):
    """
    This is a convenience wrapper to eliminate duplication in views that require pagination.
    Requires the current request object and a queryset and returns the paginated objects.
    """
    paginator = Paginator(object_list, per_page, orphans, allow_empty_first_page)

    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects

