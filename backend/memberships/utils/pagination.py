from rest_framework import pagination
from rest_framework.utils.urls import remove_query_param, replace_query_param


class PageNumberPagination(pagination.PageNumberPagination):
    """Custom pagination to allow page_size and relative next and prev url"""
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.get_full_path()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.get_full_path()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)
