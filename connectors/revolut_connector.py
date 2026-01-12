import os

class RevolutConnector:
    def __init__(self, config=None):
        self.config = config or {}

    @staticmethod
    def configure_from_env():
        return {
            'token': os.environ.get('REVOLUT_TOKEN'),
            'account_id': os.environ.get('REVOLUT_ACCOUNT_ID')
        }

    def send_payment(self, amount, currency, target):
        # TODO: call Revolut Business API
        return {'status': 'success', 'provider': 'revolut', 'amount': amount}

    def refund(self, payment_id, amount):
        # TODO: implement refund via Revolut
        return {'status': 'success', 'refund_id': 'REVOLTREF123'}
