from django.apps import AppConfig


class TradeManagementConfig(AppConfig):
    name = 'trade_management'

    def ready(self):
        import trade_management.signals
