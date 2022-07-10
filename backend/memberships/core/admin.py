from simple_history.admin import SimpleHistoryAdmin as BaseSimpleHistoryAdmin


class SimpleHistoryAdmin(BaseSimpleHistoryAdmin):
    history_list_display = ["ip_address"]
