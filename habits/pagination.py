from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    page_size = 5  # по ТЗ
    page_query_param = "page"  # ?page=1 (дефолт DRF)
    # Если хочешь жестко фиксировать 5/стр, НЕ добавляй page_size_query_param
    # page_size_query_param = "page_size"
    # max_page_size = 20
