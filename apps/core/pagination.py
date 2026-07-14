"""Paginación estándar para la API."""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginación estándar configurable.

    Query params:
        - page: número de página
        - page_size: tamaño (max 100)
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
