import os

class SepaDirectDebitConnector:
    def __init__(self, config=None):
        self.config = config or {}

    @staticmethod
    def configure_from_env():
        return {
            'creditor_id': os.environ.get('SEPA_CREDITOR_ID'),
            'bank_api_url': os.environ.get('SEPA_BANK_API')
        }

    def send_payment(self, mandate, amount, currency='EUR'):
        # TODO: implement SEPA direct debit initiation
        return {'status': 'scheduled', 'mandate': mandate, 'amount': amount}

    def refund(self, sepa_reference, amount):
        # Refunds for SEPA often require bank processing
        return {'status': 'requested', 'reference': sepa_reference}
