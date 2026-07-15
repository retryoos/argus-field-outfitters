# Paging helpers shared by the shop grid and the backoffice tables. They live
# here rather than in either app because both use them and neither owns them
from django.core.paginator import Paginator

# Nine fills the shop's three by three card grid exactly. The panel tables are
# plain rows so they take more per page
GRID_PAGE_SIZE = 9
TABLE_PAGE_SIZE = 20


def paginate(request, queryset, per_page=GRID_PAGE_SIZE):
    # get_page is used rather than page() because it already copes with a page
    # number that is missing, not a number, or past the end, so a hand typed
    # ?page=abc cannot break the listing
    return Paginator(queryset, per_page).get_page(request.GET.get('page'))


def querystring_without_page(request):
    # The pager links have to carry the search and the filters with them, so
    # everything except the page number is kept and page is added back on by
    # the template
    params = request.GET.copy()
    params.pop('page', None)
    return params.urlencode()
