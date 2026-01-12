import os

class BankConnector:
    def __init__(self, config=None):
        self.config = config or {}

    @staticmethod
    def configure_from_env():
        # Load settings from environment variables
        return {
            'api_url': os.environ.get('BANK_API_URL'),
            'api_key': os.environ.get('BANK_API_KEY')
        }

    def send_payment(self, amount, currency, account_details):
        # TODO: implement real bank API call
        # Mock behavior:
        return {'status': 'success', 'tx_id': 'BANKMOCK123', 'amount': amount}

    def refund(self, tx_id, amount):
        # TODO: call refund endpoint
        return {'status': 'success', 'refund_id': 'REFUNDMOCK123', 'tx_id': tx_id}
