import os

class PaypalConnector:
    def __init__(self, config=None):
        self.config = config or {}

    @staticmethod
    def configure_from_env():
        return {
            'client_id': os.environ.get('PAYPAL_CLIENT_ID'),
            'client_secret': os.environ.get('PAYPAL_CLIENT_SECRET'),
            'api_url': os.environ.get('PAYPAL_API_URL')
        }

    def send_payment(self, amount, currency, payer_info):
        # TODO: integrate with PayPal SDK / API
        return {'status': 'success', 'provider': 'paypal', 'amount': amount}

    def refund(self, payment_id, amount):
        # TODO: implement refund
        return {'status': 'success', 'refund_id': 'PAYPALREFUND123'}
