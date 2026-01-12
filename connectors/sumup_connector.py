import os

class SumUpConnector:
    def __init__(self, config=None):
        self.config = config or {}

    @staticmethod
    def configure_from_env():
        return {
            'client_id': os.environ.get('SUMUP_CLIENT_ID'),
            'client_secret': os.environ.get('SUMUP_CLIENT_SECRET')
        }

    def send_payment(self, amount, currency, card_info):
        # TODO: call SumUp API
        return {'status': 'success', 'provider': 'sumup', 'amount': amount}

    def refund(self, transaction_id, amount):
        # TODO: call refund
        return {'status': 'success', 'refund_id': 'SUMUPREF123'}
